"""Reconstruct the exact positive control without numerical optimization."""
from pathlib import Path
import json
from two_hub_block_certificate import realize

def run():
 root=Path(__file__).parent
 d=json.loads((root/'COMPOUND_CUT_CONTROL_PARAMETERS.json').read_text())
 out=realize(d)
 (root/'COMPOUND_CUT_CONTROL.json').write_text(json.dumps(out)+'\n')
 print(json.dumps({'entries':len(out['packings'])}))
if __name__=='__main__':run()
