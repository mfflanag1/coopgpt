#!/usr/bin/env python3
"""Exact star-swap family theorem: normalized amplification H is exactly 1.

For N>=4 take the N permutation rows P_0=identity and P_j=swap(0,j).
Columns are their 3N-2 supported matrix entries. Write normalized dual masses
alpha_0=a, alpha_j=b_j, a+sum_j b_j=1. Direct Gram multiplication gives

    p_0=N-2+2a,                 p_j=N-3+a+3b_j.

The normalized KKT conditions are p_r>=t for every off-owner row and
p_r<=t for every supported own row, with p_r=t for supported off rows.

Owner (0,0), theta=a. If a>0, some swap has positive mass: otherwise a=1
and p_0=N<=t<=N-2 is impossible. Any zero-mass swap would have potential
strictly below that positive supported off swap, contradicting feasibility.
Thus all N-1 swap masses are equal (1-a)/(N-1), and p_0<=t gives
N-4+(N+2)a<=0, impossible for N>=4 and a>0. Hence theta=0.

Owner (0,j) or (j,0), theta=b_j. If b_j>0 its own row has p_j<=t, whereas
every other swap row has p_k>=t. Hence b_j<=b_k for all k!=j and
(N-1)b_j<=sum_k b_k=1-a<=1. Therefore theta<=1/(N-1).

Owner (j,j), j>0, theta=1-b_j. Its only off row is j. If b_j=0, every
positive other swap would have p_k>p_j>=t and violate the own upper bound;
therefore all other swap masses vanish, a=1, and p_0=N>p_j=N-2 again
contradicts the own bound. Thus b_j>0 and t=p_j. If a=0, supported own
swap rows satisfy b_k<=b_j; zero ones do too, so b_j>=1/(N-1). If a>0,
p_0<=p_j gives 1+a<=3b_j, whence b_j>1/3>=1/(N-1). Thus theta<=
(N-2)/(N-1).

All three upper bounds are attained simultaneously by alpha_0=0 and
alpha_j=1/(N-1), the full projection's normalized masses. Put
D=(N-2)^2+2. Full multipliers are lambda_0=0, lambda_j=1/D. Then q_(0,0)=0,
q_(0,j)=q_(j,0)=1/D, q_(j,j)=(N-2)/D. Swap rows have value 1; identity
has value (N-1)(N-2)/D>=1, exactly because N>=4. This proves full KKT and
rho=(N-1)/D. Hence

    H=rho*[2(N-1)/(N-1)^2+(N-1)(N-2)^2/(N-1)^2]=1.

The general bound above is algebraic. Finite Fraction checks below verify
the stated matrices, full KKT certificates, orbit actions, and H identities;
they are supporting checks, not the source of the general theorem.
"""
from fractions import Fraction as F
import argparse
import hashlib
import json
from pathlib import Path


def family(N):
    labels = [(j,j) for j in range(N)] + [(0,j) for j in range(1,N)] + [(j,0) for j in range(1,N)]
    index = {edge:i for i,edge in enumerate(labels)}
    permutations = [list(range(N))]
    for j in range(1,N):
        perm = list(range(N)); perm[0],perm[j] = j,0; permutations.append(perm)
    rows = [sorted(index[(j,perm[j])] for j in range(N)) for perm in permutations]
    return labels,rows


def certificate(N):
    assert N>=4
    labels,rows = family(N); n=len(labels); D=(N-2)**2+2
    lam = [F(0)] + [F(1,D)]*(N-1)
    q = [sum((lam[r] for r,S in enumerate(rows) if j in S),F(0)) for j in range(n)]
    for r,S in enumerate(rows):
        val=sum(q[j] for j in S)
        assert val>=1 and lam[r]*(val-1)==0
    rho=sum(x*x for x in q); assert rho==F(N-1,D)==sum(lam)
    alpha=[x/rho for x in lam];theta=[sum((alpha[r] for r,S in enumerate(rows) if j in S),F(0)) for j in range(n)]
    assert theta[0]==0
    assert all(theta[j]==F(N-2,N-1) for j in range(1,N))
    assert all(theta[j]==F(1,N-1) for j in range(N,n))
    assert rho*sum(x*x for x in theta)==1
    # Verify the Gram formulas independently of symbolic derivation.
    for r,S in enumerate(rows):
        for k,T in enumerate(rows):
            expected=N if r==k else (N-2 if 0 in (r,k) else N-3)
            assert len(set(S)&set(T))==expected
    # A peripheral cycle and matrix transpose generate exactly three orbits.
    index={edge:j for j,edge in enumerate(labels)}
    cycle=lambda j: 0 if j==0 else 1+j%(N-1)
    generators=[[index[(cycle(a),cycle(b))] for a,b in labels], [index[(b,a)] for a,b in labels]]
    row_index={tuple(row):r for r,row in enumerate(rows)}; row_perms=[]
    for generator in generators:
        assert sorted(generator)==list(range(n))
        row_perms.append([row_index[tuple(sorted(generator[j] for j in row))] for row in rows])
    orbits=[]; uncovered=set(range(n))
    while uncovered:
        orbit={min(uncovered)};todo=list(orbit)
        while todo:
            j=todo.pop()
            for generator in generators:
                k=generator[j]
                if k not in orbit:orbit.add(k);todo.append(k)
        uncovered-=orbit;orbits.append(sorted(orbit))
    assert sorted(map(len,orbits))==[1,N-1,2*(N-1)]
    return {'N':N,'n_owners':n,'rows':rows,'column_labels':labels,
            'full':{'q':list(map(str,q)),'lambda':list(map(str,lam)),'rho':str(rho),'certified':True},
            'normalized_theta':list(map(str,theta)),'H':'1',
            'symmetry':{'owner_generators':generators,'row_permutations':row_perms,'owner_orbits':orbits,'verified':True}}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--numerical',action='store_true');args=parser.parse_args()
    reports=[certificate(N) for N in (4,5,6,8,12,20)]
    if args.numerical:
        import numpy as np
        import normalized_mass_search as core
        for report in reports:
            N=report['N']
            if N not in (5,8):continue
            rows=report['rows'];n=report['n_owners'];A=np.array([[int(j in S) for j in range(n)] for S in rows],dtype=float)
            lam=np.array([float(F(x)) for x in report['full']['lambda']]);rho=float(F(report['full']['rho']));baseline=(lam/rho,1/rho)
            ans=[core.optimize_owner(A,j,seconds=10,baseline=baseline) for j in (0,N,1)]
            expected=[F(0),F(1,N-1),F(N-2,N-1)]
            assert all(a['valid'] and abs(a['theta']-float(e))<1e-7 for a,e in zip(ans,expected))
            report['numerical_calibration']=ans
    payload={'theorem':'For every N>=4 the star-swap perfect-matching cover has normalized H=1 exactly.','proof':__doc__,'reports':reports,'numerical_results_are_not_proof':True,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    Path(args.output).write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({'status':'PASS','N_checked':[r['N'] for r in reports],'H':'1','general_proof':'included in module docstring and JSON'},indent=2))


if __name__=='__main__':main()
