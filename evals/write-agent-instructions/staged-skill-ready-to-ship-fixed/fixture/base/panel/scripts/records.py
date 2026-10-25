"""Runner-owned records and immutable source capture."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
from adapters.base import atomic_json


def digest(data):
    return hashlib.sha256(data).hexdigest()


def snapshot_hash(root, names=None):
    entries = []
    paths = Path(root).rglob('*') if names is None else (Path(root) / name for name in names)
    for path in sorted(paths):
        if path.is_symlink():
            target = os.readlink(path)
            if Path(target).is_absolute() or not path.resolve().is_relative_to(Path(root).resolve()):
                raise ValueError(f'Snapshot symlink points outside its root: {path}')
            entries.append([str(path.relative_to(root)), 'symlink', target])
        elif path.is_file():
            entries.append([str(path.relative_to(root)), 'file', bool(path.stat().st_mode & 0o111), digest(path.read_bytes())])
        elif not path.is_dir():
            raise ValueError(f'Snapshot special file is unsupported: {path}')
    return digest(json.dumps(entries, ensure_ascii=False).encode())


def copy_snapshot(source, destination):
    source = Path(source).resolve()
    if not source.is_dir():
        raise ValueError('source must be a directory containing the task evidence')
    snapshot_hash(source)
    shutil.copytree(source, destination, symlinks=True)
    result = snapshot_hash(destination)
    make_readonly(destination)
    return result


def make_readonly(destination):
    for path in Path(destination).rglob('*'):
        if not path.is_symlink():
            path.chmod(0o555 if path.is_dir() else 0o444 | (path.stat().st_mode & 0o111))
    Path(destination).chmod(0o555)


class Records:
    def __init__(self, root, existing=False):
        self.root = Path(root).resolve()
        if not existing:
            self.root.mkdir(parents=True, exist_ok=False, mode=0o700)
        self.lock = (self.root / '.lock').open('a')
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.lock.close()
            raise ValueError('Run already has an active writer') from None
        self.log = self.root / 'events.jsonl'
        self.events = []
        if existing and self.log.exists():
            raw = self.log.read_bytes()
            # A torn final append is not an event. Preserve its bytes for diagnosis.
            if raw and not raw.endswith(b'\n'):
                cut = raw.rfind(b'\n') + 1
                (self.root / 'torn-event').write_bytes(raw[cut:])
                with self.log.open('r+b') as stream:
                    stream.truncate(cut)
                raw = raw[:cut]
            self.events = [json.loads(line) for line in raw.splitlines()]

    def append(self, kind, phase, sender='runner', visibility=None, **data):
        event = {'id': len(self.events) + 1, 'kind': kind, 'sender': sender,
                 'phase': phase, 'visibility': visibility or ['host'], 'data': data}
        with self.log.open('a') as stream:
            stream.write(json.dumps(event, ensure_ascii=False) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        self.events.append(event)
        return event

    def save_manifest(self, manifest):
        atomic_json(self.root / 'manifest.json', manifest)

    def close(self):
        if not self.lock.closed:
            fcntl.flock(self.lock, fcntl.LOCK_UN)
            self.lock.close()
