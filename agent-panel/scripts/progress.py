"""Print participant reasoning and messages from a run's native outputs as they land."""
import argparse
import json
from pathlib import Path
import sys
import time
from adapters.base import structured


def render(line):
    """Return (kind, text) pairs for reasoning or message content in either bundled dialect; tool activity is skipped."""
    try:
        event = json.loads(line)
    except ValueError:
        return []
    if not isinstance(event, dict):
        return []
    found = []
    if event.get('type') == 'assistant':  # Claude stream-json
        for block in event.get('message', {}).get('content', []):
            if block.get('type') == 'thinking' and block.get('thinking'):
                found.append(('reasoning', block['thinking']))
            elif block.get('type') == 'text' and block.get('text'):
                found.append(('message', unwrap(block['text'])))
    elif event.get('type') == 'item.completed':  # Codex --json
        item = event.get('item', {})
        if item.get('type') == 'reasoning' and item.get('text'):
            found.append(('reasoning', item['text']))
        elif item.get('type') == 'agent_message' and item.get('text'):
            found.append(('message', unwrap(item['text'])))
    return found


def unwrap(text):
    """Show a protocol envelope's substance instead of its JSON."""
    try:
        block = structured(text)
    except ValueError:
        return text
    if block.get('decision'):
        return '\n'.join([str(block['decision'])] + [f'- {r}' for r in block.get('reasons', []) + block.get('blocking_objections', [])])
    return block.get('text') or text


def turn_key(path):
    turn, attempt = path.parent.name[1:].split('-')
    return int(turn), int(attempt)


def stream(run_dir, follow, out):
    report = run_dir / 'report.json'
    baseline = report.stat().st_mtime_ns if report.exists() else None
    offsets = {}
    while True:
        finished = report.exists() and report.stat().st_mtime_ns != baseline
        for path in sorted(run_dir.glob('participants/*/t*-*/stdout'), key=turn_key):
            with path.open('rb') as handle:
                handle.seek(offsets.get(path, 0))
                raw = handle.read()
            complete = raw.rfind(b'\n') + 1
            offsets[path] = offsets.get(path, 0) + complete
            participant, turn = path.parent.parent.name, path.parent.name.split('-')[0]
            for line in raw[:complete].decode(errors='replace').splitlines():
                for kind, text in render(line):
                    out.write(f'[{participant} {turn} {kind}]\n{text}\n\n')
                    out.flush()
        if not follow or finished:
            return
        time.sleep(0.5)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Print each participant\'s reasoning and messages from a panel run directory.')
    parser.add_argument('run_dir', help='Panel run directory')
    parser.add_argument('--follow', action='store_true', help='Keep printing until the runner writes report.json')
    args = parser.parse_args(argv)
    stream(Path(args.run_dir).resolve(), args.follow, sys.stdout)


if __name__ == '__main__':
    main()
