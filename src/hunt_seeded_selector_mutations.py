"""Adversarial mutation hunt for the multilevel selector refinements."""
from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

from audit_fresh_multilevel_selector import exact_record
from classify_saved_capacity_frontier import residual_cover_float
from hunt_exact_points import game_from_points
from hunt_off_side_carrier import core_matrices, maximize_target
from lemD import xS
from leximin import leximin_core_float


def mixed_seeds(paths):
    seeds = []
    for path in paths:
        payload = json.loads(path.read_text())
        for record in payload["records"]:
            if len({
                item["carrier_certifies"] for item in record["candidates"]
            }) < 2:
                continue
            seeds.append({
                "source": str(path),
                "points": record["points"],
                "S": record["S"],
            })
    if not seeds:
        raise RuntimeError("no mixed seed records found")
    return seeds


def mutate(points, rng, transfers, radius):
    result = [list(point) for point in points]
    n = len(result[0])
    for _ in range(transfers):
        point = result[rng.randrange(len(result))]
        source, target = rng.sample(range(n), 2)
        amount = rng.randint(1, radius)
        if rng.randrange(2):
            amount = -amount
        point[source] += amount
        point[target] -= amount
    return result


def screen(game, target):
    phi = leximin_core_float(game.n, game.v, tol=1e-9)
    if phi is None:
        return False
    rows, rhs = core_matrices(game)
    phi_target = xS(phi, target, game.n)
    maximum = maximize_target(game, target, rows, rhs)
    if maximum is None or maximum <= phi_target + 1e-7:
        return False
    star_maximum = maximize_target(game, target, rows, rhs, lower=phi)
    if star_maximum is None or star_maximum > phi_target + 1e-7:
        return False
    residuals = residual_cover_float(game, phi, target)
    return residuals is not None and len({
        round(value, 7) for value in residuals.values()
    }) >= 3


def hunt(paths, trials, seed, transfers, radius, exact_case_limit):
    seeds = mixed_seeds(paths)
    rng = random.Random(seed)
    started = time.time()
    screened = 0
    exact_records = []
    seen = set()
    for trial in range(trials):
        base = seeds[rng.randrange(len(seeds))]
        points = mutate(base["points"], rng, transfers, radius)
        game = game_from_points(len(points[0]), points)
        target = sum(1 << (player - 1) for player in base["S"])
        key = (tuple(game.v), target)
        if key in seen:
            continue
        seen.add(key)
        if not screen(game, target):
            continue
        screened += 1
        record = exact_record(game, points, target, trial)
        if record is None:
            continue
        record["seed_source"] = base["source"]
        exact_records.append(record)
        if not record["some_minimum_residual_carrier"]:
            return {
                "status": "exact selector counterexample found",
                "arithmetic": "exact rational primal-dual certification",
                "seed": seed,
                "trials_requested": trials,
                "trials_completed": trial + 1,
                "transfers": transfers,
                "radius": radius,
                "screened_multilevel_cases": screened,
                "exact_multilevel_cases": len(exact_records),
                "records": exact_records,
            }
        if len(exact_records) >= exact_case_limit:
            break
    tied = [
        record for record in exact_records
        if len(record["highest_gain_minimum_residual_players"]) > 1
    ]
    mixed = [
        record for record in tied
        if len({item["carrier_certifies"] for item in record["candidates"]}) > 1
    ]
    return {
        "status": "no exact selector counterexample found",
        "arithmetic": "exact rational primal-dual certification",
        "seed_sources": [str(path) for path in paths],
        "seed": seed,
        "trials_requested": trials,
        "trials_completed": trial + 1 if trials else 0,
        "transfers": transfers,
        "radius": radius,
        "exact_case_limit": exact_case_limit,
        "screened_multilevel_cases": screened,
        "exact_multilevel_cases": len(exact_records),
        "tied_highest_gain_cases": len(tied),
        "mixed_tie_cases": len(mixed),
        "centrality_selector_successes": sum(
            record["selected_all_certify"] for record in exact_records
        ),
        "adjacency_selector_successes": sum(
            record["adjacency_selected_all_certify"]
            for record in exact_records
        ),
        "adjacency_face_selector_successes": sum(
            record["adjacency_selected_faces_all_certify"]
            for record in exact_records
        ),
        "carrier_selector_failures": sum(
            not record["adjacency_selected_all_certify"]
            for record in exact_records
        ),
        "all_highest_gain_faces_certify_count": sum(
            record["all_highest_gain_faces_certify"]
            for record in exact_records
        ),
        "some_minimum_residual_carrier_count": sum(
            record["some_minimum_residual_carrier"]
            for record in exact_records
        ),
        "elapsed_seconds": time.time() - started,
        "records": exact_records,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--trials", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20260809)
    parser.add_argument("--transfers", type=int, default=1)
    parser.add_argument("--radius", type=int, default=2)
    parser.add_argument("--exact-case-limit", type=int, default=250)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = hunt(
        args.inputs,
        args.trials,
        args.seed,
        args.transfers,
        args.radius,
        args.exact_case_limit,
    )
    args.output.write_text(json.dumps(result, indent=2) + "\n")
