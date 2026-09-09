"""Reconcile crash leftovers without repeating potentially completed model work."""
import json
from engine import Panel
from records import Records
from execution import ExecutionPolicy
from workspace import Workspaces
from adapters.base import Terminal, recover_terminal


def recover_run(run_dir, adapters):
    records = Records(run_dir, existing=True)
    manifest = json.loads((records.root / 'manifest.json').read_text())
    if manifest['status'] != 'running' and (records.root / 'report.json').exists():
        records.close()
        return json.loads((records.root / 'report.json').read_text())
    panel = Panel.__new__(Panel)
    panel.records, panel.manifest, panel.adapters = records, manifest, adapters
    panel.people = manifest['participants']
    panel.ids, panel.required = list(panel.people), manifest['required_approvers']
    if manifest.get('version') != 3:
        records.close()
        raise ValueError('This unfinished run uses an earlier format; retain its artifacts and start a new run')
    panel.execution = ExecutionPolicy(manifest.get('execution'), panel.required, manifest['drafter'])
    panel.workspaces = Workspaces.__new__(Workspaces)
    panel.workspaces.execution = panel.execution
    panel.workspaces.root = records.root
    panel.workspaces.repository = manifest.get('workspaces', {}).get('repository')
    panel.workspaces.base_revision = manifest.get('workspaces', {}).get('base_revision')
    panel.workspaces.directories = manifest.get('workspaces', {}).get('working_directories', {})
    panel.brief_revision = manifest['brief_revision']
    panel.candidate = manifest.get('candidate')
    panel.reviews = {}
    panel.cycles_used = manifest.get('cycles_used', 0)
    import asyncio
    panel.stop = asyncio.Event()
    uncertain = []
    for event in list(records.events):
        if event['kind'] == 'candidate':
            panel.candidate = {k: value for k, value in event['data'].items() if k != 'brief_revision'}
        if event['kind'] != 'dispatch':
            continue
        data = event['data']
        pid = data['participant']
        panel.phase = event['phase']
        panel.brief_revision = data['brief_revision']
        if panel.phase == 'review':
            panel.candidate = data['candidate']
        adapter = adapters.get(panel.people[pid]['harness'])
        result = recover_terminal(adapter, data['attempt_dir']) if adapter else Terminal(None, outcome='indeterminate', error='Adapter unavailable for reconciliation')
        panel.ingest(pid, result, event, data.get('private', False))
        if result.outcome == 'indeterminate':
            uncertain.append(data['turn_id'])
    panel.brief_revision = manifest['brief_revision']
    reason = 'Crash recovery reconciled persisted results; restart explicitly for a new approval run'
    if uncertain:
        reason += '; indeterminate delivery, no redispatch: ' + ', '.join(uncertain)
    return panel.finish('incomplete', reason)
