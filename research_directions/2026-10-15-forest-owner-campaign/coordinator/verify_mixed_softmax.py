"""Certified rational-enclosure checks for mixed-owner three/four-input rules.
Expressions are rational sums of exp(-rational); equality cancels symbolically.
No floating-point tolerances are accepted. Tests supplement analytic proofs.
"""
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
from math import factorial
import json,random

def need(x,msg):
    if not x:raise RuntimeError(msg)

@lru_cache(None)
def exp_bounds(u,k):
    need(u>=0 and u<k+2,'Taylor input')
    if not u:return Q(1),Q(1)
    term=total=Q(1)
    for j in range(1,k+1):term*=u/j;total+=term
    nxt=term*u/(k+1);tail=nxt/(1-u/(k+2))
    return 1/(total+tail),1/total

class Poly:
    def __init__(self,terms=None):
        self.t={}
        for u,c in (terms or []):
            u,c=Q(u),Q(c);self.t[u]=self.t.get(u,Q(0))+c
        self.t={u:c for u,c in self.t.items() if c}
    def add(self,other,sign=1):return Poly(list(self.t.items())+[(u,sign*c) for u,c in other.t.items()])
    def scale(self,a):return Poly([(u,a*c) for u,c in self.t.items()])
    def mul(self,other):return Poly([(u+v,c*d) for u,c in self.t.items() for v,d in other.t.items()])
    def nonnegative(self,context):
        if all(c>=0 for c in self.t.values()):return
        for k in (40,80,160):
            low=high=Q(0)
            for u,c in self.t.items():
                a,b=exp_bounds(u,k);low+=c*(a if c>0 else b);high+=c*(b if c>0 else a)
            if low>=0:return
            if high<0:raise RuntimeError(('certified negative',context,str(high)))
        raise RuntimeError(('unresolved interval',context))

def payment(b,rate):
    n=len(b);k=len(b[0]);T=min(sum(r[j] for r in b) for j in range(k))
    if not T:return tuple(Poly() for _ in b),Poly([(0,1)]),T
    d=tuple(tuple(min(r[j],T) for j in range(k)) for r in b)
    exponents=[rate*(sum(r[j] for r in d)/T-1) for j in range(k)]
    W=Poly([(u,1) for u in exponents])
    return tuple(Poly([(exponents[j],r[j]) for j in range(k)]) for r in d),W,T

def check_profile(b,rate,bound,counts,monotone=True):
    nums,W,T=payment(b,rate);n=len(b);k=len(b[0]);total=Poly()
    for num in nums:num.nonnegative('individual');total=total.add(num)
    W.scale(bound*T).add(total,-1).nonnegative('budget');counts['budgets']+=1
    for mask in range(1<<n):
        worth=min(sum(b[i][j] for i in range(n) if mask>>i&1) for j in range(k))
        z=Poly()
        for i in range(n):
            if mask>>i&1:z=z.add(nums[i])
        z.add(W.scale(worth),-1).nonnegative('coalition');counts['coalitions']+=1
    if monotone:
        for i in range(n):
            for j in range(k):
                bigger=[list(r) for r in b];bigger[i][j]+=Q(1,2)
                new,WW,_=payment(tuple(map(tuple,bigger)),rate)
                new[i].mul(W).add(nums[i].mul(WW),-1).nonnegative(('own increase',i,j,b))
                counts['own_increases']+=1
    counts['profiles']+=1

def main():
    counts=dict(profiles=0,coalitions=0,own_increases=0,budgets=0)
    cases=((3,Q(1),Q(183,125)),(4,Q(9,10),Q(1671,1000)))
    for k,rate,bound in cases:
        b=rate*(bound-1)
        lower=sum(((1+b)**j/Q(factorial(j)) for j in range(20)),Q(0))
        need(b*lower>k-1,'rational upper bound on Lambert root')
        for flat in product((Q(0),Q(1)),repeat=3*k):
            rows=tuple(tuple(flat[k*i:k*i+k]) for i in range(3))
            check_profile(rows,rate,bound,counts)
    rng=random.Random(20261015)
    for k,rate,bound in cases:
        for n in range(2,9):
            for z in range(8):
                b=tuple(tuple(Q(rng.randrange(7),rng.randrange(1,4)) for j in range(k)) for i in range(n))
                check_profile(b,rate,bound,counts)
    print(json.dumps(dict(status='PASS',arithmetic='exact exponential polynomials and rational Taylor enclosures',counts=counts,limits='Finite tests supplement the all-real proofs. Rational rate9/10 checked for4inputs; sharp irrational rate is analytic only.'),indent=2))
if __name__=='__main__':main()
