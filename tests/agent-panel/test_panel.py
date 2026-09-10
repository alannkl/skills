"""Behavior scaffold from design v5. Bodies are added after the contract is pinned."""
import unittest
import asyncio
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'agent-panel' / 'scripts'))
from engine import Panel, StopRun
from recovery import recover_run
from records import Records
from adapters.base import Terminal
from fakes import FakeAdapter

PACKAGE = Path(__file__).resolve().parents[2] / 'agent-panel'


def preset(name):
    return json.loads((PACKAGE / 'presets' / (name + '.json')).read_text())


class Fixture:
    def __init__(self, root, name='independent-discussion', behavior=None, **limits):
        self.source = Path(root) / 'evidence'
        self.source.mkdir(exist_ok=True)
        (self.source / 'contract.txt').write_text('Frozen task evidence')
        self.adapter = FakeAdapter(behavior)
        self.roster = {'source': str(self.source), 'drafter': 'ada', 'leader': 'ada',
                       'participants': [{'id': pid, 'role': role, 'harness': 'fake', 'settings': {'model': 'simulation'}}
                                        for pid, role in [('ada', 'design'), ('bert', 'safety'), ('cy', 'operations')]]}
        self.panel = Panel(preset(name), 'Design a bounded runner', self.roster, Path(root) / 'run', {'fake': self.adapter},
                           **dict({'turn_seconds': 2, 'run_seconds': 30, 'max_cycles': 2}, **limits))

    async def run(self):
        return await self.panel.run()



class PanelBehavior(unittest.TestCase):
    def run_scenario(self, scenario):
        with tempfile.TemporaryDirectory() as root:
            asyncio.run(scenario(root))

    def test_independent_rounds(self):
        """Given three designers sharing an adapter, when discussing, then initial inputs exclude peers, critique uses one cutoff, sessions stay separate and all approve."""
        async def scenario(root):
            fixture = Fixture(root)
            report = await fixture.run()
            self.assertEqual(report['outcome'], 'agreed')
            self.assertEqual(set(report['reviews']), {'ada', 'bert', 'cy'})
            inputs = fixture.adapter.inputs
            first = [i for i in inputs if i['phase'] == 'initial']
            self.assertEqual(len(first), 3)
            self.assertTrue(all(not i['events'] and i['candidate'] is None for i in first))
            self.assertEqual(len({i['session'] for i in first}), 3)
            for pid in ('ada', 'bert', 'cy'):
                own = [i for i in inputs if i['participant_id'] == pid]
                self.assertEqual(len({i['session'] for i in own}), 1)
                delivered = [e['id'] for i in own for e in i['events']]
                self.assertEqual(len(delivered), len(set(delivered)))
            critique = [i for i in inputs if i['phase'] == 'critique']
            self.assertEqual(len({i['cutoff'] for i in critique}), 1)
            for i in critique:
                self.assertEqual({e['sender'] for e in i['events']}, {'ada', 'bert', 'cy'})
                self.assertTrue(all(e['phase'] == 'reveal' for e in i['events']))
            self.assertEqual(len({i['candidate']['content_hash'] for i in inputs if i['phase'] == 'review'}), 1)
        with tempfile.TemporaryDirectory() as root:
            asyncio.run(scenario(root))


    def test_leader_assignments(self):
        """Given a leader and two members, when planning, then the leader assigns the roster, integrates contributions and still needs every approval."""

        async def scenario(root):
            f = Fixture(root, 'leader-members')
            report = await f.run()
            self.assertEqual(report['outcome'], 'agreed')
            self.assertEqual([(i['phase'], i['participant_id']) for i in f.adapter.inputs[:1]], [('assign', 'ada')])
            contributions = [i for i in f.adapter.inputs if i['phase'] == 'contribute']
            self.assertEqual(len(contributions), 3)
            for i in contributions:
                self.assertEqual(set(i['events'][0]['data']['assignments']), {'ada', 'bert', 'cy'})
            self.assertEqual([i['participant_id'] for i in f.adapter.inputs if i['phase'] == 'draft'], ['ada'])
            self.assertEqual(set(report['reviews']), {'ada', 'bert', 'cy'})
        self.run_scenario(scenario)


    def test_flat_responsibilities(self):
        """Given three flat peers, when planning, then all propose responsibilities before contribution and the declared drafter integrates."""

        async def scenario(root):
            f = Fixture(root, 'flat-peers')
            report = await f.run()
            self.assertEqual(report['outcome'], 'agreed')
            responsibilities = [i for i in f.adapter.inputs if i['phase'] == 'responsibilities']
            self.assertEqual(len(responsibilities), 3)
            self.assertTrue(all(not i['events'] for i in responsibilities))
            contributions = [i for i in f.adapter.inputs if i['phase'] == 'contribute']
            self.assertEqual(len({i['cutoff'] for i in contributions}), 1)
            for i in contributions:
                self.assertEqual({e['sender'] for e in i['events']}, {'ada', 'bert', 'cy'})
            self.assertEqual(set(report['reviews']), {'ada', 'bert', 'cy'})
        self.run_scenario(scenario)


    def test_third_review_required(self):
        """Given two approvals and a missing or stale third review, when finalizing, then the outcome is incomplete."""

        for name in ('independent-discussion', 'leader-members', 'flat-peers'):
            for bad in ('fail', {'revision': 'stale'}, {'decision': 'unable'}):
                async def scenario(root):
                    f = Fixture(root, name, lambda p: bad if p['participant_id'] == 'cy' and p['phase'] == 'review' else None)
                    report = await f.run()
                    self.assertEqual(report['outcome'], 'incomplete')
                    self.assertFalse(report['approved'])
                    self.assertEqual(report['required_approvers'], ['ada', 'bert', 'cy'])
                    self.assertEqual(report['reviews']['ada']['decision'], 'approve')
                    self.assertEqual(report['reviews']['bert']['decision'], 'approve')
                self.run_scenario(scenario)


    def test_revision_invalidates_approval(self):
        """Given a blocking objection to A, when B is drafted, then all reviewers must approve B including its drafter."""

        async def scenario(root):
            def behavior(p):
                if p['phase'] == 'review' and p['participant_id'] == 'cy' and p['candidate']['revision'] == 'b1-r1':
                    return {'decision': 'object', 'blocking_objections': ['Missing cancellation semantics']}
                if p['phase'] == 'draft' and p['candidate'] is not None:
                    return {'text': 'Revised design with cancellation semantics'}
            f = Fixture(root, behavior=behavior)
            report = await f.run()
            self.assertEqual(report['outcome'], 'agreed')
            reviews = [i for i in f.adapter.inputs if i['phase'] == 'review']
            self.assertEqual(len(reviews), 6)
            for revision in ('b1-r1', 'b1-r2'):
                self.assertEqual({i['participant_id'] for i in reviews if i['candidate']['revision'] == revision}, {'ada', 'bert', 'cy'})
            self.assertTrue(all(r['revision'] == 'b1-r2' for r in report['reviews'].values()))
            self.assertTrue(all(i['unresolved_reviews'] for i in reviews if i['candidate']['revision'] == 'b1-r2'))
            self.assertEqual(Path(report['candidate']).read_text(), 'Revised design with cancellation semantics')
        self.run_scenario(scenario)


    def test_disagreement_cap(self):
        """Given persistent objections, when the round cap is reached, then return disagreement and an unapproved candidate."""

        for name in ('independent-discussion', 'leader-members', 'flat-peers'):
            async def scenario(root):
                f = Fixture(root, name, lambda p: {'decision': 'object', 'blocking_objections': ['Unresolved evidence']} if p['phase'] == 'review' else None)
                report = await f.run()
                self.assertEqual(report['outcome'], 'disagreement')
                self.assertFalse(report['approved'])
                self.assertEqual(len([i for i in f.adapter.inputs if i['phase'] == 'review']), 6)
                self.assertEqual(len([i for i in f.adapter.inputs if i['phase'] == 'clarify']), 3)
            self.run_scenario(scenario)


    def test_required_initial_failure(self):
        """Given a missing required initial contribution, when recovery is exhausted, then preserve partial output and stop incomplete before reveal."""

        async def scenario(root):
            f = Fixture(root, behavior=lambda p: 'fail' if p['participant_id'] == 'cy' else None)
            report = await f.run()
            self.assertEqual(report['outcome'], 'incomplete')
            self.assertIsNone(report['candidate'])
            self.assertEqual(len(f.adapter.inputs), 3)
            self.assertFalse(any(e['phase'] == 'reveal' for e in f.panel.records.events))
            self.assertEqual(len([e for e in f.panel.records.events if e['kind'] == 'message']), 2)
        self.run_scenario(scenario)


    def test_skipped_critique_catches_up(self):
        """Given a reconciled inactive failed critique, when that reviewer resumes, then still-uncompleted eligible events are delivered and final approval remains required."""

        async def scenario(root):
            f = Fixture(root, behavior=lambda p: 'fail' if p['participant_id'] == 'cy' and p['phase'] == 'critique' else None)
            report = await f.run()
            self.assertEqual(report['outcome'], 'agreed')
            own = [i for i in f.adapter.inputs if i['participant_id'] == 'cy']
            critique = next(i for i in own if i['phase'] == 'critique')
            review = next(i for i in own if i['phase'] == 'review')
            self.assertTrue({e['id'] for e in critique['events']} <= {e['id'] for e in review['events']})
            self.assertEqual(len({i['session'] for i in own}), 1)
            self.assertEqual(len(report['failures']), 1)
        self.run_scenario(scenario)


    def test_indeterminate_delivery(self):
        """Given possibly executed work without established completion, when recovering, then record uncertainty and stop incomplete without redispatch."""

        async def scenario(root):
            f = Fixture(root, behavior=lambda p: 'uncertain' if p['participant_id'] == 'cy' and p['phase'] == 'critique' else None)
            report = await f.run()
            self.assertEqual(report['outcome'], 'incomplete')
            self.assertIn('Indeterminate', report['reason'])
            self.assertEqual(len([i for i in f.adapter.inputs if i['participant_id'] == 'cy']), 2)
            self.assertFalse(any(i['phase'] == 'draft' for i in f.adapter.inputs))
        self.run_scenario(scenario)


    def test_recover_persisted_result_once(self):
        """Given a persisted valid harness result without an ingested terminal event, when recovering twice, then ingest it once without executing again."""

        async def scenario(root):
            f = Fixture(root, behavior=lambda p: 'crash_after_persist')
            report = await f.run()
            self.assertEqual(report['outcome'], 'agreed')
            dispatches = [e['id'] for e in f.panel.records.events if e['kind'] == 'dispatch']
            terminals = [e['data']['dispatch_id'] for e in f.panel.records.events if e['kind'] == 'terminal_result']
            self.assertEqual(sorted(dispatches), sorted(terminals))
        self.run_scenario(scenario)

        async def crash_scenario(root):
            f = Fixture(root)
            original = f.panel.records.append
            def crash(kind, *args, **kwargs):
                if kind == 'message':
                    raise OSError('Crash after durable terminal, before applying result')
                return original(kind, *args, **kwargs)
            f.panel.records.append = crash
            with self.assertRaises(StopRun):
                await f.panel.round('initial', f.panel.ids, 'Design independently', private=True)
            f.panel.records.close()
            before = len(f.adapter.inputs)
            report = recover_run(Path(root) / 'run', {'fake': f.adapter})
            second = recover_run(Path(root) / 'run', {'fake': f.adapter})
            self.assertEqual(report, second)
            self.assertEqual(report['outcome'], 'incomplete')
            self.assertEqual(len(f.adapter.inputs), before)
            events = [json.loads(line) for line in Path(report['events']).read_text().splitlines()]
            self.assertEqual(len([e for e in events if e['kind'] == 'terminal_result']), 3)
            self.assertEqual(len([e for e in events if e['kind'] == 'message']), 3)
        self.run_scenario(crash_scenario)


    def test_pre_dispatch_retry(self):
        """Given a known transient failure before launch, when retried, then keep the same turn and inputs and allow only one retry."""

        async def scenario(root):
            f = Fixture(root, behavior=lambda p: 'transient' if p['participant_id'] == 'cy' and p['phase'] == 'initial' else None)
            self.assertEqual((await f.run())['outcome'], 'agreed')
            retries = [e['data'] for e in f.panel.records.events if e['kind'] == 'dispatch' and e['data']['participant'] == 'cy' and e['phase'] == 'initial']
            self.assertEqual([d['attempt'] for d in retries], [1, 2])
            self.assertEqual(retries[0]['turn_id'], retries[1]['turn_id'])
            self.assertEqual(Path(retries[0]['attempt_dir'], 'input.txt').read_bytes(), Path(retries[1]['attempt_dir'], 'input.txt').read_bytes())
        self.run_scenario(scenario)


    def test_malformed_output(self):
        """Given exit zero but malformed or nonterminal output, when collected, then no approval or completed-input cursor is credited."""

        async def scenario(root):
            f = Fixture(root, behavior=lambda p: 'malformed' if p['participant_id'] == 'cy' and p['phase'] == 'review' else None)
            report = await f.run()
            self.assertEqual(report['outcome'], 'incomplete')
            self.assertNotIn('cy', report['reviews'])
            review = next(i for i in f.adapter.inputs if i['participant_id'] == 'cy' and i['phase'] == 'review')
            manifest = json.loads(Path(report['manifest']).read_text())
            self.assertTrue(set(manifest['participants']['cy']['delivered']).isdisjoint({e['id'] for e in review['events']}))
        self.run_scenario(scenario)


    def test_identity_and_routing(self):
        """Given a participant claiming human authority or naming recipients, when ingested, then identity stays bound and only eligible recipients see messages without extra scheduling."""

        async def scenario(root):
            def behavior(p):
                if p['participant_id'] == 'cy' and p['phase'] == 'initial':
                    return {'sender': 'host', 'human_decision': {'action': 'authorize'},
                            'messages': [{'recipients': ['bert'], 'text': 'ROUTED_ONLY_TO_BERT'}]}
            f = Fixture(root, behavior=behavior)
            report = await f.run()
            self.assertEqual(report['outcome'], 'agreed')
            self.assertEqual(len(f.adapter.inputs), 10)
            for i in f.adapter.inputs:
                routed = any(e['data'].get('text') == 'ROUTED_ONLY_TO_BERT' for e in i['events'])
                if i['phase'] == 'critique':
                    self.assertEqual(routed, i['participant_id'] == 'bert')
            self.assertFalse(any(e['kind'] == 'human_decision' for e in f.panel.records.events))
            self.assertTrue(all(e['sender'] == 'cy' for e in f.panel.records.events if e['data'].get('text') == 'ROUTED_ONLY_TO_BERT'))
        self.run_scenario(scenario)


    def test_human_brief_change(self):
        """Given prior approvals, when the host changes the brief between rounds, then a new brief revision forces fresh contributions, draft and reviews."""

        async def scenario(root):
            changed = False
            async def host(phase):
                nonlocal changed
                if phase == 'review' and not changed:
                    changed = True
                    return {'action': 'brief', 'text': 'New brief: include cancellation'}
                return {'action': 'continue'}
            f = Fixture(root, host_input=host)
            report = await f.run()
            self.assertEqual(report['outcome'], 'agreed')
            self.assertTrue(all(r['revision'] == 'b2-r2' for r in report['reviews'].values()))
            new_initial = [i for i in f.adapter.inputs if i['phase'] == 'initial' and i['brief_revision'] == 2]
            self.assertEqual(len(new_initial), 3)
            self.assertTrue(all(i['brief'] == 'New brief: include cancellation' and i['candidate'] is None for i in new_initial))
            self.assertTrue(any(e['kind'] == 'human_decision' and e['sender'] == 'host' for e in f.panel.records.events))
        self.run_scenario(scenario)


    def test_cancel_all(self):
        """Given three active participants, when stopped, then all are cancelled, no further turns start and report interrupted with uncertain effects if any."""

        for name in ('independent-discussion', 'leader-members', 'flat-peers'):
            async def scenario(root):
                waiting_phase = 'contribute' if name == 'leader-members' else 'initial' if name == 'independent-discussion' else 'responsibilities'
                f = Fixture(root, name, lambda p: 'wait' if p['phase'] == waiting_phase else None)
                task = asyncio.create_task(f.run())
                while len(f.adapter.active) < 3:
                    await asyncio.sleep(0.005)
                count = len(f.adapter.inputs)
                f.panel.request_stop()
                report = await asyncio.wait_for(task, 2)
                self.assertEqual(report['outcome'], 'interrupted')
                self.assertEqual(set(f.adapter.cancelled), {'ada', 'bert', 'cy'})
                self.assertEqual(len(f.adapter.inputs), count)
                self.assertFalse(f.adapter.active)
                self.assertEqual(len(report['cancellations']), 3)
            self.run_scenario(scenario)


    def test_deadlines(self):
        """Given slow required work, when turn or run time expires, then terminate it and reserve time for an incomplete report."""

        for limits in ({'turn_seconds': 0.03}, {'turn_seconds': 10, 'run_seconds': 5.05, 'report_seconds': 5}):
            async def scenario(root):
                f = Fixture(root, behavior=lambda p: 'wait', **limits)
                report = await asyncio.wait_for(f.run(), 2)
                self.assertEqual(report['outcome'], 'incomplete')
                self.assertEqual(set(f.adapter.cancelled), {'ada', 'bert', 'cy'})
                self.assertFalse(f.adapter.active)
            self.run_scenario(scenario)


    def test_extension(self):
        """Given another registered adapter name, when a three-member roster runs, then the unchanged scheduler reaches joint approval."""

        async def scenario(root):
            f = Fixture(root)
            extra = FakeAdapter()
            f.panel.adapters['other'] = extra
            f.panel.people['cy']['harness'] = 'other'
            report = await f.run()
            self.assertEqual(report['outcome'], 'agreed')
            self.assertEqual({i['participant_id'] for i in extra.inputs}, {'cy'})
            self.assertEqual(len({p['session_id'] for p in f.panel.people.values()}), 3)
        self.run_scenario(scenario)


    def test_invalid_roster(self):
        """Given duplicate IDs, unknown approvers or invalid settings, when starting, then fail before launching any participant."""

        for mutation in (lambda r: r['participants'].append(r['participants'][0]),
                         lambda r: r.update(required_approvers=['ghost']),
                         lambda r: r['participants'][0]['settings'].update(sandbox='danger-full-access'),
                         lambda r: r['participants'][0].update(harness='unknown'),
                         lambda r: r.update(leader='ghost'),
                         lambda r: r['participants'][0].update(id='all')):
            with tempfile.TemporaryDirectory() as root:
                f = Fixture(root)
                mutation(f.roster)
                with self.assertRaises(ValueError):
                    Panel(preset('leader-members'), 'brief', f.roster, Path(root) / 'invalid-run', {'fake': f.adapter})
                self.assertFalse(f.adapter.inputs)
                f.panel.records.close()


    def test_snapshot(self):
        """Given source files, when starting a design run, then all participants get the same frozen snapshot and source mutation stops agreement."""

        async def scenario(root):
            f = Fixture(root)
            (f.source / 'contract.txt').write_text('Caller changed original source after snapshot')
            self.assertEqual((await f.run())['outcome'], 'agreed')
            self.assertTrue(all(Path(i['source_snapshot'], 'contract.txt').read_text() == 'Frozen task evidence' for i in f.adapter.inputs))
        self.run_scenario(scenario)
        async def mutation(root):
            f = Fixture(root)
            snapshot = Path(f.panel.manifest['source']) / 'contract.txt'
            snapshot.chmod(0o644)
            snapshot.write_text('Unexpected modification')
            report = await f.run()
            self.assertEqual(report['outcome'], 'incomplete')
            self.assertIn('snapshot changed', report['reason'])
            self.assertFalse(f.adapter.inputs)
        self.run_scenario(mutation)



class AdditionalBoundaries(unittest.TestCase):
    run_scenario = PanelBehavior.run_scenario
    # New cases pin hazards found while reading cancellation and persistence control flow.
    def test_stop_while_waiting_for_host(self):
        """Given a paused boundary, when signalled to stop, then finish interrupted without requiring stdin."""
        async def scenario(root):
            waiting = asyncio.Event()
            async def host(_):
                waiting.set()
                await asyncio.sleep(3600)
            f = Fixture(root, host_input=host)
            run = asyncio.create_task(f.run())
            await asyncio.wait_for(waiting.wait(), 2)
            f.panel.request_stop()
            report = await asyncio.wait_for(run, 1)
            self.assertEqual(report['outcome'], 'interrupted')
            self.assertEqual(len(f.adapter.inputs), 3)
        self.run_scenario(scenario)

    def test_repeated_brief_changes_hit_round_cap(self):
        """Given a host changing the brief at every boundary, when the round cap is consumed, then finish incomplete within the original budget."""
        async def scenario(root):
            async def host(_):
                return {'action': 'brief', 'text': 'Another full brief'}
            f = Fixture(root, host_input=host, max_cycles=1)
            report = await f.run()
            self.assertEqual(report['outcome'], 'incomplete')
            self.assertIn('round cap', report['reason'])
            self.assertEqual(len([e for e in f.panel.records.events if e['kind'] == 'phase_start']), 5)
        self.run_scenario(scenario)

    def test_unknown_dispatch_error_is_not_retried(self):
        """Given an adapter start that fails after uncertain work, when scheduling, then record indeterminate terminal evidence without retry."""
        async def scenario(root):
            f = Fixture(root)
            def fail(*_):
                raise RuntimeError('Uncertain launch')
            f.adapter.start = fail
            report = await f.run()
            self.assertEqual(report['outcome'], 'incomplete')
            self.assertEqual(len(report['failures']), 3)
            self.assertTrue(all(x['result']['outcome'] == 'indeterminate' for x in report['failures']))
            self.assertEqual(len([e for e in f.panel.records.events if e['kind'] == 'dispatch']), 3)
        self.run_scenario(scenario)

    def test_uncertain_cancellation_is_reported(self):
        """Given an adapter unable to confirm termination, when cancelled, then retain interrupted status and uncertain effects for every participant."""
        async def scenario(root):
            f = Fixture(root, behavior=lambda _: 'wait')
            cancel = f.adapter.cancel
            async def uncertain(handle):
                await cancel(handle)
                return False
            f.adapter.cancel = uncertain
            run = asyncio.create_task(f.run())
            while len(f.adapter.active) < 3:
                await asyncio.sleep(0.005)
            f.panel.request_stop()
            report = await run
            self.assertEqual(report['outcome'], 'interrupted')
            self.assertEqual(len(report['cancellations']), 3)
            self.assertTrue(all(not c['confirmed_inactive'] and c['uncertain_effects'] for c in report['cancellations']))
        self.run_scenario(scenario)

    def test_candidate_tampering_blocks_agreement(self):
        """Given approved bytes that change before finalization, when finalizing, then never return agreed."""
        for remove in (False, True):
            async def scenario(root):
                f = Fixture(root)
                async def host(phase):
                    if phase == 'review':
                        candidate = Path(f.panel.candidate['path'])
                        if remove:
                            candidate.unlink()
                        else:
                            candidate.chmod(0o644)
                            candidate.write_text('Not the reviewed candidate')
                    return {'action': 'continue'}
                f.panel.host_input = host
                report = await f.run()
                self.assertEqual(report['outcome'], 'incomplete')
                self.assertFalse(report['approved'])
            self.run_scenario(scenario)


if __name__ == '__main__':
    unittest.main()
