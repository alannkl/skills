"""External adapter behavior pinned before adding CLI registration."""
import unittest
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'agent-panel' / 'scripts'))
from adapters import production_adapters

PACKAGE = Path(__file__).resolve().parents[2] / 'agent-panel'



class AdapterLoading(unittest.TestCase):
    def test_external_adapter_through_cli(self):
        """Given an explicitly registered external adapter, when three participants use it through every preset, then independent sessions reach agreement without scheduler changes."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            harness = root / 'harness.py'
            harness.write_text("""import json,sys
p=json.loads(sys.stdin.read().split('PANEL_INPUT\\n')[1])
phase=p['phase']
b={'participant_id':p['participant_id'],'kind':'review' if phase=='review' else 'candidate' if phase=='draft' else 'contribution','text':'Requested result','data':{},'messages':[]}
if phase=='assign': b['assignments']={person['id']:'Complete the assigned responsibility' for person in p['roster']}
if phase=='review': b.update(revision=p['candidate']['revision'],content_hash=p['candidate']['content_hash'],decision='approve',reasons=['Meets the brief'],assumptions=[],blocking_objections=[])
print(json.dumps({'session_id':sys.argv[1],'block':b}))
""")
            plugin = root / 'adapter.py'
            plugin.write_text("""import json,sys,uuid
from pathlib import Path
from adapters.base import ProcessAdapter, Terminal
class Adapter(ProcessAdapter):
    settings_keys={'model'}
    def command(self, session_id, settings):
        session=session_id or str(uuid.uuid4())
        return [sys.executable,str(Path(__file__).with_name('harness.py')),session],session
    def parse(self, output, code, session_id):
        data=json.loads(output)
        return Terminal(data['session_id'],output,data['block'],code,{},'completed' if code==0 else 'failed')
def create_adapter():
    return Adapter()
""")
            (root / 'brief.md').write_text('Return the requested result and verify it.')
            roster={'drafter':'a','leader':'a','participants':[{'id':pid,'role':'Contributor','harness':'external','settings':{'model':'fixture'}} for pid in ('a','b','c')]}
            (root / 'roster.json').write_text(json.dumps(roster))
            for preset in ('independent-discussion','leader-members','flat-peers'):
                run=root / preset
                command=[sys.executable,str(PACKAGE/'scripts/panel.py'),preset,str(root/'brief.md'),str(root/'roster.json'),'--adapter','external='+str(plugin),'--run-dir',str(run)]
                completed=subprocess.run(command,capture_output=True,text=True,timeout=15)
                self.assertEqual(completed.returncode,0,completed.stdout+completed.stderr)
                report=json.loads(completed.stdout)
                self.assertEqual(report['outcome'],'agreed')
                manifest=json.loads((run/'manifest.json').read_text())
                sessions={pid:p['session_id'] for pid,p in manifest['participants'].items()}
                self.assertEqual(len(set(sessions.values())),3)
                events=[json.loads(line) for line in (run/'events.jsonl').read_text().splitlines()]
                for pid,session in sessions.items():
                    self.assertEqual({e['data']['result']['session_id'] for e in events if e['kind']=='terminal_result' and e['data']['participant']==pid},{session})
                recovered=subprocess.run([sys.executable,str(PACKAGE/'scripts/panel.py'),'--recover',str(run),'--adapter','external='+str(plugin)],capture_output=True,text=True,timeout=5)
                self.assertEqual(recovered.returncode,0,recovered.stdout+recovered.stderr)


    def test_invalid_registration_fails_before_launch(self):
        """Given a missing module, invalid adapter contract or duplicate name, when registering, then return a clear error before any agent launch."""
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'invalid.py'
            path.write_text('def create_adapter():\n    return object()\n')
            for registrations in (['malformed'],['claude='+str(path)],['new=/missing/adapter.py'],['new='+str(path)]):
                with self.assertRaises(ValueError):
                    production_adapters(registrations)
            path.write_text('value = 1\n')
            with self.assertRaisesRegex(ValueError,'create_adapter'):
                production_adapters(['new='+str(path)])
