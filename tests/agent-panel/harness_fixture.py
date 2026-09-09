#!/usr/bin/env python3
"""Local subprocess fixture; never contacts an agent service."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid

args = sys.argv[1:]
raw = sys.stdin.read()
if 'PANEL_INPUT\n' in raw:
    payload = json.loads(raw.split('PANEL_INPUT\n')[1])
    pid, phase = payload['participant_id'], payload['phase']
    block = {'participant_id': pid, 'kind': 'review' if phase == 'review' else 'candidate' if phase == 'draft' else 'contribution',
             'text': 'Bounded design proposal', 'messages': []}
    if phase == 'assign':
        block['assignments'] = {p['id']: 'Investigate role' for p in payload['roster']}
    if phase == 'review':
        block.update(revision=payload['candidate']['revision'], content_hash=payload['candidate']['content_hash'],
                     decision='approve', reasons=['All criteria addressed'], assumptions=[], blocking_objections=[])
else:
    block = {'text': raw}

if raw == 'WAIT_WITH_CHILD':
    child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(300)'])
    def stop(*_):
        child.terminate()
        child.wait()
        sys.exit(0)
    signal.signal(signal.SIGTERM, stop)
    print(json.dumps({'parent': os.getpid(), 'child': child.pid}), flush=True)
    time.sleep(300)

if 'exec' in args:
    session = args[-2] if 'resume' in args else str(uuid.uuid4())
    for event in ({'type': 'thread.started', 'thread_id': session},
                  {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': json.dumps(block)}},
                  {'type': 'turn.completed', 'usage': {'input_tokens': 10, 'output_tokens': 3}}):
        print(json.dumps(event))
else:
    flag = '--resume' if '--resume' in args else '--session-id'
    session = args[args.index(flag) + 1]
    print(json.dumps({'type': 'result', 'subtype': 'success', 'session_id': session,
                      'is_error': False, 'result': json.dumps(block), 'usage': {'input_tokens': 10}, 'total_cost_usd': 0}))
