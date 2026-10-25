"""Adapter acceptance scenarios, fixed before subprocess fixtures."""
import unittest
import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'agent-panel' / 'scripts'))
from adapters import production_adapters
from adapters.base import atomic_json
from records import Records

PACKAGE = Path(__file__).resolve().parents[2] / 'agent-panel'
EXECUTABLE = str(Path(__file__).resolve().with_name('harness_fixture.py'))


def settings(root, attempt='turn'):
    return {'model': 'fixture', 'effort': 'high', 'cwd': root,
            'attempt_dir': str(Path(root) / attempt), 'executable': EXECUTABLE}



class AdapterBehavior(unittest.TestCase):
    def run_scenario(self, scenario):
        with tempfile.TemporaryDirectory() as root:
            asyncio.run(scenario(root))

    def test_terminal_validation(self):
        """Given valid and malformed native output, when normalized, then only a terminal success with structured JSON is completed."""

        adapters = production_adapters()
        valid_claude = {'type': 'result', 'subtype': 'success', 'session_id': 's1', 'is_error': False,
                        'result': '{"text":"ok"}', 'usage': {'input_tokens': 2}}
        valid_codex = [{'type': 'thread.started', 'thread_id': 's1'},
                       {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': '{"text":"ok"}'}},
                       {'type': 'turn.completed', 'usage': {'input_tokens': 2}}]
        encoded = lambda events: '\n'.join(json.dumps(e) for e in events)
        self.assertEqual(adapters['claude'].parse(json.dumps(valid_claude), 0, 's1').outcome, 'completed')
        self.assertEqual(adapters['codex'].parse(encoded(valid_codex), 0, None).outcome, 'completed')
        for adapter in adapters.values():
            for raw in ('not-json', '[]', '{}', 'null'):
                self.assertNotEqual(adapter.parse(raw, 0, 's1').outcome, 'completed')
        for change in ({'subtype': 'error_max_turns'}, {'is_error': True}, {'session_id': 's2'}, {'result': 'prose'}, {'permission_denials': [{'tool_name': 'Read'}]}):
            result = adapters['claude'].parse(json.dumps(dict(valid_claude, **change)), 0, 's1')
            self.assertNotEqual(result.outcome, 'completed')
            if 'permission_denials' in change:
                self.assertEqual(result.outcome, 'blocked')
        for events in (valid_codex[:-1], valid_codex + [{'type': 'error'}], valid_codex + [valid_codex[-1]],
                       valid_codex + [{'type': 'turn.failed'}]):
            self.assertNotEqual(adapters['codex'].parse(encoded(events), 0, 's1').outcome, 'completed')
        self.assertNotEqual(adapters['codex'].parse(encoded(valid_codex), 9, 's1').outcome, 'completed')
        self.assertNotEqual(adapters['codex'].parse(encoded(valid_codex), 0, 'different').outcome, 'completed')


    def test_explicit_resume_settings(self):
        """Given a recorded session and settings, when resumed, then model, effort, cwd and permissions persist without start-only flags or credential changes."""

        for name, adapter in production_adapters().items():
            first, session = adapter.command(None, settings('/tmp'))
            resumed, _ = adapter.command(session or 'known-session', settings('/tmp'))
            self.assertEqual(first[first.index('--model') + 1], 'fixture')
            self.assertEqual(resumed[resumed.index('--model') + 1], 'fixture')
            self.assertFalse(any('bypass' in x for x in first + resumed))
            if name == 'codex':
                self.assertIn('--cd', first)
                self.assertNotIn('--cd', resumed)
                self.assertNotIn('--sandbox', resumed)
                self.assertIn('sandbox_mode="read-only"', resumed)
                self.assertIn('model_reasoning_effort="high"', resumed)
                self.assertIn('approval_policy="never"', resumed)
                self.assertEqual(resumed[-2], 'known-session')
            else:
                self.assertEqual(resumed[resumed.index('--permission-mode') + 1], 'auto')
                self.assertIn('--resume', resumed)
                self.assertIn('Read,Grep,Glob', resumed)
                self.assertNotIn('--bare', resumed)


    def test_subprocess_start_resume(self):
        """Given executable harness fixtures, when started and resumed, then return immediate handles, capture outputs and reuse each distinct session."""

        async def scenario(root):
            for name, adapter in production_adapters().items():
                first = adapter.start('remember marker', settings(root, name + '-first'))
                self.assertIsNotNone(first.completion)
                self.assertFalse(first.completion.done())
                result = await asyncio.wait_for(first.completion, 3)
                self.assertEqual(result.outcome, 'completed', result.error)
                resumed = adapter.resume(result.session_id, 'repeat marker', settings(root, name + '-resume'))
                response = await asyncio.wait_for(resumed.completion, 3)
                self.assertEqual(response.outcome, 'completed', response.error)
                self.assertEqual(result.session_id, response.session_id)
                self.assertEqual(response.block, {'text': 'repeat marker'})
                self.assertTrue(Path(root, name + '-resume', 'stdout').is_file())
                command = json.loads(Path(root, name + '-resume', 'command.json').read_text())
                self.assertEqual(command['cwd'], root)
        self.run_scenario(scenario)


    def test_process_group_cancel(self):
        """Given a running process with a child, when cancelled, then stop both before confirming inactive and preserve cancellation evidence."""

        async def scenario(root):
            adapter = production_adapters()['codex']
            handle = adapter.start('WAIT_WITH_CHILD', settings(root))
            stdout = Path(root, 'turn', 'stdout')
            limit = time.monotonic() + 3
            while not stdout.exists() or not stdout.read_text().strip():
                self.assertLess(time.monotonic(), limit)
                await asyncio.sleep(0.01)
            pids = json.loads(stdout.read_text())
            self.assertTrue(await adapter.cancel(handle))
            self.assertTrue(handle.completion.done())
            self.assertIsNotNone(handle.process.returncode)
            for pid in pids.values():
                with self.assertRaises(ProcessLookupError):
                    os.kill(pid, 0)
        self.run_scenario(scenario)


    def test_cancel_before_launch(self):
        """Given a handle whose process has not started, when immediately cancelled, then no child can escape the cancellation."""

        async def scenario(root):
            adapter = production_adapters()['claude']
            handle = adapter.start('must not escape cancellation', settings(root))
            self.assertTrue(await adapter.cancel(handle))
            self.assertTrue(handle.completion.done())
            self.assertIsNone(handle.process)
            self.assertNotEqual(handle.completion.result().outcome, 'completed')
        self.run_scenario(scenario)


    def test_recover_raw_output(self):
        """Given persisted raw output and confirmed exit without normalized output, when recovered, then accept the valid terminal without execution."""

        async def scenario(root):
            adapter = production_adapters()['codex']
            result = await adapter.start('persisted result', settings(root)).completion
            Path(root, 'turn', 'terminal.json').unlink()
            recovered = adapter.recover(Path(root) / 'turn')
            self.assertEqual(recovered.outcome, 'completed')
            self.assertEqual(recovered.session_id, result.session_id)
            self.assertEqual(recovered.block, {'text': 'persisted result'})
            Path(root, 'turn', 'exit.json').unlink()
            self.assertEqual(adapter.recover(Path(root) / 'turn').outcome, 'indeterminate')
        self.run_scenario(scenario)


    def test_cli(self):
        """Given a disposable three-member roster using executable fixtures, when invoked through the CLI, then all presets print artifact paths and correct exit codes."""

        for name in ('independent-discussion', 'leader-members', 'flat-peers'):
            with tempfile.TemporaryDirectory() as root:
                source = Path(root, 'source')
                source.mkdir()
                Path(source, 'evidence.txt').write_text('Task evidence')
                Path(root, 'brief.md').write_text('Design a panel')
                roster = {'source': 'source', 'drafter': 'a', 'leader': 'a', 'participants':
                          [{'id': pid, 'role': 'designer', 'harness': harness, 'settings': {'model': 'fixture', 'executable': EXECUTABLE}}
                           for pid, harness in [('a', 'claude'), ('b', 'codex'), ('c', 'codex')]]}
                atomic_json(Path(root, 'roster.json'), roster)
                command = [sys.executable, str(PACKAGE / 'scripts' / 'panel.py'), name,
                           str(Path(root, 'brief.md')), str(Path(root, 'roster.json')), '--run-dir', str(Path(root, 'run'))]
                proc = subprocess.run(command, text=True, capture_output=True, timeout=15)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                report = json.loads(proc.stdout)
                self.assertEqual(report['outcome'], 'agreed')
                self.assertTrue(Path(report['candidate']).is_file())
                self.assertTrue(Path(report['report']).is_file())
                self.assertEqual(len(report['reviews']), 3)


    def test_single_writer(self):
        """Given an active runner, when another writer attempts recovery, then reject it without changing authoritative records."""

        with tempfile.TemporaryDirectory() as root:
            records = Records(Path(root) / 'run')
            records.append('run_start', 'setup')
            before = records.log.read_bytes()
            with self.assertRaisesRegex(ValueError, 'active writer'):
                Records(records.root, existing=True)
            self.assertEqual(records.log.read_bytes(), before)
            records.close()
