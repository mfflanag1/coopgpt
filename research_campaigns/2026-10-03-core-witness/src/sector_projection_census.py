"""Exact, solver-free census of one five-label motif on CW-01 and CW-04 only."""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import permutations, product
from math import lcm
from pathlib import Path
import json
import sys

REPO=Path('/Users/maxf/projects/economics-research/game-theory/coopgpt')
PAIRED=REPO/'research_campaigns/2026-10-03-core-witness/paired'

def need(ok,msg):
    if not ok: raise ValueError(msg)

def check_relaxed(raw):
    """Recheck the stated old relaxation and its original core, using raw rationals."""
    m=raw['m'];P=raw['P'];M=[[[Q(v) for v in row] for row in mat] for mat in raw['matrices']]
    x=list(map(Q,raw['core']));h=list(map(Q,raw['h']))
    def W(t): a,b,c=t;return M[0][a][b]+M[1][a][c]+M[2][b][c]
    allowed=[{(j,j) for j in range(m)} for _ in range(3)]
    for a,b,c in P:
        allowed[0].add((a,b));allowed[1].add((a,c));allowed[2].add((b,c))
    need(all((a,b) in allowed[k] or M[k][a][b]==0 for k,a,b in product(range(3),range(m),range(m))),'off-support pair')
    d=[W((j,j,j)) for j in range(m)]
    need(min(v for mat in M for row in mat for v in row)>=0,'nonnegative pairs')
    need(sum(d)==sum(x)==1 and min(x)>=0,'normalization/core nonnegativity')
    need(all(len({t[s] for t in P})==len(P) for s in range(3)),'P matching')
    for t in product(range(m),repeat=3):
        need(sum(x[s*m+t[s]] for s in range(3))>=W(t),'original core cover')
    U=set(range(3*m))-{s*m+j for t in P for s,j in enumerate(t)}
    wp=sum(map(W,P))
    for i in range(3*m):
        need(x[i]<=h[i]<=d[i%m],'core dominance and diagonal cap')
        if i in U:need(h[i]<=1-wp,'unmatched cap')
    budgets=[[M[0][j][j]+M[1][j][j],M[0][j][j]+M[2][j][j],M[1][j][j]+M[2][j][j]] for j in range(m)]
    for s,a,b in product(range(3),range(m),range(m)):
        t=[a,a,a];t[s]=b
        need(h[s*m+b]-h[s*m+a]>=W(t)-d[a],'completion')
        need(h[s*m+a]-h[s*m+b]<=budgets[a][s],'range')
    for team in P:
        for s,t,u in permutations(range(3)):
            a,b,c=team[s],team[t],team[u]
            need(h[u*m+c]-h[u*m+b]>=W(team)-d[b]-budgets[a][s],'P difference')
    need(wp+sum(h[i] for i in U)/3-1==Q(raw['J_relaxed']),'relaxed objective')
    return M,h,d

def census(name):
    path=PAIRED/(name+'_relaxed.json');blob=path.read_bytes();raw=json.loads(blob)
    M,H,D=check_relaxed(raw);m=raw['m']
    scale=lcm(*(v.denominator for mat in M for row in mat for v in row),*(v.denominator for v in H))
    M=[[[int(v*scale) for v in row] for row in mat] for mat in M]
    h=[int(v*scale) for v in H];ds=[int(v*scale) for v in D]
    def val(t):a,b,c=t;return M[0][a][b]+M[1][a][c]+M[2][b][c]
    best=[];total_violations=0;tested=0
    for sigma in permutations(range(3)):
        W={}
        for a,b,c in product(range(m),repeat=3):
            t=[0]*3
            for s,j in zip(sigma,(a,b,c)):t[s]=j
            W[a,b,c]=val(t)
        record=None
        for a,b,c,d,e in permutations(range(m),5):
            tested+=1
            cap=ds[a]+ds[b]+ds[c]+ds[d]+ds[e]-W[a,b,c]-W[b,d,e]-W[d,c,d]-W[e,a,a]
            need(cap>=0,'negative valid motif budget contradicts checked original core')
            violation=h[sigma[0]*m+c]-cap
            if violation>0:
                total_violations+=1
                if record is None or violation>record[0]:record=(violation,cap,(a,b,c,d,e),sigma[0]*m+c)
        if record:
            best.append({'sector_order':sigma,'violation':str(Q(record[0],scale)),
                'cap':str(Q(record[1],scale)),'labels':record[2],'target':record[3],
                'hypothetical_h':str(Q(h[record[3]],scale))})
    return {'case':name,'source_sha256':sha256(blob).hexdigest(),'baseline_relaxation_check':'PASS',
        'exact_scale':scale,'tested':tested,'violations':total_violations,'best_by_sector_order':best}

if __name__=='__main__':
    result={'scope':'all ordered five-distinct-label instantiations of the named four-team motif and six sector orders, only CW-01 and CW-04 raw relaxed matrices',
            'solver_calls':0,'python_optimized':not __debug__,'results':[census(n) for n in ['CW-01','CW-04']]}
    print(json.dumps(result,indent=2))
