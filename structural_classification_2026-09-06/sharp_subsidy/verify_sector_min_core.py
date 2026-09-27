"""Symbolic row identities for the sparse sector-minimum core formulation."""
from pathlib import Path
from itertools import combinations, permutations, product
from fractions import Fraction as Q
import json
from sector_min_core import core_rows


def require(ok,msg):
    if not ok:raise ValueError(msg)


def key(es,coeff):
    terms={('w',i):1 for i in es}
    for i,v in coeff.items():
        if v:terms[('x',i)]=v
    return tuple(sorted(terms.items()))


def symbolic(m,P,drop=None):
    edges,rows,special=core_rows(m,P);idx={e:i for i,e in enumerate(edges)}
    if drop is not None:rows=[row for k,row in enumerate(rows)if k!=drop]
    available={key(es,c)for es,c in rows}
    require(len(rows)<=7*m+10*len(P),'linear row bound')
    checks=0
    for a,b,c in product(range(m),repeat=3):
        es=[idx[e]for e in ((0,a,b),(1,a,c),(2,b,c))if e in idx]
        team=(a,m+b,2*m+c);target=key(es,{i:-1 for i in team})
        if target in available:
            checks+=1;continue
        if not es:
            # Nonnegative payoffs imply the zero-worth team inequality.
            checks+=1;continue
        require(len(es)==1,'missing local full-team row')
        p,u,v=edges[es[0]];s,t=[(0,1),(0,2),(1,2)][p];other=3-s-t
        pair=key(es,{s*m+u:-1,t*m+v:-1,3*m+other:-1})
        minimum=key([],{3*m+other:1,team[other]:-1})
        require(pair in available and minimum in available,'missing pair/minimum implication')
        combined={}
        for k,v in pair+minimum:combined[k]=combined.get(k,0)+v
        require(tuple(sorted((k,v)for k,v in combined.items()if v))==target,'symbolic coefficient identity')
        checks+=1
    return checks,len(rows)


def matchings(m):
    for r in range(m+1):
        for aa in combinations(range(m),r):
            for bb in combinations(range(m),r):
                for cc in combinations(range(m),r):
                    for b in permutations(bb):
                        for c in permutations(cc):yield list(zip(aa,b,c))


def run():
    count=0;triples=0
    for m in (1,2,3):
        for p in matchings(m):
            n,_=symbolic(m,p);triples+=n;count+=1
    require(count==187,'exhaustive small-support count')
    recs=json.loads(Path(__file__).with_name('CYCLIC_FRONTIER_CERTIFICATES.json').read_text());core_checks=0
    for rec in recs:
        d=rec['pattern'];m=d['m'];P=d['P'];n,_=symbolic(m,P);triples+=n
        edges,rows,_=core_rows(m,P);off=len(edges);scale=d['primal_scale'];weights=[Q(v,scale)for v in d['primal_integers'][:off]]
        used={s*m+j for t in P for s,j in enumerate(t)};U=sorted(set(range(3*m))-used)
        for k in range(len(U)):
            x=[Q(v,scale)for v in d['primal_integers'][off+k*3*m:off+(k+1)*3*m]]
            extended=x+[min(x[s*m:(s+1)*m])for s in range(3)]
            for es,coeff in rows:
                require(sum(weights[e]for e in es)+sum(v*extended[j]for j,v in coeff.items())<=0,'original witness violates compressed row')
                core_checks+=1
    # Delete a completion row for a two-label P-team; no pair/minimum row can
    # supply both of its positive pair-weight coefficients.
    m=3;P=[(0,0,1)];edges,rows,special=core_rows(m,P)
    k=next(k for k,(es,coeff)in enumerate(rows)if len(es)>1 and coeff=={0:-1,3:-1,7:-1})
    try:symbolic(m,P,drop=k)
    except ValueError:pass
    else:raise ValueError('missing local team constraint accepted')
    print(json.dumps({'status':'PASS','exhaustive_supports_sizes_1_to_3':count,'retained_frontier_supports':len(recs),'symbolic_full_team_checks':triples,'exact_original_core_row_checks':core_checks,'negative_controls':1,'scope':'symbolic implication and exact witness calibration; conventional all-size equivalence proved separately'}))

if __name__=='__main__':run()
