"""Brief-driven behavior, pinned before removing runtime task categories."""
import unittest
from pathlib import Path
import test_panel
from task_fixture import TaskFixture
from execution import ExecutionPolicy




class BriefContract(unittest.TestCase):
    run_scenario = test_panel.PanelBehavior.run_scenario
    def test_unregistered_work_and_arbitrary_data(self):
        """Given an unfamiliar task and custom result data, when three agents run each preset, then the brief and data are preserved without selecting a task profile."""

        for preset in ('independent-discussion', 'leader-members', 'flat-peers'):
            async def scenario(root):
                brief = 'Arrange observation slots for a fictional moon. Return slots and your allocation rationale.'
                expected = {'slots': [{'observer': 'A', 'hour': 3}], 'allocation_rationale': 'Avoid overlapping observations.'}
                def behavior(p):
                    if p['phase'] == 'draft':
                        return {'text': 'Observer A has the 03:00 slot.', 'data': expected}
                f = TaskFixture(root, name=preset, brief=brief, behavior=behavior)
                report = await f.run()
                self.assertEqual(report['outcome'], 'agreed', report['reason'])
                self.assertEqual(report['data'], expected)
                self.assertEqual(set(report['reviews']), {'ada', 'bert', 'cy'})
                self.assertTrue(all(p['brief'] == brief and 'task' not in p for p in f.adapter.inputs))
                self.assertNotIn('task_profile', f.panel.manifest)
                self.assertFalse((Path(__file__).resolve().parents[2] / 'agent-panel' / 'tasks').exists())
            self.run_scenario(scenario)


    def test_data_changes_need_fresh_approval(self):
        """Given identical prose but changed structured output, when revised, then all reviewers must approve the new result hash."""

        async def scenario(root):
            drafts = 0
            def behavior(p):
                nonlocal drafts
                if p['phase'] == 'draft':
                    drafts += 1
                    return {'text': 'Allocation result.', 'data': {'slot': drafts}}
                if p['phase'] == 'review' and p['participant_id'] == 'cy' and p['candidate']['revision'] == 'b1-r1':
                    return {'decision': 'object', 'blocking_objections': ['Use the second slot.']}
            f = TaskFixture(root, behavior=behavior, max_cycles=2)
            report = await f.run()
            self.assertEqual(report['outcome'], 'agreed')
            candidates = [e['data'] for e in f.panel.records.events if e['kind'] == 'candidate']
            self.assertEqual(candidates[0]['text'], candidates[1]['text'])
            self.assertNotEqual(candidates[0]['content_hash'], candidates[1]['content_hash'])
            self.assertEqual(report['data'], {'slot': 2})
            self.assertTrue(all(r['revision'] == 'b1-r2' for r in report['reviews'].values()))
            self.assertEqual(len([i for i in f.adapter.inputs if i['phase'] == 'review']), 6)
        self.run_scenario(scenario)


    def test_execution_is_not_inferred_from_subject(self):
        """Given any brief, when explicit access settings change, then only those settings determine web, command and file access."""

        readonly = ExecutionPolicy({}, ['a', 'b'], 'a')
        self.assertFalse(readonly.capabilities()['web'])
        self.assertFalse(readonly.capabilities()['shell'])
        inspect = ExecutionPolicy({'workspace': 'inspect', 'web': True, 'checks': [['python3', 'check.py']]}, ['a', 'b'], 'a')
        self.assertTrue(inspect.capabilities()['web'])
        self.assertTrue(inspect.capabilities()['shell'])
        self.assertFalse(inspect.capabilities()['source_edits'])
        edit = ExecutionPolicy({'workspace': 'edit', 'verification_note': 'Verify the finished artifact against the brief.'}, ['a', 'b'], 'a')
        self.assertTrue(edit.capabilities()['source_edits'])
        with self.assertRaises(ValueError):
            ExecutionPolicy({'kind': 'research'}, ['a', 'b'], 'a')
