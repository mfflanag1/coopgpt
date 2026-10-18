from fractions import Fraction as Q
from itertools import combinations, product
from math import comb
from pathlib import Path
from random import Random
import json

counts={'path_profiles':0,'path_dual_covers':0,'original_lp_optima':0,
        'ternary_primal_dual_certificates':0,'sharp_deletion_instances':0,
        'stage_max_inequalities':0,'zero_budget_failures':0}

def lin_solve(A,b):
    n=len(b); M=[list(map(Q,row))+[Q(v)] for row,v in zip(A,b)]
    for j in range(n):
        k=next((k for k in range(j,n) if M[k][j]),None)
        if k is None:return None
        M[j],M[k]=M[k],M[j]; scale=M[j][j]
        M[j]=[v/scale for v in M[j]]
        for k in range(n):
            if k!=j:
                factor=M[k][j]
                M[k]=[a-factor*b for a,b in zip(M[k],M[j])]
    return [M[j][-1] for j in range(n)]

def lp_exact(A,c,profits):
    d=len(A); n=len(profits)
    rows=[list(map(Q,row)) for row in A]+[[Q(int(i==j)) for j in range(n)] for i in range(n)]
    rhs=list(map(Q,c))+[Q(0)]*n
    best=None
    for active in combinations(range(d+n),n):
        x=lin_solve([rows[k] for k in active],[rhs[k] for k in active])
        if x is None or min(x)<0:continue
        if any(sum(A[v][e]*x[e] for e in range(n))>c[v] for v in range(d)):continue
        obj=sum(profits[e]*x[e] for e in range(n))
        if best is None or obj>best[0]:best=(obj,x)
    # Exact feasible dual with matching objective, obtained independently by vertices.
    D=[[Q(A[v][e]) for v in range(d)] for e in range(n)]+[[Q(int(i==j)) for j in range(d)] for i in range(d)]
    R=list(map(Q,profits))+[Q(0)]*d
    dual=None
    for active in combinations(range(n+d),d):
        p=lin_solve([D[k] for k in active],[R[k] for k in active])
        if p is None or min(p)<0:continue
        if any(sum(A[v][e]*p[v] for v in range(d))<profits[e] for e in range(n)):continue
        obj=sum(c[v]*p[v] for v in range(d))
        if obj==best[0]:dual=p;break
    assert best is not None and dual is not None
    counts['original_lp_optima']+=1
    return best[0],best[1],dual

# Exact path primal and dual certificates on every bounded integer profile.
for r in range(2,8):
    for x in product(range(3),repeat=r):
        m=min(x); B=sum(x[1:-1]); caps=[x[0]]
        for a in x[1:-1]:caps.extend([a,a])
        caps.append(x[-1])
        flow=[]
        for e in range(2*r-3):flow.append(m if e%2==0 else x[(e+1)//2]-m)
        assert all(a>=0 for a in flow)
        assert all((flow[v-1] if v else 0)+(flow[v] if v<len(flow) else 0)<=caps[v] for v in range(len(caps)))
        assert sum(flow)==B+m
        for k in range(1,r+1):
            C=set(range(2,2*k,2))|set(range(2*k-1,2*r-2,2))
            assert all(e in C or e+1 in C for e in range(1,2*r-2))
            assert sum(caps[v-1] for v in C)==B+x[k-1]
            counts['path_dual_covers']+=1
        counts['path_profiles']+=1

# Exact upper-bound inequality used to round arbitrary gadget stages.
for r in range(2,8):
    for z in product(range(3),repeat=r):
        assert sum(z)-sum(max(z[k],z[k+1]) for k in range(r-1))<=min(z)
        counts['stage_max_inequalities']+=1

# General OVERLAPPING activities; independently solve original primal and dual,
# then check every row/column and objective of the induced gadget certificates.
rng=Random(202610182313)
for case in range(14):
    d=4+case%2; n=2+case%2; owners=3
    A=[[rng.randrange(3) for e in range(n)] for v in range(d)]
    for e in range(n):
        if not any(A[v][e] for v in range(d)):A[e%d][e]=1
    profits=[rng.randrange(1,4) for e in range(n)]
    reports=[[Q(rng.randrange(3)) for v in range(d)] for i in range(owners)]
    ends=[[reports[i][v]+rng.randrange(3) for v in range(d)] for i in range(owners)]
    for mask in range(1<<owners):
        C=[i for i in range(owners) if mask>>i&1]
        c=[sum((reports[i][v] for i in C),Q(0)) for v in range(d)]
        F,x,p=lp_exact(A,c,profits)
        for variant in ['linear','constant']:
            source=reports if variant=='linear' else ends
            M=[]; supports=[]
            for e in range(n):
                vs=[v for v in range(d) if A[v][e]];supports.append(vs)
                M.append(sum((source[i][v]/A[v][e] for i in C for v in vs),Q(0))/len(vs))
            baseline=Q(0); primal_obj=Q(0); dual_obj=sum(c[v]*p[v] for v in range(d))
            original_use=[Q(0)]*d
            for e,vs in enumerate(supports):
                r=len(vs); pi=profits[e]; baseline+=pi*(r-1)*M[e]
                if r>1:assert x[e]<=M[e]
                z=[x[e]]*r; w=[M[e]-x[e]]*(r-1)
                assert all(a>=0 for a in z+w)
                for k in range(r-1):
                    assert z[k]+w[k]<=M[e] and z[k+1]+w[k]<=M[e]
                for k,v in enumerate(vs):original_use[v]+=A[v][e]*z[k]
                primal_obj+=pi*(sum(z)+sum(w))
                aa=[A[v][e]*p[v] for v in vs]
                u=[max(Q(0),Q(pi)-sum(aa[:k+1])) for k in range(r-1)]
                vv=[pi-a for a in u]
                assert all(a>=0 for a in u+vv)
                for k in range(r):
                    stage_cover=aa[k]+(vv[k-1] if k else 0)+(u[k] if k<r-1 else 0)
                    assert stage_cover>=pi
                    # At most one original resource and two distinct link rows.
                    assert 1+int(k>0)+int(k<r-1)<=3
                for k in range(r-1):
                    assert u[k]+vv[k]==pi
                    dual_obj+=M[e]*(u[k]+vv[k])
            assert all(original_use[v]<=c[v] for v in range(d))
            assert primal_obj==dual_obj==baseline+F
            counts['ternary_primal_dual_certificates']+=1

for r in range(2,12):
    for q in range(1,min(r,3)+1):
        full=Q(comb(r,q),comb(r,q)); deleted=Q(comb(r-1,q),comb(r,q)) if r>q else Q(0)
        assert r*(full-deleted)==q*full
        assert deleted==1-Q(q,r)
        counts['sharp_deletion_instances']+=1

# Accepted scaled binomial rule on zero-original-value image games is additive.
for variant in ['linear','constant']:
    r=4; original=[0,1,1,1]; s=2; p=Q(1,s)
    B=[Q(r-1,r)*(original[i] if variant=='linear' else 1) for i in range(r)]
    y=[]
    for i in range(r):
        others=[j for j in range(r) if j!=i]; marginal=Q(0)
        for mask in range(1<<(r-1)):
            S=[others[k] for k in range(r-1) if mask>>k&1]; k=len(S)
            marginal+=p**k*(1-p)**(r-1-k)*B[i]
        assert marginal==B[i]
        y.append(s*s*marginal-B[i])
    assert sum(y)==(s*s-1)*sum(B)>0 and min(original)==0
    counts['zero_budget_failures']+=1

# Utilization rule exact certificate for the negative double-baseline payment.
caps=list(map(Q,[1,10,10,10])); prices=[Q(29,40),Q(11,40),Q(29,40),Q(11,40)]
util=[min(2*p,1) for p in prices]; flows=[Q(1),Q(9,2),Q(11,2)]
assert sum(flows)==11
assert all(prices[j]+prices[j+1]==1 for j in range(3))
assert all((flows[v-1] if v else 0)+(flows[v] if v<3 else 0)==caps[v]*util[v] for v in range(4))
assert 10*(util[1]+util[2])-20==-Q(9,2)

result={'status':'PASS','counts':counts,
 'scope':'Exact finite primal-dual certificates and algebra supplement the all-real proofs; no multiplicative reduction or new funding exponent.'}
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
