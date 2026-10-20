from fractions import Fraction as Q
from itertools import product
import json


def verify_frozen():
    fixed_cases=[[(1,0,1),(0,1,1)],[(1,0,0),(0,2,0)],[(1,2,3),(2,1,1)]]
    choices=[(0,0,0),(1,0,0),(0,1,1),(1,1,1)]
    count_cov=count_out=count_budget=0
    for fixed in fixed_cases:
        fixed=[tuple(map(Q,b)) for b in fixed]
        A=tuple(sum(b[a] for b in fixed) for a in range(3))
        f0=min(A)
        h=[f0*sum((b[a]/A[a] if A[a] else Q(0)) for a in range(3)) for b in fixed]
        assert sum(h)<=3*f0
        profiles=[]
        for a,b in product(choices,repeat=2):
            bundles=[tuple(map(Q,a)),tuple(map(Q,b))]+fixed
            B=tuple(sum(x[r] for x in bundles) for r in range(3))
            f=min(B)
            y=[f-f0,f-f0]+h
            assert sum(y)==2*(f-f0)+sum(h)
            assert sum(y)<=3*f
            profiles.append((bundles,y,f))
            count_budget+=1
            for mask in range(1,16):
                S=[i for i in range(4) if mask>>i&1]
                v=min(sum(bundles[i][r] for i in S) for r in range(3))
                assert sum(y[i] for i in S)>=v
                count_cov+=1
        for low,high in product(profiles,repeat=2):
            lb,ly,lf=low; hb,hy,hf=high
            if any(hb[i][r]<lb[i][r] for i in range(4) for r in range(3)):
                continue
            changed={i for i in range(4) if lb[i]!=hb[i]}
            if not changed: continue
            delta=tuple(sum(hb[i][r]-lb[i][r] for i in range(4)) for r in range(3))
            for mask in range(1,16):
                C={i for i in range(4) if mask>>i&1}
                if not changed<=C: continue
                assert sum(hy[i]-ly[i] for i in C)>=min(delta)
                count_out+=1
    return dict(coverage_checks=count_cov,full_OUT_checks=count_out,budget_checks=count_budget)


def compress_harmonic(m):
    H=[Q(0)]
    for k in range(1,m): H.append(H[-1]+Q(1,k))
    div=[H[k]-H[m-1-k] for k in range(m)]
    supply={i:-d for i,d in enumerate(div) if d<0}
    demand={i:d for i,d in enumerate(div) if d>0}
    weights={(i,j):Q(1,j-i) for i in range(m) for j in range(i+1,m)}
    eps=Q(1,4*m)
    V=[2+Q(k+1,2*m) for k in range(m)]
    def rhs(i,j):
        return V[j]-V[i]-(eps if (j-i)%2 else 0)
    old_rhs=sum(mu*rhs(i,j) for (i,j),mu in weights.items())
    new={}
    path_count=0
    while any(supply.values()):
        start=next(i for i,v in supply.items() if v)
        path=[start]
        p=start
        while not demand.get(p,0):
            q=next(j for j in range(p+1,m) if weights.get((p,j),0)>0)
            path.append(q); p=q
        mass=min(supply[start],demand[p],*(weights[(a,b)] for a,b in zip(path,path[1:])))
        supply[start]-=mass; demand[p]-=mass
        for a,b in zip(path,path[1:]): weights[(a,b)]-=mass
        new[(start,p)]=new.get((start,p),Q(0))+mass
        assert rhs(start,p)>=sum(rhs(a,b) for a,b in zip(path,path[1:]))
        path_count+=1
    assert not any(weights.values()) and not any(demand.values())
    new_div=[Q(0)]*m
    for (i,j),mu in new.items():
        new_div[i]-=mu; new_div[j]+=mu
    assert new_div==div
    assert {i for i,j in new}.isdisjoint({j for i,j in new})
    new_rhs=sum(mu*rhs(i,j) for (i,j),mu in new.items())
    assert new_rhs>=old_rhs
    return dict(profiles=m,original_edges=m*(m-1)//2,compressed_edges=len(new),
                decomposed_paths=path_count,old_OUT_objective_part=str(old_rhs),
                new_OUT_objective_part=str(new_rhs),all_checks_passed=True)

if __name__=='__main__':
    print(json.dumps({'frozen_background':verify_frozen(),
                      'harmonic_compression':[compress_harmonic(m) for m in [2,4,8,16,32]],
                      'evidence':'exact finite checks supplementing written proofs'},indent=2))
