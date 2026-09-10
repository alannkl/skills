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
    """Show a protocol envelope's substance instead of its JSON. A review keeps the revision and hash it names."""
    try:
        block = structured(text)
    except ValueError:
        return text
    if block.get('decision'):
        head = ' '.join(str(block[k]) for k in ('decision', 'revision', 'content_hash') if block.get(k))
        return '\n'.join([head] + [f'- {r}' for r in block.get('reasons', []) + block.get('blocking_objections', [])])
    return block.get('text') or text


def turn_key(path):
    turn, attempt = path.parent.name[1:].split('-')
    return int(turn), int(attempt)


def first_current_turn(run_dir):
    """Turns dispatched after the latest discussion_start belong to the current discussion."""
    floor = latest = 0
    try:
        lines = (run_dir / 'events.jsonl').read_text().splitlines()
    except OSError:
        return 0
    for line in lines:
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get('kind') == 'discussion_start':
            floor = latest
        elif event.get('kind') == 'dispatch':
            latest = max(latest, int(event['data']['turn_id'][1:]))
    return floor + 1


def finished(run_dir):
    try:
        return json.loads((run_dir / 'manifest.json').read_text()).get('status') != 'running'
    except (OSError, ValueError):
        return False


def stream(run_dir, follow, out, every_discussion=False):
    offsets = {}
    while True:
        done = finished(run_dir)
        first = 1 if every_discussion else first_current_turn(run_dir)
        for path in sorted(run_dir.glob('participants/*/t*-*/stdout'), key=turn_key):
            if turn_key(path)[0] < first:
                continue
            with path.open('rb') as handle:
                handle.seek(offsets.get(path, 0))
                raw = handle.read()
            complete = raw.rfind(b'\n') + 1
            offsets[path] = offsets.get(path, 0) + complete
            participant, attempt = path.parent.parent.name, path.parent.name
            for line in raw[:complete].decode(errors='replace').splitlines():
                for kind, text in render(line):
                    out.write(f'[{participant} {attempt} {kind}]\n{text}\n\n')
                    out.flush()
        if not follow or done:
            return
        time.sleep(0.5)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Print each participant\'s reasoning and messages from a panel run directory.')
    parser.add_argument('run_dir', help='Panel run directory')
    parser.add_argument('--follow', action='store_true', help='Keep printing until the runner records a finished discussion')
    parser.add_argument('--all', action='store_true', help='Print every discussion, not only the current one')
    args = parser.parse_args(argv)
    stream(Path(args.run_dir).resolve(), args.follow, sys.stdout, args.all)


if __name__ == '__main__':
    main()
