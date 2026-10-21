from fractions import Fraction as Q
from math import comb
from itertools import combinations
from collections import defaultdict
from pathlib import Path
import json

def params(d):
 n=2**d;a=n//2-1;b=n//2-d;m=a+b;D=comb(d,2);R=a-D;K=a*(d-2)//d
 f=Q(K,a);mu=D*f;lo=mu.numerator//mu.denominator;hi=-(-mu.numerator//mu.denominator)
 assert R>0 and 0<K<=b
 assert 0<=lo<=hi<=min(K,D-d+1)
 assert 0<=K-hi<=K-lo<=R
 assert (f+(d-2)*mu/(D-d+1))/(d+1)==f
 assert Q(a,m)*f==Q(b,m)*Q(K,b)==Q(K,m)
 c=n-K-1;theta=Q(d,d+1);rho=Q(n,c*c)
 t=Q(d*d,d+1)+Q((m-K)**2,m)
 assert d*theta+(c-d)*Q(m-K,m)==t
 p=theta/t;H=rho*n*theta*theta;direct=n*p*p/rho
 return locals()

def enumerate_distribution(d):
 p=params(d);n=p['n'];K=p['K'];D=p['D'];R=p['R'];mu=p['mu'];lo=p['lo'];hi=p['hi'];m=p['m'];a=p['a'];b=p['b']
 star={0}|{1<<j for j in range(d)}
 odd=[u for u in range(n) if u.bit_count()%2==1 and u not in star]
 pair=[u for u in range(n) if u.bit_count()==2]
 rest=[u for u in range(n) if u.bit_count()%2==0 and u.bit_count()>=4]
 dist=defaultdict(Q)
 choice=[(lo,Q(1))] if lo==hi else [(lo,hi-mu),(hi,mu-lo)]
 for s in sorted(star):
  wo=Q(1,d+1)*Q(b,m)/comb(b,K)
  for sub in combinations(odd,K):dist[frozenset((s,)+sub)]+=wo
  allowed=[u for u in pair if s==0 or not(u&s)]
  for P,prob in choice:
   we=Q(1,d+1)*Q(a,m)*prob/(comb(len(allowed),P)*comb(R,K-P))
   for x in combinations(allowed,P):
    for y in combinations(rest,K-P):dist[frozenset((s,)+x+y)]+=we
 assert sum(dist.values())==1 and all(w>0 for w in dist.values())
 for I in dist:
  assert len(I)==K+1 and len(I&star)==1
  assert all((u^(1<<j)) not in I for u in I for j in range(d))
 marg=[sum(w for I,w in dist.items() if u in I) for u in range(n)]
 assert all(marg[u]==(Q(1,d+1) if u in star else Q(K,m)) for u in range(n))
 w=[1-x for x in marg];t=p['t']
 assert sum(x*x for x in w)==t
 assert all(sum(w[u] for u in range(n) if u not in I)==t for I in dist)
 q=[x/t for x in w]
 assert all(sum(weight/t for I,weight in dist.items() if u not in I)==q[u] for u in range(n))
 # Independently verify full KKT by an actual XOR orbit of one supported row.
 seed=next(iter(dist));row=set(range(n))-set(seed);c=p['c']
 assert all(sum((u^v) in row for v in range(n))==c for u in range(n))
 off_count=0
 if d==4:
  for tail in combinations(range(1,n),K):
   I={0,*tail}
   if any((u^(1<<j)) in I for u in I for j in range(d)):continue
   off_count+=1
   assert sum(q[u] for u in range(n) if u not in I)==1
 return {'d':d,'n':n,'distinct_supports':len(dist),'mass':'1','exact_marginals':True,'independence':True,'supported_kkt':True,'off_rows_exhaustively_checked':off_count,'full_xor_kkt':True}

if __name__=='__main__':
 records=[enumerate_distribution(d) for d in (4,5)]
 for d in range(4,65):params(d)
 asym=[]
 for d in (8,9,10,16,32,64,128,256):
  p=params(d);rho=p['rho'];B=rho.denominator//rho.numerator
  # Square of private-only funding lower bound /sqrt(totalowners).
  N=B*p['n']+1
  coeff_sq=(B*p['n']*p['p']/(1+B*rho))**2/N
  asym.append({'d':d,'H':float(p['H']),'direct_R':float(p['direct']),'funding_coefficient_squared':float(coeff_sq)})
 out={'status':'PASS','explicit_finite_distribution_checks':records,'rounding_and_parameter_checks':'all integers d=4,...,64 plus128,256','asymptotic_samples':asym}
 (Path(__file__).parent/'activation_hypercube_check_results.txt').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
