from fractions import Fraction as Q
from itertools import combinations
import json
if not __debug__: raise RuntimeError('Assertions must remain enabled')
A=[(0,1,0,1),(1,0,1,1),(1,1,0,0),(1,1,0,1)]
b=[Q(3),Q(3),Q(2),Q(5)]
low=b[:-1]+[Q(15,4)]
def dot(a,b):return sum((x*y for x,y in zip(a,b)),Q(0))
def solve(A,b):
 n=len(b);m=[list(map(Q,row))+[Q(v)] for row,v in zip(A,b)]
 for k in range(n):
  pivot=next((j for j in range(k,n) if m[j][k]),None)
  if pivot is None:return None
  m[k],m[pivot]=m[pivot],m[k];d=m[k][k];m[k]=[v/d for v in m[k]]
  for j in range(n):
   if j!=k:
    d=m[j][k];m[j]=[v-d*w for v,w in zip(m[j],m[k])]
 return tuple(row[-1] for row in m)
def verify_kkt(rows,rhs,q,lam):
 assert all(t>=0 for t in q) and all(t>=0 for t in lam)
 assert all(dot(row,q)>=v for row,v in zip(rows,rhs))
 assert all(t*(dot(row,q)-v)==0 for row,v,t in zip(rows,rhs,lam))
 assert all(q[j]==sum(t*row[j] for row,t in zip(rows,lam)) for j in range(4))
def projection(rows,rhs):
 for count in range(min(4,len(rows))+1):
  for ids in combinations(range(len(rows)),count):
   if not ids:
    q=(Q(0),)*4;lam=[]
   else:
    rr=[rows[j] for j in ids];lam=solve([[dot(x,y) for y in rr] for x in rr],[rhs[j] for j in ids])
    if lam is None or min(lam)<0:continue
    q=tuple(sum(t*row[j] for row,t in zip(rr,lam)) for j in range(4))
   if any(dot(row,q)<v for row,v in zip(rows,rhs)):continue
   multipliers=[Q(0)]*len(rows)
   for j,t in zip(ids,lam):multipliers[j]=t
   verify_kkt(rows,rhs,q,multipliers);return q
 raise AssertionError('No rational KKT witness')
q=(Q(3,4),Q(5,4),Q(1,2),Q(7,4));lam=(Q(1),Q(1,2),Q(0),Q(1,4))
verify_kkt(A,low,q,lam)
# Full balanced closure's five positive own rows, including redundant supersets.
own=[((0,1,0,1),Q(3)),((1,1,0,1),Q(5)),((1,0,1,1),Q(3)),((0,1,1,1),Q(3)),((1,1,1,1),Q(5))]
endpoint=[]
for mask in range(32):
 rows=[(1,1,0,0)];rhs=[Q(2)]
 for j,(row,v) in enumerate(own):
  if mask>>j&1:rows.append(row);rhs.append(v)
 endpoint.append(projection(rows,rhs)[3])
assert max(endpoint)==Q(12,7)
assert q[3]-max(endpoint)==Q(1,28)
# Enumerate exact vertices to give a concrete 5-resource production function.
def vertices(rhs):
 rows=A+[tuple(int(i==j) for i in range(4)) for j in range(4)]
 rr=rhs+[Q(0)]*4;out=set()
 for ids in combinations(range(8),4):
  z=solve([rows[j] for j in ids],[rr[j] for j in ids])
  if z is not None and all(dot(row,z)>=v for row,v in zip(rows,rr)):out.add(z)
 return sorted(out)
pfull=vertices(b);plow=vertices(low)
forms=[p+(Q(0),) for p in pfull]+[p+(Q(5),) for p in plow]
vals={};wvals={}
for s in range(16):
 base=tuple(Q(int(s>>j&1)) for j in range(4))
 v=min(dot(p,base) for p in pfull);w=min(dot(p,base) for p in plow)
 assert w<=v
 if not s&8:assert w==v
 for high in (0,1):
  z=base+(Q(high*int(bool(s&8))),)
  val=min(dot(p,z) for p in forms)
  assert val==(v if high else w)
 vals[str(s)]=str(v);wvals[str(s)]=str(w)
assert vals['15']=='5' and wvals['15']=='4'
print(json.dumps({'status':'PASS','owners':4,'resources':5,'endpoint_cases':32,'interior_payment':str(q[3]),'endpoint_maximum':str(max(endpoint)),'gap':str(q[3]-max(endpoint)),'full_vertices':[[str(t) for t in p] for p in pfull],'low_vertices':[[str(t) for t in p] for p in plow],'full_game':vals,'low_game':wvals}))
