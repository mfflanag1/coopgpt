from fractions import Fraction as Q
from itertools import combinations
import json


def total(bs):
    return tuple(sum(b[r] for b in bs) for r in range(3))


def verify(bs, edges, coverage, nu, F):
    n=len(bs); owners=len(bs[0])
    gamma=[[Q(0)]*owners for _ in bs]
    lam=[[Q(0)]*owners for _ in bs]
    rhs=Q(0); Delta=[Q(0)]*3
    for l,h,C,mu in edges:
        mu=Q(mu)
        assert mu>0 and len(C)<=2
        assert all(bs[h][i][r]>=bs[l][i][r] for i in range(owners) for r in range(3))
        changed={i for i in range(owners) if bs[l][i]!=bs[h][i]}
        assert changed<=C
        delta=tuple(sum(bs[h][i][r]-bs[l][i][r] for i in C) for r in range(3))
        rhs+=mu*F(delta)
        Delta=[a+mu*b for a,b in zip(Delta,delta)]
        for i in C: gamma[l][i]-=mu; gamma[h][i]+=mu
    cov_value=Q(0)
    for p,S,weight in coverage:
        weight=Q(weight)
        cov_value+=weight*F(total([bs[p][i] for i in S]))
        for i in S: lam[p][i]+=weight
    g=[[gamma[p][i]+lam[p][i] for i in range(owners)] for p in range(n)]
    sigma=[[Q(nu[p])-g[p][i] for i in range(owners)] for p in range(n)]
    assert all(v>=0 for row in sigma for v in row)
    D=sum(Q(nu[p])*F(total(bs[p])) for p in range(n))
    B=tuple(sum(Q(nu[p])*total(bs[p])[r] for p in range(n)) for r in range(3))
    residual=tuple(B[r]-Delta[r] for r in range(3))
    right=tuple(sum(Q(w)*sum(bs[p][i][r] for i in S) for p,S,w in coverage)
                +sum(sigma[p][i]*bs[p][i][r] for p in range(n) for i in range(owners))
                for r in range(3))
    assert residual==right
    return dict(gamma=gamma,lambda_incidence=lam,sigma=sigma,nu=list(map(Q,nu)),
                L_OUT=cov_value+rhs,L_TCWM=cov_value,D=D,resource_residual=residual)


def one_layer(edges):
    return not ({e[0] for e in edges}&{e[1] for e in edges})


def two_owner_fixture(name,xy,edges,nu,cov,middle,repair):
    bs=[[(Q(x),Q(0),Q(x)),(Q(0),Q(y),Q(0))] for x,y in xy]
    edges=[(l,h,C,1) for l,h,C in edges]
    coverage=[(cov,{0,1},1)]
    result=verify(bs,edges,coverage,nu,min)
    assert result['gamma'][middle]==[0,0]
    assert result['lambda_incidence'][middle]==result['sigma'][middle]==[0,0]
    assert nu[middle]==0
    active=[p for p in range(len(bs)) if p!=middle]
    candidates=[]; compatible=[]
    for l in active:
        for h in active:
            if l==h or not all(bs[h][i][r]>=bs[l][i][r] for i in range(2) for r in range(3)):
                continue
            changed={i for i in range(2) if bs[l][i]!=bs[h][i]}
            for C in [{0},{1},{0,1}]:
                if not changed<=C: continue
                candidates.append((l,h,sorted(C)))
                if all(result['gamma'][l][i]<0 and result['gamma'][h][i]>0 for i in C):
                    compatible.append((l,h,sorted(C)))
    assert candidates and not compatible
    repair_edges=[(*repair,{0,1},1)]
    repaired=verify(bs,repair_edges,coverage,nu,min)
    assert one_layer(repair_edges)
    assert repaired['D']==result['D'] and repaired['L_OUT']==result['L_OUT']
    result.update(name=name,profiles=xy,candidate_terminal_rows=candidates,
                  compatible_terminal_rows=compatible,
                  preserved_lambda_nu_sigma_impossibility="symbolic proof in companion note; not inferred from enumeration",
                  sigma_free_repair=repaired,all_checks_passed=True)
    return result


def sigma_free_fixed_budget_obstruction(eps):
    coords=[(1,1,1),(2,2,0),(2,2,1),(2,2,2)]
    bs=[[(Q(x),Q(0),Q(0)),(Q(0),Q(y),Q(0)),(Q(0),Q(0),Q(z))] for x,y,z in coords]
    F=lambda b:min(b[0],b[1])+eps*b[2]
    edges=[(0,2,{0,1},1),(1,2,{2},2),(2,3,{0,2},1),(2,3,{1,2},1)]
    coverage=[(0,{0,1},1)]; nu=[0,0,0,2]
    original=verify(bs,edges,coverage,nu,F)
    assert original['gamma']==[[-1,-1,0],[0,0,-2],[0,0,0],[1,1,2]]
    assert original['L_OUT']==2+4*eps and original['D']==4+4*eps
    assert original['sigma']==[[0,0,0],[0,0,2],[0,0,0],[1,1,0]]
    # All possible sinks of a one-layer feasible dual with these fixed nu
    # belong to the positive-budget support {3}; enumerate every coalition.
    allowed_coalitions=[set(C) for size in [1,2] for C in combinations(range(3),size)]
    changed_a_z={i for i in range(3) if bs[0][i]!=bs[3][i]}
    assert len(changed_a_z)==3
    assert not any(changed_a_z<=C for C in allowed_coalitions)
    # Relax the budget by funding p. Direct b->z has twice the K restoration.
    escape_edges=[(0,2,{0,1},1),(1,3,{2},2)]
    escape=verify(bs,escape_edges,coverage,[0,0,1,2],F)
    assert one_layer(escape_edges)
    assert escape['L_OUT']==original['L_OUT']
    assert escape['D']==6+5*eps
    assert escape['D']/original['D']<=Q(3,2)
    return dict(epsilon=eps,profiles=coords,original=original,
                a_to_z_changed_owners=sorted(changed_a_z),
                fixed_lambda_nu_free_sigma_impossibility="symbolic proof in companion note; not inferred from enumeration",
                budget_inflation_escape=escape,
                escape_cost_ratio=escape['D']/original['D'],all_checks_passed=True)


def serial(value):
    if isinstance(value,Q): return str(value)
    if isinstance(value,dict): return {k:serial(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [serial(v) for v in value]
    return value


if __name__=='__main__':
    merge=two_owner_fixture('unique_sink',[(1,2),(2,1),(2,2),(3,3)],
        [(0,2,{0}),(1,2,{1}),(2,3,{0,1})],[0,0,0,2],3,2,(0,3))
    split=two_owner_fixture('unique_source',[(1,1),(2,2),(3,2),(2,3)],
        [(0,1,{0,1}),(1,2,{0}),(1,3,{1})],[0,0,1,1],0,1,(0,2))
    assert (merge['L_OUT'],merge['D'])==(4,6)
    assert (split['L_OUT'],split['D'])==(2,4)
    strong=[sigma_free_fixed_budget_obstruction(eps) for eps in [Q(1,100),Q(1,2),Q(1),Q(10)]]
    print(json.dumps(serial(dict(slack_preserving_examples=[merge,split],
        sigma_free_fixed_budget_obstructions=strong,
        evidence='Exact arithmetic checks supplement the symbolic obstruction proofs.')),indent=2))
