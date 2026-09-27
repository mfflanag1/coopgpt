from pathlib import Path
import json
import hub_extension_probe as h
import numpy as np
original=h.linprog

def relaxed(c,**kwargs):
 E=kwargs['A_eq'];obj=np.asarray(E[-1].toarray()).ravel();kwargs['A_eq']=E[:-1];kwargs['b_eq']=kwargs['b_eq'][:-1]
 return original(obj,**kwargs)
h.linprog=relaxed
d=json.loads(Path(__file__).with_name('ONE_HUB_UNIFORM_PARAMETERS.json').read_text())
r,rec=h.solve(d,1);print(r.status,r.fun,flush=True)
rec.update(status=r.status,minimum_root_mass=float(r.fun)if r.success else None)
if r.success:rec['values']=r.x.tolist()
Path(__file__).with_name('RELAXED_HUB_EXTENSION.json').write_text(json.dumps(rec)+'\n')
