#!/usr/bin/env python3
"""Run a bounded task panel; stdout is one final JSON report."""
import argparse
import asyncio
import json
from pathlib import Path
import signal
import sys
import tempfile
import uuid

from adapters import production_adapters
from engine import Panel
from recovery import recover_run


async def host_input(phase):
    print(json.dumps({'awaiting_host_decision': phase, 'actions': ['continue', 'brief', 'stop']}), file=sys.stderr, flush=True)
    loop = asyncio.get_running_loop()
    future = loop.create_future()

    def ready():
        line = sys.stdin.readline()
        if not future.done():
            if not line:
                future.set_exception(ValueError('Host channel closed without a decision'))
            else:
                try:
                    future.set_result(json.loads(line))
                except ValueError as exc:
                    future.set_exception(exc)

    loop.add_reader(sys.stdin.fileno(), ready)
    try:
        return await future
    finally:
        loop.remove_reader(sys.stdin.fileno())


async def execute(args):
    adapters = production_adapters(args.adapter)
    if args.recover:
        return recover_run(args.recover, adapters)
    if not all((args.preset, args.brief, args.roster)):
        raise ValueError('preset, brief and roster are required unless using --recover')
    preset_path = Path(__file__).resolve().parent.parent / 'presets' / (args.preset + '.json')
    preset = json.loads(preset_path.read_text())
    roster_path = Path(args.roster).resolve()
    roster = json.loads(roster_path.read_text())
    for key in ('source', 'repository'):
        if roster.get(key):
            roster[key] = str((roster_path.parent / roster[key]).resolve())
    run_dir = args.run_dir or str(Path(tempfile.gettempdir()) / ('agent-panel-' + str(uuid.uuid4())))
    panel = Panel(preset, Path(args.brief).read_text(), roster, run_dir, adapters,
                  max_cycles=args.max_cycles, turn_seconds=args.turn_seconds,
                  run_seconds=args.run_seconds, report_seconds=args.report_seconds,
                  host_input=host_input if args.pause_between_rounds else None)
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, panel.request_stop)
    print(json.dumps({'run_dir': str(panel.records.root), 'status': 'started'}), file=sys.stderr, flush=True)
    try:
        return await panel.run()
    finally:
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.remove_signal_handler(sig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('preset', nargs='?', choices=['independent-discussion', 'leader-members', 'flat-peers'])
    parser.add_argument('brief', nargs='?', help='UTF-8 task brief')
    parser.add_argument('roster', nargs='?', help='JSON roster; source is relative to this file')
    parser.add_argument('--adapter', action='append', default=[], metavar='NAME=FILE',
                        help='Register a trusted Python adapter module exporting create_adapter(); repeat for additional harnesses')
    parser.add_argument('--run-dir', help='New directory outside source and the skill; defaults to a unique temporary directory')
    parser.add_argument('--max-cycles', type=int, default=3, help='Hard cap on draft/review cycles, including brief changes')
    parser.add_argument('--turn-seconds', type=float, default=180)
    parser.add_argument('--run-seconds', type=float, default=1800)
    parser.add_argument('--report-seconds', type=float, default=10)
    parser.add_argument('--pause-between-rounds', action='store_true', help='Read one host JSON decision from stdin at each boundary')
    parser.add_argument('--recover', metavar='RUN_DIR', help='Reconcile captured results once; report incomplete without redispatch')
    args = parser.parse_args()
    try:
        report = asyncio.run(execute(args))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'outcome': 'incomplete', 'error': str(exc), 'candidate': None, 'report': None}))
        return 2
    print(json.dumps(report, ensure_ascii=False))
    return {'agreed': 0, 'disagreement': 1, 'incomplete': 2, 'interrupted': 130}[report['outcome']]


if __name__ == '__main__':
    sys.exit(main())
