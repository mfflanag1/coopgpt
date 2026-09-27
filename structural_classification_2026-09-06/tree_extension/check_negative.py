from pathlib import Path
from copy import deepcopy
import json
from check_synthesis import check

base=json.loads((Path(__file__).parent/'C4_INTEGER_CERTIFICATE.json').read_text())
cases=[]
r=deepcopy(base);r['dual'][0]['weight']='2';cases.append(r)
r=deepcopy(base);r['ideal_dual']['mu']='0';cases.append(r)
r=deepcopy(base);r['x'][0]='1';cases.append(r)
r=deepcopy(base);r['matrices'].pop();cases.append(r)
for r in cases:
    try:check(r)
    except RuntimeError:continue
    raise RuntimeError('Corrupted certificate was accepted')
print(json.dumps({'status':'PASS','corrupted_certificates_rejected':len(cases)}))
