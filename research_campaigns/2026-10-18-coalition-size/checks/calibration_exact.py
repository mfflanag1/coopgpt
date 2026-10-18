"""Exact rational checks; the accompanying arguments carry universal claims."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import json
import random


def totals(rows):
    return tuple(map(sum, zip(*rows)))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def fractional_difference(rows, s):
    x = totals(rows)
    return [min(a + (s - 1) * b for a, b in zip(x, row))
            - min(a - b for a, b in zip(x, row)) for row in rows]


def huber_min(rows):
    x = totals(rows)
    m = min(x)
    if not m:
        return [Q(0)] * len(rows)
    D = sum(Q(1) / z for z in x)
    if m * D >= 2:
        p = [Q(1) / (z * D) for z in x]
    else:
        k = x.index(m)
        p = [m / (2 * z) for z in x]
        p[k] = 1 - sum(p[v] for v in range(len(x)) if v != k)
    assert sum(p) == 1 and min(p) >= 0
    return [dot(p, row) for row in rows]


def coalitions(n):
    for size in range(1, n + 1):
        yield from combinations(range(n), size)


def check_profile(rows):
    pay = huber_min(rows)
    n, r = len(rows), len(rows[0])
    assert min(pay) >= 0
    assert sum(pay) <= Q(r + 1, 2) * min(totals(rows))
    count = 0
    for C in coalitions(n):
        assert sum(pay[i] for i in C) >= min(totals([rows[i] for i in C]))
        count += 1
    return count


def main():
    delta = Q(1, 3)
    before = [(Q(1), Q(0)), (Q(1), Q(0)), (Q(0), Q(3))]
    after = [(1 + delta, Q(0)), before[1], before[2]]
    y0 = fractional_difference(before, 2)
    y1 = fractional_difference(after, 2)
    assert y0 == [2, 2, 2]
    assert y1 == [2, 2 - delta, 2 + delta]
    assert sum(y1[:2]) - sum(y0[:2]) == -delta

    rng = random.Random(20261018)
    profiles = cover_checks = transition_checks = 0
    for r in range(1, 6):
        for n in range(2, 8):
            for case in range(20):
                rows = [tuple(Q(rng.randrange(0, 13), rng.randrange(1, 6))
                              for _ in range(r)) for _ in range(n)]
                # Include production-zero profiles and crossed region boundaries.
                if case == 0:
                    rows = [tuple(Q(0) if v == 0 else z for v, z in enumerate(row))
                            for row in rows]
                cover_checks += check_profile(rows)
                profiles += 1
                y = huber_min(rows)
                for C in coalitions(n):
                    restored = list(rows)
                    for i in C:
                        # Some protected owners deliberately remain unchanged.
                        if rng.randrange(3):
                            restored[i] = tuple(z + Q(rng.randrange(0, 9), 3)
                                                for z in rows[i])
                    yy = huber_min(restored)
                    assert sum(yy[i] - y[i] for i in C) >= 0
                    transition_checks += 1

    cert = Path(__file__).parent / "fixed-positive-replay" / "POSITIVE_MARGINAL_FINITE_CERT_N16_S4_FACTOR5.json"
    assert cert.exists(), "Required exact calibration fixture is missing"
    certificate_transition_checks = 0
    if cert.exists():
        data = json.loads(cert.read_text())
        entries = data["transition_weights"]
        for entry in entries:
            q, k, t = (entry[key] for key in ("q", "k", "t"))
            assert 2 <= q <= 4 and k >= 1 and 0 <= t < k and q + k <= 16
            rows = [(Q(0), Q(0), Q(t, k))]
            rows += [(Q(0), Q(0), Q(1))] * (q - 1)
            rows += [(Q(1, k), Q(1, k), Q(0))] * k
            rows += [(Q(0), Q(0), Q(0))] * (16 - q - k)
            after = list(rows)
            after[0] = (Q(0), Q(0), Q(t + 1, k))
            y, yy = huber_min(rows), huber_min(after)
            assert sum(yy[:q]) >= sum(y[:q])
            certificate_transition_checks += 1
        assert certificate_transition_checks == 14

    result = {
        "arithmetic": "fractions.Fraction; assertions enabled",
        "seed": 20261018,
        "fractional_candidate_exact_TCWM_change": str(-delta),
        "min_calibration_profiles": profiles,
        "coverage_checks": cover_checks,
        "TCWM_restoration_checks": transition_checks,
        "fixed_positive_certificate_transitions_checked_on_min_rule": certificate_transition_checks,
        "scope": "Finite calibration only; proof is in root/MIN_HUBER_CALIBRATION.txt. No general arity-three upper and no full-OUT claim.",
    }
    path = Path(__file__).with_suffix(".json")
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
