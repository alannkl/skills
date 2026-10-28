"""Each harness's evidence extractor reports which skills actually reached the agent, and from where."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "eval-agent-instructions" / "scripts"))
import evidence  # noqa: E402
from evidence import api, claude_code, codex, openclaw, openrouter_generations  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class Extractors(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def copy(self, harness: str) -> Path:
        dest = self.tmp / harness
        shutil.copytree(FIXTURES / harness, dest)
        return dest

    def rewrite_lines(self, path: Path, edit) -> None:
        lines = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        kept = [edit(e) for e in lines]
        path.write_text("\n".join(json.dumps(e) for e in kept if e is not None) + "\n")

    def test_operations_carry_what_the_agent_read_with_its_output(self):
        ops = claude_code(FIXTURES / "claude-code")["ops"]
        self.assertTrue(any(op["kind"] == "read" and op["path"] == "/app/docs/onboarding.md" and op["output"] for op in ops))
        ops = codex(FIXTURES / "codex")["ops"]
        self.assertTrue(any(op["kind"] == "exec" and "cat /root/.agents/skills/shorten-it/SKILL.md" in op["path"]
                            and "name: shorten-it" in op["output"] for op in ops))

    def test_claude_code_counts_skill_injected_from_installed_directory(self):
        e = claude_code(FIXTURES / "claude-code")
        self.assertTrue(e["complete"])
        self.assertEqual((e["skills_loaded"], e["foreign_skills_loaded"]), (["shorten-it"], []))
        self.assertEqual(e["models"], ["claude-haiku-5-5"])
        self.assertIn("shorten-it", e["skills_listed"])
        self.assertIsNotNone(e["cost_usd"])

    def test_claude_code_reports_same_named_skill_from_elsewhere_as_foreign(self):
        agent = self.copy("claude-code")

        def move_base_dir(e):
            return json.loads(json.dumps(e).replace("/logs/agent/sessions/skills/shorten-it", "/opt/builtin/shorten-it"))
        self.rewrite_lines(agent / "claude-code.txt", move_base_dir)
        e = claude_code(agent)
        self.assertEqual((e["skills_loaded"], e["foreign_skills_loaded"]), ([], ["shorten-it"]))

    def test_claude_code_final_message_keeps_every_turns_reply_but_no_subagent_text(self):
        agent = self.tmp / "turns"
        agent.mkdir()
        say = lambda text, parent=None: {"type": "assistant", "parent_tool_use_id": parent,
                                         "message": {"model": "m", "content": [{"type": "text", "text": text}]}}
        result = lambda tokens: {"type": "result", "usage": {"input_tokens": tokens, "service_tier": "standard"},
                                 "total_cost_usd": 1.0}
        events = [say("working"), say("subagent report", parent="toolu_1"), say("full report"), result(10),
                  result(5), say("see my last message"), result(1)]
        (agent / "claude-code.txt").write_text("".join(json.dumps(e) + "\n" for e in events))
        e = claude_code(agent)
        self.assertEqual(e["final_message"], "full report\n\nsee my last message")
        self.assertEqual(e["messages"], ["working", "full report", "see my last message"])
        self.assertEqual(e["usage"]["input_tokens"], 16)

    def test_every_extractor_keeps_each_assistant_message_in_order(self):
        agent = self.copy("codex")
        said = lambda text: {"type": "item.completed", "item": {"type": "agent_message", "text": text}}
        with open(agent / "codex.txt", "a") as f:
            f.write(json.dumps(said("plan")) + "\n" + json.dumps(said("done")) + "\n")
        e = codex(agent)
        self.assertEqual(e["messages"][-2:], ["plan", "done"])
        self.assertEqual(e["final_message"], "done")
        agent = self.copy("openclaw")
        reply = lambda blocks: {"source": "transcript", "type": "assistant.message",
                                "data": {"message": {"role": "assistant", "content": blocks}}}
        with open(agent / "openclaw-trajectory" / "events.jsonl", "a") as f:
            for blocks in ([{"type": "thinking", "thinking": "t"}, {"type": "text", "text": "checking"}],
                           [{"type": "toolCall", "name": "read"}], [{"type": "text", "text": "all done"}]):
                f.write(json.dumps(reply(blocks)) + "\n")
        self.assertEqual(openclaw(agent)["messages"], ["checking", "all done"])
        # An export without transcript text still yields the reply.
        self.assertEqual(openclaw(FIXTURES / "openclaw")["messages"], [openclaw(FIXTURES / "openclaw")["final_message"]])
        (self.tmp / "api").mkdir()
        (self.tmp / "api" / "api.json").write_text(json.dumps({"text": "Refund approved."}))
        self.assertEqual(api(self.tmp / "api")["messages"], ["Refund approved."])

    def test_codex_counts_a_read_that_returned_the_skill(self):
        e = codex(FIXTURES / "codex")
        self.assertEqual(e["skills_loaded"], ["shorten-it"])
        self.assertEqual(e["models"], ["gpt-6-luna"])

    def test_codex_records_file_change_writes(self):
        agent = self.copy("codex")
        change = {"type": "item.completed", "item": {"id": "x", "type": "file_change", "status": "completed",
                                                      "changes": [{"path": "/app/AGENTS.md", "kind": "update"}]}}
        with open(agent / "codex.txt", "a") as f:
            f.write(json.dumps(change) + "\n")
        self.assertEqual(codex(agent)["writes"], ["/app/AGENTS.md"])

    def test_codex_command_that_names_the_skill_without_reading_it_is_not_a_load(self):
        agent = self.copy("codex")

        def existence_check_only(e):
            item = e.get("item") or {}
            if "SKILL.md" in item.get("command", ""):
                item["command"] = "/bin/bash -lc 'test -f /root/.agents/skills/shorten-it/SKILL.md'"
                item["aggregated_output"] = ""
            return e
        self.rewrite_lines(agent / "codex.txt", existence_check_only)
        self.assertEqual(codex(agent)["skills_loaded"], [])

    def test_codex_reading_only_the_frontmatter_is_not_a_load(self):
        agent = self.copy("codex")

        def head_only(e):
            item = e.get("item") or {}
            if "SKILL.md" in item.get("command", ""):
                item["aggregated_output"] = "---\nname: shorten-it\n"
            return e
        self.rewrite_lines(agent / "codex.txt", head_only)
        self.assertEqual(codex(agent)["skills_loaded"], [])

    def test_codex_same_named_copy_outside_the_install_root_is_foreign(self):
        agent = self.copy("codex")

        def elsewhere(e):
            item = e.get("item") or {}
            if "SKILL.md" in item.get("command", ""):
                item["command"] = item["command"].replace("/root/.agents/skills/", "/opt/builtin/.agents/skills/")
            return e
        self.rewrite_lines(agent / "codex.txt", elsewhere)
        e = codex(agent)
        self.assertEqual((e["skills_loaded"], e["foreign_skills_loaded"]), ([], ["shorten-it"]))

    def test_codex_read_of_the_task_skills_dir_counts_as_the_installed_copy(self):
        agent = self.copy("codex")

        def from_skills_dir(e):
            item = e.get("item") or {}
            if "SKILL.md" in item.get("command", ""):
                item["command"] = item["command"].replace("/root/.agents/skills/", "/skills/")
            return e
        self.rewrite_lines(agent / "codex.txt", from_skills_dir)
        e = codex(agent)
        self.assertEqual((e["skills_loaded"], e["foreign_skills_loaded"]), (["shorten-it"], []))

    def test_codex_transcript_without_turn_completed_is_unknown(self):
        agent = self.copy("codex")
        self.rewrite_lines(agent / "codex.txt", lambda e: None if e.get("type") == "turn.completed" else e)
        e = codex(agent)
        self.assertFalse(e["complete"])
        self.assertIsNone(e["skills_loaded"])
        self.assertIsNone(e["writes"])

    def test_openclaw_counts_reads_but_not_writes_that_mention_the_skill(self):
        e = openclaw(FIXTURES / "openclaw")
        self.assertEqual(e["skills_loaded"], ["shorten-it"])
        self.assertEqual(e["models"], ["deepseek/deepseek-v4.1-flash-1017"])
        self.assertIs(e["rerouted"], False)
        self.assertEqual(e["thinking"], "high")
        agent = self.copy("openclaw")

        def note_instead_of_read(e):
            args = e["data"].get("args", {})
            if "SKILL.md" in args.get("path", ""):
                e["data"]["name"] = "write"
            return e
        self.rewrite_lines(agent / "openclaw-trajectory" / "events.jsonl", note_instead_of_read)
        e = openclaw(agent)
        self.assertEqual(e["skills_loaded"], [])
        self.assertIn("$OPENCLAW_STATE_DIR/skills/shorten-it/SKILL.md", e["writes"])

    def test_openclaw_log_line_inside_the_json_envelope_is_skipped(self):
        agent = self.copy("openclaw")
        path = agent / "openclaw.txt"
        lines = path.read_text().splitlines(keepends=True)
        middle = next(i for i, line in enumerate(lines) if line.startswith("  ") and i > 5)
        lines.insert(middle, " [agents/agent-command] [agent] run x ended with stopReason=stop\n")
        path.write_text("".join(lines))
        e = openclaw(agent)
        self.assertTrue(e["complete"])
        self.assertEqual(e["thinking"], "high")

    def test_openclaw_log_line_spliced_mid_line_is_skipped(self):
        agent = self.copy("openclaw")
        path = agent / "openclaw.txt"
        text = path.read_text()
        cut = text.index('"', text.index("\n{") + 10)
        path.write_text(text[:cut] + "[agents/agent-command] [agent] run x ended with stopReason=stop\n" + text[cut:])
        e = openclaw(agent)
        self.assertTrue(e["complete"])
        self.assertEqual(e["thinking"], "high")

    def test_openclaw_export_without_its_end_event_is_unknown(self):
        agent = self.copy("openclaw")
        self.rewrite_lines(agent / "openclaw-trajectory" / "events.jsonl",
                           lambda e: None if e["type"] == "session.ended" else e)
        e = openclaw(agent)
        self.assertFalse(e["complete"])
        self.assertIsNone(e["writes"])

    def test_openclaw_run_ended_by_the_harness_records_why(self):
        agent = self.copy("openclaw")
        self.assertIsNone(openclaw(agent)["terminal_error"])
        events = agent / "openclaw-trajectory" / "events.jsonl"
        with events.open("a") as f:
            f.write(json.dumps({"type": "model.completed", "data": {"terminalError": "non_deliverable_terminal_turn"}}) + "\n")
        self.assertEqual(openclaw(agent)["terminal_error"], "non_deliverable_terminal_turn")

    def test_openrouter_lookups_are_saved_and_only_failures_repeat(self):
        agent = self.tmp / "agent"
        (agent / "openclaw-trajectory").mkdir(parents=True)
        (agent / "openclaw-trajectory" / "events.jsonl").write_text(
            '{"responseId":"gen-a"}\n{"responseId":"gen-b"}\n{"responseId":"gen-a"}\n')
        looked_up = []

        def lookup(gen_id, key):
            looked_up.append(gen_id)
            return {"id": gen_id, "provider": None, "lookup_error": "down"} if gen_id == "gen-b" and \
                looked_up.count(gen_id) == 1 else {"id": gen_id, "provider": "deepseek"}
        with mock.patch.object(evidence, "_generation", lookup), mock.patch.dict("os.environ", {"OPENROUTER_API_KEY": "k"}):
            self.assertEqual([g.get("lookup_error") for g in openrouter_generations(agent)], [None, "down"])
            self.assertEqual([g["provider"] for g in openrouter_generations(agent)], ["deepseek", "deepseek"])
        self.assertEqual(sorted(looked_up), ["gen-a", "gen-b", "gen-b"])
        # Once every lookup succeeded, a regrade needs no key.
        with mock.patch.dict("os.environ", clear=True):
            self.assertEqual(len(openrouter_generations(agent)), 2)
        # A damaged file means looking everything up again, not a crash.
        (agent / "openrouter-generations.json").write_text('[{"id": "gen-a"')
        with mock.patch.object(evidence, "_generation", lookup), mock.patch.dict("os.environ", {"OPENROUTER_API_KEY": "k"}):
            self.assertEqual(len(openrouter_generations(agent)), 2)

    def test_missing_transcript_is_unknown_not_absent(self):
        agent = self.copy("openclaw")
        shutil.rmtree(agent / "openclaw-trajectory")
        self.assertIsNone(openclaw(agent)["skills_loaded"])
        self.assertIsNone(claude_code(self.tmp / "empty")["skills_loaded"])
        self.assertIsNone(codex(self.tmp / "empty")["skills_loaded"])

    def test_input_tokens_count_cached_input_once_per_harness(self):
        self.assertEqual(evidence.input_tokens({"input_tokens": 8, "cache_creation_input_tokens": 6926,
                                                "cache_read_input_tokens": 90784, "output_tokens": 979}), 97718)
        # Codex and OpenAI count cached input inside input_tokens.
        self.assertEqual(evidence.input_tokens({"input_tokens": 64175, "cached_input_tokens": 46336}), 64175)
        self.assertEqual(evidence.input_tokens({"input": 13497, "output": 1700, "cacheRead": 102656,
                                                "cacheWrite": 0, "total": 117853}), 116153)
        self.assertEqual(evidence.input_tokens({"prompt_tokens": 900, "completion_tokens": 50}), 900)
        self.assertIsNone(evidence.input_tokens(None))


if __name__ == "__main__":
    unittest.main()
