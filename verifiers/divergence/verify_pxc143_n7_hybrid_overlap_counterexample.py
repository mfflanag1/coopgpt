#!/usr/bin/env python3
"""Exact rational replay of the PXC143 seven-player overlap counterexample.

The game is the lower envelope of nine displayed nonnegative efficient
allocations.  This makes exactness conventional: every coalition minimum is
attained by a listed core allocation.  Selector recomputation uses the
project's solver-free rational simplex implementation.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / "src"), str(HERE.parent), str(HERE.parent / "search_archive")]

from exactlp import exact_linprog  # noqa: E402

N = 7
TOTAL = 119376
X = (8507, 24825, 41719, 17026, 8555, 8519, 10225)
Z = (36, 132, 25137, 25137, 25125, 25113, 18696)
GENERATORS = (
    X,
    Z,
    (0, 132, 25233, 25209, 25077, 24993, 18732),
    (180, 0, 25029, 25413, 25077, 25137, 18540),
    (48, 0, 0, 50310, 25281, 25065, 18672),
    (8483, 25293, 58733, 0, 8231, 8399, 10237),
    (60, 41575, 66880, 8507, 0, 312, 2042),
    (8207, 33596, 58685, 8543, 96, 0, 10249),
    (60, 43785, 68754, 6501, 132, 144, 0),
)


def csum(point, coalition):
    return sum(point[i] for i in range(N) if coalition >> i & 1)


def payoff_blocks(point, reverse=False):
    return [tuple(i for i, q in enumerate(point) if q == level)
            for level in sorted(set(point), reverse=reverse)]


def staged_certificates(values, point, mode):
    """Extract one exact Farkas identity for every stage/player."""
    answer = []
    blocks = payoff_blocks(point, mode == "max")
    full = (1 << N) - 1
    tight = tuple(s for s in range(1, full) if csum(point, s) == values[s])
    for stage, block in enumerate(blocks):
        old = tuple(i for old_block in blocks[:stage] for i in old_block)
        for player in block:
            m = len(tight)
            old_index = {j: m + k for k, j in enumerate(old)}
            side_index = {j: m + len(old) + k for k, j in enumerate(block)}
            constant_index = m + len(old) + len(block)
            width = constant_index + 1
            side = F(1 if mode == "min" else -1)
            aeq, beq = [], []
            for coordinate in range(N):
                row = [F(0)] * width
                for k, coalition in enumerate(tight):
                    row[k] = F((coalition >> coordinate) & 1)
                if coordinate in old_index: row[old_index[coordinate]] = 1
                if coordinate in side_index: row[side_index[coordinate]] = side
                row[constant_index] = -1
                aeq.append(row); beq.append(-side * F(coordinate == player))
            aub, bub = [], []
            for variable in tuple(range(m)) + tuple(side_index.values()):
                row = [F(0)] * width; row[variable] = -1
                aub.append(row); bub.append(F(0))
            for variable in old_index.values():
                row = [F(0)] * width; row[variable] = F(-1 if mode == "min" else 1)
                aub.append(row); bub.append(F(0))
            status, _objective, solution = exact_linprog(
                [F(0)] * width, aub, bub, aeq, beq)
            if status != "optimal": raise AssertionError(("Farkas", mode, stage, player))
            # Recheck the complete vector identity and multiplier signs rather
            # than trusting the LP status alone.
            for row, rhs in zip(aeq, beq):
                if sum(a*b for a,b in zip(row,solution)) != rhs:
                    raise AssertionError("certificate equality")
            for row, rhs in zip(aub, bub):
                if sum(a*b for a,b in zip(row,solution)) > rhs:
                    raise AssertionError("certificate sign")
            lambdas = {str(tight[k]): str(solution[k]) for k in range(m) if solution[k]}
            previous = {str(j): str(solution[index]) for j,index in old_index.items()
                        if solution[index]}
            current = {str(j): str(solution[index]) for j,index in side_index.items()
                       if solution[index]}
            answer.append({"stage": stage, "player": player,
                           "coalition_multipliers": lambdas,
                           "previous_stratum_multipliers": previous,
                           "current_side_multipliers": current,
                           "efficiency_multiplier": str(solution[constant_index])})
    return answer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if any(sum(g) != TOTAL or min(g) < 0 for g in GENERATORS):
        raise AssertionError("generator feasibility")
    values = tuple(min(csum(g, s) for g in GENERATORS) for s in range(1 << N))
    if values[-1] != TOTAL or any(values[1 << i] for i in range(N)):
        raise AssertionError("normalization")

    # Every generator is a core allocation of the lower-envelope game, and
    # an attaining generator witnesses exactness for every coalition.
    attainment = []
    unique = Counter()
    for coalition, value in enumerate(values):
        hits = tuple(k for k, g in enumerate(GENERATORS) if csum(g, coalition) == value)
        if not hits:
            raise AssertionError(("unattained", coalition))
        attainment.append(hits)
        if len(hits) == 1:
            unique[hits[0]] += 1
    for k, g in enumerate(GENERATORS):
        if any(csum(g, s) < values[s] for s in range(1 << N)):
            raise AssertionError(("not core", k))
        if unique[k] == 0:
            raise AssertionError(("redundant generator", k))

    x, z = tuple(map(F, X)), tuple(map(F, Z))
    if any(csum(X, s) < values[s] or csum(Z, s) < values[s]
           for s in range(1 << N)):
        raise AssertionError("selector candidate outside core")
    certificates_x = staged_certificates(tuple(map(F, values)), x, "min")
    certificates_z = staged_certificates(tuple(map(F, values)), z, "max")
    # Replay the sparse conventional proof printed in the manuscript.
    lmin_bounds = (
        TOTAL - values[126],
        2 * (TOTAL - X[0]) - sum(values[s] for s in (62, 76, 82)),
        2 * (TOTAL - X[0]) - sum(values[s] for s in (62, 76, 98)),
        TOTAL - X[0] - values[62],
        4 * (TOTAL - X[0]) - sum(values[s] for s in (62, 62, 76, 82, 98, 116)),
        TOTAL - values[76] - X[0] - X[4] - X[5],
        TOTAL - values[82] - X[0] - X[3] - X[5],
    )
    if lmin_bounds != (X[0], X[5], X[4], X[6], X[3], X[1], X[2]):
        raise AssertionError(("hand Lmin chain", lmin_bounds))
    top_sum = values[12]
    lmax_bounds = (
        F(top_sum, 2),
        sum(values[s] for s in (29, 62, 76)) - TOTAL - 2 * top_sum,
        sum(values[s] for s in (45, 62, 76)) - TOTAL - 2 * top_sum,
        values[76] - top_sum,
        values[10] - Z[3],
        values[13] - top_sum,
    )
    if lmax_bounds != (Z[2], Z[4], Z[5], Z[6], Z[1], Z[0]):
        raise AssertionError(("hand Lmax chain", lmax_bounds))
    distance = sum(abs(a - b) for a, b in zip(X, Z))
    overlap = F(TOTAL) - F(distance, 2)
    target = F(7, 12) * TOTAL
    if not (distance == 99492 and overlap == 69630 and target == 69636):
        raise AssertionError((distance, overlap, target))

    x_tight = tuple(s for s in range(1, (1 << N) - 1) if csum(X, s) == values[s])
    z_tight = tuple(s for s in range(1, (1 << N) - 1) if csum(Z, s) == values[s])
    payload = {
        "claim": "PXC143 exact n=7 counterexample to the corrected hybrid-overlap inequality",
        "construction": {
            "n": N, "total": TOTAL,
            "definition": "v(S)=min_g g(S) over the nine listed generators",
            "generators": [list(g) for g in GENERATORS],
            "coalition_values": list(values),
        },
        "exactness": {
            "all_128_minima_attained": True,
            "all_generators_in_core": True,
            "singleton_values": [values[1 << i] for i in range(N)],
            "unique_attainment_counts": [unique[i] for i in range(len(GENERATORS))],
        },
        "selectors": {
            "method": "solver-free exact-rational staged Farkas identities",
            "Lmin": list(map(str, x)), "Lmax": list(map(str, z)),
            "Lmin_blocks": [list(b) for b in payoff_blocks(X)],
            "Lmax_blocks": [list(b) for b in payoff_blocks(Z, True)],
            "Lmin_tight_proper_rows": list(x_tight),
            "Lmax_tight_proper_rows": list(z_tight),
            "Lmin_stage_certificates": certificates_x,
            "Lmax_stage_certificates": certificates_z,
            "manuscript_sparse_chain": {
                "Lmin_bounds_in_stage_order": list(map(str, lmin_bounds)),
                "Lmax_bounds_in_stage_order": list(map(str, lmax_bounds)),
            },
        },
        "violation": {
            "l1_distance": str(distance),
            "distance_bound_5T_over_6": str(F(5, 6) * TOTAL),
            "distance_excess": str(F(distance) - F(5, 6) * TOTAL),
            "overlap": str(overlap), "target_7T_over_12": str(target),
            "overlap_margin": str(overlap - target),
            "normalized_overlap": str(overlap / TOTAL),
        },
        "scope": "direct counterexample at n=7; minimality additionally uses the separately proved n=6 theorem",
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
