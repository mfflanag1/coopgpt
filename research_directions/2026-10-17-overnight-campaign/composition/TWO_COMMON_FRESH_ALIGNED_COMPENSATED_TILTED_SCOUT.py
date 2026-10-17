from fractions import Fraction as Q
from itertools import combinations,product
A=(Q(1),Q(1),Q(1,4));B=(Q(1),Q(1,4),Q(1));A=tuple(a/100 for a in A);W=tuple(a+b for a,b in zip(A,B))
lines=[(Q(1),Q(0),Q(0)),(Q(0),Q(1),Q(0))]+list(zip(A,B,W))
verts=set()
for (a,b,w),(aa,bb,ww) in combinations(lines,2):
 d=a*bb-aa*b
 if d:
  p=(w*bb-ww*b)/d;q=(a*ww-aa*w)/d
  if min(p,q)>=0:verts.add((p,q))
verts=sorted(verts)
def prices(C):
 P,Qq,*c=C
 forms=[(P*p+Qq*q,tuple(max(Q(0),w-a*p-b*q) for a,b,w in zip(A,B,W)),(p,q)) for p,q in verts]
 af=[(base,sum((v*g for v,g in zip(c,grad)),Q(0)),pq+grad) for base,grad,pq in forms]
 cuts={Q(0),Q(1)}
 for (a,b,_),(aa,bb,__) in combinations(af,2):
  if b!=bb:
   t=(aa-a)/(b-bb)
   if 0<t<1:cuts.add(t)
 cuts=sorted(cuts);res=[Q(0)]*5
 for lo,hi in zip(cuts,cuts[1:]):
  mid=(lo+hi)/2;vl=min(base+mid*slope for base,slope,g in af)
  gs=[g for base,slope,g in af if base+mid*slope==vl]
  # Prefer the canonical plateau gradient, otherwise average; positive
  # generic profiles only have isolated tie points except possible plateau.
  g=next((g for g in gs if g[:2]==(1,1)),None)
  if g is None:g=tuple(sum(v[j] for v in gs)/len(gs) for j in range(5))
  for j in range(5):res[j]+=(hi-lo)*g[j]
 value=min(base+slope for base,slope,g in af)
 res[0]=value/P
 res[1]=value/Qq
 return res
count=0
for C in product((Q(1,4),Q(1),Q(4)),repeat=5):
 C=(C[0]/100,)+C[1:]
 p=prices(C)
 for j in range(5):
  CC=list(C);delta=Q(1,300) if j==0 else Q(1,3);CC[j]+=delta;pp=prices(CC)
  loss=sum((cap*max(Q(0),old-new) for cap,old,new in zip(C,p,pp)),Q(0))
  gain=delta*pp[j]
  count+=1
  if loss>gain:
   print('FAIL',C,'restore',j,'old',p,'new',pp,'loss',loss,'gain',gain);raise SystemExit
print('PASS',count)
