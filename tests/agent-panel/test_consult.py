"""Consultant behavior, pinned before implementation: one read-only session for second opinions."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[2] / 'agent-panel'
SCRIPT = str(PACKAGE / 'scripts' / 'consult.py')
EXECUTABLE = str(Path(__file__).resolve().with_name('harness_fixture.py'))


def run(*args, expect=0):
    result = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True, timeout=20)
    assert result.returncode == expect, result.stdout + result.stderr
    return json.loads(result.stdout)


class ConsultBehavior(unittest.TestCase):
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
