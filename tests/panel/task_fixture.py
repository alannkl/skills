"""Disposable task workspaces and participants with concrete, testable outputs."""
from pathlib import Path
import subprocess

from test_panel import preset
from engine import Panel
from fakes import FakeAdapter

IDS = ('ada', 'bert', 'cy')


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True).stdout


def repository(root):
    repo = Path(root) / 'input-repository'
    repo.mkdir()
    git(repo, 'init', '-q')
    (repo / '.gitignore').write_text('__pycache__/\n')
    (repo / 'solution.py').write_text('def value():\n    return 0\n')
    (repo / 'verify.py').write_text('import os, sys\nsys.path.insert(0, os.getcwd())\nfrom solution import value\nassert value() == 4, value()\nprint("value=4")\n')
    git(repo, 'add', '.')
    git(repo, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'Disposable test baseline')
    return repo


class TaskFixture:
    def __init__(self, root, kind='general', name='independent-discussion', behavior=None, execution=None, repo=None, brief=None, **limits):
        self.root = Path(root)
        self.kind, self.name = kind, name
        self.adapter = FakeAdapter(behavior or self.behavior)
        self.brief = brief or f'Complete the {kind} example. Produce the requested deliverable and supporting evidence.'
        self.roster = {'drafter': 'ada', 'leader': 'ada', 'execution': execution or {},
                       'participants': [{'id': pid, 'role': 'Task contributor', 'harness': 'fake', 'settings': {'model': 'simulation'}} for pid in IDS]}
        if repo:
            self.roster.update(repository=str(repo), base_revision='HEAD')
        self.panel = Panel(preset(name), self.brief, self.roster,
                           self.root / 'run', {'fake': self.adapter},
                           **dict({'max_cycles': 1, 'idle_seconds': 5, 'run_seconds': 60}, **limits))

    def behavior(self, payload):
        if payload['phase'] != 'draft':
            return None
        if self.kind == 'research':
            return {'text': 'The source establishes a bounded process. [Source](https://example.org/evidence)',
                    'data': {'sources': [{'reference': 'https://example.org/evidence', 'supports': 'The process has a finite deadline.'}],
                             'limitations': ['No performance measurements are available.']}}
        if self.kind == 'review':
            return {'text': 'No material findings in the supplied scope.', 'data': {'findings': []}}
        if self.kind == 'writing':
            return {'text': 'Please send the revised manuscript by Friday.'}
        if self.kind == 'debugging':
            return {'text': 'Reproduced the failure and traced it to the return value.',
                    'data': {'reproduction': {'procedure': 'python3 verify.py', 'observed': 'Expected 4; got 0'},
                             'diagnosis': {'cause': 'value() returns the wrong constant', 'evidence': 'solution.py returns 0'}}}
        return {'text': 'Requested task deliverable.'}

    async def run(self):
        return await self.panel.run()


def implement(payload):
    phase, pid = payload['phase'], payload['participant_id']
    cwd = Path(payload['working_directory'])
    competing = payload['integration'].startswith('competing')
    if phase in ('initial', 'contribute'):
        if competing:
            versions = {'ada': '2 + 2', 'bert': '4', 'cy': 'sum([2, 2])'}
            (cwd / 'solution.py').write_text(f'def value():\n    return {versions[pid]}\n')
        else:
            (cwd / (pid + '.txt')).write_text({'ada': '1', 'bert': '1', 'cy': '2'}[pid])
    if phase == 'draft':
        if competing:
            # Select one complete implementation and port a useful clarification.
            peers = [e for e in payload['events'] if e['sender'] == 'bert' and e['data'].get('artifacts')]
            peer = Path(peers[-1]['data']['artifacts']['files'])
            (cwd / 'solution.py').write_text((peer / 'solution.py').read_text() + '# The result is deterministic.\n')
        else:
            for event in payload['events']:
                artifacts = event['data'].get('artifacts')
                if artifacts and event['sender'] != pid and not (cwd / (event['sender'] + '.txt')).exists():
                    git(cwd, 'apply', artifacts['patch'])
            (cwd / 'solution.py').write_text('from pathlib import Path\ndef value():\n    return sum(int(Path(p + ".txt").read_text()) for p in ("ada", "bert", "cy"))\n')
        return {'text': 'Implemented the requested value and integrated the selected contributions.'}
    return None
