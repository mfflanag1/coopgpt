#!/usr/bin/env python3
"""Exact local refutation scout for one coupled P4 selector, not a proof of IC."""
from fractions import Fraction as F
from itertools import product
import json
class D:
 def __init__(self,x,g=None): self.x=F(x);self.g=g or (F(0),)*4
 def __add__(self,o):
  o=lift(o);return D(self.x+o.x,tuple(a+b for a,b in zip(self.g,o.g)))
 __radd__=__add__
 def __neg__(self):return D(-self.x,tuple(-a for a in self.g))
 def __sub__(self,o):return self+-lift(o)
 def __rsub__(self,o):return lift(o)+-self
 def __mul__(self,o):
  o=lift(o);return D(self.x*o.x,tuple(a*o.x+self.x*b for a,b in zip(self.g,o.g)))
 __rmul__=__mul__
 def __truediv__(self,o):
  o=lift(o);return D(self.x/o.x,tuple((a*o.x-self.x*b)/o.x**2 for a,b in zip(self.g,o.g)))
def lift(o):return o if isinstance(o,D) else D(o)
def extremum(xs,mini=True):
 vals=[z.x for z in xs];i=vals.index(min(vals) if mini else max(vals))
 if vals.count(vals[i])>1:raise ValueError('seam')
 return xs[i]
def choose(c,alpha,beta):
 A,B,C,H=[D(x,tuple(F(i==j) for j in range(4))) for i,x in enumerate(c)]
 slo=extremum([D(0),alpha*H-C],False);shi=extremum([alpha*H,A-alpha*B])
 tlo=extremum([D(0),alpha*A-B],False);thi=extremum([alpha*A,H-alpha*C])
 if slo.x>=shi.x or tlo.x>=thi.x:raise ValueError('not strict all-right-saturated chamber')
 s=(alpha*A*H-alpha*B*C+beta*A*C)/(A+C)
 t=(alpha*A*H-alpha*B*C+beta*B*H)/(B+H)
 s=extremum([extremum([s,slo],False),shi]);t=extremum([extremum([t,tlo],False),thi])
 return [(alpha*B+s)/A,(alpha*A-t)/B,(alpha*H-s)/C,(alpha*C+t)/H]
def worst(c,p):
 cases=[]
 for v in range(4):
  z=p[v].x+sum(F(c[j])*min(p[j].g[v],0) for j in range(4));cases.append((z,'coordinate',[v],0))
 for u,v in [(0,1),(0,3),(2,3)]:
  z=p[u].x+p[v].x+sum(F(c[j])*min(p[j].g[u]+p[j].g[v],0) for j in range(4))
  cases.append((z-1,'edge',[u,v],1))
 return min(cases)
def scan(alpha,beta):
 checked=skipped=0
 for c in product(range(1,7),repeat=4):
  try:p=choose(c,alpha,beta)
  except ValueError:skipped+=1;continue
  checked+=1;z,kind,coord,rhs=worst(c,p)
  if z<0:
   direction=[F(i in coord) for i in range(4)]
   hold=[F(c[j]) if sum(p[j].g[v] for v in coord)<0 else F(0) for j in range(4)]
   return {'alpha':str(alpha),'beta':str(beta),'status':'EXACT_LOCAL_FAILURE','capacity':c,
           'prices':[str(v.x) for v in p],'kind':kind,'direction':list(map(str,direction)),
           'limiting_holdings':list(map(str,hold)),'derivative':str(z+rhs),'required':rhs,
           'checked_before_failure':checked,'skipped':skipped}
 return {'alpha':str(alpha),'beta':str(beta),'status':'NO_FAILURE_ON_SCOPED_GRID','checked':checked,'skipped':skipped}
if __name__=='__main__':
 for a in [F(2,3),F(3,4),F(4,5),F(9,10)]:
  for b in [F(1,10),F(1,4),F(1,3),F(1,2),F(3,4),F(1)]:print(json.dumps(scan(a,b)),flush=True)
