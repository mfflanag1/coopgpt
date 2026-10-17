"""Exact rational KKT replay for the failed component-gluing rule."""
from fractions import Fraction as Q
import json
from pathlib import Path


def demand(condition, message):
    if not condition:
        raise RuntimeError(message)


def verify(capacities, prices, multipliers):
    edges = [(0, 2), (1, 2), (1, 3)]
    incident = [Q(0)] * 4
    tight = []
    for k, (u, v) in enumerate(edges):
        lam = multipliers[k]
        slack = prices[u] + prices[v] - 1
        demand(lam >= 0 and slack >= 0, "primal or dual feasibility")
        demand(lam * slack == 0, "complementarity")
        incident[u] += lam
        incident[v] += lam
        if slack == 0:
            tight.append(k)
    for v in range(4):
        derivative = min(2 * prices[v], Q(1))
        demand(incident[v] == capacities[v] * derivative, "stationarity")
    demand(sum(multipliers) == 2, "production lower witness")
    demand(capacities[0] + capacities[1] == 2, "production upper witness")
    return tight


def main():
    low = verify([Q(1), Q(1), Q(2), Q(3)],
                 [Q(3, 4), Q(5, 6), Q(1, 4), Q(1, 6)],
                 [Q(1), Q(0), Q(1)])
    high = verify([Q(1), Q(1), Q(4), Q(3)],
                  [Q(6, 7), Q(6, 7), Q(1, 7), Q(1, 7)],
                  [Q(1), Q(1, 7), Q(6, 7)])
    demand(low == [0, 2] and high == [0, 1, 2], "component pattern")
    # e > 1+1+1/2 =5/2, so 2/(3e)<4/15<1/3 without floating exponentials.
    e_lower = Q(1) + 1 + Q(1, 2)
    high_payment_upper = Q(2) / (3 * e_lower)
    demand(high_payment_upper < Q(1, 3), "strict incentive gain")
    result = {
        "status": "PASS",
        "exact_kkt_profiles": 2,
        "true_hardware_capacity": 4,
        "underreported_hardware_capacity": 2,
        "underreport_payment": "1/3",
        "truthful_payment": "2/(3e)",
        "truthful_payment_strict_rational_upper": str(high_payment_upper),
        "scope": "Exact failure of one report-dependent gluing architecture only."
    }
    Path(__file__).with_name("access_floor_gluing_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
