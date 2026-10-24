"""Exact diagnostic for frozen P4 proof; finite checks are not its proof."""
from fractions import Fraction as F
from functools import total_ordering
from itertools import product
import json
from pathlib import Path

@total_ordering
class Q2:
    __slots__=('a','b')
    def __init__(self,a=0,b=0):
        if isinstance(a,Q2): self.a,self.b=a.a,a.b
        else:self.a,self.b=F(a),F(b)
    def __add__(self,o):
        o=Q2(o);return Q2(self.a+o.a,self.b+o.b)
    __radd__=__add__
    def __neg__(self):return Q2(-self.a,-self.b)
    def __sub__(self,o):return self+-Q2(o)
    def __rsub__(self,o):return Q2(o)+-self
    def __mul__(self,o):
        o=Q2(o);return Q2(self.a*o.a+2*self.b*o.b,self.a*o.b+self.b*o.a)
    __rmul__=__mul__
    def __truediv__(self,o):
        o=Q2(o);d=o.a*o.a-2*o.b*o.b
        if not d:raise ZeroDivisionError
        return self*Q2(o.a/d,-o.b/d)
    def __rtruediv__(self,o):return Q2(o)/self
    def sign(self):
        a,b=self.a,self.b
        if not b:return (a>0)-(a<0)
        if not a:return (b>0)-(b<0)
        if a>0 and b>0:return 1
        if a<0 and b<0:return -1
        d=a*a-2*b*b
        return ((d>0)-(d<0))*(1 if a>0 else -1)
    def __eq__(self,o):
        o=Q2(o);return self.a==o.a and self.b==o.b
    def __lt__(self,o):return (self-Q2(o)).sign()<0
    def __str__(self):return f'{self.a}+({self.b})sqrt(2)'
    def __hash__(self):return hash((self.a,self.b))

zero=Q2();one=Q2(1);alpha=Q2(0,F(1,2));beta=Q2(F(1,2))
e=[tuple(Q2(int(i==j)) for j in range(4)) for i in range(4)]
z=(zero,)*4

def add(a,b):return tuple(x+y for x,y in zip(a,b))
def scale(a,t):return tuple(x*t for x in a)
def dot(a,c):return sum((x*y for x,y in zip(a,c)),zero)
def pick(forms,c,upper=False):return (max if upper else min)(forms,key=lambda f:dot(f,c))
def cap(target,lower,upper,c):return pick([pick([target,lower],c,True),upper],c)

def evaluate(c):
    A,B,C,D=c
    va=pick([add(e[0],e[2]),scale(add(e[1],e[3]),alpha),add(e[0],scale(e[3],alpha))],c)
    vd=pick([add(e[1],e[3]),scale(add(e[0],e[2]),alpha),add(e[3],scale(e[0],alpha))],c)
    wc=cap(scale(e[2],beta),pick([z,add(va,scale(e[0],-1))],c,True),pick([e[2],scale(e[3],alpha),va],c),c)
    wb=cap(scale(e[1],beta),pick([z,add(vd,scale(e[3],-1))],c,True),pick([e[1],scale(e[0],alpha),vd],c),c)
    W=[add(va,scale(wc,-1)),wb,wc,add(vd,scale(wb,-1))]
    w=[dot(row,c) for row in W];p=[x/y for x,y in zip(w,c)]
    assert all(zero<=w[j]<=c[j] for j in range(4))
    # Independent closed formula, not the branch selector implementation.
    expected=[min(A,alpha*B+max(zero,alpha*D-beta*C)),
              min(B,alpha*A,max(beta*B,alpha*(A+C)-D)),
              min(C,alpha*D,max(beta*C,alpha*(B+D)-A)),
              min(D,alpha*C+max(zero,alpha*A-beta*B))]
    assert w==expected
    prod=min(A+C,B+D,A+D)
    assert sum(w,zero)==dot(va,c)+dot(vd,c)
    assert sum(w,zero)<=(one+alpha)*prod
    J=[[W[j][v]/c[j]-(p[j]/c[j] if j==v else zero) for v in range(4)] for j in range(4)]
    singles=[p[v]+sum((c[j]*min(J[j][v],zero) for j in range(4)),zero) for v in range(4)]
    edges=[p[u]+p[v]+sum((c[j]*min(J[j][u]+J[j][v],zero) for j in range(4)),zero) for u,v in [(0,1),(0,3),(2,3)]]
    assert all(x>=zero for x in singles),(c,singles)
    assert all(x>=one for x in edges),(c,edges)
    return min(singles),min(edges),tuple(W)

if __name__=='__main__':
    vals=[F(1,7),F(1,2),F(1),F(2),F(7)]
    seen=set();minimum_single=None;minimum_edge=None;count=0
    for cs in product(vals,repeat=4):
        s,h,W=evaluate([Q2(c) for c in cs]);count+=1;seen.add(W)
        minimum_single=s if minimum_single is None else min(minimum_single,s)
        minimum_edge=h if minimum_edge is None else min(minimum_edge,h)
    report={'status':'PASS','arithmetic':'exact Q(sqrt(2)) using stdlib Fraction',
        'positive_profiles_checked':count,'selected_linear_use_matrices':len(seen),
        'minimum_coordinate_coefficient':str(minimum_single),
        'minimum_edge_coefficient':str(minimum_edge),
        'checks':['flow-use bounds','independent closed formulas','maximum-flow totals','funding bound','all holding-cube coordinate minima','all holding-cube edge minima'],
        'scope':'Finite diagnostic only. The global theorem is proved analytically in P4_PROTECTED_LEAF_OUT.txt; no finite replay substitutes for the all-profile argument.'}
    out=Path(__file__).with_suffix('.json');out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
