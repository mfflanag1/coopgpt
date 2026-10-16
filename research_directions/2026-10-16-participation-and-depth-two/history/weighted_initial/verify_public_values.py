"""Exact corroboration of fixed-public-value extension, standard library only."""
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
import json
from verify_continuous_rule import rule,require
from flow_oracle import value

def weighted_rule(b,values,theta):
    m=len(values);order=sorted(range(m),key=lambda i:(-values[i],i));y=[Q(0)]*(m+2)
    active=set()
    for k,i in enumerate(order):
        active.add(i);weight=values[i]-(values[order[k+1]] if k+1<m else 0)
        retained=(b[0],)+tuple(b[1+j] if j in active else Q(0) for j in range(m))+tuple(b[1+m+j] if j in active else Q(0) for j in range(m))
        component,_=rule(retained,m,theta)
        for j in range(m+2):y[j]+=weight*component[j]
    return tuple(y)

def check(values):
    values=tuple(map(Q,values));m=len(values);n=m+2;d=2*m+1
    owners=[1]+list(range(2,n))+[0]*m
    edges=[e for j in range(1,m+1) for e in [(0,j,values[j-1]),(j,m+j,values[j-1])]]
    profiles=list(product(map(Q,range(3)),repeat=d));allmask=(1<<n)-1
    @lru_cache(None)
    def val(cap):return value(cap,edges)
    for theta in [Q(1,2),Q(1)]:
        pay={};coals=transitions=0
        for b in profiles:
            y=weighted_rule(b,values,theta);pay[b]=y;T=val(b)
            absentA=tuple(b[j] if owners[j]!=0 else Q(0) for j in range(d))
            require(y[0]==theta*(T-val(absentA)),'weighted marginal floor')
            require(sum(y)<=(1+theta/4)*T,'weighted budget')
            require(all(z>=0 for z in y),'weighted nonnegativity')
            for mask in range(1,1<<n):
                cap=tuple(b[j] if mask&(1<<owners[j]) else Q(0) for j in range(d))
                require(sum(y[i] for i in range(n) if mask&(1<<i))>=val(cap),'weighted coverage');coals+=1
        for b,y in pay.items():
            for j in range(d):
                if b[j]<2:
                    nxt=list(b);nxt[j]+=1
                    require(y[owners[j]]<=pay[tuple(nxt)][owners[j]],'weighted own monotonicity');transitions+=1
        print(json.dumps({'values':list(map(str,values)),'theta':str(theta),'profiles':len(profiles),'coalitions':coals,'own_adjacent_increases':transitions,'status':'PASS','oracle':'independent exact weighted max-profit flow'}),flush=True)

if __name__=='__main__':
    for values in [(3,1),(0,2),(0,0),(3,1,2),(2,2,0)]:check(values)
