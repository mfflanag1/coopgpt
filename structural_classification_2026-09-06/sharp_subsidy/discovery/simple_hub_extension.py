from pathlib import Path
import json
from fractions import Fraction as F
import two_hub_blocks as tb
from hub_extension_probe import solve
m=7;P=[(0,1,2),(3,0,4),(5,6,0)];types,stride,*_=tb.model(m,P);L=tb.structure(m,P)[4];B=len(L);vals=[]
for b,t,s in types:vals += [F(1,4)]*B+[F(1,8)if L[c][s]else F(0)for c in range(B)]+[F(0),F(1,2)]
d={'name':'one_hub_uniform','m':m,'P':P,'types':types,'stride':stride,'values':list(map(str,vals))}
Path(__file__).with_name('ONE_HUB_UNIFORM_PARAMETERS.json').write_text(json.dumps(d)+'\n')
for j in (1,2,3,4,5,6):
 r,rec=solve(d,j);print(j,r.status,flush=True)
