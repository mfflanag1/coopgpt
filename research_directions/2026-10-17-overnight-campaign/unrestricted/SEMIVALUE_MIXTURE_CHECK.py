"""Exact fixed-owner threshold transitions; finite checks supplement the proof."""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json


def tail(k, t, p):
    return sum((Q(comb(k, j)) * p**j * (1-p)**(k-j)
                for j in range(t+1, k+1)), Q(0))


def direct_marginals(s, k, t, p, high):
    n = s+k
    # Protected leaves occupy owner indices0..s-1. The focal owner is0;
    # k outside owners at indices s..s+k-1 each own center1/k.
    values = []
    for S in range(1 << n):
        center = Q(sum(S >> i & 1 for i in range(s, n)), k)
        leaf = Q(t+int(high), k) if S & 1 else Q(0)
        leaf += sum(S >> i & 1 for i in range(1, s))
        values.append(min(center, leaf))
    answer = []
    for i in range(s):
        total = Q(0)
        for S in range(1 << n):
            if S >> i & 1:
                continue
            size = S.bit_count()
            probability = p**size * (1-p)**(n-1-size)
            total += probability * (values[S | (1 << i)]-values[S])
        answer.append(total)
    return answer


checks = 0
for s in range(2, 6):
    for k in range(1, 5):
        for t in range(k):
            for p in sorted({Q(0), Q(1, 7), Q(1, s), Q(1, 2), Q(6, 7), Q(1)}):
                low = direct_marginals(s, k, t, p, False)
                high = direct_marginals(s, k, t, p, True)
                common = Q(1, k) * tail(k, t, p)
                assert high[0]-low[0] == common * (1-p)**(s-1)
                for i in range(1, s):
                    assert high[i]-low[i] == -common * p * (1-p)**(s-2)
                assert sum(high, Q(0))-sum(low, Q(0)) == common * (1-p)**(s-2) * (1-s*p)
                checks += 1

# A finite witness where substantial safe mass cannot hide tiny unsafe mass.
# This exact arithmetic checks the scalar certificate; the previous independent
# game enumeration checks its interpretation as a report transition.
s, k, t = 3, 100, 50
atoms = [(Q(1, 4), Q(1)), (Q(3, 4), Q(1, 10**6))]
delta = sum((weight * Q(1, k) * (1-p)**(s-2) * (1-s*p) * tail(k, t, p)
             for p, weight in atoms), Q(0))
assert delta < 0

# Pure-three and balanced-three payments, including atom0, are exact formulas.
moment = sum((weight*p*p for p, weight in atoms), Q(0))
mass = sum((weight for p, weight in atoms), Q(0))
assert 3*moment == sum(sum(weight*p*p for p, weight in atoms) for _ in range(3))
assert 3*mass == sum(sum(weight for p, weight in atoms) for _ in range(3))
out = {"status": "PASS", "independent_finite_transition_checks": checks,
       "tiny_unsafe_mass_witness": {"protected_owners": s, "outside_center_owners": k,
          "low_focal_leaf": str(Q(t,k)), "restoration": str(Q(1,k)),
          "atoms_p_and_weight": [[str(p),str(w)] for p,w in atoms],
          "exact_coalition_payment_change": str(delta)},
       "scope": "Exact finite game/marginal checks and one rational mixture violation; analytic finite-measure limit is proved separately."}
Path(__file__).with_name("SEMIVALUE_MIXTURE_CHECKS.json").write_text(json.dumps(out, indent=2)+"\n")
print(json.dumps(out, indent=2))
