"""Exact finite checks for the synthetic calibrations, not a market model."""

from fractions import Fraction as Q
from itertools import combinations
import hashlib
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def coalitions(n):
    for size in range(1, n + 1):
        yield from combinations(range(n), size)


def main():
    n = 3
    x = [Q(1, 2)] * n
    requirements = {s: Q(int(len(s) >= 2)) for s in coalitions(n)}
    dual = {s: Q(1, 2) if len(s) == 2 else Q(0) for s in coalitions(n)}
    for s, b in requirements.items():
        require(sum(x[i] for i in s) >= b, f"primal fails at {s}")
    for i in range(n):
        require(sum(z for s, z in dual.items() if i in s) <= 1,
                f"dual load exceeds one for owner {i}")
    pvalue = sum(x)
    dvalue = sum(dual[s] * requirements[s] for s in requirements)
    require(pvalue == dvalue == Q(3, 2), "nonmatching LP certificates")
    require(Q(5, 2) - pvalue == 1, "incorrect residual cash")

    cash = [Q(0), Q(3), Q(8), Q(12)]
    actions = [frozenset(s) for s in coalitions(len(cash))]
    nested_count = 0
    for a in actions:
        for b in actions:
            if a <= b:
                left = min(Q(10), max(cash[i] for i in a))
                right = min(Q(10), max(cash[i] for i in b))
                require(left <= right, "nested-option monotonicity fails")
                nested_count += 1

    choices = {"a": (Q(12), Q(1)), "b": (Q(8), Q(8))}
    chosen_by_creditor = max(choices, key=lambda a: min(Q(10), choices[a][0]))
    chosen_by_controller = max(choices, key=lambda a: choices[a][1])
    require(chosen_by_creditor == "a" and chosen_by_controller == "b",
            "controller example does not separate choices")
    require(sum(choices["a"]) == 13 and sum(choices["b"]) == 16,
            "incorrect total surplus")

    samples = []
    for probability in (Q(0), Q(1, 4), Q(1, 2), Q(3, 4), Q(1)):
        receipt = probability * min(Q(8), Q(10)) + (1-probability) * Q(2)
        require(receipt == 2 + 6 * probability, "incorrect expected receipt")
        samples.append({"continuation_probability": str(probability),
                        "expected_receipt": str(receipt),
                        "funding_at_five_percent": str(receipt / Q(21, 20))})

    menu_cash = [Q(12), Q(8)]
    owner_requirement = Q(2)
    menu_face = Q(8)
    residual = [v - owner_requirement for v in menu_cash]
    robust_floor = min(menu_face, min(residual))
    controlled_receipt = min(menu_face, max(residual))
    require(robust_floor == 6 and controlled_receipt == 8,
            "incorrect operator-menu boundary")
    for v in menu_cash:
        owner_payment = v - robust_floor
        require(owner_payment >= owner_requirement and owner_payment >= 0,
                "operator-menu owner participation fails")
        require(owner_payment + robust_floor == v,
                "operator-menu budget fails")
    require(Q(1) < owner_requirement,
            "negative-residual witness must be infeasible even with q=0")

    report = {
        "status": "PASS",
        "scope": "Exact synthetic certificates and arithmetic only; no issuer valuation",
        "triangle_primal_objective": str(pvalue),
        "triangle_dual_objective": str(dvalue),
        "triangle_coalitions_checked": len(requirements),
        "nested_nonempty_action_pairs_checked": nested_count,
        "controller_receipts": {"creditor_control": 10, "customer_control": 8},
        "missing_consent_calibration": samples,
        "operator_menu": {"robust_floor": str(robust_floor),
                          "creditor_control": str(controlled_receipt),
                          "negative_residual_witness": "V=1 < tau=2: infeasible, not zero recovery"},
        "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
