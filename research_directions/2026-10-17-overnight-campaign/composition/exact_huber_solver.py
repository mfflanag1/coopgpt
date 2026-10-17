#!/usr/bin/env python3
"""Exact unit-Huber prices via density min-cuts; polynomial bit complexity.

No floating point, no optimizer dependency. Rational capacities are integerized.
Every output carries original-graph KKT and primal/dual certificates.
"""
from collections import deque
from fractions import Fraction as Q
from math import gcd, lcm
from functools import reduce
from pathlib import Path
import argparse
import json
import time

def require(condition,message):
    if not condition:
        raise RuntimeError(message)

class ExactFlow:
    """Edmonds-Karp with integer or Fraction capacities and explicit residuals."""
    def __init__(self,n):
        self.adj=[[] for _ in range(n)]
        self.res={}
        self.original={}
    def add(self,u,v,capacity):
        require(capacity>=0,'negative flow capacity')
        require((u,v) not in self.res,'parallel/antiparallel original arc')
        self.adj[u].append(v);self.adj[v].append(u)
        self.res[u,v]=capacity;self.res[v,u]=0
        self.original[u,v]=capacity
    def solve(self,source,sink):
        total=0
        while True:
            parent={source:None};queue=deque([source])
            while queue and sink not in parent:
                u=queue.popleft()
                for v in self.adj[u]:
                    if v not in parent and self.res[u,v]>0:
                        parent[v]=u;queue.append(v)
            if sink not in parent:
                break
            path=[];v=sink
            while v!=source:
                u=parent[v];path.append((u,v));v=u
            change=min(self.res[e] for e in path)
            for u,v in path:
                self.res[u,v]-=change;self.res[v,u]+=change
            total+=change
        self.value=total
        return total
    def maximal_source_side(self,source,sink):
        # Complement of vertices that can reach sink; NOT source reachability.
        reaches_sink={sink};queue=deque([sink])
        while queue:
            v=queue.popleft()
            for u in self.adj[v]:
                if u not in reaches_sink and self.res[u,v]>0:
                    reaches_sink.add(u);queue.append(u)
        require(source not in reaches_sink,'flow not maximum')
        return set(range(len(self.adj)))-reaches_sink
    def used(self,u,v):
        return self.original.get((u,v),0)-self.res.get((u,v),0)

def _density_cut(vertices,edges,integer_capacities,theta):
    theta=Q(theta);a,b=theta.numerator,theta.denominator
    local={v:j for j,v in enumerate(vertices)};n=len(vertices)
    source,sink=2*n,2*n+1
    flow=ExactFlow(2*n+2)
    C=sum(integer_capacities[v] for v in vertices)
    infinite=(a+b)*C+1
    for v,j in local.items():
        flow.add(source,j,a*integer_capacities[v])
        flow.add(n+j,sink,b*integer_capacities[v])
    for u,v in edges:
        if u in local and v in local:
            flow.add(local[u],n+local[v],infinite)
            flow.add(local[v],n+local[u],infinite)
    optimum=flow.solve(source,sink)
    side=flow.maximal_source_side(source,sink)
    X={v for v,j in local.items() if j in side}
    return optimum-a*C,X

def solve_prices(capacities,edges):
    c=tuple(map(Q,capacities));n=len(c)
    edges=tuple(sorted(tuple(sorted(e)) for e in edges))
    require(all(x>=0 for x in c),'negative capacity')
    require(len(set(edges))==len(edges),'duplicate edges')
    require(all(0<=u<v<n for u,v in edges),'invalid simple graph edge')
    D=1
    for x in c:
        D=lcm(D,x.denominator)
    integers=[int(x*D) for x in c]
    common=reduce(gcd,integers,0)
    if common:
        integers=[x//common for x in integers]
    positive={v for v in range(n) if c[v]>0}
    p=[Q(1) if c[v]==0 else None for v in range(n)]
    active=set(positive);blocks=[];calls=0
    while active:
        current=tuple(sorted(active))
        current_edges=[(u,v) for u,v in edges if u in active and v in active]
        neighbors={v:set() for v in active}
        for u,v in current_edges:
            neighbors[u].add(v);neighbors[v].add(u)
        isolated={v for v in active if not neighbors[v]}
        if isolated:
            for v in isolated:p[v]=Q(0)
            blocks.append({'low':sorted(isolated),'high':[],'ratio':Q(0)})
            active-=isolated
            continue
        sign,_=_density_cut(current,current_edges,integers,Q(1));calls+=1
        if sign>=0:
            require(sign==0,'empty set should give nonpositive reduced cut')
            for v in active:p[v]=Q(1,2)
            blocks.append({'half':sorted(active)})
            break
        C=sum(integers[v] for v in active)
        lo,hi=Q(0),Q(1)
        rounds=(4*C*C).bit_length()+1
        for _ in range(rounds):
            mid=(lo+hi)/2
            sign,_=_density_cut(current,current_edges,integers,mid);calls+=1
            if sign<0:hi=mid
            else:lo=mid
        rho=((lo+hi)/2).limit_denominator(C)
        require(lo<=rho<=hi and 0<rho<1,'exact ratio reconstruction')
        sign,X=_density_cut(current,current_edges,integers,rho);calls+=1
        Y=set().union(*(neighbors[v] for v in X)) if X else set()
        require(sign==0 and X and not (X&Y),'critical independent density set')
        require(Q(sum(integers[v] for v in Y),sum(integers[v] for v in X))==rho,
                'exact density certificate')
        for v in X:p[v]=rho/2
        for v in Y:p[v]=1-rho/2
        blocks.append({'low':sorted(X),'high':sorted(Y),'ratio':rho})
        active-=X|Y
    require(all(x is not None for x in p),'unassigned resource price')
    require(all(p[u]+p[v]>=1 for u,v in edges),'original dual feasibility')
    return tuple(p),{'density_blocks':blocks,'maxflow_calls':calls,
                     'integer_capacity_sum':sum(integers),'integerized_capacity_bits':sum(integers).bit_length()}

def price(capacities,edges):
    return solve_prices(capacities,edges)[0]

def certificate(capacities,edges):
    c=tuple(map(Q,capacities));edges=tuple(map(tuple,edges));n=len(c)
    p,metadata=solve_prices(c,edges)
    degree=[x*min(2*q,Q(1)) for x,q in zip(c,p)]
    total=sum(degree);source,sink=2*n,2*n+1
    flow=ExactFlow(2*n+2)
    for v in range(n):
        flow.add(source,v,degree[v]);flow.add(n+v,sink,degree[v])
    for u,v in edges:
        if p[u]+p[v]==1:
            flow.add(u,n+v,total);flow.add(v,n+u,total)
    require(flow.solve(source,sink)==total,'KKT degree realization failed')
    lam=[Q(flow.used(u,n+v)+flow.used(v,n+u),2) for u,v in edges]
    cert={'capacities':c,'edges':edges,'p':p,'lambda':lam,**metadata}
    verify(cert)
    return cert

def verify(cert):
    c=tuple(map(Q,cert['capacities']));p=tuple(map(Q,cert['p']))
    edges=tuple(map(tuple,cert['edges']));lam=tuple(map(Q,cert['lambda']))
    require(len(c)==len(p) and len(edges)==len(lam),'certificate lengths')
    require(all(x>=0 for x in c) and all(0<=q<=1 for q in p),'domains')
    degree=[Q(0)]*len(c)
    for (u,v),x in zip(edges,lam):
        require(x>=0 and p[u]+p[v]>=1,'dual/primal nonnegativity')
        require(x==0 or p[u]+p[v]==1,'complementarity')
        degree[u]+=x;degree[v]+=x
    require(degree==[x*min(2*q,Q(1)) for x,q in zip(c,p)],'KKT stationarity')
    rounded=[Q(0) if q<Q(1,2) else Q(1) if q>Q(1,2) else Q(1,2) for q in p]
    require(all(rounded[u]+rounded[v]>=1 for u,v in edges),'rounded dual cover')
    require(sum(lam)==sum(x*r for x,r in zip(c,rounded)),'exact optimal production')
    require(sum(x*q for x,q in zip(c,p))<=Q(3,2)*sum(lam),'funding bound')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',type=Path)
    parser.add_argument('--verify',type=Path)
    args=parser.parse_args()
    if args.verify:
        packet=json.loads(args.verify.read_text())
        for cert in packet['certificates']:verify(cert)
        print(json.dumps({'status':'PASS','mode':'exact standalone certificate replay',
                          'certificate_count':len(packet['certificates'])},indent=2))
        return
    require(args.input is not None,'provide --input or --verify')
    data=json.loads(args.input.read_text())
    result=certificate(data['capacities'],data['edges'])
    print(json.dumps(result,default=str,indent=2))

if __name__=='__main__':main()
