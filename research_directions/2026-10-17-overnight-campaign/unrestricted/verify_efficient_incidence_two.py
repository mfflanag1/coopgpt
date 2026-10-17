from fractions import Fraction as Q
from itertools import combinations,product
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

def dot(a,b):return sum(x*y for x,y in zip(a,b))

def projection_solver(C,n):
 bases=[]
 for k in range(1,min(n,len(C))+1):
  for ix in combinations(range(len(C)),k):
   B=[C[j] for j in ix];H=inverse([[dot(a,b) for b in B] for a in B])
   if H is not None:bases.append((ix,B,H))
 def solve(rhs,target):
  if all(dot(row,target)>=v for row,v in zip(C,rhs)):return target
  for ix,B,H in bases:
   rr=[rhs[j]-dot(row,target) for j,row in zip(ix,B)]
   lam=[dot(row,rr) for row in H]
   if min(lam)<0:continue
   q=[target[j]+sum(l*row[j] for l,row in zip(lam,B)) for j in range(n)]
   if all(dot(row,q)>=v for row,v in zip(C,rhs)):return q
  raise AssertionError(('no exact projection KKT witness',C,rhs,target))
 return solve

def vertex_solver(C,n):
 bases=[]
 for ix in combinations(range(len(C)),n):
  H=inverse([C[j] for j in ix])
  if H is not None:bases.append((ix,H))
 def solve(rhs):
  vals=[]
  for ix,H in bases:
   q=[dot(row,[rhs[j] for j in ix]) for row in H]
   if all(dot(row,q)>=v for row,v in zip(C,rhs)):vals.append(sum(q))
  assert vals
  return min(vals)
 return solve

families=[('row_path',3,[(0,1),(1,2)]),('row_triangle',3,[(0,1),(1,2),(0,2)]),('row_star',4,[(0,1),(0,2),(0,3)]),('row_cycle',4,[(0,1),(1,2),(2,3),(3,0)]),('column_two_big',4,[(0,1,2),(0,3)]),('column_two_three_rows',4,[(0,1),(1,2,3),(0,2)])]
profiles=monotonic_pairs=0
for name,n,sets in families:
 A=[tuple(Q(int(j in S)) for j in range(n)) for S in sets];r=len(A)
 C=A+[tuple(Q(int(i==j)) for j in range(n)) for i in range(n)]
 lp=vertex_solver(C,n);reg=projection_solver(C,n)
 CE=C+[tuple(Q(1) for _ in range(n)),tuple(Q(-1) for _ in range(n))]
 eff=projection_solver(CE,n)
 demands={tuple(Q(1) for _ in range(r)),tuple(Q(0) for _ in range(r))}
 for j in range(r):
  for v in (Q(0),Q(1,2),Q(3,2),Q(2)):
   b=[Q(1)]*r;b[j]=v;demands.add(tuple(b))
 for i in range(n):
  inc=[j for j,row in enumerate(A) if row[i]]
  for vals in product((Q(0),Q(1,2),Q(1)),repeat=len(inc)):
   b=[Q(1)]*r
   for j,v in zip(inc,vals):b[j]=v
   demands.add(tuple(b))
 solved={}
 for b in sorted(demands):
  rhs=list(b)+[Q(0)]*n;T=lp(rhs)
  e=eff(rhs+[T,-T],[Q(0)]*n)
  assert sum(e)==T and min(e)>=0 and all(dot(a,e)>=v for a,v in zip(A,b))
  qs=[reg(rhs,[Q(-1)/epsilon]*n) for epsilon in (Q(1),Q(1,4))]
  for epsilon,q in zip((Q(1),Q(1,4)),qs):
   assert sum(q)+epsilon*dot(q,q)/2<=T+epsilon*dot(e,e)/2
   assert dot(q,q)<=dot(e,e)
  solved[b]=[e]+qs;profiles+=1
 for lo,ql in solved.items():
  for hi,qh in solved.items():
   for i in range(n):
    if all(lo[j]<=hi[j] if A[j][i] else lo[j]==hi[j] for j in range(r)):
     assert all(x[i]<=y[i] for x,y in zip(ql,qh)),(name,i,lo,hi,ql,qh)
     monotonic_pairs+=1
 print({'family':name,'profiles':len(solved),'status':'PASS'},flush=True)
print({'status':'PASS','families':len(families),'exact_profile_KKT_checks':profiles,'own_comparable_profile_pairs':monotonic_pairs,'selectors_per_profile':3})
