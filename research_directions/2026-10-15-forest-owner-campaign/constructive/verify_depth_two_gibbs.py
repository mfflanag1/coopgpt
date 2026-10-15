"""Exact cover-account and analytic-bound certificates for the Gibbs obstruction."""
from fractions import Fraction as Q
from itertools import product
from math import comb, factorial
import json

def require(ok, msg):
    if not ok:
        raise ValueError(msg)

def covers(d):
    yield (0,)+(1,)*d+(0,)*d
    for hs in product((0,1), repeat=d):
        if all(hs):
            continue
        yield (1,)+hs+tuple(1-t for t in hs)

def dots(c,bundles):
    return [sum((Q(x)*v for x,v in zip(c,b)),Q(0)) for b in bundles]

checks=0
for d in range(2,10):
    n=d+2;dim=2*d+1
    budget=[[Q(0)]*dim for _ in range(n)]
    for j in range(d):
        budget[0][1+j]=Q(1,d)
        budget[j+2][1+d+j]=Q(1)
    budget[1][0]=Q(1)
    negative=[[Q(0)]*dim for _ in range(n)]
    negative[0][1]=Q(1)
    negative[1][1+d]=Q(3,4)
    for i in range(2,n):
        negative[i][0]=Q(1)
    counts=[0]*(d+1)
    neg_leaf=0
    allcovers=list(covers(d))
    require(len(allcovers)==2**d,("cover count",d))
    require(min(sum(dots(c,budget)) for c in allcovers)==1,("budget T",d))
    require(min(sum(dots(c,negative)) for c in allcovers)==1,("negative T",d))
    for c in allcovers:
        rho=sum(min(v,Q(1)) for v in dots(c,budget))
        k=sum(c[1+d:])
        if c[0]:
            require(rho==2+Q(k*(d-1),d),("budget rho",d,k,rho))
            counts[k]+=1
        else:
            require(rho==1,("short rho",d))
        nr=sum(min(v,Q(1)) for v in dots(c,negative))
        if c[1+d]:
            require(nr==d+Q(3,4),("negative leaf rho",d,nr))
            neg_leaf+=1
        checks+=1
    require(counts==[0]+[comb(d,k) for k in range(1,d+1)],("binomial counts",d))
    require(neg_leaf==2**(d-1),("leaf cover count",d))

# Exact exponential-series bounds used by the universal proof.
sum5=sum((Q(2)**k/factorial(k) for k in range(6)),Q(0))
tail=Q(2)**6/factorial(6)/(1-Q(2,7))
require(sum5+tail==Q(1663,225)<8,"exp2 upper certificate")
require(9**19>=9*8**19,"uniform d>=19 threshold")
require(1+Q(7,2)+Q(7,2)**2/2>6,"exp(7/2)>6 certificate")
require(1+5+Q(25,2)>6,"exp5>6 finite deviation certificate")
require(1+2>2,"2exp(-2)<1 certificate")
print(json.dumps({"status":"PASS","exact_cover_account_checks":checks,
 "branches_tested":"2..9","universal_budget_lower":"d/36 for d>=19, lambda<=2",
 "finite_deviation":"lambda=3, leaf report 3/4 to2/3, anyd>=2",
 "scope":"finite account corroboration plus exact analytic-bound certificates; universal proof in DEPTH_TWO_GIBBS_OBSTRUCTION.txt"}))
