"""Exact algebra for the bounded-s projective ladder; no numerical optimizer."""
from fractions import Fraction as Q
from math import comb
import json


def certificate(s, m):
    assert s >= 2 and m >= 1
    # Each row is lhs >= rhs. Final budget and coverage each have weight one.
    coeff = {"K": Q(1), "z": Q(0), f"q{m}": Q(-2 * (m - 1))}
    rhs = Q(1)
    residual = Q(2 * (m - 1))
    rows = 2
    for j in range(m, 1, -1):
        k = min(s - 1, 2 * j - 2)
        weight = residual / (k + 1)
        assert weight >= 0 and k + 1 <= s and k <= 2 * j - 2
        coeff[f"q{j}"] = coeff.get(f"q{j}", Q(0)) + weight * (k + 1)
        coeff[f"q{j-1}"] = coeff.get(f"q{j-1}", Q(0)) - weight * k
        residual = weight * k
        rows += 1
    weight = residual / 3
    coeff["q1"] = coeff.get("q1", Q(0)) + 3 * weight
    rhs += weight
    rows += 1
    assert all(v == 0 for name, v in coeff.items() if name != "K")
    product = Q(1)
    for j in range(2, m + 1):
        k = min(s - 1, 2 * j - 2)
        product *= Q(k, k + 1)
    assert rhs == 1 + Q(2 * (m - 1), 3) * product
    return rhs, rows


def run():
    total = rows = 0
    exhibits = []
    for s in range(2, 65):
        values = []
        for m in range(1, 3 * s + 2):
            bound, count = certificate(s, m)
            total += 1
            rows += count
            values.append(bound)
        best = max(values)
        peaks = [i + 1 for i, value in enumerate(values) if value == best]
        assert peaks == [s, s + 1]
        h = (s + 1) // 2
        qh = Q(4**h, 2 * comb(2*h, h))
        closed = 1 + Q(2*(s-1), 3*h) * qh * Q(s-1, s)**(s-h)
        assert best == closed
        if s in (2, 3, 4, 6, 8, 16, 32, 64):
            exhibits.append({"s": s, "M": s, "owners": 2*s+1,
                             "rows": 2**(s+1)-1, "exact_lower": str(best)})
    assert certificate(6, 6)[0] == Q(493, 243) > 2
    return {"PASS": True, "certificates": total, "inequality_rows": rows,
            "exact_peak_checks": 63, "exhibits": exhibits,
            "scope": "Exact recurrence algebra only; parent proof supplies domains and symmetry."}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
