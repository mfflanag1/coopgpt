"""Discovery: identify which transfer restriction prevents one-third coverage."""
from pathlib import Path
import sys,json
from itertools import product
import numpy as np
from scipy.sparse import coo_matrix
from scipy.optimize import linprog
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from universal_template import junctions

def run(b,mode):
 config=json.loads(Path(__file__).with_name('HARMONIC_SECTOR_NO_GO.json').read_text());m=config['m'];P=set(map(tuple,config['P']));used={s*m+j for e in P for s,j in enumerate(e)};U=sorted(set(range(3*m))-used);u=len(U)
 def pairs(e):a,b,c=e;return((0,a,b),(1,a,c),(2,b,c))
 targets=sorted(set(e for t in list(P)+[(j,j,j)for j in range(m)]for e in pairs(t)));index={e:k for k,e in enumerate(targets)}
 cols=[]
 for i in U:
  s,j=divmod(i,m)
  for t in product(range(m),repeat=3):
   if t[s]==j:continue
   if t not in P and len(set(t))>2:continue
   if mode=='same'and t not in P and len(set(t))==2 and t[(s+1)%3]!=t[(s+2)%3]:continue
   cols.append((i,t))
 n=len(cols);rhs=[1]*(u*3*m);rhs +=[-((u-5)if e[1]==e[2]else 0)-3*sum(e in pairs(t)for t in P)for e in targets]
 rr=[];cc=[];vv=[];ui={i:k for k,i in enumerate(U)}
 for k,(i,t)in enumerate(cols):
  for s,j in enumerate(t):rr.append(ui[i]*3*m+s*m+j);cc.append(k);vv.append(1)
  for e in pairs(t):
   if e in index:rr.append(u*3*m+index[e]);cc.append(k);vv.append(-1)
 for e,k in index.items():
  if e[1]==e[2]:rr.append(u*3*m+k);cc.append(n);vv.append(1)
 A=coo_matrix((vv,(rr,cc)),shape=(len(rhs),n+1)).tocsr();c=np.zeros(n+1);c[-1]=-1
 r=linprog(c,A_ub=A,b_ub=rhs,bounds=[(0,None)]*n+[(0,2)],options={'time_limit':120})
 if not r.success:raise ValueError(r.message)
 d={'m':m,'P':sorted(P),'mode':mode,'floating_parameter':r.x[-1],'variables':n,'packings':[[i,list(t),float(v)]for (i,t),v in zip(cols,r.x)if v>1e-9]}
 Path(__file__).with_name(f'COUPLING_{b}_{mode}.json').write_text(json.dumps(d)+'\n');print(json.dumps({k:v for k,v in d.items()if k not in ('P','packings')}),flush=True)
if __name__=='__main__':run('RANDOM0','same')
