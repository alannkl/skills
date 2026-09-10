#!/usr/bin/env python3
"""Run or continue a saved panel discussion; stdout is one JSON report."""
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
from conversation import continue_panel, stop_panel


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
    existing = args.continue_run or args.stop or args.recover
    bounds = (args.max_cycles, args.idle_seconds, args.run_seconds, args.report_seconds)
    if existing and any((args.preset, args.brief, args.roster, args.run_dir)):
        raise ValueError('Saved panels retain their roster, preset, execution settings and run directory; reset explicitly to change them')
    if (args.stop or args.recover) and (any(x is not None for x in bounds) or args.unbounded):
        raise ValueError('--recover and --stop take no limits; pass changed limits with --continue')
    if args.unbounded and args.run_seconds is not None:
        raise ValueError('--unbounded removes the discussion deadline; do not combine it with --run-seconds')
    if bool(args.follow_up) != bool(args.continue_run):
        raise ValueError('--continue RUN_DIR requires --follow-up FILE; --follow-up is only for continuation')
    if args.stop:
        return stop_panel(args.stop)
    adapters = production_adapters(args.adapter)
    if args.recover:
        return recover_run(args.recover, adapters)
    checkpoint = host_input if args.pause_between_rounds else None
    if args.continue_run:
        panel = continue_panel(args.continue_run, Path(args.follow_up).read_text(), adapters, checkpoint,
                               limits={'max_cycles': args.max_cycles, 'idle_seconds': args.idle_seconds,
                                       'run_seconds': args.run_seconds, 'report_seconds': args.report_seconds,
                                       'unbounded': args.unbounded})
    else:
        if not all((args.preset, args.brief, args.roster)):
            raise ValueError('preset, brief and roster are required for a new panel')
        preset_path = Path(__file__).resolve().parent.parent / 'presets' / (args.preset + '.json')
        preset = json.loads(preset_path.read_text())
        roster_path = Path(args.roster).resolve()
        roster = json.loads(roster_path.read_text())
        for key in ('source', 'repository'):
            if roster.get(key):
                roster[key] = str((roster_path.parent / roster[key]).resolve())
        run_dir = args.run_dir or str(Path(tempfile.gettempdir()) / ('agent-panel-' + str(uuid.uuid4())))
        panel = Panel(preset, Path(args.brief).read_text(), roster, run_dir, adapters,
                      max_cycles=args.max_cycles if args.max_cycles is not None else 3,
                      idle_seconds=args.idle_seconds,
                      run_seconds=None if args.unbounded else args.run_seconds if args.run_seconds is not None else 3600,
                      report_seconds=args.report_seconds if args.report_seconds is not None else 10,
                      host_input=checkpoint)
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
                        help='Register a trusted Python adapter exporting create_adapter(); repeat to add harnesses')
    parser.add_argument('--run-dir', help='New directory outside source and skill; default: unique temporary directory')
    parser.add_argument('--max-cycles', type=int, help='Draft/review cycle cap per discussion, including brief changes; default 3, or the saved value with --continue')
    parser.add_argument('--idle-seconds', type=float, help='Kill an invocation after this long without new output, and cap each check; default: each harness\'s own window (Claude 300, Codex 600), or the saved value with --continue')
    parser.add_argument('--run-seconds', type=float, help='Autonomous-work allowance per discussion; waiting for a host decision pauses it and only a new --continue renews it; default 3600, or the saved value with --continue')
    parser.add_argument('--report-seconds', type=float, help='Reporting reserve; default 10, or the saved value with --continue')
    parser.add_argument('--unbounded', action='store_true', help='Explicit opt-in: no discussion deadline; idle and round caps still apply, so a turn that keeps writing is never killed. Saved across follow-ups until --run-seconds restores a ceiling')
    parser.add_argument('--pause-between-rounds', action='store_true', help='Read one host JSON decision from stdin at each boundary')
    saved = parser.add_mutually_exclusive_group()
    saved.add_argument('--recover', metavar='RUN_DIR', help='Reconcile captured results once; report incomplete without redispatch')
    saved.add_argument('--continue', dest='continue_run', metavar='RUN_DIR', help='Resume the same participants for another discussion')
    saved.add_argument('--stop', metavar='RUN_DIR', help='End an idle panel conversation without launching participants')
    parser.add_argument('--follow-up', metavar='FILE', help='Latest user request, decisions and acceptance criteria for --continue')
    args = parser.parse_args()
    try:
        report = asyncio.run(execute(args))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'outcome': 'incomplete', 'error': str(exc), 'candidate': None, 'report': None}))
        return 2
    print(json.dumps(report, ensure_ascii=False))
    if args.stop:
        return 0
    return {'agreed': 0, 'disagreement': 1, 'incomplete': 2, 'interrupted': 130}[report['outcome']]


if __name__ == '__main__':
    sys.exit(main())
