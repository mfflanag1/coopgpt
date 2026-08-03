"""Screen the fourteen residual n=7 outside-triple cone optima at leximin.

The exact cone audit saves one normalized exact game for each residual
three-level eta-dual orbit.  This script reconstructs every zero-cost game,
computes its leximin point with the floating Maschler implementation, and
evaluates gamma and eta at that point.  It is a discovery screen: any positive
gap must be exactified separately before being used as a theorem.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from leximin import leximin_core_float


N = 7
FULL = (1 << N) - 1
S = (1 << 4) - 1
P = FULL ^ S


def mask_from_members(players):
    return sum(1 << (int(player) - 1) for player in players)


def payoff(point, coalition):
    return sum(point[player] for player in range(N) if coalition >> player & 1)


def eta_at_reference(value, reference):
    objective = np.array([
        -1.0 if player < 4 else 0.0 for player in range(N)
    ])
    rows = []
    bounds = []
    for coalition in range(1, FULL):
        rows.append([
            -1.0 if coalition >> player & 1 else 0.0
            for player in range(N)
        ])
        bounds.append(-float(value[coalition]))
    for player in range(4):
        row = [0.0] * N
        row[player] = -1.0
        rows.append(row)
        bounds.append(-float(reference[player]))
    result = linprog(
        objective,
        A_ub=np.array(rows),
        b_ub=np.array(bounds),
        A_eq=np.ones((1, N)),
        b_eq=np.array([float(value[FULL])]),
        bounds=[(None, None)] * N,
        method="highs",
    )
    if not result.success:
        raise RuntimeError(result.message)
    return -float(result.fun) - sum(reference[:4])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    audit = json.loads(args.audit.read_text())
    shape = next(shape for shape in audit["shapes"] if shape["S_size"] == 4)
    records = []
    for orbit in shape["orbits"]:
        if orbit["certificate"]["value"] != "0":
            continue
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
        records.append({
            "orbit_index": orbit["orbit_index"],
            "leximin": phi,
            "gamma_at_leximin": gamma,
            "eta_at_leximin": eta,
            "gap": gamma - eta,
            "carrier_bound_violated": eta < gamma - 1e-7,
        })
    payload = {
        "status": "floating leximin screen of exact-cone zero-cost 4+3 orbits",
        "n": N,
        "S_size": 4,
        "P_size": 3,
        "orbits_screened": len(records),
        "positive_gamma": sum(record["gamma_at_leximin"] > 1e-7 for record in records),
        "violations": sum(record["carrier_bound_violated"] for record in records),
        "minimum_eta_minus_gamma": min(
            record["eta_at_leximin"] - record["gamma_at_leximin"]
            for record in records
        ),
        "records": records,
        "scope": "discovery screen only; positive findings require exact replay",
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
