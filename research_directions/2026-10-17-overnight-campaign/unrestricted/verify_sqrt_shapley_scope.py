"""Exact scope obstructions; no verification of the live production conjecture."""
from fractions import Fraction as Q
from math import comb
if not __debug__:
    raise RuntimeError('Run with assertions enabled, without -O.')
checks=0
for k,m,case in [(4,5,1),(6,80,2)]:
    def v(a,b):
        if case==1:return Q(int(a==k or (a>=1 and b>=3)))
        if b==m:return Q(1,2)+Q(a,2*k)
        if a==k:return Q(1,2)
        if a and b>=m//2+1:return min(Q(1,2),Q(1,2*k)+Q(b,2*m))
        return Q(0)
    assert v(0,0)==0 and v(k,m)==1
    for a in range(k+1):
        for b in range(m+1):
            assert v(a,b)>=0
            if a<k:assert v(a+1,b)>=v(a,b)
            if b<m:assert v(a,b+1)>=v(a,b)
            if case==2:assert v(a,b)<=Q(a,2*k)+Q(b,2*m)
            for aa in range(k+1-a):
                for bb in range(m+1-b):
                    assert v(a,b)+v(aa,bb)<=v(a+aa,b+bb)
                    checks+=1
    phi=sum(Q(k*comb(k-1,a)*comb(m,b),(k+m)*comb(k+m-1,a+b))*(v(a+1,b)-v(a,b)) for a in range(k) for b in range(m+1))
    assert k*phi<v(k,0)**2
    if case==1:assert phi==Q(5,21)
    if case==2:assert phi==Q(1115822639,28209304620)
    print({'case':case,'n':k+m,'shapley_coalition':str(phi),'squared_coverage_ratio':str(k*phi/v(k,0)**2)})
print({'exact_superadditive_checks':checks,'status':'PASS'})
