#!/usr/bin/env python3
"""Exact identities supporting the analytic all-functions wrapper obstruction."""
from fractions import Fraction as Q
import json

def require(test, message):
    if not test:
        raise RuntimeError(message)

identities = []
for v, b, delta in [(Q(1), Q(1), Q(1,3)), (Q(2), Q(3), Q(2,5)), (Q(7,3), Q(2,7), Q(1,19))]:
    lo = v + (b-delta)*(1-(b-delta)/(2*b))
    hi = v + b/2
    require(lo == hi-delta*delta/(2*b), 'quadratic flattening identity')
    identities.append({'v':v, 'b':b, 'delta':delta, 'low':lo, 'high':hi})
partitions=[]
for N in [4,8,16,32,64]:
    s,t=Q(1),Q(2); step=(t-s)/N
    factors=[1-4*step*step/(3*(s+k*step)**2) for k in range(1,N+1)]
    product=Q(1)
    for f in factors: product*=f
    bound=1-4*N*step*step/(3*s*s)
    require(all(0<=f<=1 for f in factors) and product>=bound,'finite product bound')
    partitions.append({'N':N,'product':product,'lower_bound':bound})
# Vertex order P,a,b,c,d; activity order (P,a,b),(P,c,d).
edges=[(0,1,2),(0,3,4)]
profiles=[([1,1,1,1,1],[Q(1,2),Q(1,4),Q(1,4),Q(1,4),Q(1,4)],[Q(1,2),Q(1,2)]),
          ([1,2,1,1,1],[Q(4,7),Q(1,7),Q(2,7),Q(3,14),Q(3,14)],[Q(4,7),Q(3,7)])]
pays=[]; loads=[]
for caps,prices,lam in profiles:
    degree=[sum(lam[e] for e,edge in enumerate(edges) if v in edge) for v in range(5)]
    require(all(sum(prices[v] for v in edge)==1 for edge in edges),'dual covers tight')
    require(degree==[c*min(2*p,1) for c,p in zip(caps,prices)],'Huber KKT')
    pays.append(sum(caps[v]*prices[v] for v in [1,3,4]))
    # Unit production max is P=1. Strict quadratic objective on x1+x2=1.
    x1=Q(2)/(Q(1,caps[1])+1+2); x2=1-x1
    require(x1/caps[1]+x1==2*x2,'optimal-flow objective derivative')
    require(x1>=0 and x2>=0 and x1<=min(caps[1],caps[2]) and x2<=min(caps[3],caps[4]),'optimal flow feasible')
    loads.append(x1+2*x2)
require(pays[0]-pays[1]==Q(1,28),'Huber strict gain')
require(loads[0]-loads[1]==Q(1,14),'optimal utilization strict gain')
print(json.dumps({'status':'PASS','arithmetic':'exact Fraction identities; finite examples are corroboration of the separate analytic proof',
 'flattening_identities':identities,'partition_product_checks':partitions,'Huber_payments':pays,'Huber_gain':pays[0]-pays[1],
 'optimal_utilization_payments':loads,'optimal_utilization_gain':loads[0]-loads[1]},default=str,indent=2))
