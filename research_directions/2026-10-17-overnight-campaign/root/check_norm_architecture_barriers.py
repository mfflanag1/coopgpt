from fractions import Fraction as F
import json
from pathlib import Path
checks={'radial_parameters':0,'absolute_value_bound':0}
for p in range(2,1002):
 s=F(p-1,p+3);z=F((p-1),2)*(1-s)/s
 assert z==2
 assert (1+s)/(4*(1-s))==F(p+1,8)
 assert 2*s/((p-1)*(1-s))==F(1,2)
 checks['radial_parameters']+=1
for lam in [F(1),F(3,2),F(2),F(17),F(100)]:
 for h in range(-100,101):
  raph=F(h,7);C=lam-1-raph
  assert lam-abs(C)<=1+raph
  checks['absolute_value_bound']+=1
p=256;K=16;s=F(p-1,p+3);a=1-K+K*s
assert a==F(195,259) and 2*a==F(390,259)>1
out={'status':'PASS','checks':checks,'candidate_spatial_lower':str(2*a),'scope':'Exact scalar consequences only; Holder duality, gradient and five-owner limiting argument verified analytically by root.'}
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
