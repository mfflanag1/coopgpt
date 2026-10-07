#!/usr/bin/env python3
"""Exact finite checks of the owner-count hierarchy parameter translation.

Replays actual weighted-report certificates at small pool counts for the new
m,alpha parameters. Separately checks exact large-pool tail suppression for
h=2,3; it does NOT enumerate all histograms at those much larger pool counts.
The all-size/asymptotic claims use OWNER_COUNT_LOWER.txt, not this finite check.
"""
from fractions import Fraction as Q
import importlib.util
import json
from math import factorial
from pathlib import Path
import sys


def require(ok, message):
    if not ok:
        raise ValueError(message)


def run():
    repo = Path(__file__).resolve().parents[3]
    support = repo / "paper5/truthful_cooperation/verification/sharp"
    sys.path.insert(0, str(support))
    path = support / "poisson_certificate.py"
    require(path.is_file(), "missing original weighted certificate generator")
    spec = importlib.util.spec_from_file_location("owner_count_weighted_certificate", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows, certificates, rejected = [], [], 0
    for h, R, s in ((2, 2, 2), (3, 2, 2)):
        m, alpha = h*s, Q(1, s)
        A = (h+1)*m-h*h
        lam = A/alpha
        Z = sum((lam**r/factorial(r) for r in range(h+1)), Q(0))
        K = (2*R*Z.numerator+Z.denominator-1)//Z.denominator
        require(m > h and K >= 2, "hierarchy parameter domain")
        require(Q(K)/Z >= 2*R, "pool count ceiling")
        require(Q(A, m) == h+1-Q(h, s), "normalized lower numerator")
        # Exact rational comparison, avoiding any floating exponential/log bound.
        p0 = 1/Z
        power = (1-p0)**K
        require(power <= Q(1, (h+1)**2), "actual large-K tail bound")
        require((lam**h/factorial(h)) <= Z <= (h+1)*lam**h/factorial(h),
                "Poisson normalizer bounds")
        lower = (h+1-Q(h,s))/((1+alpha)*(1+Q(h,(h+1)**2)))
        rows.append(dict(height=h,R=R,s=s,owners_per_pool=m,alpha=str(alpha),
                         poisson_lambda=str(lam),normalizer=str(Z),
                         large_pool_count=K,total_owners=K*m,
                         tail_denominator_bits=power.denominator.bit_length(),
                         conservative_lower=str(lower),
                         large_pool_histograms_enumerated=False))
        for pools in (2,3,5):
            certificate, metadata = module.construct(pools,h,m,alpha)
            result = module.verify(certificate)
            require(Q(metadata["lambda"]) == lam, "imported lambda mismatch")
            require(Q(metadata["p0"]) == 1/Z, "imported normalizer mismatch")
            require(Q(metadata["weaker_theorem_bound"]) ==
                    Q(A)/((1+alpha)*Q(metadata["expected_T"])),
                    "imported finite lower formula mismatch")
            controls = module.controls(certificate)
            rejected += controls
            certificates.append(dict(height=h,pools=pools,rows=result["rows"],
                                     factor=result["factor"],rejected_corruptions=controls))
    require(rejected == 42, "missing corruption controls")
    return dict(status="PASS",parameter_cases=rows,small_pool_certificates=certificates,
                rejected_corruptions=rejected,
                scope="Finite exact parameter/certificate checks only; no all-size, sharp owner-count, or novelty inference.")


if __name__ == "__main__":
    print(json.dumps(run(),indent=2))
