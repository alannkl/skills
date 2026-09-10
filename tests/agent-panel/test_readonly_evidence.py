"""Regressions for the ACP evaluation's unreadable-evidence failure."""
import unittest
import json
from pathlib import Path

import test_panel
from adapters import production_adapters
from execution import ExecutionPolicy


class ReadonlyEvidence(unittest.TestCase):
    run_scenario = test_panel.PanelBehavior.run_scenario

    def test_prompt_allows_file_inspection_without_source_edits(self):
        """Given read-only evidence and three participants, when dispatched, then every prompt permits file inspection without a blanket shell prohibition or write permission."""
        for preset in ('independent-discussion', 'leader-members', 'flat-peers'):
            async def scenario(root):
                fixture = test_panel.Fixture(root, preset)
                report = await fixture.run()
                self.assertEqual(report['outcome'], 'agreed')
                dispatches = [e['data'] for e in fixture.panel.records.events if e['kind'] == 'dispatch']
                for dispatch in dispatches:
                    prompt = Path(dispatch['attempt_dir'], 'input.txt').read_text()
                    payload = json.loads(prompt.split('PANEL_INPUT\n')[1])
                    self.assertTrue(payload['capabilities'].get('file_reads', False))
                    self.assertNotIn('shell', payload['capabilities'])
                    self.assertFalse(payload['capabilities']['workspace_write'])
                    self.assertFalse(payload['capabilities']['source_edits'])
                    self.assertEqual(payload['execution']['workspace'], 'read-only')
                    self.assertIn('read-only shell commands', prompt)
            self.run_scenario(scenario)


    def test_native_readonly_boundaries_survive_resume(self):
        """Given corrected file-read permissions, when native adapters start and resume, then Codex keeps its read-only sandbox and Claude keeps only read tools."""
        capabilities = ExecutionPolicy({}, ['a', 'b'], 'a').capabilities()
        settings = {'model': 'fixture', 'cwd': '/tmp/evidence', 'capabilities': capabilities}
        for name, adapter in production_adapters().items():
            start, session = adapter.command(None, settings)
            resume, _ = adapter.command(session or 'existing-session', settings)
            if name == 'codex':
                self.assertEqual(start[start.index('--sandbox') + 1], 'read-only')
                self.assertIn('sandbox_mode="read-only"', resume)
                self.assertTrue(all('approval_policy="never"' in argv for argv in (start, resume)))
            else:
                self.assertTrue(all(argv[argv.index('--tools') + 1] == 'Read,Grep,Glob' for argv in (start, resume)))
            self.assertFalse(any('bypass' in argument for argument in start + resume))
