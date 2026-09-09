"""Adapter contract and bounded subprocess ownership. No collaboration policy here."""
import asyncio
from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path
import signal
import uuid


def atomic_json(path, value):
    path = Path(path)
    temp = path.with_name(path.name + '.tmp')
    with temp.open('w') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def structured(text):
    text = text.strip()
    if text.startswith('```json\n') and text.endswith('\n```'):
        text = text[8:-4]
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError('final response must be one JSON object')
    return value


@dataclass
class Terminal:
    session_id: str | None
    raw_text: str = ''
    block: dict | None = None
    exit_status: int | None = None
    usage: dict = field(default_factory=dict)
    outcome: str = 'failed'
    error: str = ''


@dataclass
class Handle:
    completion: asyncio.Task | None = None
    process: asyncio.subprocess.Process | None = None
    stopping: bool = False


class PreDispatchTransient(Exception):
    """Only adapters that can prove no process was launched may raise this."""


class ProcessAdapter:
    def start(self, input, settings):
        return self._start(None, input, settings)

    def resume(self, session_id, input, settings):
        return self._start(session_id, input, settings)

    def _start(self, session_id, input, settings):
        handle = Handle()
        handle.completion = asyncio.create_task(self._execute(handle, session_id, input, settings))
        return handle

    async def _execute(self, handle, session_id, input, settings):
        attempt = Path(settings['attempt_dir'])
        attempt.mkdir(parents=True, exist_ok=True)
        prompt = attempt / 'input.txt'
        prompt.write_text(input)
        result = Terminal(session_id)
        try:
            command, expected_session = self.command(session_id, settings)
            if handle.stopping:
                result = Terminal(session_id, outcome='failed', error='cancelled before launch')
                atomic_json(attempt / 'terminal.json', asdict(result))
                return result
            atomic_json(attempt / 'command.json', {'argv': command, 'cwd': settings['cwd']})
            with prompt.open('rb') as stdin, (attempt / 'stdout').open('wb') as stdout, (attempt / 'stderr').open('wb') as stderr:
                handle.process = await asyncio.create_subprocess_exec(
                    *command, cwd=settings['cwd'], stdin=stdin, stdout=stdout,
                    stderr=stderr, start_new_session=True)
                atomic_json(attempt / 'process.json', {'pid': handle.process.pid})
                if handle.stopping:
                    await self._terminate(handle)
                code = await handle.process.wait()
                stdout.flush()
                stderr.flush()
                os.fsync(stdout.fileno())
                os.fsync(stderr.fileno())
            atomic_json(attempt / 'exit.json', {'exit_status': code, 'session_id': expected_session})
            result = self.parse((attempt / 'stdout').read_text(errors='replace'), code, expected_session)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            result.error = f'{type(exc).__name__}: {exc}'
            if handle.process is not None and handle.process.returncode is None:
                confirmed = await self._terminate(handle)
                result.outcome = 'failed' if confirmed else 'indeterminate'
                result.error += '; invocation failed after launch, effects may be incomplete'
        atomic_json(attempt / 'terminal.json', asdict(result))
        return result

    async def _terminate(self, handle):
        process = handle.process
        if process is None:
            return True
        # Kill the invocation's process group, including tool children. Never use a saved PID.
        for sig in (signal.SIGTERM, signal.SIGKILL):
            try:
                os.killpg(process.pid, sig)
            except ProcessLookupError:
                return True
            await asyncio.sleep(0.1)
            try:
                await asyncio.wait_for(asyncio.shield(process.wait()), 1.5)
            except asyncio.TimeoutError:
                continue
            try:
                os.killpg(process.pid, 0)
            except ProcessLookupError:
                return True
        try:
            os.killpg(process.pid, 0)
        except ProcessLookupError:
            return True
        return False

    async def cancel(self, handle):
        handle.stopping = True
        if handle.completion.done() and (handle.process is None or handle.process.returncode is not None):
            return True
        confirmed = await self._terminate(handle)
        try:
            await asyncio.wait_for(asyncio.shield(handle.completion), 4)
        except asyncio.TimeoutError:
            return False
        # A launch may have been pending when cancel first inspected the handle.
        return await self._terminate(handle) and confirmed

    def recover(self, attempt_dir):
        attempt = Path(attempt_dir)
        if (attempt / 'terminal.json').exists():
            return Terminal(**json.loads((attempt / 'terminal.json').read_text()))
        if (attempt / 'exit.json').exists() and (attempt / 'stdout').exists():
            exit_record = json.loads((attempt / 'exit.json').read_text())
            return self.parse((attempt / 'stdout').read_text(), exit_record['exit_status'], exit_record['session_id'])
        return Terminal(None, outcome='indeterminate', error='No durable completion evidence; invocation may have executed')


def session_uuid():
    return str(uuid.uuid4())


def recover_terminal(adapter, attempt_dir):
    try:
        result = adapter.recover(attempt_dir)
        if not isinstance(result, Terminal):
            raise ValueError('Adapter recovery did not return Terminal')
        return result
    except Exception as exc:
        return Terminal(None, outcome='indeterminate',
                        error=f'Cannot establish completion from persisted output: {type(exc).__name__}')
