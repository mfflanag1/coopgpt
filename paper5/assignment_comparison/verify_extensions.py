"""Small exact checks for new graph and additive-market corollaries only."""
from pathlib import Path
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations
import json
import random
from exact_three import Q, require, optimize, selector, core as triple_core
import z3


def graph_core(n,edges):
    edges={tuple(sorted(e)):F(w) for e,w in edges.items()}
    require(all(len(e)==2 and e[0]!=e[1] and 0<=e[0]<e[1]<n and w>=0 for e,w in edges.items()),'invalid graph')
    @lru_cache(None)
    def matching(mask):
        if not mask: return F(0),()
        i=(mask & -mask).bit_length()-1
        rest=mask & ~(1<<i)
        best=matching(rest)
        for j in range(i+1,n):
            if rest>>j&1 and (i,j) in edges:
                value,chosen=matching(rest & ~(1<<j))
                candidate=(value+edges[i,j], chosen+((i,j),))
                if candidate[0]>best[0]: best=candidate
        return best
    T,chosen=matching((1<<n)-1)
    p=[z3.FreshReal('graph_p') for _ in range(n)]
    cons=[q>=0 for q in p]+[sum(p)==Q(T)]
    for mask in range(1,1<<n):
        cons.append(sum(p[i] for i in range(n) if mask>>i&1)>=Q(matching(mask)[0]))
    return p,cons,T,chosen,edges


def graph_check(label,n,edges,expect_empty=False,expected_rho=None):
    p,cons,T,chosen,edges=graph_core(n,edges)
    solver=z3.Solver(); solver.set(timeout=60000);solver.add(*cons)
    status=solver.check()
    require(status in (z3.sat,z3.unsat),'core status unknown')
    if expect_empty:
        require(status==z3.unsat,'empty-core negative control unexpectedly feasible')
        return dict(label=label,n=n,T=str(T),core_nonempty=False)
    require(status==z3.sat and T>0,'positive nonempty graph core required')
    x,xst=selector(cons,p,True); z,zst=selector(cons,p,False)
    maxima=[optimize(cons,q,True) for q in p]
    require(all(2*a>=b for a,b in zip(x,maxima)),'half-core-maximum guarantee')
    k=sum(edges[e]>0 for e in chosen)
    rho=sum(abs(a-b) for a,b in zip(x,z))/T
    require(rho<=F(k,k+1),'k-edge distance bound')
    if k==1: require(x==z,'one-edge selector equality')
    if expected_rho is not None: require(rho==expected_rho,'claimed example distance')
    M=max(z)
    absolute=[z3.If(q>=Q(a),q-Q(a),Q(a)-q) for q,a in zip(p,x)]
    solver=z3.Solver();solver.set(timeout=60000)
    solver.add(*cons,*[q<=Q(M) for q in p],sum(absolute)>Q(F(k,k+1)*T))
    require(solver.check()==z3.unsat,'some minimax core point violates finite bound')
    return dict(label=label,n=n,T=str(T),core_nonempty=True,optimal_matching=[list(e) for e in chosen],positive_matching_edges=k,edges=[dict(vertices=list(e),weight=str(w)) for e,w in sorted(edges.items())],Lmin=list(map(str,x)),Lmax=list(map(str,z)),rho=str(rho),core_maxima=list(map(str,maxima)),Lmin_stages=xst,Lmax_stages=zst,any_minimax_violation='UNSAT')


def additive_check(label,sectors):
    require(len(sectors)==3 and len(set(map(len,sectors)))==1,'balanced three sectors required')
    m=len(sectors[0]); require(m>=1,'nonempty sectors')
    w=[[[sectors[0][i]+sectors[1][j]+sectors[2][h] for h in range(m)] for j in range(m)] for i in range(m)]
    p,cons,T,feasible=triple_core(w,full=m<=3)
    require(feasible and T>0,'positive nonempty additive core required')
    minima=[min(s) for s in sectors]; S=sum(minima)
    baseline=[F(a-min(s)) for s in sectors for a in s]
    require(S>=0,'negative minimum triple value')
    require(T==sum(sum(s) for s in sectors),'integral additive matching total')
    x,xst=selector(cons,p,True); z,zst=selector(cons,p,False)
    expected=[a+F(S,3) for a in baseline]
    require(x==expected,'additive full leximin formula')
    maxima=[optimize(cons,q,True) for q in p]
    require(maxima==[a+S for a in baseline],'entire-core coordinate maxima')
    require(all(3*a>=b for a,b in zip(x,maxima)),'one-third individual guarantee')
    shifts=[p[s*m]-Q(baseline[s*m]) for s in range(3)]
    equations=[p[s*m+i]-Q(baseline[s*m+i])==shifts[s] for s in range(3) for i in range(m)]+[sum(shifts)==Q(S)]+[t>=0 for t in shifts]
    solver=z3.Solver();solver.set(timeout=60000);solver.add(*cons,z3.Not(z3.And(*equations)))
    require(solver.check()==z3.unsat,'core outside additive sector-shift simplex')
    absolute=[z3.If(q>=Q(a),q-Q(a),Q(a)-q) for q,a in zip(p,x)]
    farthest=optimize(cons,sum(absolute),True)
    require(farthest==F(4*m*S,3),'distance to farthest entire-core point')
    rho=sum(abs(a-b) for a,b in zip(x,z))/T
    require(rho<=farthest/T<=F(4,3),'additive distance bound')
    return dict(label=label,sectors=sectors,m=m,T=str(T),S=S,full_coalitions=m<=3,Lmin=list(map(str,x)),Lmax=list(map(str,z)),core_maxima=list(map(str,maxima)),rho=str(rho),farthest_core_distance=str(farthest/T),Lmin_stages=xst,Lmax_stages=zst)


def main():
    graphs=[]
    graphs.append(graph_check('empty unit-weight odd triangle',3,{(0,1):1,(0,2):1,(1,2):1},expect_empty=True))
    graphs.append(graph_check('balanced weighted triangle',3,{(0,1):2,(0,2):1,(1,2):1},expected_rho=F(0)))
    for k in (2,3):
        edges={(i,k+j):1+int(j==k-1) for i in range(k) for j in range(k)}
        edges[0,1]=1
        graphs.append(graph_check(f'nonbipartite sharp family k={k}',2*k,edges,expected_rho=F(k,k+1)))
    for case,cover in enumerate(((1,2,1,3,2,3),(0,3,2,1,4,2))):
        edges={(i,j):max(0,cover[i]+cover[j]-(i+2*j+case)%3) for i,j in combinations(range(6),2)}
        for i in (0,2,4): edges[i,i+1]=cover[i]+cover[i+1]
        graphs.append(graph_check(f'nonbipartite cover-certified dense example {case}',6,edges))
    sectors=[('zero transferable shift',[[0,2],[0,1],[0,3]]),('constant sector productivities',[[1,1],[2,2],[3,3]]),('nonuniform sector productivity maxima',[[1,5,2],[0,1,0],[2,2,3]]),('signed additive coefficients with nonnegative triple values',[[-2,0,1],[3,4,3],[1,1,2]])]
    rng=random.Random(20260905)
    for case in range(4): sectors.append((f'fixed-seed additive array {case}',[[rng.randrange(7) for _ in range(3)] for _ in range(3)]))
    additive=[additive_check(label,s) for label,s in sectors]
    payload=dict(scope='Only new corollaries: six general-graph cases including one empty-core negative control, and eight additive three-sided cases. Full selectors and individual core maxima; all minimax graph points checked by an exact infeasibility query.',graphs=graphs,additive=additive)
    Path(__file__).with_name('extension_checks.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print('PASS',len(graphs),'graph cases and',len(additive),'additive cases',flush=True)


if __name__=='__main__': main()
