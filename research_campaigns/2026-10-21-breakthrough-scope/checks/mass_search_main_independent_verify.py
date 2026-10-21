#!/usr/bin/env python3
"""Independent stdlib audit of the 104-owner normalized amplification witness.

Only the selected independent sets and rational weights are trusted as input
data. Every claimed marginal, graph property, KKT parameter, and statistic is
recomputed here. No generation code, optimizer, NumPy, or SciPy is imported.

The row universe is all complements of independent 49-subsets of the graph
on Z/104Z with differences +/-1 and52. An off-owner row for i is the complement
of an independent set containing i. That set contains none of i's neighbors,
so it meets the closed neighborhood of i exactly once. With row size55, such
a row has3 local and52 nonlocal coordinates. This finite local implication
verifies every off-owner row without enumerating the entire row universe.

For each i give demand1 to all off-i rows and to translated positive-support
rows; give demand0 to the remaining incident rows. All positive multipliers
therefore have RHS1. Local payments are75/2929 and other payments52/2929;
each positive-support or off-owner row has total(3*75+52*52)/2929=1.
Nonnegative stationarity plus these facts gives the exact minimum-norm KKT
certificate. All104 translated witness supports are checked directly below.

Full projection: every row has size55, so constant q=1/55 is feasible.
Translate one supported row104 times. Every coordinate occurs55 times;
put multiplier1/3025 on each translated row. This gives exact stationarity,
complementarity, and rho=104/3025. H=6084/3025>2 follows. Transferring this
base witness to the original diagonal claim still requires finite union and
veto amplification and production realization; those are outside this audit.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path


def audit(source_bytes):
    raw=json.loads(source_bytes)
    n=104; universe=set(range(n)); focal=0
    # Rebuild by pairwise modular-distance predicate, independently of the
    # scout's support-generation method and certificate metadata.
    edges={(a,b) for a in range(n) for b in range(a+1,n) if (b-a)%n in (1,52,103)}
    neighbors=[set() for _ in range(n)]
    for a,b in edges:neighbors[a].add(b);neighbors[b].add(a)
    assert len(edges)==156 and all(len(v)==3 for v in neighbors)
    closed=neighbors[0]|{0};assert closed=={0,1,52,103}
    reached={0}
    for _ in range(n):reached|={j for i in reached for j in neighbors[i]}
    assert reached==universe
    # Rotation is a genuine transitive graph automorphism, not degree-based
    # inference. Check every edge under every required owner translation.
    for shift in range(n):
        assert {tuple(sorted(((a+shift)%n,(b+shift)%n))) for a,b in edges}==edges
    entries=raw['support'];assert len(entries)==101
    independent=[];weights=[]
    for entry in entries:
        I=set(entry['independent_set']);weight=F(entry['weight'])
        assert len(I)==len(entry['independent_set'])==49
        assert I<=universe and weight>0
        assert all(not (a in I and b in I) for a,b in edges)
        assert len(I&closed)==1
        independent.append(I);weights.append(weight)
    assert len({tuple(sorted(I)) for I in independent})==101
    assert sum(weights)==1
    marginal=[sum((weight for I,weight in zip(independent,weights) if j in I),F(0)) for j in range(n)]
    desired=[F(1,4) if j in closed else F(12,25) for j in range(n)]
    assert marginal==desired and sum(marginal)==49
    qhat=[1-x for x in marginal]
    t=F(3)*F(3,4)+F(52)*F(13,25)
    assert t==F(2929,100)
    dual_mass=1/t;q=[v/t for v in qhat]
    assert q==[F(75,2929) if j in closed else F(52,2929) for j in range(n)]
    assert sum(v*v for v in q)==dual_mass==F(100,2929)
    # Integer common-denominator accumulation avoids rounding and checks all
    # translated witnesses explicitly, rather than only asserting symmetry.
    denominator=math.lcm(*(w.denominator for w in weights))
    numerators=[int(w*denominator) for w in weights]
    assert sum(numerators)==denominator
    support_checks=0;coordinate_checks=0
    for owner in range(n):
        local=neighbors[owner]|{owner}
        payment_numerator=[75 if j in local else 52 for j in range(n)]
        incidence=[0]*n
        for I,numerator in zip(independent,numerators):
            moved={(j+owner)%n for j in I};row=universe-moved
            assert len(moved)==49 and len(row)==55
            assert all(not (a in moved and b in moved) for a,b in edges)
            assert len(moved&local)==1
            assert sum(payment_numerator[j] for j in row)==2929
            for j in row:incidence[j]+=numerator
            support_checks+=1
        # lambda_r=100*alpha_r/2929. Stationarity is checked as integers.
        assert all(100*incidence[j]==denominator*payment_numerator[j] for j in range(n))
        coordinate_checks+=n
    # Independent full projection certificate using one orbit of rows.
    original_row=universe-independent[0]
    orbit=[{(j+shift)%n for j in original_row} for shift in range(n)]
    assert len({tuple(sorted(S)) for S in orbit})==104
    full_incidences=[sum(j in S for S in orbit) for j in range(n)]
    assert full_incidences==[55]*n
    full_lam=F(1,55**2);full_q=[full_lam*d for d in full_incidences]
    assert full_q==[F(1,55)]*n
    assert all(sum(full_q[j] for j in S)==1 for S in orbit)
    rho=sum(v*v for v in full_q)
    assert rho==sum([full_lam]*n)==F(104,3025)
    theta=q[0]/dual_mass;assert theta==F(3,4)
    H=rho*n*theta*theta;assert H==F(6084,3025)>2
    E=n*q[0]**2
    assert E<2*rho  # The normalized route is essential for this witness.
    return {'certified':True,'scope':'Exact normalized base H>2; original diagonal transfer still requires amplification and production realization.',
            'source_sha256':hashlib.sha256(source_bytes).hexdigest(),
            'n':n,'edges':sorted(edges),'closed_neighborhood_focal':sorted(closed),
            'row_universe':'complements of every independent49-subset in the specified graph',
            'row_size':55,'support_count':len(entries),'all_weights_positive':True,
            'sum_weights':'1','common_weight_denominator':str(denominator),
            'minimum_weight':str(min(weights)),
            'independent_marginals_local':'1/4','independent_marginals_other':'12/25',
            'normalized_q_local':'3/4','normalized_q_other':'13/25',
            't':str(t),'q_local':'75/2929','q_other':'52/2929',
            'L':str(dual_mass),'norm2':str(sum(v*v for v in q)),
            'full_q':'1/55','full_orbit_rows':104,'full_multiplier_per_orbit_row':str(full_lam),
            'rho':str(rho),'theta':str(theta),'H':str(H),'H_minus_two':str(H-2),
            'raw_E_over_rho':str(E/rho),'raw_E_exceeds_two_rho':False,
            'checked_owner_translations':104,'checked_support_rows':support_checks,
            'checked_stationarity_coordinates':coordinate_checks,
            'all_off_row_argument':'Independent set containing owner i meets its closed neighborhood exactly at i; complementary row therefore has3 local and52 other coordinates, giving exact payment1.',
            'proof':__doc__}


def main():
    here=Path(__file__).parent
    parser=argparse.ArgumentParser();parser.add_argument('--input',default=str(here.parent/'proofs/activation_mass_certificate.txt'));parser.add_argument('--output',default=str(here/'mass_search_main_independent_certificate.json'));args=parser.parse_args()
    result=audit(Path(args.input).read_bytes());Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('certified','n','support_count','checked_support_rows','checked_stationarity_coordinates','rho','L','theta','H','H_minus_two','scope')},indent=2))


if __name__=='__main__':main()
