from fractions import Fraction as Q
from itertools import product
from functools import lru_cache
from flow_oracle import value
import json

def check(m):
    edges=[edge for j in range(1,m+1) for edge in [(0,j,1),(j,m+j,1)]]
    n=m+2;d=2*m+1
    owner=[1]+list(range(2,m+2))+[0]*m
    profiles=list(product(range(3),repeat=d));pay={};coalitions=transitions=0
    @lru_cache(None)
    def val(cap):return value(tuple(map(Q,cap)),edges)
    def need(t,msg):
        if not t:raise RuntimeError((m,msg))
    for b in profiles:
        ls=[min(b[j],b[m+j]) for j in range(1,m+1)]
        R=min(b[0],sum(b[j]-ls[j-1] for j in range(1,m+1)))
        y=tuple(map(Q,[0,R]+ls));pay[b]=y
        need(sum(y)==val(b),'efficiency')
        for mask in range(1,1<<n):
            cap=tuple(b[j] if mask>>owner[j]&1 else 0 for j in range(d))
            need(sum(y[i] for i in range(n) if mask>>i&1)>=val(cap),'coverage');coalitions+=1
    for b,y in pay.items():
        for j in range(d):
            if b[j]<2:
                q=list(b);q[j]+=1
                need(y[owner[j]]<=pay[tuple(q)][owner[j]],'own coordinate monotonicity');transitions+=1
    return {'m':m,'owners':n,'resources':d,'profiles':len(profiles),'coalitions':coalitions,'adjacent_own_coordinate_increases':transitions,'status':'PASS','oracle':'independent exact Fraction max-profit flow','scope':'finite corroboration of written arbitrary-m all-real theorem'}
print(json.dumps({'checks':[check(m) for m in [2,3]]},indent=2))
