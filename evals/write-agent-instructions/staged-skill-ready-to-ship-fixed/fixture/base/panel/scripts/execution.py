"""Explicit execution boundaries, independent of the subject of a brief."""


class ExecutionPolicy:
    def __init__(self, config, required, integrator):
        if config is None:
            config = {}
        if not isinstance(config, dict):
            raise ValueError('execution must be an object')
        unknown = set(config) - {'workspace', 'checks', 'verification_note', 'web'}
        if unknown:
            raise ValueError('Unknown execution fields: ' + ', '.join(sorted(unknown)))
        workspace = config.get('workspace', 'read-only')
        if workspace not in ('read-only', 'inspect', 'edit'):
            raise ValueError('execution.workspace must be read-only, inspect or edit')
        self.editable = workspace == 'edit'
        self.worktree = workspace != 'read-only'
        checks = config.get('checks', [])
        if not isinstance(checks, list):
            raise ValueError('execution.checks must be a list of commands')
        normalized = []
        for check in checks:
            check = {'argv': check, 'expect_exit': 0} if isinstance(check, list) else check
            if not isinstance(check, dict) or set(check) - {'argv', 'expect_exit'}:
                raise ValueError('A check needs argv and optional expect_exit')
            argv, expected = check.get('argv'), check.get('expect_exit', 0)
            if not isinstance(argv, list) or not argv or any(not isinstance(a, str) or not a or '\0' in a for a in argv):
                raise ValueError('Check argv must be a nonempty string array')
            if type(expected) is not int or not 0 <= expected <= 255:
                raise ValueError('expect_exit must be an integer from 0 to 255')
            normalized.append({'argv': argv, 'expect_exit': expected})
        checks = normalized
        if checks and not self.worktree:
            raise ValueError('Executable checks require an isolated working copy')
        note = config.get('verification_note', '')
        if not isinstance(note, str):
            raise ValueError('verification_note must be text')
        if self.worktree and not checks and not note.strip():
            raise ValueError('Working-copy tasks need executable checks or an explicit verification_note')
        if self.worktree and not any(pid != integrator for pid in required):
            raise ValueError('Working-copy tasks require an approver other than the integrator')
        web = config.get('web', False)
        if type(web) is not bool:
            raise ValueError('execution.web must be a boolean')
        self.config = dict(config, workspace=workspace, checks=checks, web=web, verification_note=note)

    def capabilities(self):
        # Describe permitted effects; a harness may implement file reads through a shell.
        return {'file_reads': True, 'workspace_write': self.worktree, 'source_edits': self.editable,
                'web': self.config['web'],
                'tool_approval': 'automatic within task bounds',
                'verification_commands': [c['argv'] for c in self.config['checks']]}
