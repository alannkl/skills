"""A setup composed from harness, model, effort and provider resolves to the same config as its preset."""
import json
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "eval-agent-instructions" / "scripts"
sys.path.insert(0, str(SCRIPTS))
from setups import catalog, provider_order, resolve  # noqa: E402

SETTINGS = json.loads((SCRIPTS / "configs.json").read_text())


class Setups(unittest.TestCase):
    def test_a_composed_setup_matches_its_preset(self):
        name, config = resolve({"harness": "openclaw", "model": "deepseek-v4.1-flash", "provider": "morph"}, SETTINGS)
        self.assertEqual(name, "openclaw-deepseek-v4.1-flash-high-morph")
        self.assertEqual(config, catalog(SETTINGS)[name])

    def test_name_follows_harness_model_effort_and_first_provider(self):
        self.assertEqual(resolve({"harness": "claude-code", "model": "opus-5.5"}, SETTINGS)[0],
                         "claude-code-opus-5.5-high")
        self.assertEqual(resolve({"harness": "openclaw", "model": "deepseek-v4.1-flash", "effort": "max",
                                  "provider": "siliconflow"}, SETTINGS)[0],
                         "openclaw-deepseek-v4.1-flash-max-siliconflow")
        self.assertEqual(resolve({"harness": "openclaw", "model": "mimo-v2.6-pro"}, SETTINGS)[0],
                         "openclaw-mimo-v2.6-pro-high-xiaomi")
        self.assertEqual(resolve({"harness": "openclaw", "model": "mimo-v2.6-pro", "effort": "default"}, SETTINGS)[0],
                         "openclaw-mimo-v2.6-pro-default-xiaomi")

    def test_provider_order(self):
        preferred = ["morph", "siliconflow", "relace"]
        self.assertEqual(provider_order(None, preferred), preferred)
        self.assertEqual(provider_order("siliconflow", preferred), ["siliconflow", "morph", "relace"])
        self.assertEqual(provider_order("deepseek", preferred), ["deepseek"])
        self.assertEqual(provider_order("relace,morph", preferred), ["relace", "morph"])

    def test_a_model_outside_the_catalog_is_given_by_its_full_id(self):
        name, config = resolve({"harness": "openclaw", "model": "openrouter/acme/rocket-2"}, SETTINGS)
        self.assertEqual(name, "openclaw-rocket-2-high")
        self.assertEqual(config["model"], "openrouter/acme/rocket-2")
        self.assertNotIn("openrouter_providers", config)
        with self.assertRaises(SystemExit):
            resolve({"harness": "openclaw", "model": "rocket-2"}, SETTINGS)

    def test_provider_needs_an_openrouter_model(self):
        with self.assertRaises(SystemExit):
            resolve({"harness": "claude-code", "model": "opus-5.5", "provider": "morph"}, SETTINGS)


if __name__ == "__main__":
    unittest.main()
