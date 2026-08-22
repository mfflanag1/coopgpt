#!/usr/bin/env python3
"""Exact Farkas decision for one unrestricted n=5 PXC91c stratum cell.

Each invocation fixes the ordered payoff strata of x and z.  It asks exact
linear-real arithmetic for an exact singleton-normalized game, an arbitrary x-tight
row set whose retained polytope has Lmin x, and a PXC92b tangent proving that
the tight top-pair lift loses a later Lmax stage.  SAT is only a symbolic
candidate until reconstructed as a game; UNSAT is a theorem for the declared
stratum cell, conditional on the validated 280-row exact-cone description.
Active nonnegativity normals are included, and coefficients on earlier
pinned strata are free.
"""
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

N = 5; FULL = (1 << N) - 1


def exact_cone_inequalities():
    _letters, rows = catalogue.load(N); out = set()
    for item in rows:
        for perm in itertools.permutations(range(N)):
            c = [0] * (1 << N)
            for mask, coefficient in item["lam"].items():
                image = sum(1 << perm[i] for i in range(N) if mask >> i & 1)
                c[image] += coefficient
            c[FULL] -= item["r"]; out.add(tuple(c))
    return tuple(sorted(out))


def blocks_from_composition(order, composition):
    if sum(composition) != len(order) or any(q <= 0 for q in composition):
        raise ValueError("composition does not cover order")
    blocks = []; cursor = 0
    for size in composition:
        blocks.append(tuple(order[cursor:cursor + size])); cursor += size
    return tuple(blocks)


def qsum(vector, mask):
    return z3.Sum([vector[i] for i in range(N) if mask >> i & 1])


def staged_farkas(point, blocks, selected, values, mode, prefix, sign_coherent):
    """PXC92b polar certificates; old-pin coefficients may remain free."""
    constraints = []; side = 1 if mode == "min" else -1
    earlier = []
    for stage, block in enumerate(blocks):
        for designated in block:
            lam = {mask: z3.Real(f"{prefix}_s{stage}_p{designated}_l{mask}")
                   for mask in range(1, FULL)}
            old = {i: z3.Real(f"{prefix}_s{stage}_p{designated}_q{i}")
                   for i in earlier}
            current = {i: z3.Real(f"{prefix}_s{stage}_p{designated}_r{i}")
                       for i in block}
            nonnegative = {i: z3.Real(f"{prefix}_s{stage}_p{designated}_g{i}")
                           for i in range(N)}
            constant = z3.Real(f"{prefix}_s{stage}_p{designated}_c")
            constraints += [q >= 0 for q in lam.values()]
            constraints += [q >= 0 for q in current.values()]
            constraints += [q >= 0 for q in nonnegative.values()]
            if sign_coherent:
                constraints += ([q >= 0 for q in old.values()] if mode == "min"
                                else [q <= 0 for q in old.values()])
            for mask, multiplier in lam.items():
                if selected is not None:
                    constraints.append(z3.Implies(z3.Not(selected[mask]),
                                                  multiplier == 0))
                else:
                    constraints.append(z3.Or(multiplier == 0,
                                             qsum(point, mask) == values[mask]))
            for coordinate, multiplier in nonnegative.items():
                constraints.append(z3.Or(multiplier == 0, point[coordinate] == 0))
            for coordinate in range(N):
                expression = z3.Sum([
                    multiplier for mask, multiplier in lam.items()
                    if mask >> coordinate & 1
                ]) - constant
                if coordinate in old: expression += old[coordinate]
                if coordinate in current: expression += side * current[coordinate]
                expression += nonnegative[coordinate]
                constraints.append(expression == -side * (coordinate == designated))
        earlier.extend(block)
    return constraints


def rational_string(value):
    value = z3.simplify(value)
    if z3.is_rational_value(value):
        return str(value.as_fraction())
    return str(value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--x-composition", nargs="+", type=int, required=True)
    parser.add_argument("--top", nargs=2, type=int, required=True)
    parser.add_argument("--z-order", nargs=3, type=int, required=True)
    parser.add_argument("--z-composition", nargs="+", type=int, required=True)
    parser.add_argument("--timeout-ms", type=int, default=120000)
    parser.add_argument("--drop-exact-cone", action="store_true")
    parser.add_argument("--drop-singleton-normalization", action="store_true")
    parser.add_argument("--sign-coherent-old-pins", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if sorted((*args.top, *args.z_order)) != list(range(N)):
        raise ValueError("top and z-order must partition players")
    x_blocks = blocks_from_composition(tuple(range(N)), tuple(args.x_composition))
    z_blocks = (tuple(args.top),) + blocks_from_composition(
        tuple(args.z_order), tuple(args.z_composition)
    )
    v = [z3.Real(f"v{mask}") for mask in range(1 << N)]
    x = [z3.Real(f"x{i}") for i in range(N)]
    z = [z3.Real(f"z{i}") for i in range(N)]
    d = [z3.Real(f"d{i}") for i in range(N)]
    selected = {mask: z3.Bool(f"cx_{mask}") for mask in range(1, FULL)}
    solver = z3.Solver(); solver.set(timeout=args.timeout_ms)
    solver.add(v[0] == 0, v[FULL] == 1)
    if not args.drop_singleton_normalization:
        for i in range(N): solver.add(v[1 << i] == 0)
    for mask in range(1, FULL): solver.add(v[mask] >= 0)
    if not args.drop_exact_cone:
        for coefficients in exact_cone_inequalities():
            solver.add(z3.Sum([coefficients[m] * v[m] for m in range(1, FULL + 1)
                               if coefficients[m]]) <= 0)
    solver.add(z3.Sum(x) == 1, z3.Sum(z) == 1)
    solver.add(*[q >= 0 for q in x], *[q >= 0 for q in z])
    for point in (x, z):
        solver.add(*[qsum(point, mask) >= v[mask] for mask in range(1, FULL)])
    # Fixed ordered strata, with strict separation between successive blocks.
    for blocks, point in ((x_blocks, x), (z_blocks, z)):
        for block in blocks:
            solver.add(*[point[i] == point[block[0]] for i in block])
        for left, right in zip(blocks, blocks[1:]):
            if point is x:
                solver.add(point[left[0]] < point[right[0]])
            else:
                solver.add(point[left[0]] > point[right[0]])
    solver.add(z3.Or([x[i] != z[i] for i in range(N)]))
    pair = (1 << args.top[0]) | (1 << args.top[1])
    solver.add(v[pair] == qsum(z, pair))
    for mask in range(1, FULL):
        solver.add(z3.Implies(selected[mask], v[mask] == qsum(x, mask)))
    solver.add(*staged_farkas(x, x_blocks, selected, v, "min", "cxmin",
                              args.sign_coherent_old_pins))
    solver.add(*staged_farkas(z, z_blocks, None, v, "max", "fullmax",
                              args.sign_coherent_old_pins))
    # A single disjunction encodes every forbidden later-stage PXC92b tangent.
    tangent_cases = []
    for stage in range(1, len(z_blocks)):
        earlier = tuple(i for block in z_blocks[:stage] for i in block)
        block = z_blocks[stage]
        for designated in block:
            conditions = [z3.Sum(d) == 0, d[designated] < 0]
            conditions += [d[i] == 0 for i in earlier]
            conditions += [d[i] <= 0 for i in block]
            conditions += [z3.Or(z[i] > 0, d[i] >= 0) for i in range(N)]
            for mask in range(1, FULL):
                conditions.append(z3.Or(
                    z3.Not(selected[mask]), qsum(z, mask) > qsum(x, mask),
                    qsum(d, mask) >= 0,
                ))
            tangent_cases.append(z3.And(conditions))
    solver.add(z3.Or(tangent_cases))
    verdict = solver.check(); model = solver.model() if verdict == z3.sat else None
    payload = {
        "claim": "exact-cone PXC91c n=5 stratum-cell decision",
        "x_blocks": [list(q) for q in x_blocks],
        "z_blocks": [list(q) for q in z_blocks],
        "exact_cone_inequalities": 280,
        "timeout_ms": args.timeout_ms,
        "drop_exact_cone": args.drop_exact_cone,
        "drop_singleton_normalization": args.drop_singleton_normalization,
        "sign_coherent_old_pins": args.sign_coherent_old_pins,
        "farkas_encoding": "PXC92b at every Lmin/Lmax stage",
        "verdict": str(verdict),
        "scope": (
            "one ordered x/z stratum cell; UNSAT is a cell theorem under the "
            "validated five-player exact-cone description; SAT requires reconstruction"
        ),
    }
    if verdict == z3.sat:
        payload["candidate"] = {
            "v": [rational_string(model.eval(q, model_completion=True)) for q in v],
            "x": [rational_string(model.eval(q, model_completion=True)) for q in x],
            "z": [rational_string(model.eval(q, model_completion=True)) for q in z],
            "d": [rational_string(model.eval(q, model_completion=True)) for q in d],
            "cx_rows": [mask for mask in range(1, FULL)
                        if z3.is_true(model.eval(selected[mask], model_completion=True))],
        }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output: args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__": main()
