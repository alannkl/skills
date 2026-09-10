"""Persistent-panel behavior, pinned before implementation."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import test_panel
from test_panel import Fixture, preset, PACKAGE
from task_fixture import TaskFixture, repository, implement
from fakes import FakeAdapter
from engine import Panel, StopRun
from conversation import continue_panel, stop_panel
from recovery import recover_run
from adapters.base import atomic_json


def saved(root):
    return json.loads((Path(root) / 'run' / 'manifest.json').read_text())


class ContinuationBehavior(unittest.TestCase):
    run_scenario = test_panel.PanelBehavior.run_scenario

    def test_crash_during_report_publication(self):
        """Given a follow-up crash while publishing its report, when continuing or recovering, then never archive the previous answer as the new one or lose its original report."""
        for target in ('discussion-2.json', 'report.json'):
            async def scenario(root):
                f = Fixture(root)
                first = await f.run()
                prior = Path(first['discussion_report']).read_bytes()
                adapter = FakeAdapter()
                panel = continue_panel(Path(root) / 'run', 'Follow-up whose report publication fails', {'fake': adapter})
                def crash(path, value):
                    if Path(path).name == target:
                        raise OSError('Crash while publishing report')
                    return atomic_json(path, value)
                with patch('engine.atomic_json', crash):
                    with self.assertRaisesRegex(OSError, 'publishing'):
                        await panel.run()
                panel.records.close()
                with self.assertRaisesRegex(ValueError, 'recover'):
                    unexpected = continue_panel(Path(root) / 'run', 'Next question', {'fake': adapter})
                    unexpected.records.close()
                before = len(adapter.inputs)
                recovered = recover_run(Path(root) / 'run', {'fake': adapter})
                self.assertEqual(recovered['discussion'], 2)
                self.assertEqual(recovered['outcome'], 'agreed' if target == 'report.json' else 'incomplete')
                self.assertIn('b2-r1', recovered['candidate'])
                self.assertTrue(all(r['revision'] == 'b2-r1' for r in recovered['reviews'].values()))
                self.assertEqual(Path(first['discussion_report']).read_bytes(), prior)
                self.assertEqual(recover_run(Path(root) / 'run', {'fake': adapter}), recovered)
                self.assertEqual(len(adapter.inputs), before)
            with self.subTest(target=target):
                self.run_scenario(scenario)

    def test_followups_keep_sessions_and_shared_history(self):
        """Given three participants in each preset, when two follow-ups arrive after answers, then the same sessions see prior discussion and user decisions and approve each new answer."""
        for name in ('independent-discussion', 'leader-members', 'flat-peers'):
            async def scenario(root):
                f = Fixture(root, name)
                first = await f.run()
                self.assertEqual(first['outcome'], 'agreed')
                sessions = {pid: p['session_id'] for pid, p in saved(root)['participants'].items()}
                all_inputs = list(f.adapter.inputs)
                briefs = ['Design a bounded runner']
                for number, question in enumerate(('Keep the document generic. Explain the tradeoff.', 'Use that decision to recommend skill changes.'), 2):
                    adapter = FakeAdapter()
                    panel = continue_panel(Path(root) / 'run', question, {'fake': adapter})
                    report = await panel.run()
                    self.assertEqual(report['outcome'], 'agreed', report['reason'])
                    self.assertEqual(report['discussion'], number)
                    self.assertEqual(report['conversation'], 'active')
                    self.assertEqual(adapter.sessions, 0, 'A follow-up must only resume saved sessions')
                    self.assertEqual(set(report['reviews']), set(sessions))
                    for pid, session in sessions.items():
                        own = [p for p in adapter.inputs if p['participant_id'] == pid]
                        self.assertEqual({p['session'] for p in own}, {session})
                        self.assertEqual(own[0]['brief'], question)
                        self.assertEqual([b['text'] for b in own[0]['prior_briefs']], briefs)
                        prior_reviews = [e for e in own[0]['events'] if e['kind'] == 'review']
                        self.assertEqual({e['sender'] for e in prior_reviews}, set(sessions))
                        self.assertTrue(all(e['data']['brief_revision'] < own[0]['brief_revision'] for e in prior_reviews))
                        if name == 'independent-discussion':
                            self.assertFalse(any(e['data'].get('brief_revision') == number for e in own[0]['events']))
                    briefs.append(question)
                    all_inputs.extend(adapter.inputs)
                for pid in sessions:
                    delivered = [e['id'] for p in all_inputs if p['participant_id'] == pid for e in p['events']]
                    self.assertEqual(len(delivered), len(set(delivered)), 'Acknowledged events must not be redelivered')
            with self.subTest(preset=name):
                self.run_scenario(scenario)

    def test_each_answer_has_fresh_limits_and_immutable_approval(self):
        """Given an approved answer and elapsed idle time, when following up, then fresh limits apply, old approvals cannot approve the new answer, and the prior report and result stay unchanged."""
        async def scenario(root):
            offset = 0
            clock = SimpleNamespace(monotonic=lambda: time.monotonic() + offset)
            with patch('engine.time', clock), patch('conversation.time', clock):
                f = Fixture(root, max_cycles=1)
                first = await f.run()
                prior = {Path(first[key]): Path(first[key]).read_bytes() for key in ('candidate', 'discussion_report')}
                stale = first['reviews']['cy']
                adapter = FakeAdapter(lambda p: dict(stale) if p['phase'] == 'review' and p['participant_id'] == 'cy' else None)
                offset = 100000
                panel = continue_panel(Path(root) / 'run', 'A different question needing new approval', {'fake': adapter})
                second = await panel.run()
            self.assertEqual(second['outcome'], 'incomplete')
            self.assertFalse(second['approved'])
            self.assertEqual(second['required_approvers'], ['ada', 'bert', 'cy'])
            self.assertEqual(second['reviews']['ada']['revision'], 'b2-r1')
            self.assertNotIn('cy', second['reviews'])
            self.assertIn('stale', second['failures'][0]['error'])
            self.assertNotEqual(first['candidate'], second['candidate'])
            for path, content in prior.items():
                self.assertEqual(path.read_bytes(), content)
            self.assertEqual(len(second['usage']), len(adapter.inputs))
        self.run_scenario(scenario)

    def test_working_copies_survive_followup(self):
        """Given approved edits in isolated workspaces, when following up, then participants retain their workspaces and files while the caller checkout stays unchanged."""
        async def scenario(root):
            repo = repository(Path(root))
            f = TaskFixture(root, 'implementation', behavior=implement, repo=repo,
                            execution={'workspace': 'edit', 'checks': [[sys.executable, 'verify.py']]})
            first = await f.run()
            self.assertEqual(first['outcome'], 'agreed')
            directories = dict(f.panel.workspaces.directories)
            contents = {pid: (Path(cwd) / 'solution.py').read_bytes() for pid, cwd in directories.items()}
            adapter = FakeAdapter()
            panel = continue_panel(Path(root) / 'run', 'Explain the implemented change and retain it.', {'fake': adapter})
            second = await panel.run()
            self.assertEqual(second['outcome'], 'agreed', second['reason'])
            self.assertTrue(second['verification']['passed'])
            for p in adapter.inputs:
                self.assertEqual(p['working_directory'], directories[p['participant_id']])
            for pid, cwd in directories.items():
                self.assertEqual((Path(cwd) / 'solution.py').read_bytes(), contents[pid])
            self.assertEqual((repo / 'solution.py').read_text(), 'def value():\n    return 0\n')
            self.assertEqual(Path(first['artifacts']['patch']).read_bytes(), Path(second['artifacts']['patch']).read_bytes())
        self.run_scenario(scenario)

    def test_stop_prevents_dispatch_and_reset_starts_fresh(self):
        """Given an idle panel, when stopped for stop or solo, then continuation launches nobody; an explicit new panel has fresh sessions and preserves the old records."""
        async def scenario(root):
            f = Fixture(root)
            first = await f.run()
            report_bytes = Path(first['discussion_report']).read_bytes()
            first_sessions = {p['session_id'] for p in saved(root)['participants'].values()}
            stopped = stop_panel(Path(root) / 'run')
            self.assertEqual(stopped['conversation'], 'stopped')
            before = (Path(root) / 'run' / 'events.jsonl').read_bytes()
            self.assertEqual(stop_panel(Path(root) / 'run'), stopped)
            self.assertEqual((Path(root) / 'run' / 'events.jsonl').read_bytes(), before)
            adapter = FakeAdapter()
            with self.assertRaisesRegex(ValueError, 'stopped'):
                continue_panel(Path(root) / 'run', 'Another question', {'fake': adapter})
            self.assertEqual(adapter.inputs, [])
            fresh = Panel(preset('independent-discussion'), 'Explicit reset', f.roster, Path(root) / 'reset', {'fake': adapter})
            self.assertEqual((await fresh.run())['outcome'], 'agreed')
            self.assertTrue(first_sessions.isdisjoint({p['session_id'] for p in fresh.people.values()}))
            self.assertEqual(Path(first['discussion_report']).read_bytes(), report_bytes)
        self.run_scenario(scenario)

    def test_active_or_uncertain_panel_cannot_continue(self):
        """Given an active writer, unrecovered crash, or indeterminate invocation, when continuing, then reject before dispatch and preserve required participants and prior evidence."""
        async def scenario(root):
            f = Fixture(root)
            adapter = FakeAdapter()
            with self.assertRaisesRegex(ValueError, 'active writer'):
                continue_panel(Path(root) / 'run', 'Follow up', {'fake': adapter})
            f.panel.records.close()
            with self.assertRaisesRegex(ValueError, 'recover'):
                continue_panel(Path(root) / 'run', 'Follow up', {'fake': adapter})
            self.assertEqual(adapter.inputs, [])
        self.run_scenario(scenario)
        async def uncertain(root):
            f = Fixture(root)
            first = await f.run()
            before = Path(first['discussion_report']).read_bytes()
            adapter = FakeAdapter(lambda p: 'uncertain')
            panel = continue_panel(Path(root) / 'run', 'Possible effects with unknown completion', {'fake': adapter})
            self.assertEqual((await panel.run())['outcome'], 'incomplete')
            next_adapter = FakeAdapter()
            with self.assertRaisesRegex(ValueError, 'Indeterminate'):
                continue_panel(Path(root) / 'run', 'Try again', {'fake': next_adapter})
            self.assertEqual(next_adapter.inputs, [])
            self.assertEqual(saved(root)['required_approvers'], ['ada', 'bert', 'cy'])
            self.assertEqual(Path(first['discussion_report']).read_bytes(), before)
        self.run_scenario(uncertain)

    def test_resume_failure_does_not_replace_participant(self):
        """Given saved participants, when resume fails or returns a different session, then return incomplete without starting replacements or changing saved identities."""
        class WrongSession(FakeAdapter):
            def resume(self, session_id, input, settings):
                return self.launch(session_id + '-replacement', input, settings)
        for adapter in (FakeAdapter(lambda p: 'fail'), WrongSession()):
            async def scenario(root):
                f = Fixture(root)
                await f.run()
                sessions = {pid: p['session_id'] for pid, p in saved(root)['participants'].items()}
                panel = continue_panel(Path(root) / 'run', 'Follow up', {'fake': adapter})
                report = await panel.run()
                self.assertEqual(report['outcome'], 'incomplete')
                self.assertEqual(adapter.sessions, 0)
                self.assertEqual({pid: p['session_id'] for pid, p in saved(root)['participants'].items()}, sessions)
                self.assertEqual(report['required_approvers'], ['ada', 'bert', 'cy'])
            self.run_scenario(scenario)

    def test_recovery_only_reconciles_current_discussion(self):
        """Given a crash during a follow-up, when recovering repeatedly, then retain previous reports, reconcile only the current discussion once, and never reuse old approval."""
        async def scenario(root):
            f = Fixture(root)
            first = await f.run()
            first_bytes = Path(first['discussion_report']).read_bytes()
            adapter = FakeAdapter()
            panel = continue_panel(Path(root) / 'run', 'Follow up before crash', {'fake': adapter})
            original = panel.records.append
            def crash(kind, *args, **kwargs):
                if kind == 'message':
                    raise OSError('Crash after durable terminal before message')
                return original(kind, *args, **kwargs)
            panel.records.append = crash
            with self.assertRaises(StopRun):
                await panel.round('initial', panel.ids, 'Discuss follow-up', private=True)
            panel.records.close()
            before = len(adapter.inputs)
            recovered = recover_run(Path(root) / 'run', {'fake': adapter})
            self.assertEqual(recovered['outcome'], 'incomplete')
            self.assertEqual(recovered['discussion'], 2)
            self.assertIsNone(recovered['candidate'])
            self.assertEqual(recovered['reviews'], {})
            self.assertEqual(len(recovered['usage']), 3)
            self.assertEqual(recover_run(Path(root) / 'run', {'fake': adapter}), recovered)
            self.assertEqual(len(adapter.inputs), before)
            self.assertEqual(Path(first['discussion_report']).read_bytes(), first_bytes)
            resumed = continue_panel(Path(root) / 'run', 'Continue after reconciled crash', {'fake': adapter})
            self.assertEqual((await resumed.run())['outcome'], 'agreed')
        self.run_scenario(scenario)

    def test_legacy_completed_panel_continues_explicitly(self):
        """Given a completed version-3 panel, when explicitly continuing, then retain its sessions and original report while adding a new discussion."""
        async def scenario(root):
            f = Fixture(root)
            first = await f.run()
            manifest = saved(root)
            manifest['version'] = 3
            for key in ('discussion', 'discussion_start', 'conversation'):
                manifest.pop(key)
            atomic_json(Path(root) / 'run' / 'manifest.json', manifest)
            Path(first['discussion_report']).unlink()
            for key in ('discussion', 'conversation', 'discussion_report'):
                first.pop(key)
            atomic_json(Path(root) / 'run' / 'report.json', first)
            old_bytes = (Path(root) / 'run' / 'report.json').read_bytes()
            adapter = FakeAdapter()
            panel = continue_panel(Path(root) / 'run', 'Continue the old panel', {'fake': adapter})
            self.assertEqual((await panel.run())['outcome'], 'agreed')
            self.assertEqual(adapter.sessions, 0)
            self.assertEqual((Path(root) / 'run' / 'reports' / 'discussion-1.json').read_bytes(), old_bytes)
            self.assertEqual(saved(root)['version'], 4)
        self.run_scenario(scenario)

    def test_cli_continuation_and_stop(self):
        """Given a panel run through the CLI, when continuing in another process and then stopping, then preserve sessions, deliver follow-up context, and reject later continuation without model calls."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plugin = root / 'adapter.py'
            plugin.write_text('import sys\nsys.path.insert(0, ' + repr(str(Path(__file__).resolve().parent)) + ')\nfrom fakes import FakeAdapter\ndef create_adapter():\n    return FakeAdapter()\n')
            roster = {'drafter': 'a', 'participants': [{'id': pid, 'role': 'Contributor', 'harness': 'fixture', 'settings': {'model': 'fixture'}} for pid in ('a', 'b', 'c')]}
            (root / 'roster.json').write_text(json.dumps(roster))
            (root / 'brief.md').write_text('Initial question')
            (root / 'followup.md').write_text('Keep the explanation generic.')
            base = [sys.executable, str(PACKAGE / 'scripts' / 'panel.py')]
            registration = ['--adapter', 'fixture=' + str(plugin)]
            def command(*args, expect=0):
                result = subprocess.run(base + list(args) + registration, capture_output=True, text=True, timeout=15)
                self.assertEqual(result.returncode, expect, result.stdout + result.stderr)
                return json.loads(result.stdout)
            first = command('independent-discussion', str(root / 'brief.md'), str(root / 'roster.json'), '--run-dir', str(root / 'run'))
            sessions = {pid: p['session_id'] for pid, p in saved(root)['participants'].items()}
            second = command('--continue', str(root / 'run'), '--follow-up', str(root / 'followup.md'))
            self.assertEqual(second['discussion'], 2)
            self.assertEqual({pid: p['session_id'] for pid, p in saved(root)['participants'].items()}, sessions)
            prompts = [p.read_text() for p in (root / 'run' / 'participants').glob('*/*/input.txt')]
            self.assertTrue(any('Keep the explanation generic.' in p and 'Initial question' in p for p in prompts))
            for invalid in (['--run-seconds', '20'], ['--run-dir', str(root / 'replacement')]):
                failed = command('--continue', str(root / 'run'), '--follow-up', str(root / 'followup.md'), *invalid, expect=2)
                self.assertIn('retain', failed['error'])
            self.assertEqual(command('--stop', str(root / 'run'))['conversation'], 'stopped')
            events = (root / 'run' / 'events.jsonl').read_bytes()
            command('--continue', str(root / 'run'), '--follow-up', str(root / 'followup.md'), expect=2)
            self.assertEqual((root / 'run' / 'events.jsonl').read_bytes(), events)
            self.assertTrue(Path(first['candidate']).exists())
