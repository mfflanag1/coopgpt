from fractions import Fraction as Q
if not __debug__:raise RuntimeError('Assertions must remain enabled')
checks=0
for k in range(3,101):
 n=2*k-1;D=3*k+2
 sets=[set((r+j)%n for j in range(k)) for r in range(n)]
 q=[Q(4 if j in(0,k-1,k) else 3,D) for j in range(n)]
 lam=[Q(0)]*n
 for r,w in ((0,2),(k,2),(1,1),(k-1,1)):lam[r]=Q(w,D)
 assert [sum(lam[r] for r in range(n) if j in sets[r]) for j in range(n)]==q
 for r,S in enumerate(sets):
  rhs=Q(1) if r<=k else Q(3*k+1,D)
  assert sum(q[j] for j in S)==rhs
  if rhs<1:assert 0 in S and lam[r]==0
  assert lam[r]*(sum(q[j] for j in S)-rhs)==0
  checks+=1
 rho=Q(n,k*k);p=Q(4,D);L=sum(lam)
 assert L==Q(6,D) and sum(x*x for x in q)==L<=rho
 assert n*p*p/rho==Q(16*k*k,D*D)<Q(16,9)
 assert rho*n*(p/L)**2==Q(4*n*n,9*k*k)<Q(16,9)
print({'status':'PASS','growing_instances':98,'exact_row_KKT_checks':checks,'largest_owner_count':199,'limiting_ratio':'16/9','required_threshold':'2 (not reached)'})
