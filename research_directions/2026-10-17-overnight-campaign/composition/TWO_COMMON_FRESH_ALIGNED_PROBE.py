from fractions import Fraction as Q
from itertools import combinations,product
A=(Q(1),Q(1),Q(1,4));B=(Q(1),Q(1,4),Q(1));W=tuple(a+b for a,b in zip(A,B))
lines=[(Q(1),Q(0),Q(0)),(Q(0),Q(1),Q(0))]+list(zip(A,B,W))
verts=set()
for (a,b,w),(aa,bb,ww) in combinations(lines,2):
 d=a*bb-aa*b
 if d:
  p=(w*bb-ww*b)/d;q=(a*ww-aa*w)/d
  if min(p,q)>=0:verts.add((p,q))
def radial(P,Qq,c):
 forms=[(P*p+Qq*q,tuple(max(Q(0),w-a*p-b*q) for a,b,w in zip(A,B,W))) for p,q in verts]
 af=[(base,sum((v*g for v,g in zip(c,grad)),Q(0)),grad) for base,grad in forms]
 cuts={Q(0),Q(1)}
 for (a,b,_),(aa,bb,__) in combinations(af,2):
  if b!=bb:
   t=(aa-a)/(b-bb)
   if 0<t<1:cuts.add(t)
 cuts=sorted(cuts);prices=[Q(0)]*3
 for lo,hi in zip(cuts,cuts[1:]):
  mid=(lo+hi)/2;vl=min(base+mid*slope for base,slope,g in af)
  gs=[g for base,slope,g in af if base+mid*slope==vl]
  g=tuple(sum(v[j] for v in gs)/len(gs) for j in range(3))
  for j in range(3):prices[j]+=(hi-lo)*g[j]
 return prices
for c in product((Q(1,4),Q(1),Q(4)),repeat=3):
 old=radial(Q(1),Q(1),c);new=radial(Q(2),Q(1),c)
 if any(n<o for o,n in zip(old,new)):
  print('common monotonicity fails',c,old,new);break
else:print('no failure in small directed probe')
