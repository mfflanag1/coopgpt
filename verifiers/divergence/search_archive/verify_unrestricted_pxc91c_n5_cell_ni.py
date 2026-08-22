#!/usr/bin/env python3
"""Independent n=5 PXC91c cell encoding using NI-min/NI-max relations."""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path
import z3

HERE = Path(__file__).resolve(); ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "verifiers/lib"))
import catalogue  # noqa: E402

N = 5; FULL = 31


def cone_rows():
    _letters, rows = catalogue.load(N); answer = set()
    for source in rows:
        for permutation in itertools.permutations(range(N)):
            row = [0] * 32
            for mask, coefficient in source["lam"].items():
                image = sum(1 << permutation[i] for i in range(N) if mask >> i & 1)
                row[image] += coefficient
            row[FULL] -= source["r"]; answer.add(tuple(row))
    return tuple(answer)


def blocks(order, composition):
    out = []; cursor = 0
    for size in composition:
        out.append(tuple(order[cursor:cursor + size])); cursor += size
    if cursor != len(order): raise ValueError("bad composition")
    return tuple(out)


def coalition_sum(point, mask):
    return z3.Sum([point[i] for i in range(N) if mask >> i & 1])


def ni_certificates(point, strata, selected, values, mode, prefix):
    """Staged normal-incidence identities, independently normalized.

    Rows from already pinned strata have free coefficients.  Rows in the
    current stratum have coefficients with the selector-appropriate sign;
    homogeneity lets us normalize the designated coefficient to one.
    """
    constraints = []; earlier = []
    for stage, block in enumerate(strata):
        for designated in block:
            lam = {mask: z3.Real(f"{prefix}_{stage}_{designated}_l{mask}")
                   for mask in range(1, FULL)}
            old = {i: z3.Real(f"{prefix}_{stage}_{designated}_b{i}")
                   for i in earlier}
            current = {i: z3.Real(f"{prefix}_{stage}_{designated}_a{i}")
                       for i in block}
            gamma = {i: z3.Real(f"{prefix}_{stage}_{designated}_g{i}")
                     for i in range(N)}
            constant = z3.Real(f"{prefix}_{stage}_{designated}_c")
            constraints += [q >= 0 for q in (*lam.values(), *current.values(),
                                              *gamma.values())]
            constraints.append(current[designated] == 1)
            for mask, multiplier in lam.items():
                if selected is None:
                    constraints.append(z3.Or(multiplier == 0,
                                             coalition_sum(point, mask) == values[mask]))
                else:
                    constraints.append(z3.Implies(z3.Not(selected[mask]),
                                                  multiplier == 0))
            for i, multiplier in gamma.items():
                constraints.append(z3.Or(multiplier == 0, point[i] == 0))
            for coordinate in range(N):
                lhs = z3.Sum([lam[m] for m in range(1, FULL)
                              if m >> coordinate & 1]) + gamma[coordinate]
                if coordinate in old:
                    lhs += old[coordinate]
                if coordinate in current:
                    lhs += (current[coordinate] if mode == "min"
                            else -current[coordinate])
                constraints.append(lhs == constant)
        earlier.extend(block)
    return constraints


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--x-composition", nargs="+", type=int, required=True)
    parser.add_argument("--top", nargs=2, type=int, required=True)
    parser.add_argument("--z-order", nargs=3, type=int, required=True)
    parser.add_argument("--z-composition", nargs="+", type=int, required=True)
    parser.add_argument("--timeout-ms", type=int, default=30000)
    parser.add_argument("--drop-exact-cone", action="store_true")
    parser.add_argument("--drop-singleton-normalization", action="store_true")
    args = parser.parse_args()
    xblocks = blocks(tuple(range(N)), args.x_composition)
    zblocks = (tuple(args.top),) + blocks(tuple(args.z_order), args.z_composition)
    v = [z3.Real(f"v{m}") for m in range(32)]
    x = [z3.Real(f"x{i}") for i in range(N)]
    z = [z3.Real(f"z{i}") for i in range(N)]
    d = [z3.Real(f"d{i}") for i in range(N)]
    chosen = {m: z3.Bool(f"choose{m}") for m in range(1, FULL)}
    solver = z3.Solver(); solver.set(timeout=args.timeout_ms)
    solver.add(v[0] == 0, v[FULL] == 1)
    if not args.drop_singleton_normalization:
        solver.add(*[v[1 << i] == 0 for i in range(N)])
    solver.add(*[v[m] >= 0 for m in range(1, FULL)])
    if not args.drop_exact_cone:
        for row in cone_rows():
            solver.add(z3.Sum([row[m] * v[m] for m in range(1, 32) if row[m]]) <= 0)
    solver.add(z3.Sum(x) == 1, z3.Sum(z) == 1,
               *[q >= 0 for q in x], *[q >= 0 for q in z])
    for point in (x, z):
        solver.add(*[coalition_sum(point, m) >= v[m] for m in range(1, FULL)])
    for point, ordered, increasing in ((x, xblocks, True), (z, zblocks, False)):
        for block in ordered:
            solver.add(*[point[i] == point[block[0]] for i in block])
        for before, after in zip(ordered, ordered[1:]):
            solver.add(point[before[0]] < point[after[0]] if increasing
                       else point[before[0]] > point[after[0]])
    solver.add(z3.Or([x[i] != z[i] for i in range(N)]))
    pair = (1 << args.top[0]) | (1 << args.top[1])
    solver.add(v[pair] == coalition_sum(z, pair))
    for mask in range(1, FULL):
        solver.add(z3.Implies(chosen[mask], v[mask] == coalition_sum(x, mask)))
    solver.add(*ni_certificates(x, xblocks, chosen, v, "min", "xmin"))
    solver.add(*ni_certificates(z, zblocks, None, v, "max", "zmax"))
    tangent = []
    for stage in range(1, len(zblocks)):
        earlier = tuple(i for block in zblocks[:stage] for i in block)
        block = zblocks[stage]
        for designated in block:
            conditions = [z3.Sum(d) == 0, d[designated] < 0]
            conditions += [d[i] == 0 for i in earlier]
            conditions += [d[i] <= 0 for i in block]
            conditions += [z3.Or(z[i] > 0, d[i] >= 0) for i in range(N)]
            for mask in range(1, FULL):
                conditions.append(z3.Or(z3.Not(chosen[mask]),
                                        coalition_sum(z, mask) > coalition_sum(x, mask),
                                        coalition_sum(d, mask) >= 0))
            tangent.append(z3.And(conditions))
    solver.add(z3.Or(tangent)); verdict = solver.check()
    payload = {"verdict": str(verdict),
               "x_blocks": [list(q) for q in xblocks],
               "z_blocks": [list(q) for q in zblocks],
               "encoding": "independent cumulative NI-min/NI-max",
               "drop_exact_cone": args.drop_exact_cone,
               "drop_singleton_normalization": args.drop_singleton_normalization}
    if verdict == z3.sat:
        model = solver.model()
        payload["candidate"] = {
            "v": [str(model.eval(q, model_completion=True)) for q in v],
            "x": [str(model.eval(q, model_completion=True)) for q in x],
            "z": [str(model.eval(q, model_completion=True)) for q in z],
            "d": [str(model.eval(q, model_completion=True)) for q in d],
            "cx_rows": [m for m in range(1, FULL)
                        if z3.is_true(model.eval(chosen[m], model_completion=True))]}
    print(json.dumps(payload))


if __name__ == "__main__": main()
