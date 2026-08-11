#!/usr/bin/env python3
"""Exact staged-circuit/interval-packing witnesses for hostile controls.

For each named pair whose spectral plus top-selection contribution is below
the hybrid target, this verifier chooses all of the following in one rational
feasibility problem:

* a normalized sign-coherent Lmin pinning relation for every residual gainer;
* its normalized sign-coherent Lmax mirror;
* nonnegative weights on the resulting strict residual carrier intervals;
* layer capacities bounded by the exact label-currency integrand; and
* total packed interval length at least the post-top target deficit.

An interval weight is conservatively bounded by the auxiliary-player
coefficient in the normalized staged relation that supplies it.  The output
is finite exact evidence for the named controls.  It is not a proof that an
adequate jointly chosen packet exists for every exact game.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from exactlp import exact_linprog  # noqa: E402

from audit_effective_bipartition import characteristic_function  # noqa: E402
from audit_lmax_overcover import coalition_sum  # noqa: E402
from audit_sign_coherent_staged_lifts import payoff_blocks  # noqa: E402
from audit_spectral_label_currency import spectral_decomposition  # noqa: E402
from verify_labelled_branch_duals import CASES  # noqa: E402


def exact_feasible_witness(values, x, z, actual_top, deficit):
    n = len(x)
    full = (1 << n) - 1
    residual = tuple(i for i in range(n) if i not in actual_top)
    gainers = tuple(i for i in residual if z[i] > x[i])
    losers = tuple(j for j in residual if x[j] > z[j])
    levels = sorted({F(0)} | {x[i] for i in residual} | {z[i] for i in residual})
    layers = tuple(zip(levels, levels[1:]))

    names = []
    equalities = []
    equality_rhs = []
    inequalities = []
    inequality_rhs = []
    certificates = []
    edges = []

    def variable(name):
        names.append(name)
        return len(names) - 1

    def add_nonnegative(index):
        inequalities.append({index: F(-1)})
        inequality_rhs.append(F(0))

    for mode, point in (("min", x), ("max", z)):
        blocks = payoff_blocks(point, mode)
        tight = tuple(
            coalition
            for coalition in range(1, full)
            if coalition_sum(point, coalition) == values[coalition]
        )
        for player in gainers:
            stage = next(k for k, block in enumerate(blocks) if player in block)
            cumulative = tuple(j for block in blocks[: stage + 1] for j in block)
            lambda_index = {
                coalition: variable((mode, player, "lambda", coalition))
                for coalition in tight
            }
            auxiliary_index = {
                j: variable((mode, player, "aux", j)) for j in cumulative
            }
            c_index = variable((mode, player, "c"))
            for index in (*lambda_index.values(), *auxiliary_index.values()):
                add_nonnegative(index)

            side = F(1 if mode == "min" else -1)
            rhs_side = F(-1 if mode == "min" else 1)
            for coordinate in range(n):
                row = {}
                for coalition, index in lambda_index.items():
                    if coalition >> coordinate & 1:
                        row[index] = F(1)
                if coordinate in auxiliary_index:
                    row[auxiliary_index[coordinate]] = side
                row[c_index] = F(-1)
                equalities.append(row)
                equality_rhs.append(rhs_side * F(int(coordinate == player)))

            certificate = {
                "mode": mode,
                "player": player,
                "stage": stage,
                "tight": tight,
                "lambda_index": lambda_index,
                "auxiliary_index": auxiliary_index,
                "c_index": c_index,
            }
            certificates.append(certificate)

            for loser in losers:
                if loser not in auxiliary_index:
                    continue
                if mode == "min":
                    start, end = x[loser], x[player]
                else:
                    start, end = z[player], z[loser]
                if start >= end:
                    continue
                rho_index = variable((mode, player, "rho", loser))
                add_nonnegative(rho_index)
                inequalities.append(
                    {rho_index: F(1), auxiliary_index[loser]: F(-1)}
                )
                inequality_rhs.append(F(0))
                edges.append(
                    {
                        "mode": mode,
                        "gainer": player,
                        "loser": loser,
                        "start": start,
                        "end": end,
                        "rho_index": rho_index,
                        "supply_index": auxiliary_index[loser],
                    }
                )

    for low, high in layers:
        upper_x = {i for i in residual if x[i] >= high}
        upper_z = {i for i in residual if z[i] >= high}
        capacity = min(
            len(upper_x & upper_z),
            len(set(residual) - (upper_x | upper_z)),
        )
        row = {
            edge["rho_index"]: F(1)
            for edge in edges
            if edge["start"] <= low and high <= edge["end"]
        }
        inequalities.append(row)
        inequality_rhs.append(F(capacity))

    target_row = {
        edge["rho_index"]: -(edge["end"] - edge["start"])
        for edge in edges
    }
    inequalities.append(target_row)
    inequality_rhs.append(-deficit)

    width = len(names)

    def dense(row):
        result = [F(0)] * width
        for index, coefficient in row.items():
            result[index] = coefficient
        return result

    aub = [dense(row) for row in inequalities]
    aeq = [dense(row) for row in equalities]
    status, _objective, solution = exact_linprog(
        [F(0)] * width, aub, inequality_rhs, aeq, equality_rhs
    )
    if status != "optimal":
        return {"status": status}

    for row, rhs in zip(aeq, equality_rhs):
        if sum((a * b for a, b in zip(row, solution)), F(0)) != rhs:
            raise AssertionError("returned staged equality is not exact")
    for row, rhs in zip(aub, inequality_rhs):
        if sum((a * b for a, b in zip(row, solution)), F(0)) > rhs:
            raise AssertionError("returned packing inequality is not exact")

    packed = sum(
        (edge["end"] - edge["start"]) * solution[edge["rho_index"]]
        for edge in edges
    )
    if packed < deficit:
        raise AssertionError("returned witness misses the target deficit")

    certificate_output = []
    for certificate in certificates:
        certificate_output.append(
            {
                "mode": certificate["mode"],
                "player": certificate["player"],
                "stage": certificate["stage"],
                "coalition_support": {
                    str(coalition): str(solution[index])
                    for coalition, index in certificate["lambda_index"].items()
                    if solution[index]
                },
                "auxiliary_support": {
                    str(player): str(solution[index])
                    for player, index in certificate["auxiliary_index"].items()
                    if solution[index]
                },
                "constant": str(solution[certificate["c_index"]]),
            }
        )
    packing_output = [
        {
            "mode": edge["mode"],
            "gainer": edge["gainer"],
            "loser": edge["loser"],
            "interval": [str(edge["start"]), str(edge["end"])],
            "weight": str(solution[edge["rho_index"]]),
            "available_supply": str(solution[edge["supply_index"]]),
        }
        for edge in edges
        if solution[edge["rho_index"]]
    ]
    return {
        "status": "exact feasible",
        "deficit": str(deficit),
        "packed_length": str(packed),
        "residual": list(residual),
        "gainers": list(gainers),
        "losers": list(losers),
        "certificates": certificate_output,
        "packing": packing_output,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows = []
    for case in CASES:
        g = tuple(map(F, case["g"]))
        h = tuple(map(F, case["h"]))
        values = characteristic_function(g, h)
        x = tuple(case["x"])
        z = tuple(case["z"])
        decomposition = spectral_decomposition(case["name"], values, x, z)
        total = sum(x, F(0))
        deficit = F(decomposition["post_top_deficit_ratio"]) * total
        if deficit == 0:
            rows.append(
                {
                    "name": case["name"],
                    "status": "not needed: spectral plus top contribution meets target",
                    "deficit": "0",
                }
            )
            continue
        witness = exact_feasible_witness(
            values, x, z, set(decomposition["actual_top"]), deficit
        )
        if witness["status"] != "exact feasible":
            raise AssertionError({"name": case["name"], **witness})
        rows.append({"name": case["name"], **witness})

    report = {
        "status": "exact rational staged-supply interval witnesses",
        "scope": (
            "finite hostile controls only; simultaneous certificate and packing "
            "feasibility does not prove the universal packet-existence lemma"
        ),
        "supply_rule": (
            "each interval weight is at most its auxiliary coefficient in a "
            "normalized sign-coherent staged pinning relation"
        ),
        "cases": rows,
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
