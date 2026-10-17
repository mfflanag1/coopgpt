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
count=derivatives=0
for n in range(1,6):
 rows=[tuple(int(i in S) for i in range(n)) for k in (1,2) for S in combinations(range(n),k)]
 for k in range(1,n+1):
  for rr in combinations(rows,k):
   G=[[sum(a*b for a,b in zip(x,y)) for y in rr] for x in rr];inv=inverse(G)
   if inv is None:continue
   count+=1
   for j,row in enumerate(rr):
    for i in range(n):
     if row[i]:
      derivative=sum(Q(rr[l][i])*inv[l][j] for l in range(k))
      assert derivative>=0,(n,rr,j,i,derivative)
      derivatives+=1
print({'independent_bases':count,'own_row_derivatives':derivatives,'maximum_n':5,'status':'PASS'})
