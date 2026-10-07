"""Exact support checks for the campaign's hinge and influence lemmas."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import importlib.util
import json
import random

REPO = Path(__file__).resolve().parents[3]
BASE = REPO/'research_campaigns/2026-10-06-monotone-envelope/verification/verify.py'
spec = importlib.util.spec_from_file_location('base', BASE)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


def conditional(ds, cuts, e, U):
    values = [x*u for x,u in zip(ds,U)]
    A = min(b.weighted_sum(values,C & ~(1 << e)) for C in cuts if C >> e & 1)
    excluding = [b.weighted_sum(values,C) for C in cuts if not C >> e & 1]
    return min(ds[e], max(Q(0), min(excluding)-A)) if excluding else ds[e]


def run():
    rng = random.Random(7100701)
    cases = []
    for n in range(2,6):
        possible = list(combinations(range(n),2))
        for mask in range(1,1 << len(possible)):
            edges = [e for i,e in enumerate(possible) if mask >> i & 1]
            paths = b.paths(n,edges)
            if paths and set().union(*map(set,paths)) == set(range(len(edges))):
                cases.append((n,edges,paths))
    for _ in range(20):
        n=6
        edges = [(a,z) for a,z in combinations(range(n),2)
                 if z==a+1 or rng.randrange(3)==0]
        cases.append((n,edges,b.paths(n,edges)))
    edges=[(0,1),(0,2),(1,3),(1,3),(2,3),(1,2)]
    cases.append((4,edges,b.paths(4,edges)))
    counts = dict(graphs=0,profiles=0,hinge_coordinates=0,column_bounds=0,
                  gain_comparisons=0,non_antichain_rejections=0)
    for n,edges,paths in cases:
        m=len(edges)
        cuts=b.cutsets(n,edges)
        before={(e,h) for p in paths for j,e in enumerate(p) for h in p[j+1:]}
        antichains=[]
        for mask in range(1,1 << m):
            A=[e for e in range(m) if mask >> e & 1]
            if all((e,h) not in before and (h,e) not in before for e,h in combinations(A,2)):
                antichains.append(A)
        for c in ([Q(0)]*m,[Q(1)]*m,[Q(rng.randrange(13),4) for _ in edges]):
            ds=b.effective(n,edges,c)
            zeros=[]
            for e in range(m):
                c0=c.copy();c0[e]=Q(0)
                zeros.append(b.effective(n,edges,c0))
            delta=[[ds[h]-zeros[e][h] for h in range(m)] for e in range(m)]
            for h in range(m):
                for A in antichains:
                    b.require(sum(delta[e][h] for e in A)<=ds[h], 'antichain column A3')
                    counts['column_bounds']+=1
                if sum(delta[e][h] for e in range(m))>ds[h]:
                    counts['non_antichain_rejections']+=1
                b.require(sum(delta[e][h] for e in range(m))<=max(map(len,paths))*ds[h],
                          'length-weighted column bound')
            for e in range(m):
                for t in sorted({Q(0),c[e]/3,2*c[e]/3,c[e],ds[e]}):
                    ct=c.copy();ct[e]=t
                    dt=b.effective(n,edges,ct)
                    for h in range(m):
                        b.require(dt[h]==min(ds[h],t+zeros[e][h]), 'single-hinge A1')
                        b.require(ds[h]-dt[h]==max(Q(0),delta[e][h]-t), 'hinge loss A2')
                        b.require(0<=delta[e][h]<=ds[e], 'influence own-cap bound')
                        counts['hinge_coordinates']+=1
                    if t>ds[e]:
                        continue
                    for U in ([Q(0)]*m,[Q(1)]*m,
                              [Q(rng.randrange(7),6) for _ in edges]):
                        gain=conditional(dt,cuts,e,U)-conditional(ds,cuts,e,U)
                        maxcut=max(sum((max(Q(0),delta[e][h]-t)*U[h]
                                       for h in range(m) if h!=e and C>>h&1),Q(0))
                                   for C in cuts if C>>e&1)
                        b.require(gain<=min(t,maxcut),'conditional gain A4')
                        counts['gain_comparisons']+=1
            counts['profiles']+=1
        counts['graphs']+=1
    b.require(counts['non_antichain_rejections']>0,'missing antichain negative control')
    return dict(status='PASS',counts=counts,
                scope='Exact finite checks of candidate lemmas, not a universal proof or new budget bound.')


if __name__=='__main__':
    result=run()
    out=json.dumps(result,indent=2)+'\n'
    Path('/tmp/coopgt_sensitivity_result.json').write_text(out)
    print(out,end='')
