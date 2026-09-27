"""Optional regeneration; accept outputs only after the independent verifier passes."""
from pathlib import Path
import json
from harmonic_sector_test import run,random_tree
from random_coupling_probe import run as packing_run
from round_coupling import convert

if __name__=='__main__':
 run('random12_0',*random_tree(12,0))
 packing_run('RANDOM0','same')
 here=Path(__file__).resolve().parent
 result=convert(json.loads((here/'COUPLING_RANDOM0_same.json').read_text()))
 (here/'HARMONIC_FREE_CONTROL.json').write_text(json.dumps(result)+'\n')
 print('Candidate files written. Run verify_harmonic_sector.py before accepting them.')
