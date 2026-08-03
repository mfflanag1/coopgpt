"""Discovery screen for bump capacity on all residual n=7 4+3 orbit games.

The exact cone audit stores one rational primal game for each of the 34
residual three-level eta-dual orbits.  This script computes, in floating point,
the leximin reference, carrier quantities, and every exposed-face term in the
exact bump-capacity formula.  It is a search diagnostic, not a proof artifact;
positive or boundary findings must be exactified separately.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from leximin import leximin_core_float
from screen_n7_outside_triple_leximin import (
    FULL,
    N,
    P,
    S,
    eta_at_reference,
    mask_from_members,
    payoff,
)


def bump_capacity(value):
    objective = np.array([-1.0 if player < 4 else 0.0 for player in range(N)])
    rows = np.array([
        [-1.0 if coalition >> player & 1 else 0.0 for player in range(N)]
        for coalition in range(1, FULL)
    ])
    bounds = -np.array(value[1:FULL], dtype=float)
    best = None
    limiters = []
    for face in range(1, FULL + 1):
        if face == S:
            continue
        result = linprog(
            objective,
            A_ub=rows,
            b_ub=bounds,
            A_eq=np.array([
                [1.0] * N,
                [1.0 if face >> player & 1 else 0.0 for player in range(N)],
            ]),
            b_eq=np.array([float(value[FULL]), float(value[face])]),
            bounds=[(None, None)] * N,
            method="highs",
        )
        if not result.success:
            raise RuntimeError(f"face {face}: {result.message}")
        candidate = -float(result.fun) - float(value[S])
        if best is None or candidate < best - 1e-8:
            best = candidate
            limiters = [face]
        elif abs(candidate - best) <= 1e-8:
            limiters.append(face)
    return best, limiters


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    audit = json.loads(args.audit.read_text())
    shape = next(shape for shape in audit["shapes"] if shape["S_size"] == 4)
    records = []
    for orbit in shape["orbits"]:
        slack = [F(0)] * (1 << N)
        for term in orbit["certificate"]["primal_nonzero_slacks"]:
            slack[mask_from_members(term["coalition"])] = F(term["value"])
        value = [-entry for entry in slack]
        phi = leximin_core_float(N, value, tol=1e-9)
        if phi is None:
            raise RuntimeError(f"leximin failed for orbit {orbit['orbit_index']}")
        reference_slack = [
            payoff(phi, coalition) - float(value[coalition])
            for coalition in range(1 << N)
        ]
        differences = [
            reference_slack[P | coalition] - reference_slack[coalition]
            for coalition in range(1, S)
        ]
        gamma = min(differences)
        eta = eta_at_reference(value, phi)
        sigma = sum(phi[:4]) - float(value[S])
        capacity, limiters = bump_capacity(value)
        records.append({
            "orbit_index": orbit["orbit_index"],
            "exact_cone_value": orbit["certificate"]["value"],
            "leximin": phi,
            "gamma_at_leximin": gamma,
            "eta_at_leximin": eta,
            "carrier_gap": gamma - eta,
            "selection_slack_sigma": sigma,
            "exact_bump_capacity": capacity,
            "capacity_minus_sigma": capacity - sigma,
            "capacity_limiting_faces": limiters,
            "carrier_bound_violated": eta < gamma - 1e-7,
            "binding_exact_bump_exists": capacity > sigma + 1e-7,
        })

    violations = [record for record in records if record["carrier_bound_violated"]]
    payload = {
        "status": "floating bump-capacity screen of all residual n=7 4+3 orbit games",
        "n": N,
        "S_size": 4,
        "P_size": 3,
        "orbits_screened": len(records),
        "leximin_carrier_violations": len(violations),
        "binding_bump_capable": sum(
            record["binding_exact_bump_exists"] for record in records
        ),
        "both_carrier_violating_and_binding_bump_capable": sum(
            record["carrier_bound_violated"]
            and record["binding_exact_bump_exists"]
            for record in records
        ),
        "violating_orbits": [record["orbit_index"] for record in violations],
        "all_violating_orbits_have_zero_capacity": all(
            abs(record["exact_bump_capacity"]) <= 1e-8 for record in violations
        ),
        "records": records,
        "scope": "discovery screen only; structural claims require exact replay",
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
