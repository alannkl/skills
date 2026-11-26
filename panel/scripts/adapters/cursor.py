import json
from .base import ProcessAdapter, Terminal, structured

SCHEMA_INSTRUCTION = '\n\nReturn only one JSON object matching this JSON Schema, with no other text:\n'


class CursorAdapter(ProcessAdapter):
    # Cursor has no effort flag: effort is part of the model ID, such as a `-high` variant or a bracket override.
    settings_keys = {'model', 'executable'}
    idle_seconds = 600  # stream-json emits thinking deltas and tool calls as they happen; a model that hides reasoning stays silent; provisional

    def check(self, settings):
        if 'capabilities' in settings and not settings['capabilities'].get('web'):
            raise ValueError('Cursor has no per-run switch that disables web search; run this participant with web enabled')

    def _start(self, session_id, input, settings):
        # Print mode reads the prompt from stdin. No schema flag exists, so the schema travels in the prompt and the
        # final message is validated after the run.
        if settings.get('schema'):
            input += SCHEMA_INSTRUCTION + json.dumps(settings['schema'])
        return super()._start(session_id, input, settings)

    def command(self, session_id, settings):
        self.check(settings)
        capabilities = settings.get('capabilities', {})
        command = [settings.get('executable', 'agent'), '-p', '--output-format', 'stream-json',
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
        return command, session_id

    def parse(self, output, code, session_id):
        result = Terminal(session_id, exit_status=code)
        try:
            events = [json.loads(line) for line in output.splitlines() if line.strip()]
            events = [e for e in events if isinstance(e, dict)]
            # Every event carries the session, so a turn cut off before its result event still names it for a resume.
            result.session_id = next((e['session_id'] for e in events if e.get('session_id')), session_id)
            denied = any(e.get('type') == 'tool_call' and e.get('subtype') == 'completed' and any(
                isinstance(call, dict) and isinstance(call.get('result'), dict)
                and {'permissionDenied', 'rejected'} & set(call['result'])
                for call in (e.get('tool_call') or {}).values()) for e in events)
            # The result event's text joins every assistant message of the turn, narration before tool calls included;
            # the last assistant event is the final message alone.
            messages = [''.join(part.get('text', '') for part in (e.get('message') or {}).get('content') or []
                                if isinstance(part, dict)) for e in events if e.get('type') == 'assistant']
            results = [e for e in events if e.get('type') == 'result']
            result.raw_text = messages[-1] if messages else results[-1].get('result', '') if results else ''
            if denied:
                result.outcome = 'blocked'
                raise ValueError('native tool permission denied; see captured output')
            if not results:
                raise ValueError('no result event')
            data = results[-1]
            result.usage = data.get('usage', {})
            if code != 0 or data.get('is_error') or data.get('subtype') != 'success' or not data.get('session_id'):
                result.error = 'Cursor did not return a successful terminal result'
            elif data['session_id'] != result.session_id or (session_id and data['session_id'] != session_id):
                result.error = 'Cursor returned a different session ID'
            else:
                result.block = structured(result.raw_text)
                result.outcome = 'completed'
        except (ValueError, AttributeError, TypeError) as exc:
            result.error = f'Malformed Cursor output: {exc}'
        return result
