"""Exact certificates for the active-owner rank-three ladder."""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json


def ladder_D(M, s):
    product = Q(1)
    for m in range(2, M+1):
        k = min(s-1, 2*m-2)
        product *= Q(k,k+1)
    return (M-1)*product


def funding_lower(D, R):
    return (R*R+D*R)/(R*R+D)


def main():
    product_checks = recurrence_checks = elimination_checks = maxima_checks = 0
    A=Q(1)
    for M in range(1,301):
        if M>1:
            A *= Q(2*M,2*M-1)
        assert A == Q(4**M, 2*comb(2*M,M))
        if M>1:
            D=ladder_D(M,2*M-1)
            assert D==(1-Q(1,M))*A
            for R in range(2,13):
                lower=funding_lower(D,R)
                assert lower==1+D/R-D*lower/(R*R)
                # Bootstrap may have a negative lower: elimination is still exact.
                for kappa in (Q(1),Q(2),Q(7,2),Q(15)):
                    final_bound=1+D*(Q(1,R)-kappa/(R*R))
                    assert (kappa>=final_bound)==(kappa>=lower)
                    elimination_checks+=1
        product_checks+=1
    for s in range(2,131):
        values={M:ladder_D(M,s) for M in range(2,2*s+3)}
        assert values[s]==values[s+1]==max(values.values())
        m0=(s+1)//2
        A0=Q(4**m0,2*comb(2*m0,m0))
        assert values[s]==Q(s-1,m0)*A0*Q(s-1,s)**(s-m0)
        for M in range(2,2*s+2):
            k=min(s-1,2*M)
            assert values[M+1]/values[M]==Q(M,M-1)*Q(k,k+1)
            recurrence_checks+=1
        maxima_checks+=1
    D84=ladder_D(84,167)
    low84=funding_lower(D84,4)
    assert ladder_D(83,165)<=8<D84
    assert low84==Q(181672767161629977921046690736847227014054680515183,
                   90694290237781271262867309900258609040472879714927)
    assert low84>Q(20031,10000)
    D113=ladder_D(113,113)
    low113=funding_lower(D113,4)
    assert all(ladder_D(s,s)<=8 for s in range(2,113))
    assert D113>8 and low113>Q(20007,10000)
    result={
        "status":"PASS","arithmetic":"fractions.Fraction, exact",
        "central_binomial_product_checks":product_checks,
        "bounded_coalition_recurrence_checks":recurrence_checks,
        "funding_elimination_checks":elimination_checks,
        "bounded_coalition_exact_maxima":maxima_checks,
        "smaller_owner_certificate":{"M":84,"R":4,"s":167,"actual_owners":172,
                                     "resource_rows":169,"D":str(D84),"funding_lower":str(low84)},
        "smaller_coalition_certificate":{"M":113,"R":4,"s":113,"actual_owners":230,
                                         "resource_rows":227,"D":str(D113),"funding_lower":str(low113)},
        "scope":"Exact finite algebra certificates for the analytic all-profile lower; no optimality or novelty claim."
    }
    Path(__file__).with_name("finite_arity_three_ladder_checks.json").write_text(json.dumps(result,indent=2)+"\n")
    compact={k:v for k,v in result.items() if k not in ('smaller_owner_certificate','smaller_coalition_certificate')}
    compact["smaller_owner_certificate"]={k:v for k,v in result["smaller_owner_certificate"].items() if k!='D'}
    compact["smaller_coalition_certificate"]={k:v for k,v in result["smaller_coalition_certificate"].items() if k not in ('D','funding_lower')}
    print(json.dumps(compact,indent=2))


if __name__=='__main__':
    main()
