from fractions import Fraction as Q
from itertools import product

if not __debug__:raise RuntimeError('Assertions must remain enabled')

def waterfill(p,G):
    if not G:return tuple(p)
    T=sum(p)+G
    for k in range(1,len(p)+1):
        ordered=sorted(p)
        t=(T-sum(ordered[k:]))/k
        if t>=ordered[k-1] and (k==len(p) or t<=ordered[k]):
            x=tuple(max(a,t) for a in p)
            assert sum(x)==T
            return x
    raise AssertionError('No water level')

profiles=pairs=facet_rows=facet_slacks=0
for n in range(2,6):
    for p in product((Q(0),Q(1,2),Q(1)),repeat=n):
        for G in (Q(0),Q(1,4),Q(1)):
            x=waterfill(p,G)
            assert all(xi>=pi for xi,pi in zip(x,p))
            assert sum(x)==sum(p)+G
            profiles+=1
            for i in range(n):
                for delta in (Q(1,4),Q(1)):
                    raised=list(p);raised[i]+=delta
                    y=waterfill(raised,G)
                    assert y[i]>=x[i]
                    z=waterfill(p,G+delta)
                    assert z[i]>=x[i]
                    pairs+=2

for m in range(2,11):
    delta=Q(1,4*m)
    for S in range(1,1<<m):
        s=S.bit_count()
        x=[Q(1,m)-delta/s if S>>j&1 else Q(1,m)+delta for j in range(m)]
        assert all(a>0 for a in x)
        for U in range(1,1<<m):
            lhs=delta+sum(x[j] for j in range(m) if U>>j&1)
            rhs=Q(U.bit_count(),m)
            formula=delta*(1-Q((U&S).bit_count(),s))+delta*(U&~S).bit_count()
            assert lhs-rhs==formula
            assert (formula==0)==(U==S)
            assert formula>=0
            facet_slacks+=1
        facet_rows+=1

print({'status':'PASS','waterfill_profiles':profiles,'own_comparable_checks':pairs,
       'indispensable_facet_rows':facet_rows,'exact_facet_slacks':facet_slacks,
       'largest_star_leaves':10})
