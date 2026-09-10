"""Continue saved panel sessions between bounded discussions, without idle processes."""
import asyncio
import json

from engine import Panel, validate_limits, validate_roster
from execution import ExecutionPolicy
from records import Records, digest, snapshot_hash
from workspace import Workspaces, result_hash


def restore_panel(records, manifest, adapters, host_input=None):
    if manifest.get('version') not in (3, 4):
        raise ValueError('Unsupported saved panel format; retain its artifacts and reset explicitly')
    panel = Panel.__new__(Panel)
    panel.records, panel.manifest, panel.adapters = records, manifest, adapters
    panel.preset = manifest['preset']
    panel.ids, panel.required = validate_roster(manifest['roster'], adapters, panel.preset)
    panel.people = manifest['participants']
    panel.drafter = manifest['drafter']
    panel.execution = ExecutionPolicy(manifest['execution'], panel.required, panel.drafter)
    panel.workspaces = Workspaces.__new__(Workspaces)
    panel.workspaces.root, panel.workspaces.execution = records.root, panel.execution
    panel.workspaces.repository = manifest['workspaces']['repository']
    panel.workspaces.base_revision = manifest['workspaces']['base_revision']
    panel.workspaces.directories = manifest['workspaces']['working_directories']
    panel.workspaces.source_hash = manifest['source_hash']
    panel.brief_revision = manifest['brief_revision']
    panel.brief = (records.root / f'brief-{panel.brief_revision}.md').read_text()
    panel.discussion_start = manifest.get('discussion_start', 0)
    panel.candidate = manifest.get('candidate')
    panel.reviews, panel.unresolved = {}, []
    panel.cycles_used = manifest.get('cycles_used', 0)
    panel.rounds_used = 0
    # Turn IDs also name artifact directories and must never repeat across discussions.
    panel.turn = max((int(e['data']['turn_id'][1:]) for e in records.events if e['kind'] == 'dispatch'), default=0)
    if 'idle_seconds' not in manifest['limits']:
        # Panels saved before the idle bound keep their per-turn cap as the idle window.
        manifest['limits']['idle_seconds'] = manifest['limits'].pop('turn_seconds')
    set_limits(panel, manifest['limits'])
    panel.stop, panel.active = asyncio.Event(), {}
    panel.host_input, panel.phase = host_input, 'setup'
    return panel


def set_limits(panel, limits):
    panel.max_cycles, panel.max_rounds = limits['max_cycles'], limits['max_rounds']
    panel.idle_seconds = limits['idle_seconds']
    panel.run_seconds, panel.report_seconds = limits['run_seconds'], limits['report_seconds']
    panel.cancel_seconds = min(4.0, limits['report_seconds'] - 1.0)
    panel.restart_clock()


def revised_limits(panel, saved, overrides):
    """Limits bound time and cycles, not evidence, so a follow-up may change them without a reset."""
    overrides = dict(overrides or {})
    unbounded = overrides.pop('unbounded', False)
    limits = dict(saved, **{k: v for k, v in overrides.items() if v is not None})
    if unbounded:
        limits['run_seconds'] = None
    validate_limits(limits['max_cycles'], limits['idle_seconds'], limits['run_seconds'], limits['report_seconds'])
    limits['max_rounds'] = len(panel.preset['opening']) + limits['max_cycles'] * 3
    return limits


def continue_panel(run_dir, brief, adapters, host_input=None, limits=None):
    if not isinstance(brief, str) or not brief.strip():
        raise ValueError('Follow-up must contain the latest user request and acceptance criteria')
    records = Records(run_dir, existing=True)
    try:
        manifest = json.loads((records.root / 'manifest.json').read_text())
        if manifest['status'] == 'running':
            raise ValueError('Panel has unfinished work; use --recover first, without redispatch')
        if manifest.get('conversation') == 'stopped':
            raise ValueError('Panel is stopped; reset explicitly with a new run directory')
        if not (records.root / 'report.json').exists():
            raise ValueError('Panel has no completed report; use --recover first')
        report = json.loads((records.root / 'report.json').read_text())
        if report.get('discussion', 1) != manifest.get('discussion', 1):
            raise ValueError('Latest report publication is unfinished; use --recover first')
        recent = records.events[manifest.get('discussion_start', 0):]
        terminals = {e['data']['dispatch_id']: e['data'] for e in recent if e['kind'] == 'terminal_result'}
        if any(e['kind'] == 'dispatch' and e['id'] not in terminals for e in recent):
            raise ValueError('Unreconciled dispatch; use --recover first')
        if any(t['result']['outcome'] == 'indeterminate' for t in terminals.values()) or any(
                e['kind'] == 'cancel' and not e['data']['confirmed_inactive'] for e in recent):
            raise ValueError('Indeterminate delivery or termination; resolve effects before an explicit reset')
        if any(not p.get('session_id') for p in manifest['participants'].values()):
            raise ValueError('A participant has no resumable session; reset explicitly instead of replacing it')
        if snapshot_hash(manifest['source']) != manifest['source_hash']:
            raise ValueError('Source snapshot changed; restore the evidence or reset explicitly')
        if manifest.get('candidate') and result_hash(manifest['candidate']) != manifest['candidate']['content_hash']:
            raise ValueError('Previous result changed; restore its evidence before continuing')
        panel = restore_panel(records, manifest, adapters, host_input)
        manifest['limits'] = revised_limits(panel, manifest['limits'], limits)
        set_limits(panel, manifest['limits'])
        archive = records.root / 'reports' / f"discussion-{manifest.get('discussion', 1)}.json"
        if not archive.exists():
            archive.parent.mkdir(exist_ok=True)
            archive.write_bytes((records.root / 'report.json').read_bytes())
            archive.chmod(0o444)
        panel.brief, panel.brief_revision = brief, panel.brief_revision + 1
        panel.discussion_start = len(records.events)
        panel.candidate, panel.reviews, panel.unresolved = None, {}, []
        panel.cycles_used = 0
        (records.root / f'brief-{panel.brief_revision}.md').write_text(brief)
        manifest.update(version=4, discussion=manifest.get('discussion', 1) + 1,
                        discussion_start=panel.discussion_start, conversation='active', status='running',
                        reason='Follow-up discussion', candidate=None, cycles_used=0,
                        brief_revision=panel.brief_revision, brief_hash=digest(brief.encode()))
        records.save_manifest(manifest)
        records.append('discussion_start', 'setup', sender='host', visibility=['all'],
                       discussion=manifest['discussion'], brief_revision=panel.brief_revision, text=brief,
                       limits=manifest['limits'])
        return panel
    except BaseException:
        records.close()
        raise


def stop_panel(run_dir):
    records = Records(run_dir, existing=True)
    try:
        manifest = json.loads((records.root / 'manifest.json').read_text())
        if manifest['status'] == 'running':
            raise ValueError('Panel has unfinished work; stop its process and recover before closing the conversation')
        if manifest.get('conversation') != 'stopped':
            manifest['conversation'] = 'stopped'
            records.save_manifest(manifest)
            records.append('conversation_stop', 'idle', sender='host', visibility=['all'])
        return {'conversation': 'stopped', 'manifest': str(records.root / 'manifest.json'),
                'report': str(records.root / 'report.json')}
    finally:
        records.close()
