#!/usr/bin/env python3
"""Independent stdlib exact certificate replay for positive unit-graph obstruction."""
from fractions import Fraction as Q
from itertools import product
import json,pathlib,hashlib
ROOT=pathlib.Path(__file__).resolve().parent

def optimum(profile,a,b):
 L,P,*h=profile
 # Reimplement as recursive exhaustive feasible allocations, no discovery DP.
 def rec(i,leftL,leftP):
  if i==len(h): return 0
  return max(a[i]*q+b[i]*g+rec(i+1,leftL-q,leftP-g)
             for q in range(min(h[i],leftL)+1)
             for g in range(min(h[i]-q,leftP)+1))
 return rec(0,L,P)

def require(ok,msg):
 if not ok: raise RuntimeError(msg)

def dual_optimum(profile,a,b):
 L,P,*h=profile
 # Every candidate is directly dual feasible. Equality to a primal allocation
 # certifies the continuous LP value without assuming integer optimality.
 lines=[(Q(1),Q(0),Q(0)),(Q(0),Q(1),Q(0))]
 lines += [(Q(1),Q(0),Q(x)) for x in a]
 lines += [(Q(0),Q(1),Q(x)) for x in b]
 lines += [(Q(1),Q(-1),Q(x-y)) for x,y in zip(a,b)]
 best=None
 for j,(u,v,w) in enumerate(lines):
  for u2,v2,w2 in lines[j+1:]:
   d=u*v2-u2*v
   if not d:continue
   lam=(w*v2-w2*v)/d;mu=(u*w2-u2*w)/d
   if lam<0 or mu<0:continue
   beta=[max(Q(0),Q(x)-lam,Q(y)-mu) for x,y in zip(a,b)]
   val=L*lam+P*mu+sum(hi*bi for hi,bi in zip(h,beta))
   if best is None or val<best:best=val
 require(best is not None,'missing dual')
 return best

def main():
 cert=json.loads((ROOT/'decomposition_obstruction.json').read_text())
 terms=cert['terms'];a=cert['a'];b=cert['b'];m=len(a)
 def dot(aa,bb):
  vals=[]
  for t in terms:
   v=optimum(t['profile_L_P_h'],aa,bb)
   require(v==dual_optimum(t['profile_L_P_h'],aa,bb),'primal/continuous-dual mismatch')
   vals.append(Q(t['weight'])*v)
  return sum(vals)
 for t in terms:
  require(optimum(t['profile_L_P_h'],a,b)==t['weighted_value'],'stored weighted value mismatch')
 require(dot(a,b)==-1,'weighted separation failed')
 values={}
 for bits in product([0,1],repeat=2*m):
  v=dot(bits[:m],bits[m:]);require(v>=0,f'unit-graph separation failed {bits},{v}')
  values[''.join(map(str,bits))]=str(v)
 out={'status':'PASS','weighted_dot':str(dot(a,b)),'all_unit_graphs':len(values),
      'min_unit_dot':str(min(Q(v) for v in values.values())),
      'max_unit_dot':str(max(Q(v) for v in values.values())),
      'unit_dots':values,
      'certificate_sha256':hashlib.sha256((ROOT/'decomposition_obstruction.json').read_bytes()).hexdigest(),
      'checker_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
 (ROOT/'decomposition_obstruction_verified.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:v for k,v in out.items() if k!='unit_dots'},indent=2))
if __name__=='__main__': main()
