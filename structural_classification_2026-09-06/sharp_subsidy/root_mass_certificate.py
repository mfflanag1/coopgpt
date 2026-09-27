"""Realize retained exact minimum-root-mass parameters without an optimizer."""
from pathlib import Path
import json
from two_hub_block_certificate import realize

def run():
 root=Path(__file__).parent
 ds=json.loads((root/'ROOT_MASS_PARAMETERS.json').read_text())
 rows=[realize(d)for d in ds]
 (root/'ROOT_MASS_CERTIFICATES.json').write_text(json.dumps(rows)+'\n')
 print(json.dumps({'cases':len(rows),'entries':sum(len(d['packings'])for d in rows)}))
if __name__=='__main__':run()
