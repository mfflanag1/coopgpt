"""Rational primal/KKT certificate for quadratic-cover route obstructions."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json


def cover_check(R, power, private, high):
    checks = 0
    for k in range(R + 1):
        for mask in product((0, 1), repeat=4):
            pairs = mask[0] * mask[1] + int(high) * mask[2] * mask[3]
            value = min(Q(k, R), pairs)
            paid = k * power + sum(x * y for x, y in zip(mask, private))
            assert paid >= value
            checks += 1
    return checks


def main():
    count = 0
    records = []
    R = 3
    low = Q(1, R + 2)
    count += cover_check(R, low, (low, low, Q(0), Q(0)), False)
    for lam in map(Q, ("0", "1/100", "1/9", "1/3", "1", "10")):
        u = max(Q(0), (1 - R * lam) / (2 + 2 * R + 2 * R * lam))
        t = (1 - 2 * u) / R
        T = R * t + 4 * u
        count += cover_check(R, t, (u,) * 4, True)
        mu = (t + lam * T) / 2
        assert t + lam * T == 2 * mu
        if u:
            assert u + lam * T == mu
        else:
            assert lam * T >= mu
        delta = 3 * u - 2 * low
        assert delta <= -Q(1, 40)
        records.append({"lambda": str(lam), "high_private": str(u),
                        "high_power": str(t), "protected_change": str(delta)})

    pair_records = []
    for lam, R in ((Q(1, 2), 2), (Q(1, 3), 3), (Q(1, 10), 10), (Q(2, 7), 4)):
        assert R * lam >= 1
        low = Q(1, R + 2)
        count += cover_check(R, low, (low, low, Q(0), Q(0)), False)
        count += cover_check(R, Q(1, R), (Q(0),) * 4, True)
        mu = (Q(1, R) + lam) / 2
        assert 2 * mu == Q(1, R) + lam and lam >= mu
        pair_records.append({"lambda": str(lam), "power_owners": R,
                             "pair_change": str(-low), "private_KKT_slack": str(lam - mu)})

    result = {"status": "PASS", "arithmetic": "exact Fraction",
              "symmetry_reduced_all_coalition_checks": count,
              "seven_owner_penalty_examples": records,
              "pair_KKT_examples": pair_records,
              "scope": "Architecture obstruction, not an unrestricted mechanism lower; all-profile claims follow from the written parametric proof."}
    Path(__file__).with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
