from fractions import Fraction as F
from itertools import product,combinations
from copy import deepcopy
import random
from check_certificate import check
rng=random.Random(431910)
shapes=[]
for m in (1,2):
 teams=list(product(range(m),repeat=3))
 for r in range(m+1):
  for ps in combinations(teams,r):
   if all(len({t[s]for t in ps})==r for s in range(3)):shapes.append((m,ps))
shapes.extend([(3,((0,0,1),(1,2,2))), (3,((0,1,2),(1,2,0),(2,0,1))), (3,((0,1,1),)), (3,())])
count=0
for m,ps in shapes:
 U=[s*m+j for s in range(3)for j in range(m)if all(t[s]!=j for t in ps)]
 targets=U or [-1]
 # Independent support construction through pair endpoints and membership tests.
 endpoints=((0,1),(0,2),(1,2))
 E=[(k,a,b)for k,(s,t)in enumerate(endpoints)for a in range(m)for b in range(m)if a==b or any(team[s]==a and team[t]==b for team in ps)]
 mats=[[[str(F(1,3*m))if(k,a,b)in E else 0 for b in range(m)]for a in range(m)]for k in range(3)]
 cert=dict(schema='core-witness-v1',m=m,P=list(map(list,ps)),unmatched=U,support=list(map(list,E)),matrices=mats,witness_targets=targets,witnesses=[[str(F(1,3*m))]*(3*m)for t in targets],primal_J=str(F(len(ps),m)+F(len(U),9*m)-1))
 rows=list(product(targets,range(m),range(m),range(m)))
 for _ in range(20):
  selected=rng.sample(rows,min(9,len(rows)))
  multipliers=[(*row,F(rng.randrange(5),rng.randrange(1,5)))for row in selected]
  nu0=F(rng.randrange(-4,6),rng.randrange(1,5));nus=[F(rng.randrange(-4,6),rng.randrange(1,5))for t in targets]
  residuals=[]
  for k,a,b in E:
   s,t=endpoints[k]
   obj=3*sum(team[s]==a and team[t]==b for team in ps)
   used=sum(w for target,*team,w in multipliers if team[s]==a and team[t]==b)
   residuals.append(obj-used-(nu0 if a==b else 0))
  for target,nu in zip(targets,nus):
   for player in range(3*m):
    s,j=divmod(player,m)
    hit=sum(w for row_target,*team,w in multipliers if row_target==target and team[s]==j)
    residuals.append(int(target!=-1 and target==player)+hit-nu)
  upper=(nu0+sum(nus)+sum(max(v,0)for v in residuals))/3-1
  cert['dual']=dict(normalization=str(nu0),totals=list(map(str,nus)),upper=str(upper),**{'lambda':[[*row,str(w)]for *row,w in multipliers]})
  result=check(cert)
  if result['upper']!=str(upper):raise RuntimeError('independent upper mismatch')
  broken=deepcopy(cert);broken['dual']['upper']=str(upper+F(1,1000003))
  try:check(broken)
  except ValueError:pass
  else:raise RuntimeError('one-bit exact upper mutation accepted')
  count+=1
print({'independent_cases':count,'support_shapes':len(shapes),'upper_mutations_rejected':count,'sizes':sorted({m for m,p in shapes})})
# Explicit non-diagonal violation: every diagonal sum and witness total stays valid.
m=2;ps=((0,1,1),);U=[1,2,4];E=sorted({(k,j,j)for k in range(3)for j in range(m)}|{(0,0,1),(1,0,1),(2,1,1)})
base=dict(schema='core-witness-v1',m=m,P=[list(ps[0])],unmatched=U,support=list(map(list,E)),matrices=[[[str(F(1,6))if(k,a,b)in E else 0 for b in range(m)]for a in range(m)]for k in range(3)],witness_targets=U,witnesses=[['1/2','1/2',0,0,0,0]]*3,primal_J='-1/3',dual={'lambda':[],'normalization':0,'totals':[0,0,0],'upper':3})
check(base)
bad=deepcopy(base);bad['witnesses'][0]=[0,'1/2','1/2',0,0,0]
try:check(bad)
except ValueError as e:
 if 'core violation' not in str(e):raise RuntimeError(str(e))
 print({'diagonals_preserved_non_diagonal_violation':'rejected','reason':str(e)})
else:raise RuntimeError('non-diagonal corruption accepted')
