"""Exact algebraic audit for the Shannon defect-stability corollary."""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction as F
from pathlib import Path

from verify_n5_exact_leximin_monotonicity_counterexample import (
    BASE_GENERATORS,
    PHI_BASE,
    lower_envelope,
)


# Elements a+b*sqrt(43), represented exactly as pairs of rationals.
def qadd(left, right):
    return left[0] + right[0], left[1] + right[1]


def qmul(left, right):
    return (
        left[0] * right[0] + F(43) * left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def qsub(left, right):
    return left[0] - right[0], left[1] - right[1]


def qnonnegative(value):
    a, b = value
    if b == 0:
        return a >= 0
    if b > 0:
        return a >= 0 or F(43) * b * b >= a * a
    return a >= 0 and a * a >= F(43) * b * b


def qvalue(value):
    return float(value[0]) + float(value[1]) * math.sqrt(43)


def qsum(values):
    result = (F(0), F(0))
    for value in values:
        result = qadd(result, value)
    return result


def entropy(point):
    return -sum(value * math.log(value) for value in point if value > 0)


def audit_five_state_upper_entropy():
    root = "sqrt(43)"
    candidate = (
        (F(-12), F(2)),
        (F(14), F(-2)),
        (F(13), F(-1)),
        (F(-8), F(2)),
        (F(13), F(-1)),
    )
    if qsum(candidate) != (F(20), F(0)):
        raise AssertionError("upper-entropy candidate has wrong total")
    if not all(qnonnegative(value) for value in candidate):
        raise AssertionError("upper-entropy candidate is not positive")
    values = lower_envelope(BASE_GENERATORS)
    for coalition in range(1, 1 << 5):
        amount = qsum(
            candidate[i] for i in range(5) if coalition >> i & 1
        )
        if not qnonnegative(qsub(amount, (F(values[coalition]), F(0)))):
            raise AssertionError(f"candidate violates coalition {coalition}")
    left = 0b10101  # {1,3,5}
    right = 0b11100  # {3,4,5}
    if qsum(candidate[i] for i in range(5) if left >> i & 1) != (F(14), F(0)):
        raise AssertionError("first entropy KKT face is not tight")
    if qsum(candidate[i] for i in range(5) if right >> i & 1) != (F(18), F(0)):
        raise AssertionError("second entropy KKT face is not tight")
    # KKT stationarity for the relaxed total-plus-two-face polytope reduces to
    # x_1*x_4=x_2*x_3, with positive multipliers because x_1,x_4>x_2.
    if qmul(candidate[0], candidate[3]) != qmul(candidate[1], candidate[2]):
        raise AssertionError("exact Shannon KKT product identity failed")
    if not qnonnegative(qsub(candidate[0], candidate[1])):
        raise AssertionError("first KKT multiplier is negative")
    if not qnonnegative(qsub(candidate[3], candidate[1])):
        raise AssertionError("second KKT multiplier is negative")
    normalized = [qvalue(value) / 20 for value in candidate]
    phi = [float(value / 20) for value in PHI_BASE]
    upper_entropy = entropy(normalized)
    phi_entropy = entropy(phi)
    epsilon = 1 / 20
    binary_entropy = -epsilon * math.log(epsilon) - (1 - epsilon) * math.log(1 - epsilon)
    bound = binary_entropy + epsilon * math.log(4)
    regret = upper_entropy - phi_entropy
    if not (0 < regret < bound):
        raise AssertionError("five-state Shannon regret is outside the theorem bound")
    return {
        "quadratic_field": f"Q({root})",
        "unnormalized_unique_upper_entropy_point": [
            "2*sqrt(43)-12",
            "14-2*sqrt(43)",
            "13-sqrt(43)",
            "2*sqrt(43)-8",
            "13-sqrt(43)",
        ],
        "normalized_decimal": [f"{value:.15f}" for value in normalized],
        "exact_core_feasibility_checked": True,
        "tight_kkt_faces": [[1, 3, 5], [3, 4, 5]],
        "exact_kkt_identity": "x1*x4=x2*x3=x2*x5",
        "incmax_entropy_nats": f"{phi_entropy:.15f}",
        "upper_entropy_nats": f"{upper_entropy:.15f}",
        "actual_entropy_regret_nats": f"{regret:.15f}",
        "suffix_slack_epsilon": "1/20",
        "fannes_audenaert_bound_nats": f"{bound:.15f}",
        "bound_verified": True,
    }


def audit_global_sharpness():
    cases = []
    for n, tau in ((2, F(1, 4)), (3, F(1, 3)), (5, F(1, 5))):
        phi = [F(1)] + [F(0)] * (n - 1)
        point = [F(1) - tau] + [tau / (n - 1)] * (n - 1)
        epsilon = phi[0] - point[0]
        if epsilon != tau:
            raise AssertionError("sharp family has wrong face slack")
        h_phi = entropy([float(value) for value in phi])
        h_point = entropy([float(value) for value in point])
        t = float(tau)
        sharp_bound = -t * math.log(t) - (1 - t) * math.log(1 - t)
        sharp_bound += t * math.log(n - 1)
        if abs((h_point - h_phi) - sharp_bound) > 1e-14:
            raise AssertionError("Shannon continuity constant is not attained")
        cases.append(
            {
                "states": n,
                "epsilon": str(tau),
                "entropy_regret_nats": f"{h_point - h_phi:.15f}",
                "bound_attained": True,
            }
        )
    return cases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = {
        "status": "Shannon defect-stability corollary audited",
        "finite_audit_is_not_proof": True,
        "five_state_exact_upper_entropy": audit_five_state_upper_entropy(),
        "global_bound_sharpness_family": audit_global_sharpness(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
