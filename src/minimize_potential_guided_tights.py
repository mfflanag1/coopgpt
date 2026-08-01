"""Greedily minimize arm-potential threshold witness families."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path

from analyze_potential_guided_exactness import analyze, candidate_tights
from audit_potential_guided_sources import CASES, type_i_payload


VERIFIED = "POTENTIAL-GUIDED EXACTNESS CERTIFICATE VERIFIED"


def threshold_sources(capacity_detail, masks):
    descriptions = {mask: [] for mask in masks}
    potentials = [
        [F(value) for value in vector]
        for vector in capacity_detail["dual_obstruction"]["game_player_potentials"]
    ]
    for game in (1, 2):
        vector = potentials[game]
        for level in sorted(set(vector)):
            weak = sum(1 << i for i, value in enumerate(vector) if value >= level)
            strict = sum(1 << i for i, value in enumerate(vector) if value > level)
            if weak in descriptions:
                descriptions[weak].append({
                    "game": game, "relation": ">=", "level": str(level)
                })
            if strict in descriptions:
                descriptions[strict].append({
                    "game": game, "relation": ">", "level": str(level)
                })
    return {str(mask): descriptions[mask] for mask in masks}


def verify_single_witness(circuit, index, coalition, blocks):
    """Check the manuscript's single-witness recoloring identities over Q."""
    n = circuit["n"]
    A, B = circuit["A_mask"], circuit["B_mask"]
    detail = circuit["circuits"][index - 1]
    aggregate = defaultdict(F)
    required_A = required_B = F(0)
    for meta, raw_weight in zip(detail["active_rows"], detail["circuit_weights"]):
        if meta[0] != "core":
            continue
        game, support_coalition = int(meta[1]), int(meta[2])
        weight = F(raw_weight)
        aggregate[support_coalition] += weight
        if game == 1 and support_coalition == A:
            required_A += weight
        if game == 2 and support_coalition == B:
            required_B += weight

    collections = [defaultdict(F) for _ in range(3)]
    alpha, delta = [F(0)] * 3, [F(0)] * 3
    seen_games = set()
    for block in blocks:
        game = block["game"]
        assert block["tight_coalition"] == coalition
        assert game not in seen_games
        seen_games.add(game)
        alpha[game], delta[game] = F(block["alpha"]), F(block["delta"])
        for support_coalition, weight in block["collection"].items():
            collections[game][int(support_coalition)] += F(weight)

    coverage_exact = True
    for game in range(3):
        for player in range(n):
            coverage = sum(
                weight for support_coalition, weight in collections[game].items()
                if support_coalition >> player & 1
            )
            target = alpha[game] + (
                delta[game] if coalition >> player & 1 else F(0)
            )
            coverage_exact &= coverage == target

    Delta = sum(delta, F(0))
    all_coalitions = set(aggregate) | set().union(*map(set, collections)) | {coalition}
    aggregate_exact = all(
        sum(collections[game][support_coalition] for game in range(3))
        == aggregate[support_coalition]
        + (Delta if support_coalition == coalition else F(0))
        for support_coalition in all_coalitions
    )
    efficiency_exact = sum(alpha, F(0)) == sum(
        (F(value) for value in detail["efficiency_weights"]), F(0)
    )
    bump_exact = (
        collections[1][A] - (delta[1] if coalition == A else F(0)) >= required_A
        and collections[2][B] - (delta[2] if coalition == B else F(0)) >= required_B
    )
    return coverage_exact and aggregate_exact and efficiency_exact and bump_exact


def shrink(circuit, capacity, index, reverse=False):
    n = circuit["n"]
    A = circuit["A_mask"]
    B = circuit["B_mask"]
    detail = circuit["circuits"][index - 1]
    capacity_detail = capacity["circuits"][index - 1]
    candidates = list(candidate_tights(
        n, A, B, detail, capacity_detail, mode="arm-potentials"
    ))
    initial_count = len(candidates)

    # First discard every threshold unused by one exact dual optimum.
    first = analyze(
        circuit, capacity, index, candidate_mode="arm-potentials",
        candidate_tights_override=candidates,
    )
    assert first["status"] == VERIFIED
    candidates = list(first["used_tights"])

    # Then seek an inclusion-minimal family; two orders expose some degeneracy.
    changed = True
    while changed:
        changed = False
        for coalition in sorted(candidates, reverse=reverse):
            trial = [value for value in candidates if value != coalition]
            result = analyze(
                circuit, capacity, index, candidate_mode="arm-potentials",
                candidate_tights_override=trial,
            )
            if result["status"] == VERIFIED:
                candidates = trial
                changed = True
    final = analyze(
        circuit, capacity, index, candidate_mode="arm-potentials",
        candidate_tights_override=candidates,
    )
    assert final["status"] == VERIFIED
    return {
        "initial_candidate_count": initial_count,
        "irreducible_candidate_count": len(candidates),
        "irreducible_candidates": candidates,
        "threshold_sources": threshold_sources(capacity_detail, candidates),
        "block_count": final["block_count"],
        "used_tight_count": final["used_tight_count"],
        "circuit_margin": final["circuit_margin"],
        "primal_exact": final["primal_exact"],
        "dual_exact": final["dual_exact"],
        "blocks": final["blocks"],
    }


def best_shrink(circuit, capacity, index):
    forward = shrink(circuit, capacity, index, reverse=False)
    reverse = shrink(circuit, capacity, index, reverse=True)
    best = min(
        (forward, reverse),
        key=lambda item: (item["irreducible_candidate_count"], item["block_count"]),
    )
    n, A, B = circuit["n"], circuit["A_mask"], circuit["B_mask"]
    detail = circuit["circuits"][index - 1]
    capacity_detail = capacity["circuits"][index - 1]
    initial = candidate_tights(
        n, A, B, detail, capacity_detail, mode="arm-potentials"
    )
    singletons = []
    for coalition in initial:
        result = analyze(
            circuit, capacity, index, candidate_mode="arm-potentials",
            candidate_tights_override=[coalition],
        )
        if result["status"] == VERIFIED:
            singletons.append({
                "coalition": coalition,
                "block_count": result["block_count"],
                "blocks": result["blocks"],
            })
    if singletons:
        chosen = min(singletons, key=lambda item: item["block_count"])
        best = {
            "initial_candidate_count": len(initial),
            "irreducible_candidate_count": 1,
            "irreducible_candidates": [chosen["coalition"]],
            "threshold_sources": threshold_sources(
                capacity_detail, [chosen["coalition"]]
            ),
            "block_count": chosen["block_count"],
            "used_tight_count": 1,
            "circuit_margin": "0",
            "primal_exact": True,
            "dual_exact": True,
            "blocks": chosen["blocks"],
        }
    best["single_witness_recoloring_exact"] = verify_single_witness(
        circuit, index, best["irreducible_candidates"][0], best["blocks"]
    )
    best["verified_single_candidates"] = [
        {"coalition": item["coalition"], "block_count": item["block_count"]}
        for item in singletons
    ]
    successful = {item["coalition"] for item in singletons}
    block_counts = {
        item["coalition"]: item["block_count"] for item in singletons
    }
    potentials = [
        [F(value) for value in vector]
        for vector in capacity_detail["dual_obstruction"]["game_player_potentials"]
    ]
    grand = (1 << circuit["n"]) - 1
    top_thresholds = []
    for game in (1, 2):
        vector = potentials[game]
        maximum = max(vector)
        coalition = sum(
            1 << player for player, value in enumerate(vector) if value == maximum
        )
        proper = 0 < coalition < grand
        top_thresholds.append({
            "game": game,
            "maximum": str(maximum),
            "coalition": coalition if proper else None,
            "verified": proper and coalition in successful,
            "block_count": block_counts.get(coalition) if proper else None,
        })
    best["top_thresholds"] = top_thresholds
    best["some_arm_top_threshold_verified"] = any(
        item["verified"] for item in top_thresholds
    )
    best["initial_candidates"] = list(initial)
    best["initial_threshold_sources"] = threshold_sources(capacity_detail, initial)
    best["failed_single_candidates"] = [
        coalition for coalition in initial if coalition not in successful
    ]
    return best


def minimize_corpus(results_dir):
    records = []
    circuit, capacity, index = type_i_payload(results_dir)
    records.append({
        "label": "n5-Type-I", **best_shrink(circuit, capacity, index)
    })
    for label, circuit_name, capacity_name, index in CASES:
        circuit = json.loads((results_dir / circuit_name).read_text())
        capacity = json.loads((results_dir / capacity_name).read_text())
        records.append({
            "label": label, **best_shrink(circuit, capacity, index)
        })
    return {
        "status": "exact inclusion-minimal arm-potential threshold audit",
        "case_count": len(records),
        "maximum_irreducible_candidate_count": max(
            record["irreducible_candidate_count"] for record in records
        ),
        "maximum_block_count": max(record["block_count"] for record in records),
        "all_cases_have_verified_arm_top_threshold": all(
            record["some_arm_top_threshold_verified"] for record in records
        ),
        "verified_top_threshold_cases_by_game": {
            str(game): sum(
                record["top_thresholds"][game - 1]["verified"] for record in records
            )
            for game in (1, 2)
        },
        "cases": records,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = minimize_corpus(args.results_dir)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
