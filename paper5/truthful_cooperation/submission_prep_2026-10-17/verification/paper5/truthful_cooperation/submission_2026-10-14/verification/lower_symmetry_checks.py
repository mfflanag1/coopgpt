#!/usr/bin/env python3
"""Bounded exact cut and fixed-owner symmetry checks; standard library only.

Run with --repo-root pointing to a coopgpt checkout. Imports only graph-building
and integer maxflow helpers from the named repository checker. Explicit runtime
checks remain enabled with python -O. Prints JSON; does not write repository files.
Finite tests supplement the written proof, not its all-profile/asymptotic claims.
"""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import time


DEPENDENCY = Path(
    "research_campaigns/2026-10-07-six-hour-campaign/verification/simple_dag_lower.py"
)
CAPACITIES = (11, 3, 5, 2, 7, 4, 6, 9, 8, 7, 2, 6, 3, 4, 9, 5)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def connected(edges, deleted, source, sink):
    """Reachability after deletion, independent of the imported cut enumerator."""
    reached = {source}
    for index, (tail, head) in enumerate(edges):
        if not (deleted >> index & 1) and tail in reached:
            reached.add(head)
    return sink in reached


def brute_minimal_cuts(edges, source, sink):
    require(all(tail < head for tail, head in edges), "Expected topological labels")
    require([tail for tail, _ in edges] == sorted(tail for tail, _ in edges),
            "Reachability scan requires topologically ordered edges")
    cuts = []
    for deleted in range(1 << len(edges)):
        if connected(edges, deleted, source, sink):
            continue
        if all(connected(edges, deleted ^ (1 << index), source, sink)
               for index in range(len(edges)) if deleted >> index & 1):
            cuts.append(deleted)
    return cuts


def run(repo_root):
    started = time.monotonic()
    dependency = repo_root / DEPENDENCY
    require(dependency.is_file(), "Missing checker dependency: " + str(dependency))
    dependency_hash = source_hash(dependency)
    spec = importlib.util.spec_from_file_location("bounded_simple_dag_helpers", dependency)
    require(spec is not None and spec.loader is not None, "Cannot load dependency")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    series_results = []
    for pools, branches, fans, expected_local, expected_series in (
        (2, 1, 1, 5, 10), (3, 1, 1, 5, 15), (2, 2, 1, 11, 22)
    ):
        edges, modules, source, sink = module.make_series(pools, branches, fans)
        cuts = brute_minimal_cuts(edges, source, sink)
        local, _, a, b = module.make_module(branches, fans)
        local_cuts = brute_minimal_cuts(local, a, b)
        require(len(local_cuts) == expected_local, "Unexpected module cut count")
        require(len(cuts) == expected_series == pools * len(local_cuts),
                "Series count differs from k times module count")
        require(all(sum(bool(cut & (((1 << len(kinds)) - 1) << start))
                        for start, kinds, _, _ in modules) == 1 for cut in cuts),
                "A minimal cut spans multiple modules")
        series_results.append(dict(
            k=pools, m=branches, R=fans, edges=len(edges),
            series_deletion_subsets=1 << len(edges),
            module_deletion_subsets=1 << len(local),
            module_cuts=len(local_cuts), series_cuts=len(cuts),
            every_minimal_series_cut_in_one_module=True,
        ))

    edges, modules, source, sink = module.make_series(2, 2, 1)
    local_size = len(modules[0][1])
    require(len(CAPACITIES) == len(edges) == 16 and local_size == 8,
            "Asymmetric-capacity scope changed")
    values = [module.maxflow(
        edges, [capacity if mask >> i & 1 else 0
                for i, capacity in enumerate(CAPACITIES)], source, sink
    ) for mask in range(1 << 16)]
    require(sum(value > 0 for value in values) == 225,
            "Positive-worth coalition count changed")

    permutations = [("swap_modules", [i + local_size if i < local_size
                                      else i - local_size for i in range(16)])]
    for pool in (0, 1):
        permutation = list(range(16))
        offset, kinds, _, _ = modules[pool]
        lookup = {kind: i for i, kind in enumerate(kinds)}
        for i, kind in enumerate(kinds):
            if kind[0] == "var":
                changed = (kind[0], 1 - kind[1])
            elif kind[0] == "lu":
                changed = (kind[0], kind[1], 1 - kind[2])
            elif kind[0] == "vr":
                changed = (kind[0], 1 - kind[1], kind[2])
            else:
                changed = kind
            permutation[offset + i] = offset + lookup[changed]
        permutations.append(("swap_branches_module_" + str(pool), permutation))

    comparisons = 0
    for name, permutation in permutations:
        require(sorted(permutation) == list(range(16)), "Not an owner permutation")
        permuted_capacities = [0] * 16
        for i, destination in enumerate(permutation):
            permuted_capacities[destination] = CAPACITIES[i]
        for mask in range(1 << 16):
            permuted_mask = sum(1 << permutation[i] for i in range(16)
                                if mask >> i & 1)
            value = module.maxflow(
                edges, [capacity if permuted_mask >> i & 1 else 0
                        for i, capacity in enumerate(permuted_capacities)], source, sink)
            require(value == values[mask], name + " violates coalition equivariance")
            comparisons += 1
    require(comparisons == 196608, "Equivariance comparison scope changed")
    require(source_hash(dependency) == dependency_hash, "Dependency changed during run")
    return dict(
        status="PASS", schema_version=1,
        checker_sha256=source_hash(Path(__file__)),
        dependency_path=str(DEPENDENCY), dependency_sha256=dependency_hash,
        series_checks=series_results,
        owner_equivariance=dict(
            k=2, m=2, R=1, capacities_in_make_series_order=list(CAPACITIES),
            generators=[name for name, _ in permutations],
            coalition_masks_per_generator=1 << 16, positive_value_masks=225,
            comparisons=comparisons,
        ),
        elapsed_seconds=time.monotonic() - started,
        scope="Finite exact checks only; no all-profile, asymptotic, or novelty inference.",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.repo_root.resolve()), indent=2, sort_keys=True))
