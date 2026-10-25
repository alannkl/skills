"""Prompts reach the model as the artifact says: system text per job or per API call, user text before the request."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "eval-agent-instructions" / "scripts"))
import api_runner  # noqa: E402
from eval_instructions import agent_args, job_plan, trial_dirs  # noqa: E402
from evidence import api  # noqa: E402
from graders import run_graders  # noqa: E402
from tasks import PROBE_CASE, build_tasks, load_suite  # noqa: E402

CLAUDE = {"harness": "claude-code", "model": "anthropic/claude-haiku-5-5", "effort": "high"}
CODEX = {"harness": "codex", "model": "openai/gpt-6-luna", "effort": "high"}
OPENCLAW = {"harness": "openclaw", "model": "openrouter/deepseek/x", "effort": "high",
            "openrouter_providers": ["deepseek"], "context_window": 1000}


class Prompts(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name) / "repo"
        self.suite = self.repo / "evals" / "support"
        case = self.suite / "refund"
        case.mkdir(parents=True)
        (case / "instruction.md").write_text("I want my money back.\n")
        (case / "vars.json").write_text(json.dumps({"product": "Acme"}))
        (case / "graders.json").write_text(json.dumps({"graders": []}))
        (self.repo / "prompt.md").write_text("You answer {{product}} support questions.\n")
        self.out = Path(self._tmp.name) / "tasks"

    def build(self, role, runner="harness", cases=("refund",)):
        (self.suite / "eval.json").write_text(json.dumps(
            {"artifact": {"type": "prompt", "path": "prompt.md", "role": role, "runner": runner}}))
        build_tasks(self.repo, load_suite(self.repo, "support"), [self.suite / c for c in cases],
                    ["with", "without"], "base:test", self.out)

    def test_system_prompt_is_rendered_into_the_with_task_only(self):
        self.build("system")
        self.assertEqual((self.out / "refund--with" / "prompt" / "system.md").read_text(),
                         "You answer Acme support questions.\n")
        self.assertFalse((self.out / "refund--without" / "prompt").exists())
        self.assertEqual((self.out / "refund--with" / "instruction.md").read_text(), "I want my money back.\n")

    def test_user_prompt_goes_before_the_request(self):
        self.build("user")
        self.assertEqual((self.out / "refund--with" / "instruction.md").read_text(),
                         "You answer Acme support questions.\n\nI want my money back.\n")
        self.assertEqual((self.out / "refund--without" / "instruction.md").read_text(), "I want my money back.\n")

    def test_unfilled_placeholder_and_user_prompt_probe_stop_the_build(self):
        (self.suite / "refund" / "vars.json").unlink()
        with self.assertRaises(SystemExit):
            self.build("system")
        with self.assertRaises(SystemExit):
            self.build("user", cases=(PROBE_CASE,))

    def test_each_system_prompt_task_gets_its_own_job(self):
        self.build("system")
        plan = job_plan(self.out, ["refund--with", "refund--without"], [], load_suite(self.repo, "support")["artifact"])
        self.assertEqual(plan, [("main", ["refund--without"], None),
                                ("refund--with", ["refund--with"], "You answer Acme support questions.\n")])

    def test_system_prompt_reaches_each_harness_its_own_way(self):
        self.assertIn("append_system_prompt=Be brief.", agent_args(CLAUDE, "Be brief."))
        codex = agent_args(CODEX, "Be brief.")
        config = json.loads(codex[codex.index("--ak", codex.index("reasoning_effort=high")) + 1].split("=", 1)[1])
        self.assertEqual(config, {"skills": {"bundled": {"enabled": False}}, "developer_instructions": "Be brief."})
        with self.assertRaises(SystemExit):
            agent_args(OPENCLAW, "Be brief.")
        self.assertEqual(agent_args(CODEX), agent_args(CODEX, None))

    def test_api_requests_carry_the_system_prompt_per_provider(self):
        env = {"ANTHROPIC_BASE_URL": "http://proxy", "ANTHROPIC_AUTH_TOKEN": "t", "OPENROUTER_API_KEY": "k"}
        with mock.patch.dict(os.environ, env):
            url, body, _ = api_runner.build_request({"model": "anthropic/claude-haiku-5-5", "effort": "high"}, "S", "U")
            self.assertEqual((url, body["system"], body["output_config"]), ("http://proxy/v1/messages", "S",
                                                                            {"effort": "high"}))
            url, body, _ = api_runner.build_request({"model": "openai/gpt-6-luna"}, "S", "U")
            self.assertEqual((url, body["instructions"], body["input"]), ("http://proxy/v1/responses", "S", "U"))
            url, body, _ = api_runner.build_request({"model": "openrouter/deepseek/x", "effort": "max",
                                                     "openrouter_providers": ["a", "b"], "max_tokens": 9}, None, "U")
            self.assertEqual(body["messages"], [{"role": "user", "content": "U"}])
            self.assertEqual((body["reasoning"], body["provider"], body["max_tokens"]),
                             ({"effort": "max"}, {"order": ["a", "b"], "allow_fallbacks": False}, 9))

    def test_api_trial_is_graded_like_a_harness_trial(self):
        self.build("system", "api")
        reply = {"text": '{"refund": true}', "model": "claude-haiku-5-5", "usage": {}, "cost_usd": None,
                 "provider": None}
        jobs = Path(self._tmp.name) / "jobs" / "api-haiku" / "api"
        with mock.patch.object(api_runner, "call", return_value=reply) as call:
            api_runner.run_api_job({"model": "anthropic/claude-haiku-5-5"}, self.out, ["refund--with"], 2, jobs, 2)
        self.assertEqual(call.call_args.args[1:], ("You answer Acme support questions.\n", "I want my money back.\n"))
        trials = trial_dirs(jobs.parent)
        self.assertEqual(len(trials), 2)
        evidence = api(trials[0] / "agent")
        self.assertEqual((evidence["complete"], evidence["final_message"]), (True, '{"refund": true}'))
        result = run_graders([{"name": "shape", "type": "json", "required": ["refund"]},
                              {"name": "missing", "type": "json", "required": ["reason"]}],
                             "with", trials[0] / "verifier" / "workspace", trials[0] / "verifier" / "workspace",
                             "api", {"final_message": evidence["final_message"], "writes": []}, [])
        self.assertEqual((result["shape"]["pass"], result["missing"]["pass"]), (True, False))


if __name__ == "__main__":
    unittest.main()
