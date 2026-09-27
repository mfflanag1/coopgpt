"""Balance P coefficients exactly, then shrink other teams to exact capacity."""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
import json,math

def convert(d):
 m=d['m'];P={tuple(e)for e in d['P']};D=10**12
 p={};other={}
 for i,e,v in d['packings']:
  e=tuple(e)
  if e in P:p[i,e]=max(0,min(D,round(v*D)))
  else:other[i,e]=max(0,math.floor(v*D))
 for e in P:
  keys=[k for k in p if k[1]==e];missing=3*D-sum(p[k]for k in keys)
  for k in sorted(keys,key=lambda k:min(p[k],D-p[k]),reverse=True):
   if missing>0:a=min(missing,D-p[k])
   else:a=max(missing,-p[k])
   p[k]+=a;missing-=a
   if not missing:break
  if missing:raise ValueError('cannot balance P')
 loads=defaultdict(lambda:[0,0])
 for group,kinds in ((p,0),(other,1)):
  for (i,e),v in group.items():
   for s,j in enumerate(e):loads[i,s*m+j][kinds]+=v
 scale=F(1)
 for a,b in loads.values():
  if a>D:raise ValueError('P capacity')
  if b:scale=min(scale,F(D-a,b))
 rows=[[i,list(e),str(F(v,D))]for(i,e),v in p.items()if v]
 rows +=[[i,list(e),str(F(v,D)*scale)]for(i,e),v in other.items()if v]
 return {'m':m,'P':sorted(P),'parameter':'1','packings':rows,'rounding_scale':str(scale),'mode':d['mode']}

if __name__=='__main__':
 out=[]
 for b in (2,4,8):
  d=json.loads(Path(__file__).with_name(f'COUPLING_{b}_same.json').read_text());r=convert(d);r['junctions']=b;out.append(r)
 Path(__file__).with_name('VARIABLE_P_CERTIFICATES.json').write_text(json.dumps(out,indent=2)+'\n')
 print([(d['m'],len(d['packings']),d['rounding_scale'])for d in out])
