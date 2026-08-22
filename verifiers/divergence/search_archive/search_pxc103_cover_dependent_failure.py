#!/usr/bin/env python3
"""Targeted exact falsifier for the PXC103 common-direction mechanism.

This is not a random search for more PXC91c counterexamples.  It retains only
exact singleton-normalized six-player games with two Lmax-top players, a fully
enumerated complete-Cx pool, and a fixed Cx for which every qualifying extreme
top cover is unfaithful.  It then asks the sharply targeted question left open
after PXC103: does one staged Lmax descent annihilate the union of *all* cover
supports?  A retained hit with no such direction is a second, cover-dependent
failure mechanism and falsifies the proposed universal common-direction
classification.

Discovery allocations are integral and every retained profile is replayed in
exact rational arithmetic.  A non-common hit remains a candidate until an
independent implementation reconstructs the full game and cover/Cx censuses.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
DIV = ROOT / "verifiers" / "divergence"
sys.path[:0] = [str(ROOT / "src"), str(DIV), str(HERE.parent)]

from exactlp import exact_linprog  # noqa: E402
from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from audit_sign_coherent_staged_lifts import payoff_blocks  # noqa: E402
from unrestricted_pxc91c_exact_search import (  # noqa: E402
    audit_game,
    canonical_cx,
    covers as cover_census,
    csum,
    matrix_rank,
    N6_COUNTEREXAMPLE_X,
    N6_COUNTEREXAMPLE_Z,
    PXC90_Z,
    PXC_X,
    selector_from_constraints,
    tight_rows,
)
from unrestricted_pxc91c_random_envelopes import (  # noqa: E402
    capped_two_top_generators,
    random_allocation,
)


def _row(mask: int, n: int) -> list[F]:
    return [F((mask >> i) & 1) for i in range(n)]


def common_staged_direction_xz(x, z, cx, covers):
    """Return an exact PXC103 common direction, or ``None``.

    The Cx rows active at z are inequalities.  Every row appearing positively
    in some qualifying cover is imposed as an equality.  Homogeneity lets us
    normalize the designated improving coordinate to at most -1.
    """
    n = len(z)
    union = tuple(sorted({row for cover in covers for row in cover["rows"]}))
    common_cx = tuple(row for row in cx if csum(x, row) == csum(z, row))
    blocks = payoff_blocks(z, "max")
    for stage in range(1, len(blocks)):
        earlier = tuple(i for block in blocks[:stage] for i in block)
        block = tuple(blocks[stage])
        for designated in block:
            aub, bub = [], []
            for row in common_cx:
                aub.append([-q for q in _row(row, n)])
                bub.append(F(0))
            for i, value in enumerate(z):
                if value == 0:
                    coeff = [F(0)] * n
                    coeff[i] = F(-1)  # d_i >= 0
                    aub.append(coeff)
                    bub.append(F(0))
            for i in block:
                coeff = [F(0)] * n
                coeff[i] = F(1)       # d_i <= 0
                aub.append(coeff)
                bub.append(F(-1) if i == designated else F(0))
            aeq = [[F(1)] * n]
            beq = [F(0)]
            for i in earlier:
                coeff = [F(0)] * n
                coeff[i] = F(1)
                aeq.append(coeff)
                beq.append(F(0))
            for row in union:
                aeq.append(_row(row, n))
                beq.append(F(0))
            status, _opt, direction = exact_linprog(
                [F(0)] * n, A_ub=aub, b_ub=bub, A_eq=aeq, b_eq=beq
            )
            if status == "optimal":
                if direction[designated] > -1:
                    raise AssertionError("normalization lost")
                return {
                    "stage": stage,
                    "designated": designated,
                    "direction": list(map(str, direction)),
                    "cover_union": list(union),
                    "common_active_cx": list(common_cx),
                }
    return None


def generated_allocations(rng, mode, n, total, count):
    if mode == "capped":
        return capped_two_top_generators(rng, n, total, count)
    if mode == "top_symmetric":
        base = tuple(
            random_allocation(rng, n, total, j % n)
            for j in range(max(n, (count + 1) // 2))
        )
        return base + tuple((g[1], g[0], *g[2:]) for g in base)
    return tuple(random_allocation(rng, n, total, j % n) for j in range(count))


def float_selector_from_constraints(constraints, n, total, mode):
    """Fast discovery-only staged selector; exact replay gates every survivor."""
    pinned = {}
    free = set(range(n))

    def base(width):
        aub, bub = [], []
        for mask, bound in constraints.items():
            row = [-float((mask >> i) & 1) for i in range(n)]
            aub.append(row + [0.0] * (width - n))
            bub.append(-float(bound))
        aeq = [[1.0] * n + [0.0] * (width - n)]
        beq = [float(total)]
        for player, value in pinned.items():
            row = [0.0] * width
            row[player] = 1.0
            aeq.append(row)
            beq.append(value)
        return aub, bub, aeq, beq

    while free:
        width = n + 1
        aub, bub, aeq, beq = base(width)
        for player in free:
            row = [0.0] * width
            row[player], row[n] = ((-1.0, 1.0) if mode == "min"
                                   else (1.0, -1.0))
            aub.append(row)
            bub.append(0.0)
        objective = [0.0] * width
        objective[n] = -1.0 if mode == "min" else 1.0
        result = linprog(objective, A_ub=np.asarray(aub), b_ub=np.asarray(bub),
                         A_eq=np.asarray(aeq), b_eq=np.asarray(beq),
                         bounds=[(0, None)] * n + [(None, None)], method="highs")
        if not result.success:
            return None
        level = float(result.x[n])
        aub, bub, aeq, beq = base(n)
        for player in free:
            row = [0.0] * n
            row[player] = -1.0 if mode == "min" else 1.0
            aub.append(row)
            bub.append(-level if mode == "min" else level)
        newly = []
        for player in sorted(free):
            objective = [0.0] * n
            objective[player] = -1.0 if mode == "min" else 1.0
            result = linprog(objective, A_ub=np.asarray(aub), b_ub=np.asarray(bub),
                             A_eq=np.asarray(aeq), b_eq=np.asarray(beq),
                             bounds=[(0, None)] * n, method="highs")
            if not result.success:
                return None
            trial = -float(result.fun) if mode == "min" else float(result.fun)
            if abs(trial - level) <= 1e-7:
                newly.append(player)
        if not newly:
            return None
        for player in newly:
            pinned[player] = level
            free.remove(player)
    return tuple(pinned[i] for i in range(n))


def calibration_controls():
    pxc98 = common_staged_direction_xz(
        N6_COUNTEREXAMPLE_X, N6_COUNTEREXAMPLE_Z, (7, 11),
        ({"rows": [3]}, {"rows": [7, 11, 51]}),
    )
    if pxc98 is None or 17 in pxc98["cover_union"]:
        raise AssertionError("PXC98 common forced-zero calibration failed")
    if csum(tuple(map(F, pxc98["direction"])), 17) >= 0:
        raise AssertionError("PXC98 blocker no longer cuts the direction")

    pxc90 = common_staged_direction_xz(
        PXC_X, PXC90_Z, (7, 11, 13),
        ({"rows": [23, 27, 39, 75, 114]},),
    )
    if pxc90 is not None:
        raise AssertionError("full-rank PXC90 acquired a common descent")

    control_x = tuple(map(F, (F(25, 4), F(25, 4), F(1, 2),
                              F(9, 4), F(1, 2), F(9, 4))))
    control_z = tuple(map(F, (6, 6, 0, 2, 1, 3)))
    control_covers = tuple({"rows": rows} for rows in (
        [3], [19, 47], [23, 43], [4, 19, 43], [7, 19, 43],
    ))
    second = common_staged_direction_xz(
        control_x, control_z, (19, 43), control_covers,
    )
    if second is None or 39 in second["cover_union"]:
        raise AssertionError("second n=6 common-direction control failed")
    return {"pxc98": pxc98, "pxc90_common_direction": pxc90,
            "second_n6_control": second}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260822)
    parser.add_argument("--mode", choices=("plain", "capped", "top_symmetric"),
                        default="capped")
    parser.add_argument("--total-min", type=int, default=10)
    parser.add_argument("--total-max", type=int, default=20)
    parser.add_argument("--generators-min", type=int, default=5)
    parser.add_argument("--generators-max", type=int, default=9)
    parser.add_argument("--cx-pool-max", type=int, default=12)
    parser.add_argument("--stop-after", type=int, default=1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    controls = calibration_controls()
    rng = random.Random(args.seed)
    stats = Counter()
    common_controls, second_mechanism_candidates = [], []
    for round_index in range(args.rounds):
        total = rng.randint(args.total_min, args.total_max)
        count = rng.randint(args.generators_min, args.generators_max)
        generators = generated_allocations(rng, args.mode, 6, total, count)
        if any(min(g[i] for g in generators) != 0 for i in range(6)):
            continue
        values = lower_envelope(generators)
        stats["exact_envelopes"] += 1
        all_constraints = {m: values[m] for m in range(1, 63) if values[m]}
        fx = float_selector_from_constraints(all_constraints, 6, total, "min")
        fz = float_selector_from_constraints(all_constraints, 6, total, "max")
        if fx is None or fz is None or tuple(fx) == tuple(fz):
            continue
        if sum(q == max(fz) for q in fz) != 2:
            continue
        fx, fz = tuple(map(F, fx)), tuple(map(F, fz))
        fast_covers = cover_census(values, fz)
        if not fast_covers:
            stats["floating_no_cover"] += 1
            continue
        outsiders = tuple(i for i in range(6) if fz[i] < max(fz))
        if any(
            cert[1] > 0
            and matrix_rank([
                [F((row >> i) & 1) for row in rows] for i in outsiders
            ]) == 4
            for rows, cert in fast_covers
        ):
            stats["floating_full_rank_cover"] += 1
            continue
        stats["floating_low_rank_cover_profile"] += 1
        cover_records = [{"rows": list(rows)} for rows, _cert in fast_covers]
        # This is a deliberately stronger prefilter: if a common direction
        # exists even before any active Cx inequalities are added, the profile
        # cannot falsify the common-direction conjecture through that route.
        pre_common = common_staged_direction_xz(fx, fz, (), cover_records)
        if pre_common is not None:
            stats["union_only_common_direction"] += 1
            continue
        stats["union_only_no_common_direction"] += 1
        full_cx = tight_rows(values, fx)
        any_float_faithful = False
        for rows, _cert in fast_covers:
            reduced = {row: csum(fx, row) for row in full_cx}
            reduced.update({row: csum(fz, row) for row in rows})
            reduced_z = float_selector_from_constraints(reduced, 6, total, "max")
            if (reduced_z is not None
                    and all(abs(reduced_z[i] - float(fz[i])) <= 1e-7
                            for i in range(6))):
                any_float_faithful = True
                break
        if any_float_faithful:
            stats["full_tight_cx_float_faithful"] += 1
            continue
        stats["full_tight_cx_float_all_cover_failure"] += 1
        constraints = all_constraints
        x = selector_from_constraints(constraints, 6, F(total), "min")
        z = selector_from_constraints(constraints, 6, F(total), "max")
        if x == z or sum(q == max(z) for q in z) != 2:
            stats["floating_false_positive"] += 1
            continue
        stats["exact_divergent_two_top"] += 1
        exact_covers = cover_census(values, z)
        if not exact_covers:
            stats["exact_no_cover"] += 1
            continue
        fixed = canonical_cx(values, x)
        exact_pre_common = common_staged_direction_xz(
            x, z, fixed, [{"rows": list(rows)} for rows, _ in exact_covers]
        )
        if exact_pre_common is not None:
            stats["exact_filter_false_positive"] += 1
            continue
        audit = audit_game(
            f"pxc103_target_seed{args.seed}_round{round_index}",
            values, x, z, pool_max=args.cx_pool_max, replay_exact=False,
        )
        if audit is None or not audit["cx_subsets_exhausted"]:
            stats["cx_not_exhausted"] += 1
            continue
        covers = audit["covers"]
        if not covers:
            stats["no_cover"] += 1
            continue
        failing = audit.get("pin", {}).get("failing_complete_cx", [])
        if not failing:
            continue
        stats["all_cover_failing_cx"] += len(failing)
        for item in failing:
            cx = tuple(item["cx_rows"])
            common = common_staged_direction_xz(x, z, cx, covers)
            record = {
                "label": audit["label"],
                "round": round_index,
                "generators": [list(map(int, g)) for g in generators],
                "x": list(map(str, x)),
                "z": list(map(str, z)),
                "cx": list(cx),
                "covers": [q["rows"] for q in covers],
                "common_direction": common,
            }
            if common is None:
                record["promotion_status"] = (
                    "candidate second mechanism; requires independent exact replay"
                )
                second_mechanism_candidates.append(record)
                stats["cover_dependent_candidates"] += 1
                if len(second_mechanism_candidates) >= args.stop_after:
                    break
            elif len(common_controls) < 12:
                common_controls.append(record)
                stats["common_direction_controls"] += 1
        if len(second_mechanism_candidates) >= args.stop_after:
            break
    payload = {
        "claim": "targeted exact falsifier of universal common-direction classification",
        "parameters": vars(args) | {"output": str(args.output) if args.output else None},
        "stats": dict(stats),
        "calibration_controls": controls,
        "common_direction_controls": common_controls,
        "cover_dependent_candidates": second_mechanism_candidates,
        "scope": (
            "seeded six-player integer lower envelopes only; retained profiles "
            "have exact selector replay and exhaustive complete-Cx/qualifying-cover "
            "censuses. Zero candidates is finite evidence only, never a theorem."
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
