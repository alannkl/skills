"""The report counts the tokens of each text the with arm loads, and a failed count never stops a run."""
import io
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "eval-agent-instructions" / "scripts"))
import token_counts  # noqa: E402
from token_counts import loaded_texts, loaded_tokens  # noqa: E402

ENV = {"ANTHROPIC_BASE_URL": "http://proxy/", "ANTHROPIC_AUTH_TOKEN": "secret-token"}


class LoadedTexts(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def test_skill_counts_each_text_file_in_its_folder_skill_md_first(self):
        skill = self.root / "target"
        (skill / "references").mkdir(parents=True)
        (skill / "evals").mkdir()
        (skill / "SKILL.md").write_text("---\nname: target\n---\nBody\n")
        (skill / "references" / "a.md").write_text("Ref\n")
        (skill / "README.md").write_text("Readme\n")
        (skill / "evals" / "case.md").write_text("not shipped\n")
        (skill / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n\xff\xfe")
        texts = loaded_texts({"type": "skill", "name": "target"}, skill)
        self.assertEqual(texts, [("target/SKILL.md", "---\nname: target\n---\nBody\n"),
                                 ("target/README.md", "Readme\n"), ("target/references/a.md", "Ref\n")])

    def test_instruction_file_counts_as_delivered_and_prompt_as_written(self):
        path = self.root / "SKILL.md"
        path.write_text("---\nname: c\n---\n# Rules\n")
        self.assertEqual(loaded_texts({"type": "instruction-file"}, path, "CLAUDE.md"), [("CLAUDE.md", "# Rules\n")])
        path.write_text("You answer {{product}} questions.\n")
        self.assertEqual(loaded_texts({"type": "prompt", "role": "system"}, path),
                         [("system prompt", "You answer {{product}} questions.\n")])


class LoadedTokens(unittest.TestCase):
    def fake_endpoint(self, counts, sent):
        def urlopen(request, timeout):
            sent.append(request)
            text = json.loads(request.data)["messages"][0]["content"]
            return io.BytesIO(json.dumps({"input_tokens": counts[text]}).encode())
        return urlopen

    def test_anthropic_counts_come_from_the_endpoint_less_a_minimal_message(self):
        sent = []
        with mock.patch.dict(os.environ, ENV), \
                mock.patch.object(token_counts.urllib.request, "urlopen", self.fake_endpoint({"x": 8, "rules": 120}, sent)):
            counts = loaded_tokens({"claude": [("CLAUDE.md", "rules")]}, {"claude": "anthropic/claude-opus-5-5"})
        self.assertEqual(counts, {"claude": [{"path": "CLAUDE.md", "tokens": 112, "method": "count_tokens endpoint"}]})
        request = sent[0]
        self.assertEqual(request.full_url, "http://proxy/v1/messages/count_tokens")
        self.assertEqual((request.get_header("X-api-key"), request.get_header("Authorization")),
                         ("secret-token", "Bearer secret-token"))
        self.assertEqual(json.loads(request.data)["model"], "claude-opus-5-5")

    def test_other_models_get_a_labelled_tiktoken_estimate(self):
        encoding = types.SimpleNamespace(encode=lambda text, disallowed_special: text.split())
        fake = types.SimpleNamespace(get_encoding=lambda name: encoding if name == "o200k_base" else None)
        with mock.patch.dict(sys.modules, {"tiktoken": fake}):
            counts = loaded_tokens({"codex": [("AGENTS.md", "one two three")]}, {"codex": "openai/gpt-6-astra"})
        self.assertEqual(counts["codex"], [{"path": "AGENTS.md", "tokens": 3,
                                            "method": "estimate with tiktoken o200k_base"}])

    def test_a_count_that_fails_is_recorded_with_its_reason_and_never_raises(self):
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.dict(sys.modules, {"tiktoken": None}):
            counts = loaded_tokens({"claude": [("CLAUDE.md", "rules")], "codex": [("AGENTS.md", "rules")]},
                                   {"claude": "anthropic/claude-opus-5-5", "codex": "openai/gpt-6-astra"})
        self.assertEqual(counts["claude"], [{"path": "CLAUDE.md", "tokens": None,
                                             "not_counted": "ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN not set"}])
        self.assertEqual(counts["codex"], [{"path": "AGENTS.md", "tokens": None,
                                            "not_counted": "tiktoken is not installed"}])

        def refused(request, timeout):
            raise token_counts.urllib.error.HTTPError(request.full_url, 404, "Not Found", {}, None)
        with mock.patch.dict(os.environ, ENV), mock.patch.object(token_counts.urllib.request, "urlopen", refused):
            counts = loaded_tokens({"claude": [("CLAUDE.md", "rules")]}, {"claude": "anthropic/claude-opus-5-5"})
        self.assertIsNone(counts["claude"][0]["tokens"])
        self.assertIn("404", counts["claude"][0]["not_counted"])
        self.assertNotIn("secret-token", json.dumps(counts))


if __name__ == "__main__":
    unittest.main()
