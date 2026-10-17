from fractions import Fraction as Q
from math import comb
from itertools import combinations
import random, json
from pathlib import Path
rng=random.Random(20261017)
counts={'upper_profiles':0,'upper_coverage':0,'upper_outside':0,'recursion_identities':0,'finite_potential_checks':0}
m=2
A=Q(3,2)**3-1
assert A==Q(19,8)
c0=Q(1,342)
E=Q(0)
for r in range(3,6):
 E=Q(3,2)*(E+1)
 assert E==3*(Q(3,2)**(r-2)-1)
 counts['recursion_identities']+=1
assert E==Q(57,8)
assert 3*E==Q(171,8)
# Zero-sum mergers have two null prices; for r>=4 this fits the same bound.
for r in (4,5):
 prior=3*(Q(3,2)**(r-3)-1)
 assert 2<=prior+1
assert Q(1,8)/(6*E)==c0

def potential(x,kind):
 if 0<=x<=2:return Q(0)
 if x<0:return -potential(2-x,kind)
 t=x-2
 if kind==0:return t/2
 if kind==1:return t*(2+t)/(2+2*t)
 raise ValueError(kind)
for kind in (0,1):
 q=lambda x:potential(x,kind)
 assert q(Q(3))>=Q(1,2)
 total=Q(0)
 for k in range(3):
  t=Q(k)
  L=(-q(t+2)+2*q(t+1)-2*q(t-1)+q(t-2))/4
  # Direct internal Banzhaf coalition total checks the cancellation in(9).
  z=[Q(2),Q(-1),Q(-1)]
  direct=Q(0)
  for i in range(3):
   others=[j for j in range(3) if j!=i]
   for mask in range(4):
    zR=sum((z[others[j]] for j in range(2) if mask>>j&1),Q(0))
    direct+=(q(t+zR+z[i])-q(t+zR))/4
  assert direct==L
  total+=Q(comb(2,k),4)*L
  counts['finite_potential_checks']+=1
 assert total==-q(Q(4))/8
 assert total<=Q(-1,8)

for case in range(240):
 n=2+case%5;d=2+case%3
 rows=[[Q(rng.randrange(6)) for _ in range(d)] for _ in range(1+case%5)]
 def F(x):return min(sum((row[j]*x[j] for j in range(d)),Q(0)) for row in rows)
 b=[[Q(rng.randrange(5),2) for _ in range(d)] for _ in range(n)]
 def value(sub):return F([sum((b[i][j] for i in sub),Q(0)) for j in range(d)])
 def pay(bb):
  f=[F(x) for x in bb];T=F([sum((x[j] for x in bb),Q(0)) for j in range(d)])
  G=T-sum(f,Q(0));assert G>=0
  y=[x+G/2 for x in f]
  assert sum(y,Q(0))==sum(f,Q(0))+Q(n,2)*G
  return y
 y=pay(b)
 for mask in range(1<<n):
  sub=[i for i in range(n) if mask>>i&1]
  assert sum((y[i] for i in sub),Q(0))>=value(sub)
  counts['upper_coverage']+=1
 for size in (1,2):
  for sub in combinations(range(n),size):
   high=[x[:] for x in b]
   ds=[]
   for i in sub:
    delta=[Q(rng.randrange(3),3) for _ in range(d)]
    ds.append(delta);high[i]=[b[i][j]+delta[j] for j in range(d)]
   yh=pay(high)
   withheld=[sum((x[j] for x in ds),Q(0)) for j in range(d)]
   assert sum((yh[i]-y[i] for i in sub),Q(0))>=F(withheld)
   counts['upper_outside']+=1
 counts['upper_profiles']+=1
out={'status':'PASS','counts':counts,'five_active_owner_potential_gap_at_least_one_eighth':True,'lower_coefficient_exact':str(c0),'lower_coefficient_float':float(c0),'scope':'Exact finite identities and sampled rational upper-rule diagnostics; analytic all-profile lower proof is in the companion note.'}
Path(__file__).with_name('pairwise_gain_linear_checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
