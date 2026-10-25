"""Exact replay of the specified finite theorem; standard library only."""
from fractions import Fraction as Q
import itertools
import json

N = range(4)
bundles = ((1,0,2),(0,2,0),(2,0,1),(1,2,2))
reports = (((1,0,2),(0,0,0),(0,0,0),(1,2,2)),
           ((1,0,2),(0,0,0),(2,0,1),(1,2,2)),
           ((1,0,2),(0,2,0),(0,0,0),(1,2,2)))
masks = range(1,16)
members = lambda S: [i for i in N if S >> i & 1]
production = lambda cap: min(cap)


def coalition_value(p,S):
    return production(tuple(sum(reports[p][i][j] for i in members(S)) for j in range(3)))


def comparisons():
    rows=[]
    for l,h in itertools.permutations(range(3),2):
        if any(reports[l][i][j]>reports[h][i][j] for i in N for j in range(3)):continue
        changed={i for i in N if reports[l][i]!=reports[h][i]}
        delta=tuple(sum(reports[h][i][j]-reports[l][i][j] for i in N) for j in range(3))
        for C in masks:
            if C.bit_count()<=2 and changed.issubset(members(C)):
                rows.append((l,h,C,production(delta)))
    return rows


def check_payments(pay,k):
    for p in range(3):
        assert all(v>=0 for v in pay[p])
        assert sum(pay[p])<=k*coalition_value(p,15)
    for l,h,C,d in comparisons():
        assert sum(pay[h][i]-pay[l][i] for i in members(C))>=d
    return {(p,S) for p in range(3) for S in masks
            if sum(pay[p][i] for i in members(S))<coalition_value(p,S)}


def main():
    global reports
    assert __debug__, 'Run without Python -O: assertions are the verifier.'
    assert all(0<=reports[p][i][j]<=bundles[i][j] for p in range(3) for i in N for j in range(3))
    assert [coalition_value(p,15) for p in range(3)]==[2,2,2]
    cmp=comparisons(); assert len(cmp)==8 and all(d==0 for *_,d in cmp)
    lam={(0,9):1,(1,9):1,(1,12):1,(2,3):1,(2,9):1}
    mu={(0,1,5):1,(0,2,10):1};nu=(0,2,2)
    g=[[Q(0) for i in N] for p in range(3)]
    L=Q(0)
    for (p,S),w in lam.items():
        L+=w*coalition_value(p,S)
        for i in members(S):g[p][i]+=w
    for (l,h,C),w in mu.items():
        assert (l,h,C,0) in cmp
        for i in members(C):g[l][i]-=w;g[h][i]+=w
    assert g==[[0,-1,-1,0],[2,0,2,2],[2,2,0,2]]
    assert all(g[p][i]<=nu[p] for p in range(3) for i in N)
    D=sum(nu[p]*coalition_value(p,15) for p in range(3))
    assert L==9 and D==8
    pay=((Q(1,2),0,0,Q(3,2)),(Q(1,4),0,Q(1,4),Q(7,4)),(Q(3,4),Q(1,4),0,Q(5,4)))
    assert check_payments(pay,Q(9,8))==set()
    u=((0,0,0,2),)*3;v=(u[0],u[1],(0,1,0,1))
    bad_u=check_payments(u,1);bad_v=check_payments(v,1)
    assert bad_u=={(2,3),(2,7)} and bad_v=={(2,9),(2,13)}
    for _,S in bad_u:
        for _,T in bad_v:assert S&T and S&~T and T&~S
    # Independently enumerate every coverage support at q, not only maximal
    # laminar families. At a,p both arrays cover all possible rows.
    count=0
    for bitmap in range(1<<15):
        family=[S for S in masks if bitmap>>(S-1)&1]
        if any(S&T and S&~T and T&~S for S,T in itertools.combinations(family,2)):continue
        count+=1
        assert not any((2,S) in bad_u for S in family) or not any((2,S) in bad_v for S in family)
    assert count==832
    # Exact positive-report perturbation, independent of the symbolic
    # epsilon-family argument in the proof.
    epsilon=Q(1,32)
    reports=tuple(tuple(tuple(epsilon*x for x in bundles[i]) if not any(row) else row
                        for i,row in enumerate(profile)) for profile in reports)
    assert all(any(row) for profile in reports for row in profile)
    assert all(coalition_value(p,15)==2+2*epsilon for p in range(3))
    assert sum(w*coalition_value(p,S) for (p,S),w in lam.items())==9
    assert comparisons()==cmp
    shifted=lambda table: tuple(tuple(Q(v)+ (2*epsilon if i in (1,2) else 0)
                                      for i,v in enumerate(row)) for row in table)
    laminar_upper=(1+2*epsilon)/(1+epsilon)
    assert check_payments(shifted(u),laminar_upper).issubset(bad_u)
    assert check_payments(shifted(v),laminar_upper).issubset(bad_v)
    lower=Q(9)/(8*(1+epsilon))
    perturbed_D=sum(nu[p]*coalition_value(p,15) for p in range(3))
    assert perturbed_D==8*(1+epsilon) and Q(9)/perturbed_D==lower
    assert lower==Q(12,11)>laminar_upper==Q(34,33)
    print(json.dumps({'exact_finite_optimum':str(L/D),'laminar_optimum':'1',
       'profiles':3,'owners':4,'resources':3,'arity':3,'protection_size':2,
       'coverage_rows_checked':45,'comparisons_checked':len(cmp),
       'laminar_supports_exhausted_at_q':count,
       'dual_L':str(L),'dual_D':str(D),
       'failed_coverage_U':sorted(bad_u),'failed_coverage_V':sorted(bad_v),
       'positive_report_epsilon':str(epsilon),'positive_report_lower':str(lower),
       'positive_report_laminar_upper':str(laminar_upper),
       'evidence_scope':'Exact finite Q theorem; not an all-real-profile upper bound.'},indent=2))


if __name__=='__main__':main()
