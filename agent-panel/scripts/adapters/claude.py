import json
from .base import ProcessAdapter, Terminal, session_uuid, structured


class ClaudeAdapter(ProcessAdapter):
    settings_keys = {'model', 'effort', 'max_turns', 'max_budget_usd', 'executable'}

    def command(self, session_id, settings):
        session = session_id or session_uuid()
        capabilities = settings.get('capabilities', {})
        tools = ['Read', 'Grep', 'Glob']
        grants = ['Read,Grep,Glob']
        if capabilities.get('web'):
            tools += ['WebSearch', 'WebFetch']
            grants += ['WebSearch', 'WebFetch']
        if capabilities.get('workspace_write'):
            tools += ['Bash']
            if capabilities.get('source_edits'):
                tools += ['Edit', 'Write']
        permission_mode = 'auto'
        command = [settings.get('executable', 'claude'), '-p', '--output-format', 'stream-json', '--verbose',
                   '--model', settings['model'], '--permission-mode', permission_mode,
                   '--permission-prompts', 'none',
                   '--allowedTools', *grants, '--tools', ','.join(tools),
                   '--max-turns', str(settings.get('max_turns', 8)),
                   '--append-system-prompt', 'Work within declared capabilities. Modify only your own working copy when authorized; preserve source evidence and peer artifacts. After reveal, read peer evidence through runner-captured artifacts.files and artifacts.patch references. Bash starts in your working_directory; run commands there. Use file tools for inspection and edits. Keep Bash commands simple: put multiline code, loops or Unicode test data in a script in your artifact_directory and run it with a task-appropriate executable, never in Bash -c arguments or heredocs. Do not commit, push, publish, or launch further agents. Return only the requested JSON.']
        if capabilities.get('workspace_write') and not capabilities.get('source_edits') and settings.get('scratch_dir'):
            # Scratch scripts may be written while the source worktree stays read-only.
            command[command.index('--tools') + 1] += ',Write'
            command += ['--disallowedTools', 'Edit(/' + settings['cwd'] + '/**)']
        if settings.get('read_dirs'):
            command += ['--add-dir', *settings['read_dirs']]
        command += ['--resume' if session_id else '--session-id', session]
        if settings.get('effort'):
            command += ['--effort', settings['effort']]
        if settings.get('max_budget_usd') is not None:
            command += ['--max-budget-usd', str(settings['max_budget_usd'])]
        return command, session

    def parse(self, output, code, session_id):
        result = Terminal(session_id, exit_status=code)
        try:
            # stream-json writes one event per line as the turn runs; the single result event is terminal.
            events = [json.loads(line) for line in output.splitlines() if line.strip()]
            results = [e for e in events if isinstance(e, dict) and e.get('type') == 'result']
            if len(results) != 1:
                raise ValueError('expected exactly one result event')
            data = results[0]
            result.session_id = data.get('session_id', session_id)
            result.raw_text = data.get('result', '')
            result.usage = {'tokens': data.get('usage', {}), 'cost_usd': data.get('total_cost_usd')}
            if data.get('permission_denials'):
                result.outcome = 'blocked'
                result.error = 'Native tool permission denied; see captured output'
            elif code != 0 or data.get('is_error') or data.get('subtype') != 'success':
                result.error = 'Claude did not return a successful terminal result'
            elif result.session_id != session_id:
                result.error = 'Claude returned a different session ID'
            else:
                result.block = data.get('structured_output') or structured(result.raw_text)
                if not isinstance(result.block, dict):
                    raise ValueError('structured output must be an object')
                result.outcome = 'completed'
        except (ValueError, AttributeError, TypeError) as exc:
            result.error = f'Malformed Claude output: {exc}'
        return result
