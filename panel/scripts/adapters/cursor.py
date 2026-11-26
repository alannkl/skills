import json
from .base import ProcessAdapter, Terminal, structured


class CursorAdapter(ProcessAdapter):
    # Cursor has no effort flag: effort is part of the model ID, such as a `-high` variant or a bracket override.
    settings_keys = {'model', 'executable'}
    idle_seconds = 600  # partial output streams text and exposed reasoning deltas; a model that hides reasoning stays silent; provisional

    def _start(self, session_id, input, settings):
        # Print mode takes the prompt only as an argument, not on stdin.
        return super()._start(session_id, input, dict(settings, prompt=input))

    def command(self, session_id, settings):
        if settings.get('effort'):
            raise ValueError('Cursor sets effort through the model ID; omit effort')
        capabilities = settings.get('capabilities', {})
        if 'capabilities' in settings and not capabilities.get('web'):
            raise ValueError('Cursor has no per-run switch that disables web search; run this participant with web enabled')
        command = [settings.get('executable', 'agent'), '-p', '--output-format', 'stream-json', '--stream-partial-output',
                   '--model', settings['model'], '--trust', '--workspace', settings['cwd']]
        # --force runs every tool without approval; without it, ask mode stays read-only and rejects approval-gated actions.
        command += ['--force'] if capabilities.get('full_tools') else ['--mode', 'ask']
        directories = list(settings.get('read_dirs') or [])
        if capabilities.get('full_tools') and settings.get('scratch_dir'):
            directories.append(settings['scratch_dir'])
        for directory in directories:
            command += ['--add-dir', directory]
        if session_id:
            command += ['--resume', session_id]
        prompt = settings.get('prompt', '')
        if settings.get('schema'):
            # No schema flag; the final message is validated as JSON after the run.
            prompt += ('\n\nReturn only one JSON object matching this JSON Schema, with no other text:\n'
                       + json.dumps(settings['schema']))
        # Linux caps one argument at 128 KiB; a longer prompt fails to launch with E2BIG.
        command += ['--', prompt]
        return command, session_id

    def parse(self, output, code, session_id):
        result = Terminal(session_id, exit_status=code)
        try:
            events = [json.loads(line) for line in output.splitlines() if line.strip()]
            results = [e for e in events if isinstance(e, dict) and e.get('type') == 'result']
            if not results:
                raise ValueError('no result event')
            data = results[-1]
            result.session_id = data.get('session_id')
            result.raw_text = data.get('result', '')
            result.usage = data.get('usage', {})
            if code != 0 or data.get('is_error') or data.get('subtype') != 'success' or not result.session_id:
                result.error = 'Cursor did not return a successful terminal result'
            elif session_id and result.session_id != session_id:
                result.error = 'Cursor returned a different session ID'
            else:
                result.block = structured(result.raw_text)
                result.outcome = 'completed'
        except (ValueError, AttributeError, TypeError) as exc:
            result.error = f'Malformed Cursor output: {exc}'
        return result
