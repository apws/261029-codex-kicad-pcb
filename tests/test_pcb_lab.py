"""Recovery and output-boundary tests for the local harness; no router required."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'tools' / 'pcb-lab.py'

def run(*args):
    return subprocess.run([sys.executable, str(TOOL), *map(str,args)], capture_output=True, text=True)

class LabTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root/'source'; self.source.mkdir()
        (self.source/'Board.kicad_pcb').write_text('fixture bytes\n')
        (self.source/'library').mkdir()
        (self.source/'library'/'part.kicad_mod').write_text('library bytes\n')

    def test_copy_preserves_source_and_dependencies(self):
        before = {str(p.relative_to(self.source)):p.read_bytes() for p in self.source.rglob('*') if p.is_file()}
        dest = self.root/'experiment'
        r=run('init','--source',self.source,'--dest',dest)
        self.assertEqual(r.returncode,0,r.stderr)
        for rel,data in before.items():
            self.assertEqual((self.source/rel).read_bytes(),data)
            self.assertEqual((dest/'design'/rel).read_bytes(),data)
        self.assertTrue((dest/'source-manifest.json').exists())
        self.assertTrue((dest/'board-brief.adoc').exists())

    def test_existing_destination_is_not_overwritten(self):
        dest=self.root/'existing';dest.mkdir();(dest/'keep').write_text('keep')
        self.assertEqual(run('init','--source',self.source,'--dest',dest).returncode,2)
        self.assertEqual((dest/'keep').read_text(),'keep')

    def test_recursive_copy_is_rejected(self):
        self.assertEqual(run('init','--source',self.source,'--dest',self.source/'nested').returncode,2)
        self.assertFalse((self.source/'nested').exists())

    def test_external_symlink_is_rejected(self):
        (self.source/'external').symlink_to(self.root)
        self.assertEqual(run('init','--source',self.source,'--dest',self.root/'copy').returncode,2)

    def test_changed_pad_net_is_not_accepted(self):
        b={'footprints':[{'ref':'J1','pads':[['1','GND']]}],'tracks':[], 'metrics':{}}
        n={'footprints':[{'ref':'J1','pads':[['1','VCC']]}],'tracks':[], 'metrics':{}}
        for name,obj in [('before',b),('after',n)]: (self.root/name).write_text(json.dumps(obj))
        r=run('compare',self.root/'before',self.root/'after')
        self.assertEqual(r.returncode,1,r.stderr)
        self.assertFalse(json.loads(r.stdout)['footprints_and_pad_nets_unchanged'])

    def test_lost_locked_track_is_not_accepted(self):
        b={'footprints':[],'tracks':[{'locked':True,'net':'critical'}], 'metrics':{}}
        n={'footprints':[],'tracks':[], 'metrics':{}}
        for name,obj in [('before',b),('after',n)]: (self.root/name).write_text(json.dumps(obj))
        r=run('compare',self.root/'before',self.root/'after')
        self.assertEqual(r.returncode,1,r.stderr)
        self.assertFalse(json.loads(r.stdout)['locked_tracks_preserved_exactly'])

if __name__=='__main__': unittest.main()
