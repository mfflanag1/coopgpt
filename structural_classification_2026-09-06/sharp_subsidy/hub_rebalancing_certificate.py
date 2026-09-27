"""Reconstruct the two new-tree controls from retained rational parameters."""
from pathlib import Path
import json
from two_hub_block_certificate import realize

def run():
 root=Path(__file__).parent
 ds=json.loads((root/'HUB_REBALANCING_PARAMETERS.json').read_text())
 names={'REBALANCING_SHARP':'REBALANCING_SHARP_CERTIFICATE.json','EXTENSION_CONTROL':'HUB_EXTENSION_CONTROL.json'}
 for d in ds:
  out=realize(d)
  (root/names[d['name']]).write_text(json.dumps(out)+'\n')
 print(json.dumps({'controls':len(ds)}))
if __name__=='__main__':run()
