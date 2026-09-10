"""Pinned source evidence, isolated worktrees, and reviewable file artifacts."""
import json
import os
from pathlib import Path
import shutil
import subprocess

from records import copy_snapshot, digest, snapshot_hash, make_readonly


def git(directory, *args, accepted=(0,)):
    result = subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-C', str(directory), *args],
                            capture_output=True, timeout=30)
    if result.returncode not in accepted:
        raise ValueError('Git operation failed: ' + result.stderr.decode(errors='replace').strip())
    return result.stdout


def worktree_files(directory):
    names = git(directory, 'ls-files', '--cached', '--others', '--exclude-standard', '-z').decode().split('\0')
    return sorted({name for name in names if name and os.path.lexists(Path(directory) / name)})


def copy_files(source, destination, names):
    source, destination = Path(source), Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    for name in names:
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts or '.git' in relative.parts:
            raise ValueError('Unsafe artifact path: ' + name)
        src, dst = source / relative, destination / relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_symlink():
            target = os.readlink(src)
            if Path(target).is_absolute() or not src.resolve().is_relative_to(source.resolve()):
                raise ValueError('Artifact symlink points outside its working copy: ' + name)
            dst.symlink_to(target)
        elif src.is_file():
            shutil.copy2(src, dst)
        else:
            raise ValueError('Only regular files and internal symlinks are supported; submodule: ' + name)
    return snapshot_hash(destination)


class Workspaces:
    def __init__(self, root, roster, execution, ids):
        self.root, self.execution = Path(root), execution
        self.repository = None
        self.base_revision = None
        self.directories = {}
        repository = roster.get('repository')
        if execution.worktree and not repository:
            raise ValueError('This task needs repository and base_revision for isolated worktrees')
        if repository and 'source' in roster:
            raise ValueError('Select source evidence or a pinned repository, not both')
        if repository:
            repository = Path(repository).resolve()
            revision = roster.get('base_revision')
            if not isinstance(revision, str) or not revision or revision.startswith('-'):
                raise ValueError('repository requires an explicit base_revision')
            self.base_revision = git(repository, 'rev-parse', '--verify', revision + '^{commit}').decode().strip()
            # A private clone prevents participant Git metadata writes from touching the caller.
            self.repository = root / 'repository.git'
            git(root, 'clone', '--bare', '--no-hardlinks', str(repository), str(self.repository))
            git(self.repository, 'remote', 'remove', 'origin')
            base = root / 'base'
            self.add_worktree(base)
            copy_files(base, root / 'source', worktree_files(base))
            make_readonly(root / 'source')
        elif roster.get('source'):
            copy_snapshot(roster['source'], root / 'source')
        else:
            (root / 'source').mkdir()
            make_readonly(root / 'source')
        self.source_hash = snapshot_hash(root / 'source')
        for pid in ids:
            artifact_dir = root / 'participants' / pid
            artifact_dir.mkdir(parents=True)
            (artifact_dir / 'scratch').mkdir()
            cwd = artifact_dir / 'workspace' if execution.worktree else root / 'source'
            if execution.worktree:
                self.add_worktree(cwd)
            self.directories[pid] = str(cwd)

    def add_worktree(self, path):
        git(self.repository, 'worktree', 'add', '--detach', str(path), self.base_revision)

    def patch(self, pid):
        cwd = self.directories[pid]
        content = git(cwd, 'diff', '--binary', '--no-ext-diff', '--no-textconv', self.base_revision, '--', '.')
        names = git(cwd, 'ls-files', '--others', '--exclude-standard', '-z').decode().split('\0')
        for name in sorted(n for n in names if n):
            content += git(cwd, 'diff', '--binary', '--no-ext-diff', '--no-index', '--', '/dev/null', name, accepted=(0, 1))
        return content

    def contribution(self, pid, attempt_dir):
        if not self.execution.worktree:
            return None
        path = Path(attempt_dir) / 'changes.patch'
        files = Path(attempt_dir) / 'files'
        if not path.exists():
            patch = self.patch(pid)
            if not self.execution.editable and patch:
                raise ValueError('Source changes are not permitted by execution.workspace=inspect')
            path.write_bytes(patch)
            path.chmod(0o444)
        if not files.exists():
            copy_files(self.directories[pid], files, worktree_files(self.directories[pid]))
            make_readonly(files)
        return {'patch': str(path), 'patch_hash': digest(path.read_bytes()),
                'files': str(files), 'tree_hash': snapshot_hash(files), 'base_revision': self.base_revision}

    def freeze(self, pid, destination):
        destination = Path(destination)
        patch = self.patch(pid)
        if not self.execution.editable and patch:
            raise ValueError('Source changes are not permitted by execution.workspace=inspect')
        patch_path = destination / 'changes.patch'
        patch_path.write_bytes(patch)
        patch_path.chmod(0o444)
        files = destination / 'files'
        tree_hash = copy_files(self.directories[pid], files, worktree_files(self.directories[pid]))
        make_readonly(files)
        return {'files': str(files), 'tree_hash': tree_hash, 'patch': str(patch_path),
                'patch_hash': digest(patch), 'base_revision': self.base_revision}

    def verification_workspace(self, destination, patch):
        workspace = Path(destination) / 'verification-workspace'
        self.add_worktree(workspace)
        if Path(patch).stat().st_size:
            git(workspace, 'apply', '--binary', '--whitespace=nowarn', str(patch))
        return workspace

    def describe(self):
        return {'repository': str(self.repository) if self.repository else None,
                'base_revision': self.base_revision, 'working_directories': self.directories}


def result_hash(candidate):
    if not candidate.get('bundle'):
        return digest(Path(candidate['path']).read_bytes())
    bundle = dict(candidate['bundle'])
    bundle['text_hash'] = digest(Path(candidate['path']).read_bytes())
    artifacts = candidate.get('artifacts')
    if artifacts:
        bundle['tree_hash'] = snapshot_hash(artifacts['files'])
        bundle['patch_hash'] = digest(Path(artifacts['patch']).read_bytes())
    return digest(json.dumps(bundle, ensure_ascii=False, sort_keys=True).encode())
