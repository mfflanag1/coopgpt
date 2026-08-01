"""Classify exact circuit orbits by balancedness neutralization.

Input is the exact orbit enumeration emitted by
``enumerate_disjoint_circuits_exact.py``.  HiGHS is used only to discover a
candidate LP dual.  Every accepted balancedness certificate is then checked
coefficientwise with :class:`fractions.Fraction`; a floating-point optimum is
never itself treated as proof.  Non-neutralized circuits are re-solved by the
project's exact rational simplex to produce an exact balanced endpoint witness.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from minimize_both_sensitive_support import balanced_endpoint_margin


def add(target, key, value):
    target[key] = target.get(key, F(0)) + F(value)
    if target[key] == 0:
        del target[key]


def as_circuit(detail):
    core, core_weights, mono, mono_weights = [], [], [], []
    for meta, weight in zip(detail["active_rows"], detail["circuit_weights"]):
        if meta[0] == "core":
            core.append((int(meta[1]), int(meta[2])))
            core_weights.append(int(weight))
        else:
            mono.append(tuple(int(value) for value in meta[1:]))
            mono_weights.append(int(weight))
    return {
        "core": tuple(core),
        "core_weights": tuple(core_weights),
        "mono": tuple(mono),
        "mono_weights": tuple(mono_weights),
        "efficiency": tuple(int(value) for value in detail["efficiency_weights"]),
    }


def build_balanced_lp(n, A, B, circuit):
    grand = (1 << n) - 1
    worth_offset = 3 * n
    d_A = worth_offset + grand - 1
    d_B = d_A + 1
    variable_count = d_B + 1
    objective = np.zeros(variable_count)
    for (game, coalition), weight in zip(circuit["core"], circuit["core_weights"]):
        objective[worth_offset + coalition - 1] -= weight
        if game == 1 and coalition == A:
            objective[d_A] -= weight
        if game == 2 and coalition == B:
            objective[d_B] -= weight

    A_ub, b_ub, rowmeta = [], [], []
    for game in range(3):
        for coalition in range(1, grand):
            row = np.zeros(variable_count)
            row[worth_offset + coalition - 1] = 1
            if game == 1 and coalition == A:
                row[d_A] = 1
            if game == 2 and coalition == B:
                row[d_B] = 1
            for player in range(n):
                if coalition >> player & 1:
                    row[game * n + player] = -1
            A_ub.append(row)
            b_ub.append(0)
            rowmeta.append((game, coalition))
    A_eq, b_eq = [], []
    for game in range(3):
        row = np.zeros(variable_count)
        row[game * n:(game + 1) * n] = 1
        A_eq.append(row)
        b_eq.append(1)
    bounds = [(None, None)] * variable_count
    bounds[d_A] = (0, None)
    bounds[d_B] = (0, None)
    return objective, A_ub, b_ub, A_eq, b_eq, bounds, rowmeta, (d_A, d_B)


def rationalize(value):
    return F(float(value)).limit_denominator(1_000_000)


def discover_and_verify_balanced_dual(n, A, B, circuit):
    (objective, A_ub, b_ub, A_eq, b_eq, bounds, rowmeta,
     bump_indices) = build_balanced_lp(n, A, B, circuit)
    result = linprog(
        objective,
        A_ub=np.asarray(A_ub), b_ub=np.asarray(b_ub),
        A_eq=np.asarray(A_eq), b_eq=np.asarray(b_eq),
        bounds=bounds, method="highs",
    )
    if not result.success:
        return None
    expected = sum(circuit["efficiency"])
    if rationalize(result.fun) != -expected:
        return None

    lower = {
        index: rationalize(value)
        for index, value in enumerate(result.lower.marginals)
        if abs(value) > 1e-8
    }
    if any(index not in bump_indices or value <= 0
           for index, value in lower.items()):
        return None
    lower_bumps = {}
    for label,index in zip(("A", "B"), bump_indices):
        if index in lower:
            lower_bumps[label] = lower[index]

    collections = [dict() for _ in range(3)]
    for index, value in enumerate(result.ineqlin.marginals):
        if abs(value) <= 1e-8:
            continue
        weight = rationalize(-value)
        if weight <= 0:
            return None
        game, coalition = rowmeta[index]
        collections[game][coalition] = weight
    totals = {
        game: rationalize(-result.eqlin.marginals[game])
        for game in range(3)
    }
    if any(total < 0 for total in totals.values()):
        return None

    for game, collection in enumerate(collections):
        coverage = [
            sum((weight for coalition, weight in collection.items()
                 if coalition >> player & 1), F(0))
            for player in range(n)
        ]
        if coverage != [totals[game]] * n:
            return None

    dual_worths = {}
    for game, collection in enumerate(collections):
        for coalition, weight in collection.items():
            add(dual_worths, ("b", coalition), weight)
            if game == 1 and coalition == A:
                add(dual_worths, ("d", "A"), weight)
            if game == 2 and coalition == B:
                add(dual_worths, ("d", "B"), weight)
    circuit_worths = {}
    for (game, coalition), weight in zip(circuit["core"], circuit["core_weights"]):
        add(circuit_worths, ("b", coalition), weight)
        if game == 1 and coalition == A:
            add(circuit_worths, ("d", "A"), weight)
        if game == 2 and coalition == B:
            add(circuit_worths, ("d", "B"), weight)
    expected_dual_worths = dict(circuit_worths)
    for label,weight in lower_bumps.items():
        add(expected_dual_worths, ("d", label), weight)
    if dual_worths != expected_dual_worths:
        return None
    if sum(totals.values()) != expected:
        return None

    return {
        "class": (
            "balancedness-plus-bump-nonnegativity-neutralized"
            if lower_bumps else "balancedness-neutralized"
        ),
        "collection_totals": [str(totals[game]) for game in range(3)],
        "collections": [
            [[coalition, str(weight)] for coalition, weight in sorted(collection.items())]
            for collection in collections
        ],
        "bump_nonnegativity_multipliers": {
            label: str(weight) for label,weight in sorted(lower_bumps.items())
        },
        "coefficient_identity_exact": True,
    }


def classify(payload):
    n, A, B = payload["n"], payload["A_mask"], payload["B_mask"]
    classified = []
    counts = {
        "balancedness-neutralized": 0,
        "balancedness-plus-bump-nonnegativity-neutralized": 0,
        "balanced-counterexample": 0,
    }
    for orbit_index, detail in enumerate(payload["circuits"], 1):
        circuit = as_circuit(detail)
        certificate = discover_and_verify_balanced_dual(n, A, B, circuit)
        if certificate is None:
            # The exact endpoint LP takes the enumerator's exact support and
            # primitive circuit weights, so its sign is proof-level evidence.
            # balanced_endpoint_margin expects global row indices and metadata;
            # map the exact enumerated rows back into the full matrix ordering.
            from search_both_sensitive_circuits import eliminated_matrix
            _matrix, _ineq, _eq, rowmeta = eliminated_matrix(n, A, B)
            metadata_index = {tuple(meta): index for index, meta in enumerate(rowmeta)}
            global_support = [metadata_index[tuple(meta)] for meta in detail["active_rows"]]
            exact = balanced_endpoint_margin(
                n, A, B, global_support, detail["circuit_weights"], rowmeta,
                detail["efficiency_weights"],
            )
            if exact.get("status") != "optimal" or not exact.get("balanced_counterexample"):
                raise AssertionError(
                    f"orbit {orbit_index}: neither exact balanced dual nor negative exact witness"
                )
            certificate = {"class": "balanced-counterexample", "exact_witness": exact}
        counts[certificate["class"]] += 1
        classified.append({
            "orbit_index": orbit_index,
            "support_size": detail["support_size"],
            "orbit_size": detail["orbit_size"],
            "classification": certificate,
        })
    return {
        "status": "every enumerated orbit classified with an exact certificate",
        "enumeration_status": payload["status"],
        "n": n,
        "A_mask": A,
        "B_mask": B,
        "orbit_counts": counts,
        "transported_support_counts": {
            key: sum(item["orbit_size"] for item in classified
                     if item["classification"]["class"] == key)
            for key in counts
        },
        "orbits": classified,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    payload = classify(json.loads(args.input.read_text()))
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")
