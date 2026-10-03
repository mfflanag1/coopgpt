"""Recover one RP-relaxation dual without modifying the frozen discovery source."""
import json,sys,time,hashlib
from fractions import Fraction as Q
from pathlib import Path
from itertools import product,permutations

def main():
 root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root/'src'))
 import residual_relaxation as module
 original=module.linprog;capture={}
 def tapped(c,**kw):
  result=original(c,**kw);capture.update(c=c,kw=kw,result=result);return result
 module.linprog=tapped
 raw=json.loads((root/'paired/CW-01_relaxed.json').read_text());m=raw['m'];P=raw['P'];start=time.monotonic()
 candidate=module.solve(m,P,1800)
 if 'schema' not in candidate:raise ValueError(candidate)
 module.check(candidate)
 result=capture['result'];kw=capture['kw'];A=kw['A_ub'];B=kw['A_eq'];rhs=kw['b_ub']
 U=sorted(set(range(3*m))-{s*m+t[s] for t in P for s in range(3)})
 names=[['core',*t] for t in product(range(m),repeat=3)]
 for i in range(3*m):names.extend([['diagonal_cap',i],['core_dominance',i]])
 names += [['unmatched_cap',i] for i in U]
 for s in range(3):
  for a in range(m):
   for b in range(m):
    if a!=b:names.extend([['completion',s,a,b],['range',s,a,b]])
 for j,t in enumerate(P):
  names += [['P_induced',j,*perm] for perm in permutations(range(3))]
 names += [['residual',i] for i in U]
 if len(names)!=A.shape[0]:raise ValueError('row labelling mismatch')
 masses=[max(Q(0),Q(float(-v)).limit_denominator(10**6)) for v in result.ineqlin.marginals]
 nu=[Q(float(-v)).limit_denominator(10**6) for v in result.eqlin.marginals]
 residual=[Q(int(-v)) for v in capture['c']]
 for k,mass in enumerate(masses):
  for pos in range(A.indptr[k],A.indptr[k+1]):residual[A.indices[pos]]-=mass*int(A.data[pos])
 for k,n in enumerate(nu):
  for j,coef in enumerate(B[k]):residual[j]-=n*int(coef)
 correction=sum(max(Q(0),r) for r in residual)
 upper=(sum(nu)+sum(mass*int(b) for mass,b in zip(masses,rhs))+correction)/3-1
 candidate['residual_dual']={'rows':[{'constraint':name,'mass':str(mass)} for name,mass in zip(names,masses) if mass],'normalization':str(nu[0]),'core_total':str(nu[1]),'box_correction':str(correction),'upper':str(upper)}
 candidate['provenance']={'recovery_attempt':1,'source_sha256':hashlib.sha256((root/'src/residual_relaxation.py').read_bytes()).hexdigest(),'support':'CW-01','elapsed_seconds':time.monotonic()-start,'scope':'independent semantic dual check required'}
 out=Path(sys.argv[2]);out.write_text(json.dumps(candidate,indent=2)+'\n')
 grouped={}
 for r in candidate['residual_dual']['rows']:
  name=r['constraint'][0];grouped[name]=grouped.get(name,0)+1
 print(json.dumps({'lower':candidate['J_relaxed'],'upper':str(upper),'gap':str(upper-Q(candidate['J_relaxed'])),'box_correction':str(correction),'rows':grouped,'nu':list(map(str,nu)),'elapsed_seconds':time.monotonic()-start}))
if __name__=='__main__':main()
