#!/usr/bin/env python3
"""Coverage-only audit for the superseded 736-orbit n=5 prototype.

This verifier deliberately does not import the search driver.  It generates
all weak payoff orders as surjective rank words, reconstructs the safe
stabilizer orbits for each residual Lmax shape, and checks that the pinned
artifact contains exactly one UNSAT query for every resulting orbit.  The
prototype omitted active zero-coordinate selector normals and is not theorem
evidence; the promoted 3,840-cell encodings replace it.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
DEFAULT_INPUT = (
    ROOT / "verifiers/divergence/search_archive/"
    "unrestricted_pxc91c_n5_lra_cegar.json"
)
PLAYERS = tuple(range(5))
Z_BLOCKS = {
    "all_tied": ((0, 1), (2, 3, 4)),
    "unique_high": ((0, 1), (2,), (3, 4)),
    "tied_high": ((0, 1), (2, 3), (4,)),
    "strict": ((0, 1), (2,), (3,), (4,)),
}
EXPECTED_ORBITS = {
    "all_tied": 76,
    "unique_high": 176,
    "tied_high": 176,
    "strict": 308,
}
EXPECTED_HISTOGRAMS = {
    "all_tied": {1: 3, 2: 5, 3: 10, 6: 33, 12: 25},
    "unique_high": {1: 13, 2: 62, 4: 101},
    "tied_high": {1: 13, 2: 62, 4: 101},
    "strict": {1: 75, 2: 233},
}


def weak_orders():
    """Generate ordered partitions independently as consecutive rank words."""
    answer = set()
    for ranks in itertools.product(range(5), repeat=5):
        used = set(ranks)
        if used != set(range(max(ranks) + 1)):
            continue
        blocks = tuple(
            tuple(i for i, rank in enumerate(ranks) if rank == level)
            for level in range(max(ranks) + 1)
        )
        answer.add(blocks)
    if len(answer) != 541:
        raise AssertionError(("ordered Bell number", len(answer)))
    return answer


def stabilizer(blocks):
    """Generate only permutations preserving every labelled z stratum."""
    choices = [tuple(itertools.permutations(block)) for block in blocks]
    for images in itertools.product(*choices):
        permutation = list(PLAYERS)
        for block, image in zip(blocks, images):
            for source, target in zip(block, image):
                permutation[source] = target
        yield tuple(permutation)


def act(partition, permutation):
    return tuple(tuple(sorted(permutation[i] for i in block)) for block in partition)


def independent_orbits(raw, z_blocks):
    group = tuple(stabilizer(z_blocks))
    unseen = set(raw)
    representatives = set()
    sizes = Counter()
    expanded = set()
    while unseen:
        seed = min(unseen)
        orbit = {act(seed, permutation) for permutation in group}
        if not orbit <= raw:
            raise AssertionError("z-stabilizer did not preserve weak orders")
        representative = min(orbit)
        representatives.add(representative)
        sizes[len(orbit)] += 1
        expanded.update(orbit)
        unseen.difference_update(orbit)
    if expanded != raw:
        raise AssertionError("orbit expansion did not recover all weak orders")
    return representatives, dict(sorted(sizes.items()))


def blocks_from_json(value):
    return tuple(tuple(block) for block in value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    source = args.input.read_bytes()
    data = json.loads(source)
    if data.get("pattern_source") != "all" or not data.get("coverage_complete"):
        raise AssertionError("input is not the uncapped exhaustive artifact")
    if data.get("exact_cone_inequality_count") != 280:
        raise AssertionError("exact-cone catalogue count changed")
    expected_status = {"sat": 0, "unsat": 736, "unknown": 0, "error": 0}
    if data.get("status_counts") != expected_status:
        raise AssertionError(("status counts", data.get("status_counts")))
    if data.get("selected_branch_count") != 736 or data.get("controls_enabled"):
        raise AssertionError("wrong exhaustive branch mode")

    raw = weak_orders()
    computed = {}
    expected_keys = set()
    for shape, z_blocks in Z_BLOCKS.items():
        representatives, histogram = independent_orbits(raw, z_blocks)
        if len(representatives) != EXPECTED_ORBITS[shape]:
            raise AssertionError((shape, len(representatives)))
        if histogram != EXPECTED_HISTOGRAMS[shape]:
            raise AssertionError((shape, histogram))
        expected_keys.update((shape, partition) for partition in representatives)
        computed[shape] = {
            "raw_weak_orders": len(raw),
            "orbit_count": len(representatives),
            "orbit_size_histogram": {str(k): v for k, v in histogram.items()},
            "expanded_count": sum(k * v for k, v in histogram.items()),
        }

    actual_keys = []
    smt_hashes = []
    for result in data["results"]:
        if result.get("status") != "unsat" or result.get("stderr"):
            raise AssertionError(("non-UNSAT result", result.get("index")))
        key = (result["shape"], blocks_from_json(result["x_blocks_low_to_high"]))
        actual_keys.append(key)
        smt_hashes.append(result["smt2_sha256"])
    if len(actual_keys) != len(set(actual_keys)):
        raise AssertionError("duplicate symmetry query")
    if set(actual_keys) != expected_keys:
        raise AssertionError("pinned queries do not equal independent orbit representatives")
    if len(smt_hashes) != len(set(smt_hashes)):
        raise AssertionError("distinct branches produced duplicate SMT payloads")
    if [item["index"] for item in data["results"]] != list(range(736)):
        raise AssertionError("result indices are not contiguous")

    payload = {
        "claim": "coverage-only orbit and status audit for the superseded n=5 prototype",
        "raw_weak_order_count_per_shape": 541,
        "shape_audits": computed,
        "total_orbit_count": len(expected_keys),
        "queried_orbit_count": len(actual_keys),
        "all_queries_unsat": True,
        "unique_smt_payload_count": len(set(smt_hashes)),
        "coverage_exact": True,
        "provenance": {
            "verifier": str(HERE.relative_to(ROOT)),
            "verifier_sha256": hashlib.sha256(HERE.read_bytes()).hexdigest(),
            "input": str(args.input.resolve().relative_to(ROOT.resolve())),
            "input_sha256": hashlib.sha256(source).hexdigest(),
        },
        "scope": (
            "This verifies only the prototype's discrete symmetry expansion and "
            "status ledger. Because that encoding omitted active zero-coordinate "
            "selector normals, its UNSAT output is not theorem evidence; the promoted "
            "3,840-cell raw and independent-NI encodings replace it."
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
