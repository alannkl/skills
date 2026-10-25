import json
from .base import ProcessAdapter, Terminal, structured


class CodexAdapter(ProcessAdapter):
    settings_keys = {'model', 'effort', 'executable'}

    def command(self, session_id, settings):
        capabilities = settings.get('capabilities', {})
        sandbox = 'workspace-write' if capabilities.get('workspace_write') else 'read-only'
        command = [settings.get('executable', 'codex'), 'exec']
        if session_id:
            command += ['resume']
        command += ['--model', settings['model'], '-c', 'approval_policy="never"',
                    '--strict-config', '--json', '--skip-git-repo-check']
        if session_id:
            command += ['-c', 'sandbox_mode=' + json.dumps(sandbox)]
        else:
            command += ['--cd', settings['cwd'], '--sandbox', sandbox]
        if 'capabilities' in settings:
            command += ['-c', 'web_search=' + json.dumps('live' if capabilities.get('web') else 'disabled')]
        if settings.get('effort'):
            command += ['-c', 'model_reasoning_effort=' + json.dumps(settings['effort'])]
        if session_id:
            command += [session_id]
        command += ['-']
        return command, session_id

    def parse(self, output, code, session_id):
        result = Terminal(session_id, exit_status=code)
        try:
            events = [json.loads(line) for line in output.splitlines() if line.strip()]
            terminal = []
            texts = []
            for event in events:
                kind = event.get('type')
                item = event.get('item', {})
                error = event.get('error', {})
                denied = isinstance(error, dict) and error.get('code') in ('permission_denied', 'approval_denied', 'sandbox_denied')
                if isinstance(item, dict) and item.get('type') == 'command_execution':
                    output_text = str(item.get('aggregated_output', '')).lower()
                    denied = denied or item.get('status') in ('declined', 'denied') or (
                        item.get('status') == 'failed' and any(marker in output_text for marker in
                        ('permission denied', 'approval denied', 'sandbox denied', 'rejected by policy')))
                if denied:
                    result.outcome = 'blocked'
                    raise ValueError('Native tool permission denied; see captured output')
                if kind == 'thread.started':
                    known = event.get('thread_id')
                    if session_id and known != session_id:
                        raise ValueError('resume returned a different session ID')
                    result.session_id = known
                elif kind in ('turn.failed', 'error'):
                    raise ValueError('Codex reported a failed turn; see captured output')
                elif kind == 'turn.completed':
                    terminal.append(event)
                    result.usage = event.get('usage', {})
                elif kind == 'item.completed' and event.get('item', {}).get('type') == 'agent_message':
                    texts.append(event['item']['text'])
            result.raw_text = texts[-1] if texts else ''
            if code != 0 or len(terminal) != 1 or not result.session_id or not texts:
                raise ValueError('missing successful terminal event, session ID or final message')
            result.block = structured(result.raw_text)
            result.outcome = 'completed'
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            result.error = f'Invalid Codex terminal output: {exc}'
        return result
