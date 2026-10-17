"""Exact rational feasible-plan certificate for interacting public demand types."""
from fractions import Fraction as Q
from random import Random
from pathlib import Path
import json
rng=Random(761010);checks=0
for L in range(1,6):
 for trial in range(1000):
  T=rng.randrange(1,9);P=[Q(rng.randrange(1,10),rng.randrange(1,5)) for _ in range(L)]
  types=[]
  for tau in range(T):
   a=[Q(rng.randrange(4),rng.randrange(1,5)) for _ in range(L)]
   if not any(a):a[rng.randrange(L)]=Q(1)
   M=rng.randrange(1,9)
   capacities=[Q(rng.randrange(6),rng.randrange(1,5)) for _ in range(M)]
   profit=[Q(rng.randrange(6),rng.randrange(1,5)) for _ in range(M)]
   K=Q(rng.randrange(1,7),rng.randrange(1,4))+1
   budget=min(P[v]/a[v] for v in range(L) if a[v]);left=budget
   z=[Q(0)]*M
   for j in sorted(range(M),key=lambda j:-profit[j]):
    z[j]=min(left,capacities[j]);left-=z[j]
   value=sum(z[j]*profit[j] for j in range(M))
   types.append((a,capacities,profit,K,z,value))
  D=max(sum(ty[3] for ty in types if ty[0][v]) for v in range(L))
  loads=[Q(0)]*L;combined_value=Q(0);proxy=Q(0)
  for a,c,w,K,z,val in types:
   scale=K/D
   assert scale<=1
   assert all(scale*z[j]<=c[j] for j in range(len(c)))
   for v in range(L):loads[v]+=a[v]*sum(z)*scale
   combined_value+=scale*val;proxy+=K*val
  assert all(loads[v]<=P[v] for v in range(L))
  assert combined_value==proxy/D
  checks+=1
out={'status':'PASS','exact_feasible_combination_certificates':checks,
 'shared_rows_up_to':5,'types_up_to':8,'branches_per_type_up_to':8,
 'limits':'Certifies weighted isolated optima combine feasibly at congestionD; all-profile incentive transfer is analytic.'}
Path(__file__).with_name('TYPE_CONGESTION_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
