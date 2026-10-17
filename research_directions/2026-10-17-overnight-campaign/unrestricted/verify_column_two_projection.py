from fractions import Fraction as Q
from itertools import combinations
if not __debug__:raise RuntimeError('Assertions must remain enabled')
def inverse(A):
 n=len(A);m=[[Q(x) for x in row]+[Q(int(i==j)) for j in range(n)] for i,row in enumerate(A)]
 for k in range(n):
  p=next((i for i in range(k,n) if m[i][k]),None)
  if p is None:return None
  m[k],m[p]=m[p],m[k];v=m[k][k];m[k]=[x/v for x in m[k]]
  for i in range(n):
   if i!=k:
    v=m[i][k];m[i]=[x-v*y for x,y in zip(m[i],m[k])]
 return [row[n:] for row in m]
bases=derivatives=0
for r in range(1,6):
 cols=[tuple(int(j in S) for j in range(r)) for size in (1,2) for S in combinations(range(r),size)]
 for n in range(r,min(7,len(cols))+1):
  for selected in combinations(cols,n):
   G=[[sum(c[i]*c[j] for c in selected) for j in range(r)] for i in range(r)]
   H=inverse(G)
   if H is None:continue
   bases+=1
   assert all(G[i][i]>=sum(G[i][j] for j in range(r) if j!=i) for i in range(r))
   for source in range(r):
    w=[H[j][source] for j in range(r)]
    assert w[source]>0 and all(abs(v)<=w[source] for v in w)
    for c in selected:
     if c[source]:
      assert sum(c[j]*w[j] for j in range(r))>=0
      derivatives+=1
for k in range(1,101):
 shared=Q(2,k+2);private=Q(1,k+2)
 assert shared+k*private==1
 assert shared==2*private
 assert shared+2*k*private==Q(2*(k+1),k+2)<2
print({'status':'PASS','independent_gram_bases':bases,'own_derivatives':derivatives,'maximum_active_rows':5,'maximum_columns':7,'sharp_family_checks':100})
