"""Deterministic adapter boundary, including faults after possible execution."""
import asyncio
from dataclasses import asdict
import json
from pathlib import Path
from adapters.base import Handle, PreDispatchTransient, Terminal, atomic_json


class FakeAdapter:
    settings_keys = {'model', 'effort', 'max_turns', 'max_budget_usd', 'executable'}

    def __init__(self, behavior=None):
        self.behavior = behavior or (lambda p: None)
        self.inputs = []
        self.cancelled = []
        self.sessions = 0
        self.active = set()
        self.retries = set()

    def start(self, input, settings):
        self.sessions += 1
        return self.launch(f'session-{id(self)}-{self.sessions}', input, settings)

    def resume(self, session_id, input, settings):
        return self.launch(session_id, input, settings)

    def launch(self, session, input, settings):
        payload = json.loads(input.split('PANEL_INPUT\n')[1])
        payload['retry'] = input.startswith('RUNNER NOTICE')
        key = (payload['participant_id'], payload['phase'])
        action = self.behavior(payload)
        if action == 'transient' and key not in self.retries:
            self.retries.add(key)
            raise PreDispatchTransient('temporary unavailable before launch')
        self.inputs.append(dict(payload, session=session, schema=settings.get('schema')))
        handle = Handle()
        handle.pid = payload['participant_id']
        handle.directory = settings['attempt_dir']
        atomic_json(Path(settings['attempt_dir']) / 'launch.json', {'session_id': session})

        async def complete():
            if session in self.active:
                raise AssertionError('Concurrent invocation in one session')
            self.active.add(session)
            try:
                if action == 'wait':
                    await asyncio.sleep(3600)
                if action == 'busy':
                    for _ in range(12):
                        await asyncio.sleep(0.05)
                        Path(settings['attempt_dir'], 'stdout').open('a').write('progress\n')
                await asyncio.sleep(0.002 * (1 + len(payload['participant_id'])))
                phase = payload['phase']
                block = {'participant_id': payload['participant_id'],
                         'kind': 'review' if phase == 'review' else 'candidate' if phase == 'draft' else 'contribution',
                         'text': f"PROVENANCE_{payload['participant_id']}_{phase}_{payload['brief_revision']}", 'messages': []}
                if phase == 'review':
                    block.update(revision=payload['candidate']['revision'], content_hash=payload['candidate']['content_hash'],
                                 decision='approve', reasons=['Meets the frozen brief'], assumptions=[], blocking_objections=[])
                if phase == 'assign':
                    block['assignments'] = {p['id']: 'Investigate ' + p['role'] for p in payload['roster']}
                if isinstance(action, dict):
                    block.update(action)
                terminal = Terminal(session, json.dumps(block), block, 0, {'tokens': 12}, 'completed')
                if action == 'fail':
                    terminal = Terminal(session, exit_status=1, error='known exited failure')
                if action == 'malformed':
                    terminal = Terminal(session, 'not JSON', None, 0, outcome='failed', error='Malformed JSON')
                if action == 'blocked':
                    terminal = Terminal(session, exit_status=0, outcome='blocked', error='Native tool permission denied')
                if action == 'uncertain':
                    raise RuntimeError('crash after dispatch, before durable completion')
                atomic_json(Path(settings['attempt_dir']) / 'terminal.json', asdict(terminal))
                if action == 'corrupt_persist':
                    Path(settings['attempt_dir'], 'terminal.json').write_text('{')
                    raise RuntimeError('Crash with a corrupt persisted result')
                if action == 'crash_after_persist':
                    raise RuntimeError('crash after result persisted')
                return terminal
            finally:
                self.active.remove(session)

        handle.completion = asyncio.create_task(complete())
        return handle

    async def cancel(self, handle):
        self.cancelled.append(handle.pid)
        handle.completion.cancel()
        try:
            await handle.completion
        except asyncio.CancelledError:
            pass
        return True

    def recover(self, attempt_dir):
        path = Path(attempt_dir) / 'terminal.json'
        if path.exists():
            return Terminal(**json.loads(path.read_text()))
        launch = Path(attempt_dir) / 'launch.json'
        session = json.loads(launch.read_text())['session_id'] if launch.exists() else None
        return Terminal(session, outcome='indeterminate')
