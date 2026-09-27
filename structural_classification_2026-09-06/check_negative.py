from copy import deepcopy
from pathlib import Path
import json
from check_cycle import check

base=json.loads((Path(__file__).parent/'FOUR_CYCLE_CERTIFICATE.json').read_text())
bad=[]
r=deepcopy(base);r['residual_dual'][0]['weight']='1';bad.append(('incorrect dual weight',r))
r=deepcopy(base);r['optimal_matching'][1]=r['optimal_matching'][0];bad.append(('repeated matching team',r))
r=deepcopy(base);r['ideal_witness'][3]='6';bad.append(('incorrect ideal witness',r))
r=deepcopy(base);r['matrices'].pop();bad.append(('missing edge matrix',r))
for name,r in bad:
    try:check(r)
    except RuntimeError:continue
    raise RuntimeError(f'Failed to reject {name}')
print(json.dumps({'status':'PASS','corrupted_certificates_rejected':len(bad)}))
