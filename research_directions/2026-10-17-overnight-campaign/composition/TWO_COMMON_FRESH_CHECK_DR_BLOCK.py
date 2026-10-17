"""Exact polyhedral block-price checker. No floating quadrature or tolerances."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import random,json
R=random.Random(701043);root=Path(__file__).resolve().parent

def dot(a,b):return sum((x*y for x,y in zip(a,b)),Q(0))
def cdf(x):
    if x is None:return Q(1)
    return x/2 if x<=1 else 1-Q(1,2)/x

def rule(rank,C):
    P,*c=C;m=len(c)
    forms=[(P*rank[S],sum((c[j] for j in range(m) if not S>>j&1),Q(0)),S) for S in range(1<<m)]
    value=min(a+b for a,b,S in forms)
    if value==0:return value,[Q(0)]*(m+1)
    cuts={Q(0)}
    for (a,b,S),(aa,bb,SS) in combinations(forms,2):
        if a!=aa:
            x=(bb-b)/(a-aa)
            if x>0:cuts.add(x)
    cuts=sorted(cuts)+[None];prices=[Q(0)]*(m+1)
    for lo,hi in zip(cuts,cuts[1:]):
        mid=lo+1 if hi is None else (lo+hi)/2
        best=min(a*mid+b for a,b,S in forms)
        chosen=0
        for a,b,S in forms:
            if a*mid+b==best:chosen|=S
        assert P*rank[chosen]*mid+sum((c[j] for j in range(m) if not chosen>>j&1),Q(0))==best
        gradient=[rank[chosen]]+[Q(not chosen>>j&1) for j in range(m)]
        mass=cdf(hi)-cdf(lo)
        for j in range(m+1):prices[j]+=mass*gradient[j]
    for j in range(m+1):
        if not C[j]:prices[j]=Q(0)
    return value,prices

counts={'submodular_pairs':0,'funding_profiles':0,'mixed_owner_coordinate_comparisons':0,'coverage_bundles':0}
for tech in range(26):
    m=2+tech%3
    features=[R.randrange(1,1<<m) for _ in range(4)]
    weights=[Q(R.randrange(1,4),R.randrange(1,4)) for _ in features]
    # Public polymatroid: sum of a uniform rank and weighted coverage ranks.
    rank=[]
    for S in range(1<<m):
        rank.append(Q(min(2,S.bit_count()))+sum((w for f,w in zip(features,weights) if S&f),Q(0)))
    for A in range(1<<m):
        for B in range(1<<m):
            assert rank[A]+rank[B]>=rank[A&B]+rank[A|B]
            counts['submodular_pairs']+=1
    for trial in range(5):
        C=tuple(Q(R.randrange(0,7),R.randrange(1,4)) for _ in range(m+1))
        f,p=rule(rank,C)
        assert min(p)>=0 and dot(C,p)<=Q(3,2)*f
        counts['funding_profiles']+=1
        for j in range(m+1):
            d=Q(R.randrange(1,6),R.randrange(1,5));CC=list(C);CC[j]+=d
            ff,pp=rule(rank,CC)
            assert min(pp)>=0 and dot(CC,pp)<=Q(3,2)*ff
            # Exact worst coalition holding box; all coalition fractions are
            # covered, not just the generated pure-owner corners.
            worst_loss=sum((cap*max(Q(0),old-new) for cap,old,new in zip(C,p,pp)),Q(0))
            assert d*pp[j]>=worst_loss,(rank,C,j,d,p,pp,worst_loss)
            counts['mixed_owner_coordinate_comparisons']+=1
        for t in range(4):
            D=tuple(x*Q(R.randrange(0,5),4) for x in C)
            fd=min(D[0]*rank[S]+sum((D[j+1] for j in range(m) if not S>>j&1),Q(0)) for S in range(1<<m))
            assert dot(D,p)>=fd
            counts['coverage_bundles']+=1
# Binary minimum specializes exactly to the previously proved Huber prices.
for P in (Q(1,4),Q(1),Q(7)):
 for c in (Q(1,3),Q(1),Q(8)):
    f,p=rule([Q(0),Q(1)],(P,c))
    expected=[1-P/(2*c),P/(2*c)] if P<=c else [c/(2*P),1-c/(2*P)]
    assert p==expected
out={'status':'PASS',**counts,'binary_huber_specializations':9,'integration':'Exact ratio t/s CDF: x/2 below1,1-1/(2x) above1.','scope':'These finite tests supplement the universal analytic proof; they do not prove the compactness extension or historical novelty.'}
(root/'TWO_COMMON_FRESH_DR_BLOCK_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
