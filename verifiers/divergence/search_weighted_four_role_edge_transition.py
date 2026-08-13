#!/usr/bin/env python3
"""Beam search over exactified slab bounds for a noncommon edge transition.

Unlike generator mutations, this search perturbs the complete singleton,
pair, and complementary upper-bound description of the core.  Each neighbor
is replaced by its exact core closure before its weighted selectors are
recomputed.  The search is deterministic exact-rational discovery evidence.
"""

from __future__ import annotations

import argparse
import json
import random
from fractions import Fraction as F
from pathlib import Path

import explore_weighted_four_role_faces as faces

START = tuple(map(F, (0, 0, 0, 4, 0, 0, 6, 6, 0, 4, 0, 5, 6, 6, 7, 12)))


def evaluate(values, weights):
    lmin, _ = faces.weighted_lex_point(values, weights, "min")
    lmax, _ = faces.weighted_lex_point(values, weights, "max")
    active_lmin = faces.active_pair_endpoints(values, lmin)
    active_lmax = faces.active_pair_endpoints(values, lmax)
    common = active_lmin & active_lmax
    common_count = len({partition for partition, _ in common})
    distance = sum(abs(a - b) for a, b in zip(lmin, lmax))
    score = (not bool(distance), common_count if distance else 4, -distance / values[15])
    return {
        "score": score,
        "lmin": lmin,
        "lmax": lmax,
        "active_lmin": active_lmin,
        "active_lmax": active_lmax,
        "common": common,
        "common_count": common_count,
        "distance": distance,
    }


def neighbor(rng, values, weights):
    candidate = list(values)
    coalition = rng.randrange(1, 15)
    step = rng.choice((-1, 1))
    candidate[coalition] += step
    if candidate[coalition] < 0:
        return None
    exact = faces.exactify_role_game(tuple(candidate))
    if exact is None or exact[15] != values[15]:
        return None
    if any(weights[i] == 1 and exact[1 << i] != 0 for i in range(4)):
        return None
    return exact


def encode(values, weights, row):
    overlap = sum(min(a, b) for a, b in zip(row["lmin"], row["lmax"]))
    return {
        "weights": list(weights),
        "values": [str(value) for value in values],
        "lmin": [str(value) for value in row["lmin"]],
        "lmax": [str(value) for value in row["lmax"]],
        "active_lmin": [list(label) for label in sorted(row["active_lmin"])],
        "active_lmax": [list(label) for label in sorted(row["active_lmax"])],
        "common_pair_endpoints": [list(label) for label in sorted(row["common"])],
        "common_independent_partitions": row["common_count"],
        "selector_l1_distance": str(row["distance"]),
        "overlap_ratio": str(overlap / values[15]),
        "atomic_target": str(faces.target(sum(weights))),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", default="5,1,1,1")
    parser.add_argument("--rounds", type=int, default=50)
    parser.add_argument("--beam", type=int, default=20)
    parser.add_argument("--neighbors", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260812)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    weights = tuple(map(int, args.weights.split(",")))
    rng = random.Random(args.seed)
    start_row = evaluate(START, weights)
    beam = [(START, start_row)]
    best = beam[0]
    seen = {START}
    evaluated = 1
    found = None
    for round_index in range(args.rounds):
        candidates = list(beam)
        for values, _ in beam:
            for _ in range(args.neighbors):
                exact = neighbor(rng, values, weights)
                if exact is None or exact in seen:
                    continue
                seen.add(exact)
                row = evaluate(exact, weights)
                evaluated += 1
                candidates.append((exact, row))
                if row["distance"] and row["common_count"] < 2:
                    found = (exact, row)
                    break
            if found:
                break
        if found:
            break
        candidates.sort(key=lambda item: item[1]["score"])
        beam = candidates[: args.beam]
        if beam[0][1]["score"] < best[1]["score"]:
            best = beam[0]
    result = found or best
    report = {
        "status": (
            "noncommon divergent edge transition found"
            if found
            else "no noncommon divergent edge transition found"
        ),
        "evidence_class": "exact rational deterministic discovery search",
        "seed": args.seed,
        "rounds_completed": round_index + 1,
        "candidates_evaluated": evaluated,
        "hit": bool(found),
        "best": encode(result[0], weights, result[1]),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(
        json.dumps(
            {
                "status": report["status"],
                "candidates_evaluated": evaluated,
                "best_common_partitions": result[1]["common_count"],
                "best_overlap_ratio": report["best"]["overlap_ratio"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
