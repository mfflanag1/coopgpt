#!/usr/bin/env python3
"""Independent exact check of the172-owner base and its570-block veto lift.

No search/solver module is imported. Only raw independent sets and their
Fraction weights are read. Graph, marginals, all translated base witnesses,
and full-projection orbit multipliers are recomputed independently.

Graph: cycle C172 plus antipodal matching. Rows: complements of all its
independent83-subsets. Every row has89 vertices. For focal i, an independent
set containing i avoids all3 neighbors; hence its complementary off-i row
contains3 closed-neighborhood vertices and86 others. Payments63/3887 locally
and43/3887 elsewhere total1 on every such row. Each certified positive row
also has this local incidence. Set demand1 on off-i and positive-support
rows, demand0 on other own rows. Stationarity and complementarity then certify
the unique minimum-norm point, with L=84/3887 and p_i=63/3887.

The full point is1/89 per vertex. Translates of any supported row give172
valid rows, each coordinate appearing89 times. Multipliers1/7921 therefore
certify rho=172/7921. All172 owner witnesses follow by checked translations.

For J=570 take J disjoint base blocks and a common veto u; each full row is
u+x^b(S)>=1. T=min l1=1 (u=1 is feasible and any row requires total>=1).
Its full projection is u0=J*rho/(1+J*rho), x^b=z/(1+J*rho). For any block
owner use a=1/[1+(J-1)rho+L], u=1-a, focal block a*q, other blocks a*z.
Scale focal multipliers by a and others by a; their mass is u, certifying
veto stationarity. Incident demand is u+a*b_S, all off-owner demands stay1.
Thus all J*172 block owners have envelope at least a*p, and the veto owner
has envelope at least u0. The exact diagonal lower bound exceeds T^2=1.
The finite production realization is outside this independent cover audit.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path


def verify(raw_bytes):
    raw=json.loads(raw_bytes);n=172;U=set(range(n));k=89;isize=83
    # Independent pairwise graph reconstruction; no generator imports.
    edges={(a,b) for a in range(n) for b in range(a+1,n) if b-a in (1,86,171)}
    adjacency=[set() for _ in range(n)]
    for a,b in edges:adjacency[a].add(b);adjacency[b].add(a)
    assert len(edges)==258 and all(len(N)==3 for N in adjacency)
    local0={0}|adjacency[0];assert local0=={0,1,86,171}
    for shift in range(n):
        assert {tuple(sorted(((a+shift)%n,(b+shift)%n))) for a,b in edges}==edges
    weights=[];sets=[]
    assert len(raw['support'])==168
    for entry in raw['support']:
        I=set(entry['independent_set']);a=F(entry['weight'])
        assert len(I)==len(entry['independent_set'])==isize and I<=U and a>0
        assert all(not ({x,y}<=I) for x,y in edges)
        assert len(I&local0)==1
        sets.append(I);weights.append(a)
    assert len({tuple(sorted(I)) for I in sets})==168 and sum(weights)==1
    marginals=[sum((a for a,I in zip(weights,sets) if v in I),F(0)) for v in range(n)]
    assert marginals==[F(1,4) if v in local0 else F(41,84) for v in range(n)]
    assert sum(marginals)==isize
    D=math.lcm(*(a.denominator for a in weights));nums=[int(a*D) for a in weights]
    assert sum(nums)==D
    row_checks=0;stationarity_checks=0
    for owner in range(n):
        local={owner}|adjacency[owner];qn=[63 if v in local else 43 for v in range(n)]
        stationarity=[0]*n
        for I,a in zip(sets,nums):
            moved={(v+owner)%n for v in I};row=U-moved
            assert len(row)==k and len(moved&local)==1
            assert all(not ({x,y}<=moved) for x,y in edges)
            assert sum(qn[v] for v in row)==3887
            for v in row:stationarity[v]+=a
            row_checks+=1
        # lambda=84*alpha/3887, q=qn/3887: exact integer stationarity.
        assert all(84*stationarity[v]==D*qn[v] for v in range(n))
        stationarity_checks+=n
    q=[F(63,3887) if v in local0 else F(43,3887) for v in range(n)]
    L=F(84,3887);p=q[0]
    assert sum(v*v for v in q)==L
    assert p/L==F(3,4)
    # Full-point KKT from a directly counted translation orbit.
    row0=U-sets[0];orbit=[{(v+s)%n for v in row0} for s in range(n)]
    assert len({tuple(sorted(S)) for S in orbit})==172
    counts=[sum(v in S for S in orbit) for v in range(n)];assert counts==[89]*n
    full_lambda=F(1,7921);z=[count*full_lambda for count in counts]
    assert z==[F(1,89)]*n
    assert all(sum(z[v] for v in S)==1 for S in orbit)
    rho=sum(v*v for v in z);assert rho==172*full_lambda==F(172,7921)
    E=n*p*p;H=rho*n*F(3,4)**2
    assert E/rho==F(31438449,15108769)>2 and H==F(16641,7921)>2
    # Finite common-veto lift; no numerical thresholds or asymptotics.
    J=570;excess=E-2*rho;assert J*excess>1
    full_scale=1/(1+J*rho);u_full=J*rho*full_scale
    assert u_full+full_scale==1
    assert J*full_scale*rho==u_full  # Full veto stationarity.
    a=1/(1+(J-1)*rho+L);u=1-a
    assert a*((J-1)*rho+L)==u       # Relaxed veto stationarity.
    assert 0<u<1 and 0<a<1
    assert u+a==1                   # Every off-owner row remains demand1.
    # Focal supported rows and all nonfocal rows have base value1.
    assert u+a*sum(q[v] for v in U-sets[0])==1
    assert all(u+a*sum(z[v] for v in S)==1 for S in orbit)
    diagonal=u_full*u_full+J*n*(a*p)**2
    conservative=(J*J*rho*rho+J*E)/(1+J*rho)**2
    gap_bound=(J*excess-1)/(1+J*rho)**2
    assert conservative-1==gap_bound>0
    assert L<=rho and diagonal>=conservative>1
    assert gap_bound==F(170738667911,169637232162345649)
    return {'certified':True,'scope':'Exact base and finite common-veto cover diagonal violation; production realization remains a separate obligation.',
            'source_sha256':hashlib.sha256(raw_bytes).hexdigest(),
            'n':n,'graph_edges':sorted(edges),'row_size':k,'independent_set_size':isize,
            'support_count':len(sets),'common_weight_denominator':str(D),'minimum_weight':str(min(weights)),
            'independent_marginals_local':'1/4','independent_marginals_other':'41/84',
            'q_local':'63/3887','q_other':'43/3887','L':str(L),'t':str(1/L),
            'full_q':'1/89','full_orbit_multiplier':str(full_lambda),'rho':str(rho),
            'theta':'3/4','E':str(E),'E_over_rho':str(E/rho),'E_minus_two_rho':str(excess),'H':str(H),
            'checked_translated_support_rows':row_checks,'checked_stationarity_coordinates':stationarity_checks,
            'veto_blocks':J,'final_owners':J*n+1,'full_veto_payment':str(u_full),
            'relaxed_scale':str(a),'relaxed_veto_payment':str(u),'focal_block_owner_payment':str(a*p),
            'minimum_l1':'1','diagonal_lower_bound':str(diagonal),'diagonal_gap':str(diagonal-1),
            'conservative_diagonal_gap':str(gap_bound),'proof':__doc__}


def main():
    here=Path(__file__).parent
    parser=argparse.ArgumentParser();parser.add_argument('--input',default=str(here.parent/'proofs/activation_mass_certificate_172.txt'));parser.add_argument('--output',default=str(here/'mass_search_main_independent_172.json'));args=parser.parse_args()
    result=verify(Path(args.input).read_bytes());Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('certified','n','support_count','checked_translated_support_rows','rho','L','E_over_rho','H','veto_blocks','final_owners','conservative_diagonal_gap','scope')},indent=2))


if __name__=='__main__':main()
