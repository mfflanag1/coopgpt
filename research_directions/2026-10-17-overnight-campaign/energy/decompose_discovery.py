#!/usr/bin/env python3
from itertools import product
from functools import lru_cache
from pathlib import Path
import sys,json,random,numpy as np
from scipy.optimize import linprog
sys.path.insert(0,str(Path(__file__).parent));from shared_discovery import value

def try_cases(n,grid,trials):
 ps=list(product(range(grid+1),repeat=n+2));masks=list(product([0,1],repeat=2*n))[1:]
 mat=np.array([[float(value(list(pr[2:]),pr[0],pr[1],m[:n],m[n:])) for m in masks] for pr in ps])
 rng=random.Random(1710+n)
 for z in range(trials):
  a=[rng.randrange(6) for _ in range(n)];b=[rng.randrange(6) for _ in range(n)]
  f=np.array([float(value(list(pr[2:]),pr[0],pr[1],a,b)) for pr in ps])
  r=linprog(np.ones(len(masks)),A_eq=mat,b_eq=f,bounds=(0,None),method='highs')
  if not r.success:
   out={'n':n,'grid':grid,'a':a,'b':b,'status':'INFEASIBLE','message':r.message}
   print(json.dumps(out),flush=True)
   np.savez(Path(__file__).with_name('decompose_failure.npz'),mat=mat,f=f,profiles=np.array(ps),masks=np.array(masks))
   Path(__file__).with_name('decompose_failure.json').write_text(json.dumps(out,indent=2)+'\n');return out
  if z<5 or z%10==0:
   out={'a':a,'b':b,'status':'finite feasible','terms':[(masks[i],float(x)) for i,x in enumerate(r.x) if x>1e-8]};print(out,flush=True)
 return {'n':n,'grid':grid,'passed':trials}
if __name__=='__main__':
 print(try_cases(3,2,40))
