"""Bounded complete mixed-owner lattices. Float screening, exact value oracles."""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path
import json, random, time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

OUT = Path(__file__).resolve().parent
N = 4
STATES = list(product((0, 1), repeat=2))
PROFILES = list(product(range(4), repeat=N))
P_INDEX = {p: k for k, p in enumerate(PROFILES)}
COALS = [tuple(c) for k in range(1, N + 1) for c in combinations(range(N), k)]
PROTECTED = [c for c in COALS if len(c) <= 2]


def make_case(seed):
    rng = random.Random(seed)
    d = 4 + seed % 3
    pairs = [tuple(sorted(rng.sample(range(d), 2))) for _ in range(N)]
    # Ensure the union covers every resource, while keeping exactly two rows
    # under each fixed owner's control.
    while len(set(a for pair in pairs for a in pair)) < d:
        pairs = [tuple(sorted(rng.sample(range(d), 2))) for _ in range(N)]
    caps = [[rng.choice((1, 1, 2)) for _ in range(2)] for i in range(N)]
    supports = list(combinations(range(d), 3))
    rng.shuffle(supports)
    supports = supports[:min(len(supports), 4 + seed % 5)]
    A = [[0 for _ in supports] for _ in range(d)]
    for e, support in enumerate(supports):
        for a in support:
            A[a][e] = rng.choice((1, 1, 2))
    pi = [Q(rng.choice((2, 3, 4, 5)), 2) for _ in supports]
    return dict(seed=seed, d=d, pairs=pairs, caps=caps, A=A, pi=list(map(str, pi)))


def solve_case(case):
    start = time.monotonic()
    d, A = case['d'], case['A']
    pi = list(map(Q, case['pi']))
    af, pf = np.array(A, dtype=float), np.array(list(map(float, pi)))
    owner_states = []
    for pair, caps in zip(case['pairs'], case['caps']):
        values = []
        for bits in STATES:
            b = [0] * d
            for j, a in enumerate(pair): b[a] = bits[j] * caps[j]
            values.append(tuple(b))
        owner_states.append(values)
    b = [[owner_states[i][p[i]] for i in range(N)] for p in PROFILES]
    oracle = {}
    def val(cap):
        cap = tuple(cap)
        if cap in oracle: return oracle[cap][0]
        sol = linprog(-pf, A_ub=af, b_ub=cap, bounds=(0, None), method='highs')
        if not sol.success: raise RuntimeError(sol.message)
        x = [Q(float(v)).limit_denominator(10**6) for v in sol.x]
        p = [Q(float(-v)).limit_denominator(10**6) for v in sol.ineqlin.marginals]
        primal = sum(pi[e] * x[e] for e in range(len(pi)))
        dual = sum(p[a] * cap[a] for a in range(d))
        assert min(x) >= 0 and min(p) >= 0 and primal == dual
        assert all(sum(A[a][e]*x[e] for e in range(len(pi))) <= cap[a] for a in range(d))
        assert all(sum(A[a][e]*p[a] for a in range(d)) >= pi[e] for e in range(len(pi)))
        oracle[cap] = (primal, x, p)
        return primal
    def cap(k, C): return tuple(sum(b[k][i][a] for i in C) for a in range(d))
    V = [val(cap(k, range(N))) for k in range(len(PROFILES))]
    rows, rhs, tags = [], [], []
    def add(terms, right, tag):
        row = defaultdict(Q)
        for j, v in terms: row[j] += v
        rows.append({j: v for j, v in row.items() if v}); rhs.append(Q(right)); tags.append(tag)
    K = len(PROFILES) * N
    for k in range(len(PROFILES)):
        add([(N*k+i, 1) for i in range(N)] + [(K, -V[k])], 0, ['budget', k])
        for C in COALS:
            add([(N*k+i, -1) for i in C], -val(cap(k, C)), ['cover', k, list(C)])
    for lo, state in enumerate(PROFILES):
        for C in PROTECTED:
            high_options = []
            for i in range(N):
                if i not in C: high_options.append([state[i]]); continue
                high_options.append([j for j in range(4) if all(x<=y for x,y in zip(STATES[state[i]], STATES[j]))])
            for hi_state in product(*high_options):
                if hi_state == state: continue
                hi = P_INDEX[hi_state]
                delta = tuple(sum(b[hi][i][a]-b[lo][i][a] for i in C) for a in range(d))
                add([(N*lo+i,1) for i in C]+[(N*hi+i,-1) for i in C], -val(delta), ['out', lo, hi, list(C)])
    def matrix(rs, nv):
        rr, cc, dd = [], [], []
        for k, row in enumerate(rs):
            for j, v in row.items(): rr.append(k); cc.append(j); dd.append(float(v))
        return coo_matrix((dd,(rr,cc)),shape=(len(rs),nv)).tocsr()
    base = matrix(rows, K+1)
    obj = np.zeros(K+1); obj[K] = 1
    sol = linprog(obj,A_ub=base,b_ub=np.array(list(map(float,rhs))),bounds=(0,None),method='highs',options={'time_limit':35})
    if not sol.success: return dict(case=case, failure=sol.message)
    # Efficient-price-floor comparison. Same complete contract rows.
    floor_rows = list(rows); floor_rhs = list(rhs)
    eq, eqrhs = [], []
    for k in range(len(PROFILES)):
        for e in range(len(pi)):
            floor_rows.append({K+1+k*d+a: -Q(A[a][e]) for a in range(d) if A[a][e]});floor_rhs.append(-pi[e])
        for i in range(N):
            row = {N*k+i: Q(-1)}
            row.update({K+1+k*d+a: Q(b[k][i][a]) for a in range(d) if b[k][i][a]})
            floor_rows.append(row);floor_rhs.append(Q(0))
        eq.append({K+1+k*d+a: Q(v) for a,v in enumerate(cap(k,range(N))) if v});eqrhs.append(V[k])
    nv = K+1+len(PROFILES)*d
    objf = np.zeros(nv);objf[K]=1
    sf=linprog(objf,A_ub=matrix(floor_rows,nv),b_ub=list(map(float,floor_rhs)),A_eq=matrix(eq,nv),b_eq=list(map(float,eqrhs)),bounds=(0,None),method='highs',options={'time_limit':35})
    # Exact rationalize the unrestricted dual; add only budget multipliers
    # needed to repair any negative payment coefficient from rounding.
    weights=[Q(float(max(0,-v))).limit_denominator(10**6) for v in sol.ineqlin.marginals]
    combo=defaultdict(Q);right=Q(0)
    for row, rb, w in zip(rows,rhs,weights):
        if not w:continue
        for j,v in row.items():combo[j]+=w*v
        right+=w*rb
    repairs=[]
    for k in range(len(PROFILES)):
        w=max([Q(0)]+[-combo[N*k+i] for i in range(N)])
        if w:
            row_index=k*16;weights[row_index]+=w;repairs.append((k,str(w)))
            for j,v in rows[row_index].items():combo[j]+=w*v
    assert all(v>=0 for j,v in combo.items() if j!=K) and combo[K]<0
    exact_lower=right/combo[K]
    L, D = -right, -combo[K]
    # Signed efficient-price identity, with original shared coalition weights.
    u=[]
    for k in range(len(PROFILES)):
        p=oracle[cap(k,range(N))][2]
        u.append([sum(p[a]*b[k][i][a] for a in range(d)) for i in range(N)])
    pos=neg=cover_slack=Q(0); edges=[];cover_used=[];nu=defaultdict(Q)
    for row,rb,tag,w in zip(rows,rhs,tags,weights):
        if not w:continue
        if tag[0]=='budget':nu[tag[1]]+=w
        elif tag[0]=='cover':
            _,k,C=tag;cover_slack+=w*(sum(u[k][i] for i in C)+rb);cover_used.append((k,C,w))
        else:
            _,lo,hi,C=tag;a=sum(u[lo][i]-u[hi][i] for i in C)-rb
            pos+=w*max(a,0);neg+=w*max(-a,0);edges.append((lo,hi,C,w,a))
    sigma_price=sum(combo[N*k+i]*u[k][i] for k in range(len(PROFILES)) for i in range(N))
    assert L-D==pos-neg-cover_slack-sigma_price
    adjacency=defaultdict(set)
    for lo,hi,*_ in edges:adjacency[lo].add(hi);adjacency[hi].add(lo)
    seen=set();components=[]
    for root in adjacency:
        if root in seen:continue
        nodes={root};todo=[root];seen.add(root)
        while todo:
            for h in adjacency[todo.pop()]:
                if h not in seen:seen.add(h);nodes.add(h);todo.append(h)
        es=[e for e in edges if e[0] in nodes]
        varying=[i for i in range(N) if len({b[k][i] for k in nodes})>1]
        ghost=[i for i in range(N) if all(not any(b[k][i]) for k in nodes)]
        productive=[i for i in range(N) if any(V[k]>val(cap(k,[j for j in range(N) if j!=i])) for k in nodes)]
        covered={i for k,C,w in cover_used if k in nodes for i in C}
        erasable=[i for i in range(N) if i not in varying and (i in ghost or i not in covered)]
        components.append(dict(profiles=len(nodes),comparison_rows=len(es),varying_owners=varying,productive_owners=productive,zero_ghosts=ghost,erasable_frozen=erasable,
            positive_defect=str(sum(w*max(a,0) for lo,hi,C,w,a in es)),negative_defect=str(sum(w*max(-a,0) for lo,hi,C,w,a in es)),budget_denominator=str(sum(nu[k]*V[k] for k in nodes)),
            changed_counts=dict(Counter(i for lo,hi,C,w,a in es for i in C if b[lo][i]!=b[hi][i])),passive_edges=sum(any(b[lo][i]==b[hi][i] for i in C) for lo,hi,C,w,a in es)))
    result=dict(case=case,profiles=len(PROFILES),coverage_rows=256*15,out_rows=sum(t[0]=='out' for t in tags),all_rows=len(rows),oracle_count=len(oracle),
        unrestricted_float=sol.fun,price_floor_float=sf.fun if sf.success else None,price_floor_status=sf.message,exact_unrestricted_lower=str(exact_lower),dual_budget_repairs=repairs,
        dual_L=str(L),dual_D=str(D),positive_defect=str(pos),negative_defect=str(neg),coverage_price_slack=str(cover_slack),nonnegative_price_slack=str(sigma_price),
        dual_nonzero_rows=sum(bool(w) for w in weights),components=sorted(components,key=lambda x:-x['comparison_rows']),elapsed=time.monotonic()-start,
        floating_status='Solver optima are diagnostic; unrestricted rational dual and production oracles checked exactly by author code.')
    packet=dict(case=case,profiles=PROFILES,owner_states=owner_states,K=K,
        oracles=[dict(cap=cap,value=str(v),x=list(map(str,x)),p=list(map(str,p))) for cap,(v,x,p) in oracle.items()],
        certificate=[dict(tag=tag,weight=str(w)) for tag,w in zip(tags,weights) if w],exact_lower=str(exact_lower))
    (OUT/f'case_{case["seed"]}_certificate.json').write_text(json.dumps(packet,indent=2)+'\n')
    (OUT/f'case_{case["seed"]}.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('case','unrestricted_float','price_floor_float','exact_unrestricted_lower','dual_nonzero_rows','elapsed')}),flush=True)
    return result


if __name__=='__main__':
    results=[]
    for seed in (10,11,12,13,14,15,16,17):
        results.append(solve_case(make_case(seed)))
    (OUT/'results.json').write_text(json.dumps(results,indent=2)+'\n')
