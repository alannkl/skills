import json
import os
from pathlib import Path
import re
import sys
from .base import ProcessAdapter, Terminal, session_uuid, structured


# User-level skill installs. Granting them keeps installed skills and their reference files readable by rule,
# independent of the native permission classifier, so participants can apply skills such as delegate.
SKILL_ROOTS = ('~/.claude/skills', '~/.agents/skills')


def skill_roots(home=None):
    roots = []
    for root in SKILL_ROOTS:
        path = Path(root.replace('~', home, 1)) if home else Path(root).expanduser()
        if path.is_dir() and str(path) not in roots:
            roots.append(str(path))
    return roots


class ClaudeAdapter(ProcessAdapter):
    settings_keys = {'model', 'effort', 'max_turns', 'max_budget_usd', 'executable', 'prompt_cache_ttl'}
    idle_seconds = 300  # partial-message deltas keep the capture growing while the model thinks

    def session_unavailable(self, stderr, session_id):
        return bool(re.fullmatch(r'(?:Error: )?No conversation found with session ID: ' + re.escape(session_id) + r'\.?',
                                 stderr.strip(), re.IGNORECASE))

    def command(self, session_id, settings):
        session = session_id or session_uuid()
        capabilities = settings.get('capabilities', {})
        web = ['WebSearch', 'WebFetch'] if capabilities.get('web') else []
        if capabilities.get('full_tools'):
            tools = None  # the harness's full tool set; subagents inherit it
            grants = ['Read,Grep,Glob,Skill,Agent,Bash,Edit,Write,NotebookEdit'] + web
        else:
            # Read-only consultants: file reads, skills and subagents, which inherit this restricted set.
            tools = ['Read', 'Grep', 'Glob', 'Skill', 'Agent'] + web
            grants = ['Read,Grep,Glob,Skill,Agent'] + web
        permission_mode = 'auto'
        command = [settings.get('executable', 'claude'), '-p', '--output-format', 'stream-json', '--verbose', '--include-partial-messages',
                   '--model', settings['model'], '--permission-mode', permission_mode,
                   '--permission-prompts', 'none',
                   '--allowedTools', *grants,
                   '--append-system-prompt', 'Work within declared capabilities. Modify only your own working copy when authorized; preserve source evidence and peer artifacts. After reveal, read peer evidence through runner-captured artifacts.files and artifacts.patch references. Bash starts in your working_directory; run commands there. Use file tools for inspection and edits. Keep Bash commands simple: put multiline code, loops or Unicode test data in a script in your artifact_directory and run it with a task-appropriate executable, never in Bash -c arguments or heredocs. Do not commit, push or publish. Return only the requested JSON.']
        if tools is not None:
            command += ['--tools', ','.join(tools)]
        elif not web:
            command += ['--disallowedTools', 'WebSearch', 'WebFetch']
        grants_dirs = list(settings.get('read_dirs') or []) + [r for r in skill_roots() if r not in (settings.get('read_dirs') or [])]
        if grants_dirs:
            command += ['--add-dir', *grants_dirs]
        if settings.get('schema'):
            command += ['--json-schema', json.dumps(settings['schema'])]
        command += ['--resume' if session_id else '--session-id', session]
        if settings.get('effort'):
            command += ['--effort', settings['effort']]
        if settings.get('max_turns') is not None:
            command += ['--max-turns', str(settings['max_turns'])]
        if settings.get('max_budget_usd') is not None:
            command += ['--max-budget-usd', str(settings['max_budget_usd'])]
        return command, session

    def delegated_work_pending(self, attempt_dir):
        """True while a subagent the participant launched has not returned its result."""
        launched, returned = set(), set()
        stdout = Path(attempt_dir) / 'stdout'
        if not stdout.exists():
            return False
        for line in stdout.read_text(errors='replace').splitlines():
            if '"parent_tool_use_id":null' not in line.replace(' ', ''):
                continue
            try:
                event = json.loads(line)
            except ValueError:
                continue
            for part in (event.get('message') or {}).get('content') or []:
                if not isinstance(part, dict):
                    continue
                if event.get('type') == 'assistant' and part.get('type') == 'tool_use' and part.get('name') in ('Agent', 'Task'):
                    launched.add(part.get('id'))
                elif event.get('type') == 'user' and part.get('type') == 'tool_result':
                    returned.add(part.get('tool_use_id'))
        return bool(launched - returned)

    def environment(self, settings):
        ttl = settings.get('prompt_cache_ttl')
        if not ttl:
            return None
        if ttl != '5m' and os.environ.get('FORCE_PROMPT_CACHING_5M'):
            print(json.dumps({'warning': f'prompt_cache_ttl {ttl} requested, but FORCE_PROMPT_CACHING_5M is set in the '
                                         'runner environment and may hold the cache at 5 minutes'}), file=sys.stderr, flush=True)
        return dict(os.environ, CLAUDE_CODE_PROMPT_CACHE_TTL=ttl)

    def parse(self, output, code, session_id):
        result = Terminal(session_id, exit_status=code)
        try:
            # stream-json writes one event per line as the turn runs, including partial-message deltas that keep the
            # capture growing during long reasoning. A resumed session may flush a pending notification as its own
            # result before answering, so the last result event is the terminal state.
            events = [json.loads(line) for line in output.splitlines() if line.strip()]
            results = [e for e in events if isinstance(e, dict) and e.get('type') == 'result']
            if not results:
                raise ValueError('no result event')
            data = results[-1]
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
