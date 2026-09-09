"""General-task contracts, pinned before extending the design-only runner."""
import unittest
import asyncio
import json
from pathlib import Path
import sys
import tempfile

import test_panel
from test_panel import preset
from task_fixture import TaskFixture, repository, implement, git
from engine import Panel
from adapters import production_adapters
from execution import ExecutionPolicy
from fakes import FakeAdapter



class TaskBehavior(unittest.TestCase):
    run_scenario = test_panel.PanelBehavior.run_scenario
    def test_task_dependent_outputs(self):
        """Given research, review, writing and general briefs, when each preset runs with three participants, then instructions and final artifacts match the task and retain all required approvals."""

        for kind in ('research', 'review', 'writing', 'general'):
            for name in ('independent-discussion', 'leader-members', 'flat-peers'):
                async def scenario(root):
                    f = TaskFixture(root, kind, name)
                    report = await f.run()
                    self.assertEqual(report['outcome'], 'agreed', report['reason'])
                    self.assertNotIn('task', report)
                    self.assertEqual(set(report['reviews']), {'ada', 'bert', 'cy'})
                    self.assertTrue(all(i['brief'] == f.brief and 'task' not in i for i in f.adapter.inputs))
                    draft = next(i for i in f.adapter.inputs if i['phase'] == 'draft')
                    self.assertNotIn('shared design', draft['instruction'])
                    if kind == 'writing':
                        self.assertEqual(Path(report['candidate']).read_text(), 'Please send the revised manuscript by Friday.')
                    self.assertEqual(len({p['session_id'] for p in f.panel.people.values()}), 3)
                self.run_scenario(scenario)


    def test_research_sources_and_empty_review(self):
        """Given research evidence or a review with no material findings, when finalized, then retain the cited sources or explicit empty findings without inventing design proposals."""

        async def scenario(root):
            f = TaskFixture(root, 'research', execution={'web': True})
            report = await f.run()
            self.assertEqual(report['data']['sources'], [{'reference': 'https://example.org/evidence', 'supports': 'The process has a finite deadline.'}])
            self.assertEqual(report['data']['limitations'], ['No performance measurements are available.'])
            self.assertTrue(all(i['capabilities']['web'] for i in f.adapter.inputs))
        self.run_scenario(scenario)
        async def empty(root):
            f = TaskFixture(root, 'review')
            report = await f.run()
            self.assertEqual(report['outcome'], 'agreed')
            self.assertEqual(report['data']['findings'], [])
            self.assertEqual(Path(report['candidate']).read_text(), 'No material findings in the supplied scope.')
        self.run_scenario(empty)


    def test_three_writers_integrate(self):
        """Given three participants at one pinned revision, when implementing through every preset, then edits stay in separate worktrees, one integrator assembles the result, checks pass there, and a non-author reviews the frozen patch."""

        for name in ('independent-discussion', 'leader-members', 'flat-peers'):
            async def scenario(root):
                repo = repository(root)
                f = TaskFixture(root, 'implementation', name, behavior=implement,
                                execution={'workspace': 'edit', 'checks': [[sys.executable, 'verify.py']]}, repo=repo)
                report = await f.run()
                self.assertEqual(report['outcome'], 'agreed', report['reason'])
                self.assertTrue(report['verification']['passed'])
                self.assertEqual(Path(report['verification']['checks'][0]['stdout']).read_text(), 'value=4\n')
                workspaces = f.panel.workspaces.directories
                self.assertEqual(len(set(workspaces.values())), 3)
                self.assertTrue(all(Path(w, '.git').is_file() for w in workspaces.values()))
                self.assertEqual({git(w, 'rev-parse', 'HEAD') for w in workspaces.values()}, {git(repo, 'rev-parse', 'HEAD')})
                self.assertEqual((repo / 'solution.py').read_text(), 'def value():\n    return 0\n')
                for pid in workspaces:
                    own = [i for i in f.adapter.inputs if i['participant_id'] == pid]
                    self.assertEqual({i['working_directory'] for i in own}, {workspaces[pid]})
                reviews = [i for i in f.adapter.inputs if i['phase'] == 'review']
                self.assertEqual({i['participant_id'] for i in reviews}, {'ada', 'bert', 'cy'})
                self.assertTrue(all(i['candidate']['artifacts']['tree_hash'] == report['artifacts']['tree_hash'] for i in reviews))
                self.assertTrue(Path(report['artifacts']['patch']).read_bytes())
                self.assertFalse(Path(report['artifacts']['files'], '.git').exists())
            self.run_scenario(scenario)


    def test_failed_check_blocks_agreement(self):
        """Given unanimous model approvals but a failing executable check, when finalizing, then never report successful completion and preserve the failed result for bounded rework."""

        async def scenario(root):
            repo = repository(root)
            f = TaskFixture(root, 'implementation', behavior=implement, repo=repo,
                            execution={'workspace': 'edit', 'checks': [[sys.executable, '-c', 'raise SystemExit(7)']]}, max_cycles=2)
            report = await f.run()
            self.assertEqual(report['outcome'], 'incomplete')
            self.assertFalse(report['verification']['passed'])
            self.assertTrue(all(r['decision'] == 'approve' for r in report['reviews'].values()))
            self.assertFalse(report['approved'])
            self.assertEqual(report['verification']['checks'][0]['exit_status'], 7)
            self.assertEqual(len([i for i in f.adapter.inputs if i['phase'] == 'review']), 6)
            self.assertTrue(Path(report['artifacts']['patch']).exists())
        self.run_scenario(scenario)


    def test_code_revision_invalidates_approvals(self):
        """Given unchanged prose but changed implementation bytes, when revised, then generate a different result hash and require fresh approval of that artifact set."""

        async def scenario(root):
            repo = repository(root)
            drafts = 0
            def behavior(p):
                nonlocal drafts
                result = implement(p)
                if p['phase'] == 'draft':
                    drafts += 1
                    if drafts == 2:
                        path = Path(p['working_directory']) / 'solution.py'
                        path.write_text(path.read_text() + '# Clarified after review.\n')
                if p['phase'] == 'review' and p['participant_id'] == 'cy' and p['candidate']['revision'] == 'b1-r1':
                    return {'decision': 'object', 'blocking_objections': ['Clarify the implementation comment.']}
                return result
            f = TaskFixture(root, 'implementation', behavior=behavior, repo=repo,
                            execution={'workspace': 'edit', 'checks': [[sys.executable, 'verify.py']]}, max_cycles=2)
            report = await f.run()
            self.assertEqual(report['outcome'], 'agreed', report['reason'])
            candidates = [e['data'] for e in f.panel.records.events if e['kind'] == 'candidate']
            self.assertEqual(candidates[0]['text'], candidates[1]['text'])
            self.assertNotEqual(candidates[0]['artifacts']['patch_hash'], candidates[1]['artifacts']['patch_hash'])
            self.assertNotEqual(candidates[0]['content_hash'], candidates[1]['content_hash'])
            self.assertTrue(all(r['revision'] == 'b1-r2' for r in report['reviews'].values()))
            self.assertEqual(len([i for i in f.adapter.inputs if i['phase'] == 'review']), 6)
        self.run_scenario(scenario)


    def test_debug_diagnosis_and_fix(self):
        """Given debugging with diagnosis or fix selected, when run, then deliver reproduction and cause evidence, and permit source edits only in fix mode."""

        for mode in ('diagnose', 'fix'):
            async def scenario(root):
                repo = repository(root)
                def behavior(p):
                    result = implement(p) if mode == 'fix' else None
                    if p['phase'] == 'draft':
                        return dict(result or {}, text='The constant return value causes the failure.',
                                    data={'reproduction': {'procedure': 'python3 verify.py', 'observed': 'Expected 4, got 0'},
                                          'diagnosis': {'cause': 'Incorrect constant in value()', 'evidence': 'The baseline returns 0'}})
                    return result
                f = TaskFixture(root, 'debugging', behavior=behavior, repo=repo,
                                execution={'workspace': 'inspect' if mode == 'diagnose' else 'edit', 'checks': [{'argv': [sys.executable, 'verify.py'], 'expect_exit': 1 if mode == 'diagnose' else 0}]})
                report = await f.run()
                self.assertEqual(report['outcome'], 'agreed', report['reason'])
                self.assertEqual(report['data']['diagnosis']['cause'], 'Incorrect constant in value()')
                self.assertEqual(bool(Path(report['artifacts']['patch']).read_bytes()), mode == 'fix')
                self.assertTrue(report['verification']['passed'])
            self.run_scenario(scenario)
        async def forbidden_edit(root):
            repo = repository(root)
            f = TaskFixture(root, 'debugging', behavior=implement, repo=repo,
                            execution={'workspace': 'inspect', 'checks': [[sys.executable, 'verify.py']]})
            report = await f.run()
            self.assertEqual(report['outcome'], 'incomplete')
            self.assertIn('Source changes are not permitted', report['failures'][0]['error'])
        self.run_scenario(forbidden_edit)


    def test_task_permissions_persist(self):
        """Given research or implementation participants, when resuming, then preserve web/read/write/command grants and each participant's working directory."""

        for kind in ('research', 'implementation'):
            task = ExecutionPolicy({'workspace': 'edit', 'checks': [[sys.executable, '-m', 'unittest']]} if kind == 'implementation' else {'web': True}, ['a', 'b'], 'a')
            for name, adapter in production_adapters().items():
                settings = {'model': 'fixture', 'cwd': '/tmp/workspace', 'capabilities': task.capabilities()}
                first, session = adapter.command(None, settings)
                resumed, _ = adapter.command(session or 'existing', settings)
                if name == 'claude':
                    tools = first[first.index('--tools') + 1].split(',')
                    self.assertEqual(tools, resumed[resumed.index('--tools') + 1].split(','))
                    self.assertEqual('WebSearch' in tools, kind == 'research')
                    self.assertEqual('Edit' in tools, kind == 'implementation')
                    self.assertEqual('Bash' in tools, kind == 'implementation')
                else:
                    self.assertEqual('web_search="live"' in resumed, kind == 'research')
                    mode = 'workspace-write' if kind == 'implementation' else 'read-only'
                    self.assertEqual(first[first.index('--sandbox') + 1], mode)
                    self.assertIn('sandbox_mode="' + mode + '"', resumed)
                    self.assertNotIn('--cd', resumed)


    def test_cancel_validation(self):
        """Given an assembled-result check still running, when the host cancels, then terminate its process and report interrupted without approval."""

        async def scenario(root):
            repo = repository(root)
            f = TaskFixture(root, 'implementation', behavior=implement, repo=repo,
                            execution={'workspace': 'edit', 'checks': [[sys.executable, '-c', 'import time; time.sleep(60)']]})
            run = asyncio.create_task(f.run())
            async def wait_for_check():
                while '@verification' not in f.panel.active or f.panel.active['@verification'][1].process is None:
                    await asyncio.sleep(0.005)
                return f.panel.active['@verification'][1]
            handle = await asyncio.wait_for(wait_for_check(), 3)
            f.panel.request_stop()
            report = await asyncio.wait_for(run, 5)
            self.assertEqual(report['outcome'], 'interrupted')
            self.assertTrue(handle.completion.done())
            self.assertIsNotNone(handle.process.returncode)
            self.assertFalse(any(i['phase'] == 'review' for i in f.adapter.inputs))
            self.assertTrue(Path(report['artifacts']['patch']).exists())
            self.assertTrue(Path(report['candidate']).exists())
        self.run_scenario(scenario)


    def test_code_configuration_is_explicit(self):
        """Given a writable task missing a pinned repository, checks or a non-integrating reviewer, when starting, then fail before launching any agent."""

        with tempfile.TemporaryDirectory() as root:
            repo = repository(root)
            for bad in ({}, {'repository': str(repo)}, {'repository': str(repo), 'base_revision': 'HEAD', 'required_approvers': ['ada']}):
                adapter = FakeAdapter()
                roster = {'drafter': 'ada', 'execution': {'workspace': 'edit', 'checks': [[sys.executable, 'verify.py']]},
                          'participants': [{'id': p, 'role': 'Implementer', 'harness': 'fake', 'settings': {'model': 'simulation'}} for p in ('ada', 'bert')]}
                roster.update(bad)
                with self.assertRaises(ValueError):
                    Panel(preset('independent-discussion'), 'Implement the behavior', roster, Path(root) / ('bad-' + str(len(bad))), {'fake': adapter})
                self.assertFalse(adapter.inputs)
            with self.assertRaises(ValueError):
                ExecutionPolicy({'workspace': 'edit'}, ['ada', 'bert'], 'ada')


    def test_input_checkout_is_preserved(self):
        """Given a dirty caller checkout, when using an explicit base revision, then retain its staged, unstaged and untracked content and return changes in the run artifacts only."""

        async def scenario(root):
            repo = repository(root)
            (repo / 'solution.py').write_text('def value():\n    return 9\n')
            git(repo, 'add', 'solution.py')
            (repo / 'solution.py').write_text('def value():\n    return 10\n')
            (repo / 'untracked.txt').write_text('Unrelated work')
            commands = [('status', '--porcelain'), ('diff', '--cached'), ('diff',), ('rev-parse', 'HEAD'), ('worktree', 'list', '--porcelain')]
            before = [git(repo, *command) for command in commands]
            f = TaskFixture(root, 'implementation', behavior=implement, repo=repo,
                            execution={'workspace': 'edit', 'checks': [[sys.executable, 'verify.py']]})
            report = await f.run()
            self.assertEqual(report['outcome'], 'agreed', report['reason'])
            self.assertEqual([git(repo, *command) for command in commands], before)
            self.assertEqual((repo / 'untracked.txt').read_text(), 'Unrelated work')
            self.assertFalse(git(f.panel.workspaces.repository, 'remote').strip())
        self.run_scenario(scenario)



class LiveRegression(unittest.TestCase):
    def test_native_auto_permissions(self):
        """Given any task kind, when agents launch or resume, then Claude uses native auto and Codex never prompts, while task tool/sandbox boundaries remain."""
        for kind in ('research', 'implementation'):
            config = {'workspace': 'edit', 'checks': [['python3', 'verify.py']]} if kind == 'implementation' else {'web': True}
            task = ExecutionPolicy(config, ['a', 'b'], 'a')
            for name, adapter in production_adapters().items():
                settings = {'model': 'fixture', 'cwd': '/tmp/workspace', 'capabilities': task.capabilities()}
                command, session = adapter.command(None, settings)
                resumed, _ = adapter.command(session or 'existing', settings)
                for argv in (command, resumed):
                    self.assertFalse(any('bypass' in argument for argument in argv))
                    if name == 'claude':
                        self.assertEqual(argv[argv.index('--permission-mode') + 1], 'auto')
                        self.assertEqual(argv[argv.index('--permission-prompts') + 1], 'none')
                        self.assertFalse(any(argument.startswith('Bash(') for argument in argv))
                    else:
                        self.assertIn('approval_policy="never"', argv)



class ArtifactAccess(unittest.TestCase):
    run_scenario = test_panel.PanelBehavior.run_scenario

    def test_read_directories_follow_reveal(self):
        """Given private initial work, when phases advance, then source/check directories are declared from the start and peer artifact access is added only after reveal and retained across resume."""

        async def scenario(root):
            repo = repository(root)
            f = TaskFixture(root, 'implementation', behavior=implement, repo=repo,
                            execution={'workspace': 'edit', 'checks': [[sys.executable, str(repo / 'verify.py')]], 'verification_note': ''})
            report = await f.run()
            self.assertEqual(report['outcome'], 'agreed', report['reason'])
            for initial in [i for i in f.adapter.inputs if i['phase'] == 'initial']:
                self.assertIn(f.panel.manifest['source'], initial['read_directories'])
                self.assertIn(str(repo), initial['read_directories'])
                for peer in ('ada', 'bert', 'cy'):
                    if peer != initial['participant_id']:
                        self.assertFalse(any('/participants/' + peer + '/' in d or d.endswith('/participants/' + peer) for d in initial['read_directories']))
            for pid in ('ada', 'bert', 'cy'):
                own = [i for i in f.adapter.inputs if i['participant_id'] == pid]
                previous = set()
                for turn in own:
                    current = set(turn['read_directories'])
                    self.assertTrue(previous <= current)
                    previous = current
                critique = next(i for i in own if i['phase'] == 'critique')
                self.assertTrue(any('/participants/' + ('bert' if pid != 'bert' else 'ada') + '/' in d for d in critique['read_directories']))
            settings = {'model': 'fixture', 'read_dirs': ['/tmp/source-evidence', '/tmp/check-evidence']}
            command, session = production_adapters()['claude'].command(None, settings)
            resumed, _ = production_adapters()['claude'].command(session, settings)
            for value in ('--add-dir', '/tmp/source-evidence', '/tmp/check-evidence'):
                self.assertIn(value, command)
                self.assertIn(value, resumed)
        self.run_scenario(scenario)


    def test_contribution_files_are_frozen(self):
        """Given a captured contribution, when its author's working copy later changes, then other participants still receive the exact captured files for the round."""

        async def scenario(root):
            repo = repository(root)
            def behavior(payload):
                result = implement(payload)
                if payload['phase'] == 'critique' and payload['participant_id'] == 'bert':
                    Path(payload['working_directory'], 'solution.py').write_text('def value():\n    return 99\n')
                return result
            f = TaskFixture(root, 'implementation', behavior=behavior, repo=repo,
                            execution={'workspace': 'edit', 'checks': [[sys.executable, 'verify.py']]})
            await f.run()
            initial = next(e for e in f.panel.records.events if e['kind'] == 'message' and e['phase'] == 'reveal' and e['sender'] == 'bert')
            frozen = Path(initial['data']['artifacts']['files'], 'solution.py')
            self.assertEqual(frozen.read_text(), 'def value():\n    return 4\n')
            self.assertEqual(Path(f.panel.workspaces.directories['bert'], 'solution.py').read_text(), 'def value():\n    return 99\n')
            for turn in [i for i in f.adapter.inputs if i['phase'] == 'critique']:
                peer = next(e for e in turn['events'] if e['sender'] == 'bert')
                self.assertEqual(peer['data']['artifacts']['files'], str(frozen.parent))
        self.run_scenario(scenario)


    def test_diagnosis_review_cannot_edit_source(self):
        """Given diagnosis-only work, when a reviewer changes its source, then the run is incomplete even if every review approves."""

        async def scenario(root):
            repo = repository(root)
            def behavior(payload):
                if payload['phase'] == 'draft':
                    return {'text': 'The return value causes the failure.',
                            'data': {'reproduction': {'procedure': 'python3 verify.py', 'observed': 'Expected 4; got 0'},
                                     'diagnosis': {'cause': 'Wrong constant', 'evidence': 'solution.py returns 0'}}}
                if payload['phase'] == 'review' and payload['participant_id'] == 'cy':
                    Path(payload['working_directory'], 'solution.py').write_text('def value():\n    return 4\n')
            f = TaskFixture(root, 'debugging', behavior=behavior, repo=repo,
                            execution={'workspace': 'inspect', 'checks': [{'argv': [sys.executable, 'verify.py'], 'expect_exit': 1}]})
            report = await f.run()
            self.assertEqual(report['outcome'], 'incomplete')
            self.assertIn('Source changes are not permitted', report['reason'])
        self.run_scenario(scenario)
