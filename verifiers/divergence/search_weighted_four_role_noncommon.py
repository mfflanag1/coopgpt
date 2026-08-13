#!/usr/bin/env python3
"""Targeted exact search for a divergent non-common-two-flat role game.

This is a deterministic beam search around the normalized four-role
obstruction.  It is a hostile discovery tool, not proof evidence.  A hit is
reported with the full lower-envelope generators, worth table, rational
selectors, and active pair-slab endpoints so it can be independently replayed.
"""

from __future__ import annotations

import argparse
import json
import random
from fractions import Fraction as F
from pathlib import Path

import explore_weighted_four_role_faces as faces


def neighbor(rng, generators, weights):
    points = [list(point) for point in generators]
    point = rng.choice(points)
    donor = rng.choice([i for i, amount in enumerate(point) if amount])
    receiver = rng.choice([i for i in range(4) if i != donor])
    point[donor] -= 1
    point[receiver] += 1
    result = tuple(tuple(point) for point in points)
    if any(
        weights[role] == 1 and min(point[role] for point in result) != 0
        for role in range(4)
    ):
        return None
    return result


def evaluate(generators, weights):
    values = faces.role_values(generators)
    lmin, lmin_trace = faces.weighted_lex_point(values, weights, "min")
    lmax, lmax_trace = faces.weighted_lex_point(values, weights, "max")
    active_lmin = faces.active_pair_endpoints(values, lmin)
    active_lmax = faces.active_pair_endpoints(values, lmax)
    common = active_lmin & active_lmax
    common_partitions = len({partition for partition, _ in common})
    distance = sum(abs(a - b) for a, b in zip(lmin, lmax))
    # Divergence is mandatory; among divergent rows minimize common flats and
    # then retain a robust (rather than infinitesimal) selector displacement.
    score = (
        1 if distance == 0 else 0,
        common_partitions if distance else 4,
        -distance / values[15],
    )
    return {
        "score": score,
        "values": values,
        "lmin": lmin,
        "lmax": lmax,
        "lmin_trace": lmin_trace,
        "lmax_trace": lmax_trace,
        "active_lmin": active_lmin,
        "active_lmax": active_lmax,
        "common": common,
        "common_partitions": common_partitions,
        "distance": distance,
    }


def encode(generators, weights, row):
    total = row["values"][15]
    overlap = sum(min(a, b) for a, b in zip(row["lmin"], row["lmax"]))
    return {
        "weights": list(weights),
        "generators": [list(point) for point in generators],
        "values": [str(value) for value in row["values"]],
        "lmin": [str(value) for value in row["lmin"]],
        "lmax": [str(value) for value in row["lmax"]],
        "active_lmin": [list(label) for label in sorted(row["active_lmin"])],
        "active_lmax": [list(label) for label in sorted(row["active_lmax"])],
        "common_pair_endpoints": [list(label) for label in sorted(row["common"])],
        "common_independent_partitions": row["common_partitions"],
        "selector_l1_distance": str(row["distance"]),
        "overlap_ratio": str(overlap / total),
        "atomic_target": str(faces.target(sum(weights))),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", default="3,1,1,1")
    parser.add_argument("--rounds", type=int, default=80)
    parser.add_argument("--beam", type=int, default=24)
    parser.add_argument("--neighbors", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260812)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    weights = tuple(map(int, args.weights.split(",")))
    if len(weights) != 4 or not all(weight > 0 for weight in weights):
        parser.error("--weights requires four positive integers")
    rng = random.Random(args.seed)
    start = faces.NORMALIZED_OBSTRUCTION_GENERATORS
    beam = [(start, evaluate(start, weights))]
    seen = {start}
    best = beam[0]
    evaluated = 1
    found = None
    for round_index in range(args.rounds):
        candidates = list(beam)
        for generators, _ in beam:
            for _ in range(args.neighbors):
                candidate = neighbor(rng, generators, weights)
                if candidate is None or candidate in seen:
                    continue
                seen.add(candidate)
                row = evaluate(candidate, weights)
                evaluated += 1
                candidates.append((candidate, row))
                if row["distance"] and row["common_partitions"] < 2:
                    found = (candidate, row)
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
            "non-common-two-flat divergent exact game found"
            if found
            else "no non-common-two-flat divergence found in deterministic beam"
        ),
        "evidence_class": "exact rational discovery search; not a theorem",
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
                "hit": bool(found),
                "best_common_independent_partitions": result[1]["common_partitions"],
                "best_overlap_ratio": report["best"]["overlap_ratio"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
