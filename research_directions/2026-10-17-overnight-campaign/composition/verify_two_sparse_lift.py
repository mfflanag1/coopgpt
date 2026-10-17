#!/usr/bin/env python3
"""Exact all-rational finite regressions for the all-real bin-lift proof.

Independent dual vertex enumeration vs exact maxflow value; explicit primal
embedding and binary cover certificates, with unary residualization replay.
No scipy, no floating point, and no checks disabled by Python optimization.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import importlib.util, random, json
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('huber',HERE/'exact_huber_solver.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
def check(c,m):
    if not c: raise RuntimeError(m)
def linear_solve(A,b):
    n=len(b);m=[[Q(a) for a in A[i]]+[Q(b[i])] for i in range(n)]
    for j in range(n):
        k=next((k for k in range(j,n) if m[k][j]),None)
        if k is None: return None
        m[j],m[k]=m[k],m[j];d=m[j][j];m[j]=[x/d for x in m[j]]
        for k in range(n):
            if k!=j and m[k][j]:
                d=m[k][j];m[k]=[x-d*y for x,y in zip(m[k],m[j])]
    return tuple(row[-1] for row in m)
def bounded_vertices(n,activities,floors=None):
    floors=[Q(0)]*n if floors is None else list(map(Q,floors))
    M=list(floors)
    for u,v,a,b,w in activities:
        M[u]=max(M[u],w/a);M[v]=max(M[v],w/b)
    rows=[];rhs=[]
    for v in range(n):
        row=[Q(0)]*n;row[v]=1;rows.append(row);rhs.append(floors[v])
        row=[Q(0)]*n;row[v]=-1;rows.append(row);rhs.append(-M[v])
    for u,v,a,b,w in activities:
        row=[Q(0)]*n;row[u]=a;row[v]=b;rows.append(row);rhs.append(w)
    vertices=set()
    for ix in combinations(range(len(rows)),n):
        p=linear_solve([rows[k] for k in ix],[rhs[k] for k in ix])
        if p is not None and all(sum(a*b for a,b in zip(row,p))>=d for row,d in zip(rows,rhs)):
            vertices.add(p)
    check(vertices,'empty bounded dual');return M,vertices

def make_lift(n,activities,grids):
    bins=[];by_resource=[[] for _ in range(n)]
    for v,g in enumerate(grids):
        for lo,hi in zip(g,g[1:]):
            check(hi>lo,'grid ordering');by_resource[v].append(len(bins));bins.append((v,lo,hi))
    edges=set()
    for u,v,a,b,w in activities:
        for i in by_resource[u]:
            for j in by_resource[v]:
                if a*bins[i][1]+b*bins[j][1]<w:edges.add(tuple(sorted((i,j))))
    return bins,sorted(edges),by_resource

def graph_value(cap,edges):
    n=len(cap);s,t=2*n,2*n+1;f=h.ExactFlow(2*n+2);infty=sum(cap)+1
    for i,c in enumerate(cap):f.add(s,i,c);f.add(n+i,t,c)
    for u,v in edges:f.add(u,n+v,infty);f.add(v,n+u,infty)
    total=f.solve(s,t);lam=[(f.used(u,n+v)+f.used(v,n+u))/2 for u,v in edges]
    degree=[Q(0)]*n
    for (u,v),x in zip(edges,lam):degree[u]+=x;degree[v]+=x
    check(all(x<=c for x,c in zip(degree,cap)),'lift primal capacity')
    check(sum(lam)==total/2,'double-cover symmetrization')
    return total/2

def primal_embedding(n,activities,bins,edges,by_resource,x,c):
    index={e:k for k,e in enumerate(edges)};flow=[Q(0)]*len(edges)
    for e,(u,v,a,b,w) in enumerate(activities):
        cuts={Q(0),w}
        for j in by_resource[u]:
            for point in bins[j][1:]:
                z=a*point
                if 0<=z<=w:cuts.add(z)
        for j in by_resource[v]:
            for point in bins[j][1:]:
                z=w-b*point
                if 0<=z<=w:cuts.add(z)
        cuts=sorted(cuts)
        for lo,hi in zip(cuts,cuts[1:]):
            mid=(lo+hi)/2;s=mid/a;t=(w-mid)/b
            i=next(k for k in by_resource[u] if bins[k][1]<s<bins[k][2])
            j=next(k for k in by_resource[v] if bins[k][1]<t<bins[k][2])
            key=tuple(sorted((i,j)));check(key in index,'primal uses absent edge')
            flow[index[key]]+=x[e]*(hi-lo)
    degree=[Q(0)]*len(bins)
    for (u,v),f in zip(edges,flow):degree[u]+=f;degree[v]+=f
    check(all(z<=(hi-lo)*c[v] for z,(v,lo,hi) in zip(degree,bins)),'bin load')
    check(sum(flow)==sum(x[e]*a[-1] for e,a in enumerate(activities)),'embedded objective')

def main():
    cases=[
      ('inconsistent_triangle',3,[(0,1,2,1,1),(1,2,2,1,1),(2,0,2,1,1)]),
      ('asymmetric_triangle',3,[(0,1,2,1,1),(1,2,3,1,2),(2,0,5,1,4)]),
      ('parallel_activities',2,[(0,1,1,3,2),(0,1,2,1,3),(0,1,5,2,5)]),
      ('heterogeneous_K4',4,[(0,1,1,2,2),(0,2,3,1,3),(0,3,2,5,1),(1,2,4,3,5),(1,3,1,7,4),(2,3,5,2,7)]),
      ('inconsistent_four_cycle',4,[(0,1,2,3,7),(1,2,5,1,2),(2,3,3,2,4),(3,0,1,7,3)]),
      ('weighted_C6',6,[(0,1,1,1,2),(1,2,1,1,1),(2,3,1,1,3),(3,4,1,1,2),(4,5,1,1,1),(5,0,1,1,4)]),
      ('isolated_and_fractional',4,[(0,1,Q(2,3),Q(7,5),Q(11,13)),(1,2,Q(5,7),Q(4,3),Q(9,11))]),
    ]
    rng=random.Random(17100533);out=[];profiles=0;embeddings=0;coalitionchecks=0;transitions=0
    for label,n,raw in cases:
        acts=[(u,v,Q(a),Q(b),Q(w)) for u,v,a,b,w in raw]
        M,vertices=bounded_vertices(n,acts)
        grids=[sorted({Q(0),M[v],*(p[v] for p in vertices)}) for v in range(n)]
        bins,edges,by=make_lift(n,acts,grids)
        for trial in range(8):
            owners=[[Q(rng.randrange(5),rng.randrange(1,4)) for _ in range(n)] for _ in range(3)]
            for mask in range(8):
                c=[sum(owners[i][v] for i in range(3) if mask>>i&1) for v in range(n)]
                p=min(vertices,key=lambda p:sum(x*y for x,y in zip(c,p)))
                target=sum(x*y for x,y in zip(c,p));cap=[(hi-lo)*c[v] for v,lo,hi in bins]
                actual=graph_value(cap,edges)
                cover=[int(lo<p[v]) for v,lo,hi in bins]
                check(all(cover[u]+cover[v]>=1 for u,v in edges),'binary lift cover')
                check(sum(c*q for c,q in zip(cap,cover))==target,'binary lift cost')
                check(actual==target,f'identity {label} trial{trial} mask{mask}')
                profiles+=1
            x=[Q(rng.randrange(5),rng.randrange(1,4)) for _ in acts];c=[Q(rng.randrange(3)) for _ in range(n)]
            for (u,v,a,b,w),z in zip(acts,x):c[u]+=a*z;c[v]+=b*z
            primal_embedding(n,acts,bins,edges,by,x,c);embeddings+=1
        # One complete mixed-owner payment replay per technology plus a joint increase.
        owners=[[Q(rng.randrange(4),rng.randrange(1,4)) for _ in range(n)] for _ in range(3)]
        c=[sum(o[v] for o in owners) for v in range(n)];cap=[(hi-lo)*c[v] for v,lo,hi in bins]
        price=h.price(cap,edges);pay=[sum((hi-lo)*o[v]*p for (v,lo,hi),p in zip(bins,price)) for o in owners]
        F=min(sum(a*b for a,b in zip(c,p)) for p in vertices)
        check(sum(pay)<=Q(3,2)*F,'3/2 funding')
        for mask in range(8):
            cs=[sum(owners[i][v] for i in range(3) if mask>>i&1) for v in range(n)]
            Fs=min(sum(a*b for a,b in zip(cs,p)) for p in vertices)
            check(sum(pay[i] for i in range(3) if mask>>i&1)>=Fs,'coverage');coalitionchecks+=1
        old=pay[0]+pay[2]
        for i in (0,2):
            for v in range(n):owners[i][v]+=Q(rng.randrange(4),rng.randrange(1,4))
        c=[sum(o[v] for o in owners) for v in range(n)];cap=[(hi-lo)*c[v] for v,lo,hi in bins]
        price=h.price(cap,edges)
        new=sum((hi-lo)*(owners[0][v]+owners[2][v])*p for (v,lo,hi),p in zip(bins,price))
        check(new>=old,'coalition report increase');transitions+=1
        out.append({'case':label,'dual_vertices':len(vertices),'lift_vertices':len(bins),'lift_edges':len(edges),'coalition_profiles':64,'primal_embeddings':8})
    # Unary residualization: enumerate original bounded dual directly with unary floors.
    # Binary coefficients below, gamma=(2,1/2,0); one binary activity disappears.
    n=3;gamma=[Q(2),Q(1,2),Q(0)]
    original=[(0,1,Q(1),Q(2),Q(2)),(1,2,Q(3),Q(1),Q(4)),(0,2,Q(1),Q(1),Q(5))]
    residual=[(u,v,a,b,w-a*gamma[u]-b*gamma[v]) for u,v,a,b,w in original if w>a*gamma[u]+b*gamma[v]]
    M,d=bounded_vertices(n,residual);grids=[sorted({Q(0),M[v],*(p[v] for p in d)}) for v in range(n)]
    bins,edges,by=make_lift(n,residual,grids)
    # Original dual polytope represented by shifted residual vertices; additionally
    # verify every shifted vertex satisfies all original unary and binary constraints.
    for p in d:
        orig=[p[v]+gamma[v] for v in range(n)]
        check(all(orig[v]>=gamma[v] for v in range(n)),'unary dual floor')
        check(all(a*orig[u]+b*orig[v]>=w for u,v,a,b,w in original),'original binary dual')
    original_M,original_vertices=bounded_vertices(n,original,gamma)
    for trial in range(12):
        c=[Q(rng.randrange(7),rng.randrange(1,4)) for _ in range(n)]
        residual_value=min(sum(a*b for a,b in zip(c,p)) for p in d)
        check(graph_value([(hi-lo)*c[v] for v,lo,hi in bins],edges)==residual_value,'unary residual lift')
        original_value=min(sum(a*b for a,b in zip(c,p)) for p in original_vertices)
        check(original_value==sum(a*b for a,b in zip(c,gamma))+residual_value,'independent original unary dual identity')
    print(json.dumps({'status':'PASS','arithmetic':'Fraction; explicit raises; no floating point',
       'comparison':'bounded original dual vertices versus independently computed unit double-cover maxflow; vertex binary covers and primal embeddings',
       'coalition_profiles':profiles,'primal_embeddings':embeddings,'payment_coalition_checks':coalitionchecks,
       'joint_increase_checks':transitions,'unary_residual_profiles':12,'cases':out},default=str,indent=2))
if __name__=='__main__':main()
