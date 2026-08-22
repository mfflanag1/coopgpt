#!/usr/bin/env python3
"""Exact-generator deletion/merge probe for the promoted n=6 obstruction."""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve(); ROOT = HERE.parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "verifiers/divergence"), str(HERE.parent)]
from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from unrestricted_pxc91c_exact_search import audit_game, selector_pair  # noqa: E402

G = (
    (0, 13, 1, 3, 0, 1), (12, 0, 0, 1, 1, 4),
    (12, 5, 0, 0, 0, 1), (4, 10, 1, 0, 0, 3),
    (11, 3, 0, 1, 0, 3), (3, 11, 1, 3, 0, 0),
)


def merged(pair):
    a, b = pair; out = []
    for row in G:
        point = [row[i] for i in range(6) if i != b]
        point[a if a < b else a - 1] += row[b]
        out.append(tuple(map(F, point)))
    return tuple(out)


def main():
    records = []
    for a in range(6):
        for b in range(a + 1, 6):
            generators = merged((a, b)); values = lower_envelope(generators)
            constraints = {m: values[m] for m in range(1, 31) if values[m]}
            replay, x, z = selector_pair(constraints, 5, F(18))
            if replay != values: raise AssertionError("minor envelope replay")
            row = {"merged_coordinates": [a, b], "x": list(map(str, x)),
                   "z": list(map(str, z)), "divergent": x != z,
                   "two_top": sum(q == max(z) for q in z) == 2,
                   "singleton_normalized": all(values[1 << i] == 0 for i in range(5))}
            if row["divergent"] and row["two_top"] and row["singleton_normalized"]:
                row["audit"] = audit_game(
                    f"merge_{a}_{b}", values, x, z, pool_max=10,
                    replay_exact=False,
                )
            records.append(row)
    payload = {"claim": "all 15 coordinate merges of the n=6 generator obstruction",
               "records": records,
               "candidate_failures": [r for r in records if (r.get("audit") or {}).get(
                   "fixed_faithful_cover_exists") is False],
               "scope": "finite exact-generator minor probe, not a five-player theorem"}
    print(json.dumps(payload, indent=2))


if __name__ == "__main__": main()
