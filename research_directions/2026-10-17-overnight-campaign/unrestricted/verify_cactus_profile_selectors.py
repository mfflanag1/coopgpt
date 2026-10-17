from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path

if not __debug__:raise RuntimeError('Assertions must remain enabled')

# Reuse only the exact rational solver definitions, not prior test outcomes.
# These independently enumerate all candidate KKT bases and LP vertices.
source=Path(__file__).with_name('verify_efficient_incidence_two.py').read_text()
namespace={}
exec(source.split('\nfamilies=')[0],namespace)
projection_solver=namespace['projection_solver']
vertex_solver=namespace['vertex_solver']
dot=namespace['dot']

families=[
 ('single_cycle_both_degrees_three',5,[(0,1,2),(0,1,3),(0,4)]),
 ('two_cycles_sharing_row_with_pin',6,[(0,1,2,3),(0,1,4),(2,3,5),(0,)]),
 ('two_cycles_sharing_row_with_branch',7,[(0,1,2,3),(0,1,4),(2,3,5),(0,6)]),
]
profiles=pairs=0
for name,n,sets in families:
    A=[tuple(Q(i in S) for i in range(n)) for S in sets];m=len(A)
    C=A+[tuple(Q(i==j) for j in range(n)) for i in range(n)]
    lp=vertex_solver(C,n);project=projection_solver(C,n)
    efficient=projection_solver(C+[tuple([Q(1)]*n),tuple([Q(-1)]*n)],n)
    demands={tuple([Q(1)]*m),tuple([Q(0)]*m)}
    for r in range(m):
        for amount in (Q(0),Q(1,2),Q(3,2),Q(2)):
            b=[Q(1)]*m;b[r]=amount;demands.add(tuple(b))
    for i in range(n):
        b=[Q(1,2) if row[i] else Q(1) for row in A]
        demands.add(tuple(b))
    targets=[tuple([Q(0)]*n),tuple([Q(-1)]*n),tuple([Q(-4)]*n),
             tuple(Q(3,2) if i%2 else Q(-2) for i in range(n))]
    solved={}
    for b in sorted(demands):
        rhs=list(b)+[Q(0)]*n;T=lp(rhs)
        e=efficient(rhs+[T,-T],[Q(0)]*n)
        qs=[project(rhs,target) for target in targets]
        assert sum(e)==T
        for epsilon,q in zip((Q(1),Q(1,4)),qs[1:3]):
            assert sum(q)+epsilon*dot(q,q)/2<=T+epsilon*dot(e,e)/2
            assert dot(q,q)<=dot(e,e)
        solved[b]=[e]+qs;profiles+=1
    localpairs=0
    for lo,ql in solved.items():
        for hi,qh in solved.items():
            for i in range(n):
                if all(lo[r]<=hi[r] if A[r][i] else lo[r]==hi[r] for r in range(m)):
                    assert all(x[i]<=y[i] for x,y in zip(ql,qh)),(name,i,lo,hi,ql,qh)
                    pairs+=1;localpairs+=1
    print({'family':name,'owners':n,'profiles':len(solved),
           'comparable_pairs':localpairs,'status':'PASS'},flush=True)
print({'status':'PASS','families':len(families),'exact_profiles':profiles,
       'own_comparable_pairs':pairs,'selectors_per_profile':5,
       'scope':'Exact efficient selector plus four fixed-target projections; finite checks supplement the general proof.'})
