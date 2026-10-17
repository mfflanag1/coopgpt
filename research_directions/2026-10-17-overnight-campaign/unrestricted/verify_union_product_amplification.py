from fractions import Fraction as Q
from itertools import product
from math import prod
if not __debug__:raise RuntimeError('Assertions must remain enabled')
n=5;A=[tuple(int((j-r)%n<3) for j in range(n)) for r in range(n)]
z=[Q(1,3)]*n;lam=[Q(1,9)]*n;rho=Q(5,9)
b=[Q(11,12)]+[Q(1)]*4;q=[Q(5,18),Q(13,36),Q(5,18),Q(13,36),Q(13,36)]
l=[Q(t,108) for t in (1,19,10,10,19)];L=sum(l);p=q[1]
previous=Q(0);rows_checked=0
for K in range(1,6):
 alpha=rho/(rho+(K-1)*L);beta=L/(rho+(K-1)*L)
 xx=[alpha*x for x in q]+[beta*x for _ in range(K-1) for x in z]
 full=[x/K for _ in range(K) for x in z]
 station=[Q(0)]*(K*n);fullstation=[Q(0)]*(K*n);mass=Q(0)
 for rs in product(range(n),repeat=K):
  row=[v for r in rs for v in A[r]]
  rhs=alpha*b[rs[0]]+(K-1)*beta
  if not row[1]:assert rhs==1
  mu=alpha*l[rs[0]]*prod(lam[r] for r in rs[1:])/rho**(K-1)
  fullmu=prod(lam[r] for r in rs)/(K*rho**(K-1))
  lhs=sum(v*x for v,x in zip(row,xx))
  assert lhs>=rhs and mu*(lhs-rhs)==0
  assert sum(v*x for v,x in zip(row,full))==1
  for j,v in enumerate(row):station[j]+=mu*v;fullstation[j]+=fullmu*v
  mass+=mu;rows_checked+=1
 assert station==xx and fullstation==full
 assert mass==alpha*L
 assert sum(x*x for x in full)==rho/K
 ratio=K*K*rho*n*p*p/(rho+(K-1)*L)**2
 assert previous<=ratio<=rho*n*(p/L)**2
 previous=ratio
print({'status':'PASS','union_tuple_KKT_rows':rows_checked,'maximum_blocks':5,'limit_normalized_ratio':str(rho*n*(p/L)**2),'threshold_violated':rho*n*(p/L)**2>2})
