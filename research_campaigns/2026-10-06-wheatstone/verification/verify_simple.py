"""Exact checks of the simple-DAG extension; standard library only."""
from fractions import Fraction as Q
from math import comb,factorial
from pathlib import Path
from collections import deque
import importlib.util
import argparse,json,random

def require(ok,msg):
    if not ok:raise ValueError(msg)

def maxflow(n,edges,c,s,t):
    residual=[[0]*n for _ in range(n)]
    for (u,v),d in zip(edges,c):residual[u][v]+=d
    value=0
    while True:
        parent=[-1]*n;parent[s]=s;queue=deque([s])
        while queue and parent[t]<0:
            u=queue.popleft()
            for v in range(n):
                if residual[u][v]>0 and parent[v]<0:
                    parent[v]=u;queue.append(v)
        if parent[t]<0:return value
        v=t;amount=None
        while v!=s:
            u=parent[v];amount=residual[u][v] if amount is None else min(amount,residual[u][v]);v=u
        v=t
        while v!=s:
            u=parent[v];residual[u][v]-=amount;residual[v][u]+=amount;v=u
        value+=amount

def moment_ideal(x):
    eps=Q(1,20);b=x+eps
    ms=[Q(1)]+[eps**j/Q(j+1)-Q(j)*eps**(j+1)/Q((j+1)*(j+2))/b for j in range(1,7)]
    g=Q(5,72)-ms[1]/3+ms[2]/2-2*ms[4]/3+8*ms[5]/15-4*ms[6]/45
    reflected=sum(Q(comb(6,j))*(-1)**j*(1-x)**(6-j)*ms[j] for j in range(7))
    return g-Q(4,45)*reflected

def run(repo):
    p=repo/'research_campaigns/2026-10-06-series-parallel/verification/verify.py'
    spec=importlib.util.spec_from_file_location('cdf',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    rp=m.minimum(m.uniform(Q(1,2)),m.uniform(Q(1,2)));r=m.convolution(rp,rp)
    ideals=[]
    for x in (Q(9,10),Q(19,20)):
        a=m.minimum(m.uniform(Q(1,20)),m.uniform(x+Q(1,20)))
        pa=m.convolution(m.uniform(Q(1)),a)
        cdf_value=m.expectation(m.minimum(r,m.convolution(pa,m.atom(x))),Q(1))-m.expectation(m.minimum(r,pa),Q(1))
        require(cdf_value==moment_ideal(x),'simple ideal moment/CDF mismatch')
        ideals.append(cdf_value)
    drop=ideals[0]-ideals[1]
    require(drop==Q(1290353,191520000000),'simple ideal drop')
    error=Q(20,9)**14/Q(factorial(14));delta=drop-error
    require(delta==Q(700533736635095043154291,118415105665157830969440000000),'simple certificate')
    require(delta>0,'actual payment decrease not certified')

    k=14;n=k+7;edges=[(0,1),(0,2),(2,3),(1,2),(0,3)]
    for j in range(k):edges.extend([(1,5+j),(5+j,3)])
    for a in (5+k,6+k):edges.extend([(3,a),(a,4)])
    require(len(edges)==2*k+9 and len(set(edges))==len(edges),'simple graph owner count')
    # Explicit topological order certifies acyclicity without assuming vertex IDs.
    order=[0,1,2]+list(range(5,5+k))+[3,5+k,6+k,4]
    rank={v:i for i,v in enumerate(order)}
    require(len(rank)==n and all(rank[u]<rank[v] for u,v in edges),'acyclic graph')
    low=(18,1,40,40,40)+(40,)*(2*k)+(10,)*4;high=(19,)+low[1:]
    require([i for i in range(len(low)) if low[i]!=high[i]]==[0],'fixed-owner report pair')
    rng=random.Random(190211);comparisons=0
    for c in (low,high):
        ds=(c[0],1,c[0]+1,c[0],20)+(c[0],)*(2*k)+(10,)*4
        require(maxflow(n,edges,c,0,4)==20,'simple grand flow')
        for i,(u,v) in enumerate(edges):
            limits=[c[i]]
            if u!=0:limits.append(maxflow(n,edges,c,0,u))
            if v!=4:limits.append(maxflow(n,edges,c,v,4))
            require(min(limits)==ds[i],'simple effective capacity')
        for _ in range(256):
            random_c=[d*rng.randrange(17) for d in ds]
            random_c[0]=16*ds[0]
            f1=maxflow(n,edges,random_c,0,4)
            random_c[0]=0
            f0=maxflow(n,edges,random_c,0,4)
            y,w,h,p=random_c[1:5]
            z=sum(min(random_c[5+2*j],random_c[6+2*j]) for j in range(k))
            r=sum(min(random_c[5+2*k+2*j],random_c[6+2*k+2*j]) for j in range(2))
            a=min(y,w)
            q=min(16*ds[0],max(0,min(z+min(h,max(0,w-y)),r-p-a)))
            ideal=min(16*ds[0],max(0,r-p-a))
            require(f1-f0==q,'simple conditional identity versus exact maxflow')
            require(0<=ideal-q<=320*(z<320),'ideal comparison bound')
            comparisons+=1
    return {'status':'passed','arithmetic':'exact Fraction/integer, explicit exceptions',
            'vertices':n,'owners':len(edges),'effective_cap_checks':2*len(edges),
            'conditional_identity_checks':comparisons,
            'ideal_low':str(ideals[0]),'ideal_high':str(ideals[1]),'ideal_drop':str(drop),
            'error_upper_bound_k14':str(error),'actual_payment_drop_lower_bound':str(delta),
            'scope':'Conventional proof covers all k>=14; finite checks are support, not extrapolation.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path);args=ap.parse_args()
    root=args.repo if args.repo else Path(__file__).resolve().parents[3]
    print(json.dumps(run(root),indent=2))
