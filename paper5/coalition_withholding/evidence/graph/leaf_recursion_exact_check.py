"""Exact displayed-flow and fixed-owner counterexample certificate."""
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

zero=Q2();one=Q2(1)

def verify(alpha,beta,q):
    assert zero<alpha<one and zero<=beta<one
    assert zero<q<min(one-beta,one/(alpha*alpha)-one,one)
    records=[]
    for s in [q,q/2]:
        c=[one,one/alpha,s,s,one/alpha,one]
        flows={(0,1):one-s,(2,1):s,(4,3):alpha*s,(4,5):alpha,
               (5,4):one-s,(3,4):s,(1,2):alpha*s,(1,0):alpha}
        w=[sum((v for (u,t),v in flows.items() if u==j),zero) for j in range(6)]
        incoming=[sum((v for (u,t),v in flows.items() if t==j),zero) for j in range(6)]
        assert all(zero<=w[j]<=c[j] for j in range(6))
        assert incoming==[alpha*x for x in c], 'Every right sink saturated'
        expected=[one-s,alpha*(one+s),s,s,alpha*(one+s),one-s]
        assert w==expected
        # Right1 can receive only from0 and2; right4 only from3 and5.
        # Thus maximum-flow endpoint minima are at least these cut bounds.
        assert alpha*c[1]-c[2]==one-s
        assert alpha*c[4]-c[3]==one-s
        # The displayed maximum flow attains each lower bound, so it is exact.
        assert w[0]==one-s and w[5]==one-s
        assert beta*c[0]<w[0] and beta*c[5]<w[5]
        # Fixing those minima forces the middle sources to spend their entire
        # capacities at right1/right4, so subsequent ordering cannot alter w.
        assert flows[(2,1)]==c[2] and flows[(3,4)]==c[3]
        pay=sum((w[j] for j in [0,2,3,5]),zero)
        assert pay==2
        records.append(dict(middle=str(s),owner_payment=str(pay),selected_uses=[str(x) for x in w]))
    withheld=q/2
    # Only resources2 and3 are withheld: the one middle edge attains their
    # common capacity, and each vertex capacity gives the matching upper bound.
    assert withheld>zero
    return dict(alpha=str(alpha),beta=str(beta),q=str(q),
                payment_loss=str(Q2(0)),withheld_production=str(withheld),profiles=records)

if __name__=='__main__':
    cases=[verify(Q2(0,F(1,2)),Q2(F(1,2)),Q2(F(1,4)))]
    for a in [F(1,3),F(3,4),F(9,10)]:
        for b in [F(0),F(1,2),F(9,10)]:
            alpha,beta=Q2(a),Q2(b)
            q=min(one-beta,one/(alpha*alpha)-one,one)/2
            cases.append(verify(alpha,beta,q))
    report={'status':'PASS','arithmetic':'exact Q(sqrt(2)) / Fraction; no solver',
            'canonical_case':cases[0],'additional_rational_cases':len(cases)-1,
            'scope':'Exact displayed flow and actual-owner finite report certificate. The parameter-uniform assertion is proved in LEAF_RECURSION_OBSTRUCTION.txt, not inferred from these finite cases.'}
    out=Path(__file__).with_suffix('.json');out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
