"""Consultant behavior, pinned before implementation: one read-only session for second opinions."""
import json
from contextlib import contextmanager
import time
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[2] / 'panel'
SCRIPT = str(PACKAGE / 'scripts' / 'consult.py')
EXECUTABLE = str(Path(__file__).resolve().with_name('harness_fixture.py'))


def run(*args, expect=0):
    result = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True, timeout=20)
    assert result.returncode == expect, result.stdout + result.stderr
    return json.loads(result.stdout)


@contextmanager
def consultation(harness='claude', web_args=()):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / 'brief.md').write_text('Remember the original decision: keep the API stable.')
        (root / 'question.md').write_text('Apply the new user decision.')
        (root / 'attachment.md').write_text('Original attached evidence: retain the response schema.')
        (root / 'repo').mkdir()
        plugin = root / 'adapter.py'
        plugin.write_text('import asyncio, json, sys\nfrom pathlib import Path\n'
                          'sys.path.insert(0, ' + repr(str(PACKAGE / 'scripts')) + ')\n'
                          'from adapters.' + harness + ' import ' + harness.capitalize() + 'Adapter\n'
                          'from adapters.base import Handle, Terminal\n'
                          'class Fixture(' + harness.capitalize() + 'Adapter):\n'
                          '    def note(self, kind, session, prompt, settings):\n'
                          '        root = Path(settings["cwd"]).parent\n'
                          '        with (root / "calls.jsonl").open("a") as stream:\n'
                          '            stream.write(json.dumps(dict(kind=kind, session=session, prompt=prompt)) + "\\n")\n'
                          '        return (root / "mode").read_text() if (root / "mode").exists() else ""\n'
                          '    def start(self, prompt, settings):\n'
                          '        self.note("start", None, prompt, settings)\n'
                          '        return super().start(prompt, settings)\n'
                          '    def resume(self, session, prompt, settings):\n'
                          '        mode = self.note("resume", session, prompt, settings)\n'
                          '        if mode:\n'
                          '            async def reply():\n'
                          '                if mode == "wait":\n                    await asyncio.sleep(3600)\n'
                          '                if mode == "different":\n'
                          '                    return Terminal("other", block={"text":"wrong session"}, exit_status=0, outcome="completed")\n'
                          '                return Terminal(session, exit_status=1, outcome=mode, error=mode)\n'
                          '            return Handle(completion=asyncio.create_task(reply()))\n'
                          '        return super().resume(session, prompt, settings)\n'
                          '    def command(self, session, settings):\n'
                          '        return super().command(session, dict(settings, executable=' + repr(EXECUTABLE) + '))\n'
                          'def create_adapter():\n    return Fixture()\n')
        base = ['--adapter', f'fixture={plugin}']
        run(*base, 'open', str(root / 'c'), '--harness', 'fixture', '--model', 'fixture', '--effort', 'high',
            '--brief', str(root / 'brief.md'), '--read', str(root / 'repo'), '--attach', str(root / 'attachment.md'), *web_args)
        yield root, base


class ConsultBehavior(unittest.TestCase):
    def test_web_default_and_opt_out_persist(self):
        """Given no web flag, --web or --no-web, both harnesses enable web unless opted out and retain that choice on ask and reopen."""
        for harness in ('claude', 'codex'):
            for flags, expected in (((), True), (('--web',), True), (('--no-web',), False)):
                with consultation(harness, flags) as (root, base), self.subTest(harness=harness, flags=flags):
                    directory = root / 'c'
                    run(*base, 'ask', str(directory), '--question', str(root / 'question.md'))
                    run(*base, 'close', str(directory))
                    run(*base, 'reopen', str(directory), '--question', str(root / 'question.md'))
                    manifest = json.loads((directory / 'consult.json').read_text())
                    self.assertIs(manifest['web'], expected)
                    commands = [json.loads((directory / 'turns' / f't{turn}' / 'command.json').read_text())['argv']
                                for turn in (1, 2, 3)]
                    for command in commands:
                        if harness == 'claude':
                            tools = command[command.index('--tools') + 1].split(',')
                            self.assertEqual('WebSearch' in tools, expected)
                            self.assertEqual('WebFetch' in tools, expected)
                            self.assertNotIn('Edit', tools)
                            self.assertNotIn('Write', tools)
                        else:
                            setting = 'web_search="live"' if expected else 'web_search="disabled"'
                            self.assertIn(setting, command)


    def test_reopen_preserves_session_settings_and_history(self):
        """A closed consultation explicitly reopens into its saved session without losing records or settings."""
        for harness in ('claude', 'codex'):
            with consultation(harness) as (root, base), self.subTest(harness=harness):
                c = root / 'c'
                original = json.loads((c / 'consult.json').read_text())
                previous = (c / 'log.jsonl').read_bytes()
                run(*base, 'close', str(c))
                closed = (c / 'consult.json').read_bytes()
                run(*base, 'ask', str(c), '--question', str(root / 'question.md'), expect=2)
                self.assertEqual((c / 'consult.json').read_bytes(), closed)
                missing = run(*base, 'reopen', str(c), '--question', str(root / 'missing.md'), expect=2)
                self.assertFalse(missing['ok'])
                self.assertEqual((c / 'consult.json').read_bytes(), closed)
                result = run(*base, 'reopen', str(c), '--question', str(root / 'question.md'))
                self.assertTrue(result['reopened'])
                self.assertEqual(result['turn'], 2)
                self.assertIn('new user decision', result['text'])
                manifest = json.loads((c / 'consult.json').read_text())
                self.assertEqual(manifest['status'], 'open')
                for key in ('session_id', 'settings', 'harness', 'read_dirs', 'web'):
                    self.assertEqual(manifest[key], original[key])
                self.assertTrue((c / 'log.jsonl').read_bytes().startswith(previous))
                self.assertIn('already open', run(*base, 'reopen', str(c), '--question', str(root / 'question.md'), expect=2)['error'])
                self.assertEqual(run(*base, 'ask', str(c), '--question', str(root / 'question.md'))['turn'], 3)

    def test_reopen_rejects_unavailable_or_unfinished_state(self):
        """Missing identity and incomplete or uncertain records cannot reopen or dispatch."""
        for case in ('no-session', 'pending', 'unrecorded', 'uncertain', 'missing-log'):
            with consultation() as (root, base), self.subTest(case=case):
                c = root / 'c'
                run(*base, 'close', str(c))
                manifest = json.loads((c / 'consult.json').read_text())
                if case == 'no-session':
                    manifest['session_id'] = None
                elif case == 'pending':
                    manifest['pending_turn'] = 2
                elif case == 'unrecorded':
                    (c / 'turns' / 't2').mkdir()
                elif case == 'uncertain':
                    last = json.loads((c / 'log.jsonl').read_text())
                    last.update(ok=False, error='consultant timed out; process may still be running')
                    (c / 'log.jsonl').write_text(json.dumps(last) + '\n')
                else:
                    (c / 'log.jsonl').unlink()
                (c / 'consult.json').write_text(json.dumps(manifest))
                before = (c / 'consult.json').read_bytes()
                calls = (c / 'calls.jsonl').read_bytes()
                result = run(*base, 'reopen', str(c), '--question', str(root / 'question.md'), expect=2)
                self.assertFalse(result['ok'])
                self.assertEqual((c / 'consult.json').read_bytes(), before)
                self.assertEqual((c / 'calls.jsonl').read_bytes(), calls)

    def test_reopen_failure_never_starts_a_replacement(self):
        """Unclassified failure, wrong identity and uncertain delivery never trigger a fresh session."""
        for mode in ('failed', 'different', 'indeterminate'):
            with consultation() as (root, base), self.subTest(mode=mode):
                c = root / 'c'
                run(*base, 'close', str(c))
                original = json.loads((c / 'consult.json').read_text())['session_id']
                (c / 'mode').write_text(mode)
                result = run(*base, 'reopen', str(c), '--question', str(root / 'question.md'), expect=2)
                self.assertFalse(result['ok'])
                manifest = json.loads((c / 'consult.json').read_text())
                self.assertEqual(manifest['session_id'], original)
                calls = [json.loads(line) for line in (c / 'calls.jsonl').read_text().splitlines()]
                self.assertEqual([v['kind'] for v in calls], ['start', 'resume'])
                if mode == 'indeterminate':
                    self.assertEqual(manifest['pending_turn'], 2)
                    run(*base, 'close', str(c), expect=2)
                    run(*base, 'ask', str(c), '--question', str(root / 'question.md'), expect=2)
                    self.assertEqual((c / 'calls.jsonl').read_text().count('"kind"'), 2)

    def test_terminal_resume_failure_starts_fresh_with_saved_context(self):
        """A definitively unavailable saved session starts fresh once with prior questions and replies."""
        with consultation() as (root, base):
            c = root / 'c'
            original = json.loads((c / 'consult.json').read_text())
            previous = (c / 'log.jsonl').read_bytes()
            run(*base, 'close', str(c))
            (c / 'mode').write_text('session_unavailable')
            result = run(*base, 'reopen', str(c), '--question', str(root / 'question.md'))
            self.assertTrue(result['ok'])
            replacement = result['replacement']
            self.assertEqual(replacement['previous_session'], original['session_id'])
            self.assertNotEqual(replacement['new_session'], original['session_id'])
            manifest = json.loads((c / 'consult.json').read_text())
            self.assertEqual(manifest['session_id'], replacement['new_session'])
            self.assertEqual(manifest['retired_sessions'], [original['session_id']])
            self.assertNotIn('pending_turn', manifest)
            self.assertTrue((c / 'log.jsonl').read_bytes().startswith(previous))
            calls = [json.loads(line) for line in (c / 'calls.jsonl').read_text().splitlines()]
            self.assertEqual([v['kind'] for v in calls], ['start', 'resume', 'start'])
            self.assertIn('keep the API stable', calls[-1]['prompt'])
            self.assertIn('Original attached evidence: retain the response schema.', calls[-1]['prompt'])
            self.assertIn('new user decision', calls[-1]['prompt'])
            self.assertIn('reply', calls[-1]['prompt'])
            (c / 'mode').unlink()
            self.assertEqual(run(*base, 'ask', str(c), '--question', str(root / 'question.md'))['turn'], 3)

    def test_inflight_consultation_rejects_other_writers(self):
        """An in-flight turn rejects competing asks, closes and reopens; a host crash leaves a blocking marker."""
        with consultation() as (root, base):
            c = root / 'c'
            (c / 'mode').write_text('wait')
            child = subprocess.Popen([sys.executable, SCRIPT, *base, 'ask', str(c), '--question', str(root / 'question.md')],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                deadline = time.monotonic() + 5
                while 'pending_turn' not in json.loads((c / 'consult.json').read_text()):
                    self.assertLess(time.monotonic(), deadline)
                    time.sleep(.01)
                for command in ('ask', 'close', 'reopen'):
                    extra = [] if command == 'close' else ['--question', str(root / 'question.md')]
                    result = run(*base, command, str(c), *extra, expect=2)
                    self.assertIn('active writer', result['error'])
            finally:
                child.terminate()
                child.communicate(timeout=5)
            result = run(*base, 'ask', str(c), '--question', str(root / 'question.md'), expect=2)
            self.assertIn('unfinished or uncertain', result['error'])

    def test_open_ask_close_keeps_one_session(self):
        """Given a brief, when opened then asked with an attachment, then both harnesses answer from one session that sees the readable directories and attachment, and a closed consultation refuses further questions."""
        for harness in ('claude', 'codex'):
            with tempfile.TemporaryDirectory() as root, self.subTest(harness=harness):
                root = Path(root)
                (root / 'brief.md').write_text('Task: tighten the parser. First question: where is the risk?')
                (root / 'question.md').write_text('Second question: is the retry safe?')
                (root / 'notes.txt').write_text('ATTACHED EVIDENCE LINE')
                (root / 'repo').mkdir()
                plugin = root / 'plugin.py'
                plugin.write_text('import sys\nsys.path.insert(0, ' + repr(str(PACKAGE / "scripts")) + ')\n'
                                  'from adapters.' + harness + ' import ' + harness.capitalize() + 'Adapter\n'
                                  'class Fixture(' + harness.capitalize() + 'Adapter):\n'
                                  '    def command(self, session_id, settings):\n'
                                  '        return super().command(session_id, dict(settings, executable=' + repr(EXECUTABLE) + '))\n'
                                  'def create_adapter():\n    return Fixture()\n')
                base = ['--adapter', f'fixture={plugin}']
                opened = run(*base, 'open', str(root / 'c'), '--harness', 'fixture', '--model', 'fixture', '--effort', 'high',
                             '--brief', str(root / 'brief.md'), '--read', str(root / 'repo'))
                self.assertTrue(opened['ok'], opened)
                self.assertIn('where is the risk?', opened['text'])
                self.assertIn(str(root / 'repo'), opened['text'], 'the consultant is told what it may read')
                manifest = json.loads((root / 'c' / 'consult.json').read_text())
                self.assertTrue(manifest['session_id'])
                asked = run(*base, 'ask', str(root / 'c'), '--question', str(root / 'question.md'), '--attach', str(root / 'notes.txt'))
                self.assertTrue(asked['ok'], asked)
                self.assertIn('is the retry safe?', asked['text'])
                self.assertIn('ATTACHED EVIDENCE LINE', asked['text'])
                self.assertEqual(json.loads((root / 'c' / 'consult.json').read_text())['session_id'], manifest['session_id'])
                commands = [json.loads(p.read_text()) for p in sorted((root / 'c' / 'turns').glob('t*/command.json'))]
                self.assertEqual(len(commands), 2)
                self.assertTrue(all('--json-schema' in c['argv'] or '--output-schema' in c['argv'] for c in commands))
                if harness == 'claude':
                    self.assertIn(str(root / 'repo'), commands[1]['argv'])
                    self.assertNotIn('Edit', ','.join(commands[1]['argv']).split('--tools')[1].split(' ')[0])
                self.assertEqual(len((root / 'c' / 'log.jsonl').read_text().splitlines()), 2)
                self.assertEqual(run(*base, 'close', str(root / 'c'))['status'], 'closed')
                refused = run(*base, 'ask', str(root / 'c'), '--question', str(root / 'question.md'), expect=2)
                self.assertIn('closed', refused['error'])

    def test_timeout_is_reported_and_cancelled(self):
        """Given a consultant that never answers, when the timeout passes, then the turn is cancelled, reported as a failure, and the session stays open for another try."""
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            plugin = root / 'slow.py'
            plugin.write_text('import asyncio, sys\nsys.path.insert(0, ' + repr(str(PACKAGE / "scripts")) + ')\n'
                              'from adapters.base import Handle, Terminal\n'
                              'class Slow:\n'
                              '    settings_keys = {"model", "effort"}\n'
                              '    def start(self, input, settings):\n'
                              '        h = Handle(); h.completion = asyncio.create_task(asyncio.sleep(3600)); return h\n'
                              '    resume = lambda self, session, input, settings: self.start(input, settings)\n'
                              '    async def cancel(self, handle):\n'
                              '        handle.completion.cancel()\n'
                              '        try:\n            await handle.completion\n        except asyncio.CancelledError:\n            pass\n'
                              '        return True\n'
                              'def create_adapter():\n    return Slow()\n')
            (root / 'brief.md').write_text('Slow question')
            failed = run('--adapter', f'slow={plugin}', 'open', str(root / 'c'), '--harness', 'slow', '--model', 'm',
                         '--brief', str(root / 'brief.md'), '--timeout', '0.3', expect=2)
            self.assertIn('timed out', failed['error'])
            manifest = json.loads((root / 'c' / 'consult.json').read_text())
            self.assertEqual((manifest['status'], manifest['turns'], manifest['session_id']), ('open', 1, None))


if __name__ == '__main__':
    unittest.main()
