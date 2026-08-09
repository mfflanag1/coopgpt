#!/usr/bin/env python3
"""Core-equivalent full-staged decision encoding for the six-player bound.

The earlier pipeline imposed exactness by adjoining one attaining core point
for every proper coalition.  That is unnecessary for a statement depending
only on the core selections.  Given any compact nonempty core polytope C, its
closure

    vhat(S) = min_{w in C} w(S)

is exact and has Core(vhat)=C.  Consequently it is enough to enforce one core
witness with coordinate i equal to zero for each player i.  The closure is then
singleton-normalized, while Lmin and Lmax are unchanged.

This module combines that reduction with shared tightness markers and the full
per-player staged Farkas certificates from ``nsix.py``.  SAT models must still
be closed and independently recomputed before being reported as games; UNSAT
is a verdict for the specified stratum/table configuration.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path

import z3


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nsix  # noqa: E402


def pipeline2_core_closure(n, r, c, table, target=F(2, 3), fail=True):
    """Return the reduced full-staged solver and its principal variables."""
    full = (1 << n) - 1
    proper = tuple(range(1, full))
    cell = nsix.layout(n, r, c, table)
    row_count, column_count = len(r), len(c)
    solver = z3.Solver()
    m, maximum_levels = nsix.levels(n, r, c, solver)
    x = [m[cell[i][0]] for i in range(n)]
    z = [maximum_levels[cell[i][1]] for i in range(n)]
    v = [z3.Real(f"v{coalition}") for coalition in range(1 << n)]
    solver.add(v[0] == 0, v[full] == 1)
    for i in range(n):
        solver.add(v[1 << i] == 0)

    def point_sum(point, coalition):
        return z3.Sum([point[i] for i in range(n) if coalition >> i & 1])

    for coalition in proper:
        solver.add(v[coalition] <= point_sum(x, coalition))
        solver.add(v[coalition] <= point_sum(z, coalition))

    # Only singleton attainment is required.  Closing the resulting compact
    # core polytope exactifies every other coalition without changing the core.
    singleton_witnesses = []
    for i in range(n):
        witness = [z3.Real(f"singleton_witness_{i}_{j}") for j in range(n)]
        singleton_witnesses.append(witness)
        solver.add(z3.Sum(witness) == 1, witness[i] == 0)
        for coalition in proper:
            solver.add(point_sum(witness, coalition) >= v[coalition])

    tight_x = {coalition: z3.Bool(f"tight_x_{coalition}") for coalition in proper}
    tight_z = {coalition: z3.Bool(f"tight_z_{coalition}") for coalition in proper}
    for coalition in proper:
        # These are shared support-eligibility markers, not declarations of the
        # entire tight family.  Only marker => tightness is needed: a model can
        # mark exactly the coalitions used by at least one staged certificate.
        # Requiring the reverse implication creates 124 unnecessary Boolean
        # decisions and was the main residue in the first closure census.
        solver.add(
            z3.Implies(tight_x[coalition], point_sum(x, coalition) == v[coalition])
        )
        solver.add(
            z3.Implies(tight_z[coalition], point_sum(z, coalition) == v[coalition])
        )

    row_blocks = [
        [i for i in range(n) if cell[i][0] == k] for k in range(row_count)
    ]
    column_blocks = [
        [i for i in range(n) if cell[i][1] == k] for k in range(column_count)
    ]

    def staged_farkas(point, blocks, ceiling, tag, tight):
        sign = 1 if ceiling else -1
        rhs = -1 if ceiling else 1
        pinned = []
        for stage, block in enumerate(blocks):
            for i in block:
                weights = {
                    coalition: z3.Real(f"{tag}_weight_{stage}_{i}_{coalition}")
                    for coalition in proper
                }
                efficiency = z3.Real(f"{tag}_efficiency_{stage}_{i}")
                old_pin = {
                    j: z3.Real(f"{tag}_old_pin_{stage}_{i}_{j}") for j in pinned
                }
                level_side = {
                    j: z3.Real(f"{tag}_level_side_{stage}_{i}_{j}") for j in block
                }
                for coalition in proper:
                    solver.add(weights[coalition] >= 0)
                    solver.add(z3.Implies(weights[coalition] > 0, tight[coalition]))
                for j in block:
                    solver.add(level_side[j] >= 0)
                for j in range(n):
                    stationarity = -z3.Sum(
                        [weights[S] for S in proper if S >> j & 1]
                    ) + efficiency
                    if j in pinned:
                        stationarity += old_pin[j]
                    if j in block:
                        stationarity += sign * level_side[j]
                    solver.add(stationarity == (rhs if j == i else 0))
            pinned.extend(block)

    staged_farkas(x, row_blocks, False, "floor", tight_x)
    staged_farkas(z, column_blocks[::-1], True, "ceiling", tight_z)

    distance = z3.Sum(
        [
            nsix.q(table[k][l]) * z3.Abs(m[k] - maximum_levels[l])
            for k in range(row_count)
            for l in range(column_count)
            if table[k][l]
        ]
    )
    solver.add(distance > nsix.q(target) if fail else distance <= nsix.q(target))
    return {
        "solver": solver,
        "v": v,
        "lmin_levels": m,
        "lmax_levels": maximum_levels,
        "lmin": x,
        "lmax": z,
        "singleton_witnesses": singleton_witnesses,
        "distance": distance,
        "cell": cell,
        "tight_lmax": tight_z,
    }


def pipeline2_generator_normal_form(n, r, c, table, target=F(2, 3), fail=True):
    """Full-staged encoding directly in the ``n+2``-generator normal form.

    This is existence-equivalent to :func:`pipeline2_core_closure`.  It omits
    the provisional characteristic function: a support coalition is tight at
    x (respectively z) exactly when every other displayed generator has at
    least the x-sum (respectively z-sum) on that coalition.
    """
    full = (1 << n) - 1
    proper = tuple(range(1, full))
    cell = nsix.layout(n, r, c, table)
    solver = z3.Solver()
    m, maximum_levels = nsix.levels(n, r, c, solver)
    x = [m[cell[i][0]] for i in range(n)]
    z = [maximum_levels[cell[i][1]] for i in range(n)]

    singleton_witnesses = []
    for i in range(n):
        witness = [z3.Real(f"singleton_witness_{i}_{j}") for j in range(n)]
        singleton_witnesses.append(witness)
        solver.add(z3.Sum(witness) == 1, witness[i] == 0)
        solver.add(*[coordinate >= 0 for coordinate in witness])

    def point_sum(point, coalition):
        return z3.Sum([point[i] for i in range(n) if coalition >> i & 1])

    generators = [x, z] + singleton_witnesses
    tight_x = {coalition: z3.Bool(f"tight_x_{coalition}") for coalition in proper}
    tight_z = {coalition: z3.Bool(f"tight_z_{coalition}") for coalition in proper}
    for coalition in proper:
        x_sum = point_sum(x, coalition)
        z_sum = point_sum(z, coalition)
        solver.add(
            z3.Implies(
                tight_x[coalition],
                z3.And(
                    [x_sum <= point_sum(g, coalition) for g in generators[1:]]
                ),
            )
        )
        solver.add(
            z3.Implies(
                tight_z[coalition],
                z3.And(
                    [z_sum <= point_sum(g, coalition) for g in [x] + singleton_witnesses]
                ),
            )
        )

    row_blocks = [
        [i for i in range(n) if cell[i][0] == k] for k in range(len(r))
    ]
    column_blocks = [
        [i for i in range(n) if cell[i][1] == k] for k in range(len(c))
    ]

    def staged_farkas(blocks, ceiling, tag, tight):
        sign = 1 if ceiling else -1
        rhs = -1 if ceiling else 1
        pinned = []
        for stage, block in enumerate(blocks):
            for i in block:
                weights = {
                    coalition: z3.Real(f"{tag}_weight_{stage}_{i}_{coalition}")
                    for coalition in proper
                }
                efficiency = z3.Real(f"{tag}_efficiency_{stage}_{i}")
                old_pin = {
                    j: z3.Real(f"{tag}_old_pin_{stage}_{i}_{j}") for j in pinned
                }
                level_side = {
                    j: z3.Real(f"{tag}_level_side_{stage}_{i}_{j}") for j in block
                }
                for coalition in proper:
                    solver.add(weights[coalition] >= 0)
                    solver.add(z3.Implies(weights[coalition] > 0, tight[coalition]))
                for j in block:
                    solver.add(level_side[j] >= 0)
                for j in range(n):
                    stationarity = -z3.Sum(
                        [weights[S] for S in proper if S >> j & 1]
                    ) + efficiency
                    if j in pinned:
                        stationarity += old_pin[j]
                    if j in block:
                        stationarity += sign * level_side[j]
                    solver.add(stationarity == (rhs if j == i else 0))
            pinned.extend(block)

    staged_farkas(row_blocks, False, "floor", tight_x)
    staged_farkas(column_blocks[::-1], True, "ceiling", tight_z)

    distance = z3.Sum(
        [
            nsix.q(table[k][l]) * z3.Abs(m[k] - maximum_levels[l])
            for k in range(len(r))
            for l in range(len(c))
            if table[k][l]
        ]
    )
    solver.add(distance > nsix.q(target) if fail else distance <= nsix.q(target))
    return {
        "solver": solver,
        "v": None,
        "lmin_levels": m,
        "lmax_levels": maximum_levels,
        "lmin": x,
        "lmax": z,
        "singleton_witnesses": singleton_witnesses,
        "distance": distance,
        "cell": cell,
        "tight_lmax": tight_z,
        "generators": generators,
        "encoding": "n+2-generator normal form",
    }


def require_equality_without_uniform_triple_anchor(data, lmax_composition):
    """Add the negation of the observed six-player equality geometry.

    A tight coalition of three Lmax-top players gives the zero-baseline
    over-cover ``(1/3) 1_A = alpha`` with alpha uniform on that triple.  This
    helper asks for distance 2/3 while forbidding every such coalition.
    """
    data["solver"].add(data["distance"] == z3.RealVal("2/3"))
    top_column = len(lmax_composition) - 1
    top = [i for i, (_, column) in enumerate(data["cell"]) if column == top_column]
    triple_masks = []
    for triple in itertools.combinations(top, 3):
        coalition = sum(1 << i for i in triple)
        triple_masks.append(coalition)
        coalition_sum = z3.Sum([data["lmax"][i] for i in triple])
        if data["v"] is not None:
            data["solver"].add(coalition_sum != data["v"][coalition])
        else:
            data["solver"].add(
                z3.Or(
                    [
                        z3.Sum([g[i] for i in triple]) < coalition_sum
                        for g in data["generators"]
                        if g is not data["lmax"]
                    ]
                )
            )
    return tuple(triple_masks)


def require_equality_with_subthird_overcover(data, lmax_composition):
    """Ask for equality together with an Lmax over-cover of dispersion <1/3."""
    solver = data["solver"]
    solver.add(data["distance"] == z3.RealVal("2/3"))
    n = len(data["cell"])
    full = (1 << n) - 1
    proper = tuple(range(1, full))
    top_column = len(lmax_composition) - 1
    top = tuple(i for i, (_, column) in enumerate(data["cell"]) if column == top_column)
    weights = {S: z3.Real(f"dispersion_weight_{S}") for S in proper}
    eta = z3.Real("dispersion_eta")
    alpha = {i: z3.Real(f"dispersion_alpha_{i}") for i in top}
    solver.add(eta >= 0)
    for coalition in proper:
        solver.add(weights[coalition] >= 0)
        solver.add(
            z3.Implies(weights[coalition] > 0, data["tight_lmax"][coalition])
        )
    for i in top:
        solver.add(alpha[i] >= 0, alpha[i] < z3.RealVal("1/3"))
    solver.add(z3.Sum([alpha[i] for i in top]) == 1)
    for i in range(n):
        load = z3.Sum([weights[S] for S in proper if S >> i & 1])
        solver.add(load == eta + (alpha[i] if i in alpha else 0))
    return {"weights": weights, "eta": eta, "alpha": alpha}


def parse_composition(raw):
    return tuple(int(part) for part in raw.split(",") if part)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lmin", required=True, help="ascending stratum sizes, e.g. 1,3,1,1")
    parser.add_argument("--lmax", required=True, help="ascending stratum sizes, e.g. 1,1,1,1,2")
    parser.add_argument("--table-index", type=int, default=0)
    parser.add_argument("--timeout", type=int, default=600, help="seconds")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    r, c = parse_composition(args.lmin), parse_composition(args.lmax)
    if sum(r) != 6 or sum(c) != 6:
        parser.error("both compositions must sum to six")
    tables = nsix.tables(r, c)
    if not 0 <= args.table_index < len(tables):
        parser.error(f"table index must lie in [0,{len(tables)})")
    table = tables[args.table_index]
    data = pipeline2_core_closure(6, r, c, table)
    data["solver"].set(timeout=args.timeout * 1000)
    started = time.monotonic()
    verdict = data["solver"].check()
    elapsed = time.monotonic() - started
    report = {
        "status": str(verdict),
        "scope": "one exact stratum/table configuration; closure reduction",
        "lmin_composition": r,
        "lmax_composition": c,
        "table_index": args.table_index,
        "table": table,
        "target_l1_distance": "2/3",
        "strict_failure_test": True,
        "elapsed_seconds": round(elapsed, 3),
    }
    if verdict == z3.sat:
        model = data["solver"].model()
        report["candidate_lmin"] = [str(model.eval(value)) for value in data["lmin"]]
        report["candidate_lmax"] = [str(model.eval(value)) for value in data["lmax"]]
        report["candidate_singleton_witnesses"] = [
            [str(model.eval(value)) for value in witness]
            for witness in data["singleton_witnesses"]
        ]
        report["candidate_distance"] = str(model.eval(data["distance"]))
        report["warning"] = (
            "form the lower envelope of Lmin, Lmax, and the singleton witnesses; "
            "then independently recompute both selections"
        )
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
