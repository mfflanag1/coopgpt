#!/usr/bin/env python3
"""Independent rational diagnostic for the all-real proof in MIN2_SEPARATION.txt.

No optimizer, floating point, external data, or random search. The finite grid
does not establish the all-real theorem; the adjacent analytic proof does.
"""
from fractions import Fraction as Q
from itertools import product, combinations
import json
from pathlib import Path


def payment(profile):
    a = sum(t[0] for t in profile)
    b = sum(t[1] for t in profile)
    f = min(a, b)
    return tuple(f * ((x / a if a else 0) + (z / b if b else 0))
                 for x, z in profile)


def value(profile, coalition):
    return min(sum(profile[i][0] for i in coalition),
               sum(profile[i][1] for i in coalition))


def main():
    values = (Q(0), Q(1, 2), Q(1))
    bundles = tuple(product(values, repeat=2))
    profiles = tuple(product(bundles, repeat=3))
    payments = {p: payment(p) for p in profiles}
    coalitions = tuple(c for k in range(1, 4)
                       for c in combinations(range(3), k))
    counts = {"profiles": 0, "coverage_rows": 0, "full_out_rows": 0}
    for high in profiles:
        y = payments[high]
        assert all(z >= 0 for z in y)
        assert sum(y) == 2 * value(high, range(3))
        counts["profiles"] += 1
        for c in coalitions:
            yh = sum(y[i] for i in c)
            assert yh >= value(high, c)
            counts["coverage_rows"] += 1
            options = [tuple(b for b in bundles
                             if b[0] <= high[i][0] and b[1] <= high[i][1])
                       if i in c else (high[i],) for i in range(3)]
            for low in product(*options):
                delta = tuple((high[i][0] - low[i][0],
                               high[i][1] - low[i][1]) for i in range(3))
                assert yh - sum(payments[low][i] for i in c) >= value(delta, c)
                counts["full_out_rows"] += 1
    seed = ((Q(1), Q(0)), (Q(0), Q(1)), (Q(0), Q(0)))
    restored = ((Q(1), Q(0)), (Q(0), Q(1)), (Q(1), Q(0)))
    assert payment(seed)[0] == 1 and payment(restored)[0] == Q(1, 2)
    result = {
        "status": "PASS", "arithmetic": "fractions.Fraction",
        "scope": "finite diagnostic; all-real theorem proved separately",
        "grid": [str(x) for x in values], "owners": 3, **counts,
        "population_monotonicity_counterexample": {
            "seed": [[str(x) for x in t] for t in seed],
            "restored": [[str(x) for x in t] for t in restored],
            "seed_payments": list(map(str, payment(seed))),
            "restored_payments": list(map(str, payment(restored))),
            "unchanged_owner_0_decreases": True,
        },
    }
    output = Path(__file__).with_suffix(".json")
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
