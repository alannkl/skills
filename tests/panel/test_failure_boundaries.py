"""Additional failure cases pinned before adapting cancellation/reconciliation."""
import unittest
import asyncio
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import test_panel
from test_panel import Fixture
from adapters import production_adapters
from adapters.base import Handle



class FailureBoundaries(unittest.TestCase):
    run_scenario = test_panel.PanelBehavior.run_scenario
    def test_slow_cancel_is_bounded(self):
        """Given an adapter whose cancel never returns, when the host stops, then report interrupted with uncertain termination within the reporting allowance."""

        async def scenario(root):
            f = Fixture(root, behavior=lambda p: 'wait', report_seconds=5)
            async def stuck_cancel(_):
                await asyncio.sleep(3600)
            f.adapter.cancel = stuck_cancel
            run = asyncio.create_task(f.run())
            while len(f.adapter.active) < 3:
                await asyncio.sleep(0.005)
            f.panel.request_stop()
            report = await asyncio.wait_for(run, 5)
            self.assertEqual(report['outcome'], 'interrupted')
            self.assertEqual(len(report['cancellations']), 3)
            self.assertTrue(all(not c['confirmed_inactive'] for c in report['cancellations']))
        self.run_scenario(scenario)


    def test_corrupt_recovery_is_indeterminate(self):
        """Given corrupt persisted terminal output after execution, when collecting or recovering, then record indeterminate delivery without retry."""

        async def scenario(root):
            f = Fixture(root, behavior=lambda p: 'corrupt_persist' if p['participant_id'] == 'cy' else None)
            report = await f.run()
            self.assertEqual(report['outcome'], 'incomplete')
            self.assertEqual(len(f.adapter.inputs), 3)
            self.assertEqual(report['failures'][0]['result']['outcome'], 'indeterminate')
            self.assertEqual(report['failures'][0]['input_event_ids'], [])
        self.run_scenario(scenario)


    def test_native_permission_denial_blocks(self):
        """Given a native denied tool followed by a plausible final answer, when normalized, then report blocked rather than accepting the answer."""

        for denied in ({'type':'error','error':{'code':'permission_denied'}},
                       {'type':'item.completed','item':{'type':'command_execution','status':'declined'}},
                       {'type':'item.completed','item':{'type':'command_execution','status':'failed','aggregated_output':'Command rejected by policy'}}):
            events = [{'type':'thread.started','thread_id':'s'}, denied,
                      {'type':'item.completed','item':{'type':'agent_message','text':'{"text":"all good"}'}},
                      {'type':'turn.completed'}]
            result = production_adapters()['codex'].parse('\n'.join(json.dumps(e) for e in events),0,'s')
            self.assertEqual(result.outcome,'blocked')


    def test_completed_handle_cancel_avoids_stale_pid(self):
        """Given an already completed invocation, when cancel is called later, then do not signal its possibly reused process group."""

        async def scenario(root):
            completion = asyncio.create_task(asyncio.sleep(0))
            await completion
            handle = Handle(completion=completion,process=SimpleNamespace(pid=12345,returncode=0))
            with patch('adapters.base.os.killpg') as kill:
                self.assertTrue(await production_adapters()['claude'].cancel(handle))
                kill.assert_not_called()
        self.run_scenario(scenario)
