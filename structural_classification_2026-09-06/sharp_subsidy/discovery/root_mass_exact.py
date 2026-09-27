import two_hub_blocks as tb
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from two_hub_block_certificate import realize
import numpy as np,json
from pathlib import Path
original=tb.linprog
rows=[]
for same in (False,True):
 m,P=tb.example(same,0);types,stride,*_=tb.model(m,P);L=tb.structure(m,P)[4]
 def minimize(c,**kwargs):
  obj=np.zeros(len(c))
  for k,(b,t,s)in enumerate(types):obj[k*stride+b]=L[b][t]
  return original(obj,**kwargs)
 tb.linprog=minimize
 d=tb.run('ROOT_MIN_'+str(same),m,P,exact=True);r=realize(d);rows.append(r)
 tb.linprog=original
Path(__file__).with_name('ROOT_MASS_CERTIFICATES.json').write_text(json.dumps(rows)+'\n')
