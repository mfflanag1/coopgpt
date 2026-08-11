#!/usr/bin/env python3
"""Exact audit of the mixed block-star one-witness boundary theorem.

The dimension-free inequality is proved in the accompanying human note.  The
script checks its polynomial identity on a parameter grid, independently
certifies a new three-generator n=7 control by explicit staged identities,
and verifies a hard-coded primal/dual proof that its unique ceiling-root
one-witness relaxation has optimum exactly 7/12.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_lmax_overcover import coalition_sum  # noqa: E402
from audit_sign_coherent_staged_lifts import payoff_blocks  # noqa: E402
from verify_labelled_branch_duals import CASES, branch_system  # noqa: E402
from verify_n7_neutral_rectangle_control import X as NEUTRAL_X  # noqa: E402
from verify_n7_neutral_rectangle_control import Z as NEUTRAL_Z  # noqa: E402


N = 7
FULL = (1 << N) - 1
GENERATORS = (
    tuple(map(F, (2, 4, 0, 16, 2, 0, 0))),
    tuple(map(F, (0, 8, 5, 0, 0, 8, 3))),
    tuple(map(F, (1, 0, 7, 8, 0, 3, 5))),
)
VALUES = tuple(
    min(coalition_sum(generator, coalition) for generator in GENERATORS)
    for coalition in range(1 << N)
)
X = tuple(map(F, (2, 4, 4, 6, 2, 4, 2)))
Z = (F(7, 4), F(9, 2), F(9, 2), F(9, 2), F(7, 4), F(9, 2), F(5, 2))
X_SUPPORT = (46, 78, 106, 108, 111, 126)
Z_SUPPORT = (46, 78)
FULL_X_TIGHT = (46, 78, 106, 108, 110, 111, 126)
FULL_Z_TIGHT = (46, 78, 106, 108)
MIXED_PROJECTION = COOPGAMES / "verifiers" / "divergence" / "mixed_witness_projection.json"


# (stage, player, coalition multipliers, old-pin coefficients,
#  other-current-block coefficients, constant).  Lmax old coefficients have
# their actual negative sign.
LMIN_CERTIFICATES = (
    (0, 0, ((126, F(1)),), (), (), F(1)),
    (0, 4, ((111, F(1)),), (), (), F(1)),
    (0, 6, ((46, F(1)),), (), ((0, F(1)), (4, F(1))), F(1)),
    (1, 1, ((108, F(1)),), ((0, F(1)), (4, F(1))), (), F(1)),
    (1, 2, ((106, F(1)),), ((0, F(1)), (4, F(1))), (), F(1)),
    (1, 5, ((78, F(1)),), ((0, F(1)), (4, F(1))), (), F(1)),
    (
        2, 3, (),
        ((0, F(1)), (4, F(1)), (6, F(1)), (1, F(1)), (2, F(1)), (5, F(1))),
        (), F(1),
    ),
)
LMAX_CERTIFICATES = (
    (0, 1, ((46, F(1)),), (), ((2, F(1)), (3, F(1)), (5, F(1))), F(0)),
    (0, 2, ((46, F(1)),), (), ((1, F(1)), (3, F(1)), (5, F(1))), F(0)),
    (0, 3, ((46, F(1)),), (), ((1, F(1)), (2, F(1)), (5, F(1))), F(0)),
    (0, 5, ((46, F(1)),), (), ((1, F(1)), (2, F(1)), (3, F(1))), F(0)),
    (
        1, 6, ((78, F(1)),),
        ((1, F(-1)), (2, F(-1)), (3, F(-1))), (), F(0),
    ),
    (
        2, 0, (),
        ((1, F(-1)), (2, F(-1)), (3, F(-1)), (5, F(-1)), (6, F(-1))),
        ((4, F(1)),), F(-1),
    ),
    (
        2, 4, (),
        ((1, F(-1)), (2, F(-1)), (3, F(-1)), (5, F(-1)), (6, F(-1))),
        ((0, F(1)),), F(-1),
    ),
)


def audit_staged_identity(point, mode, entry):
    stage, player, coalitions, old, current, constant = entry
    blocks = payoff_blocks(point, mode)
    expected_old = {i for block in blocks[:stage] for i in block}
    expected_current = set(blocks[stage])
    if player not in expected_current:
        raise AssertionError("forced player has the wrong stage")
    if any(i not in expected_old for i, _weight in old):
        raise AssertionError("old pin has the wrong stage")
    if any(i not in expected_current - {player} for i, _weight in current):
        raise AssertionError("current coefficient has the wrong stage")
    if any(coalition_sum(point, S) != VALUES[S] for S, _weight in coalitions):
        raise AssertionError("certificate coalition is not tight")
    if any(weight < 0 for _S, weight in coalitions + current):
        raise AssertionError("negative coalition/current multiplier")
    if mode == "min" and any(weight < 0 for _i, weight in old):
        raise AssertionError("Lmin old-pin sign failed")
    if mode == "max" and any(weight > 0 for _i, weight in old):
        raise AssertionError("Lmax old-pin sign failed")
    side = F(1 if mode == "min" else -1)
    for coordinate in range(N):
        lhs = sum(
            (weight for S, weight in coalitions if S >> coordinate & 1), F(0)
        )
        lhs += sum(weight for i, weight in old if i == coordinate)
        lhs += side * sum(weight for i, weight in current if i == coordinate)
        lhs += side * F(coordinate == player)
        if lhs != constant:
            raise AssertionError((mode, stage, player, coordinate, lhs, constant))


def restricted_root_system():
    case = {
        "g": (F(24),) + (F(0),) * 6,
        "x": X,
        "z": Z,
        "support_x": FULL_X_TIGHT,
        "support_z": FULL_Z_TIGHT,
    }
    system = branch_system(case)
    root = 3
    allowed = {0, 1, 2 + root}
    columns = [generator * N + i for generator in sorted(allowed) for i in range(N)]
    inequality_rows = []
    for k, label in enumerate(system["inequality_labels"]):
        if label[0] == "nonnegative" and label[1] not in allowed:
            continue
        if label[0] == "tight" and label[3] not in allowed:
            continue
        inequality_rows.append(k)
    equality_rows = []
    for k, label in enumerate(system["equality_labels"]):
        if label[0] == "total" and label[1] not in allowed:
            continue
        if label[0] == "witness_zero" and label[1] != root:
            continue
        equality_rows.append(k)
    return {
        "inequalities": [
            [system["inequalities"][k][j] for j in columns] for k in inequality_rows
        ],
        "inequality_rhs": [system["inequality_rhs"][k] for k in inequality_rows],
        "inequality_labels": [system["inequality_labels"][k] for k in inequality_rows],
        "equalities": [
            [system["equalities"][k][j] for j in columns] for k in equality_rows
        ],
        "equality_rhs": [system["equality_rhs"][k] for k in equality_rows],
        "equality_labels": [system["equality_labels"][k] for k in equality_rows],
        "objective": [system["objective"][j] for j in columns],
    }


def audit_root_primal_dual():
    system = restricted_root_system()
    primal = (
        F(1, 12), F(1, 12), F(1, 12), F(1, 2), F(1, 12), F(1, 12), F(1, 12),
        F(1, 32), F(3, 16), F(3, 16), F(3, 16), F(1, 32), F(3, 16), F(3, 16),
        F(0), F(1, 4), F(1, 4), F(0), F(0), F(1, 4), F(1, 4),
    )
    for row, rhs in zip(system["inequalities"], system["inequality_rhs"]):
        if sum((a * b for a, b in zip(row, primal)), F(0)) > rhs:
            raise AssertionError("rooted primal violates an inequality")
    for row, rhs in zip(system["equalities"], system["equality_rhs"]):
        if sum((a * b for a, b in zip(row, primal)), F(0)) != rhs:
            raise AssertionError("rooted primal violates an equality")
    optimum = sum((a * b for a, b in zip(system["objective"], primal)), F(0))
    if optimum != F(7, 12):
        raise AssertionError("rooted primal objective changed")

    inequality_weights = {
        ("nonnegative", 5, 0): F(7, 4),
        ("nonnegative", 5, 4): F(7, 4),
        ("tight", "x", 46, 5): F(7, 12),
        ("tight", "x", 78, 5): F(7, 12),
        ("tight", "x", 106, 5): F(7, 12),
        ("tight", "x", 108, 5): F(7, 12),
        ("tight", "z", 78, 0): F(1),
        ("stratum_order", 0, 0, 1): F(9, 4),
    }
    equality_weights = {
        ("total", 0): F(4, 3),
        ("total", 1): F(1),
        ("total", 5): F(-7, 4),
        ("witness_zero", 3): F(-7, 12),
        ("stratum_equal", 0, 0, 4): F(-4, 3),
        ("stratum_equal", 0, 0, 6): F(5, 12),
        ("stratum_equal", 0, 1, 2): F(5, 12),
        ("stratum_equal", 0, 1, 5): F(17, 12),
        ("stratum_equal", 1, 1, 3): F(1),
        ("stratum_equal", 1, 1, 5): F(-1),
    }
    nu = [inequality_weights.get(label, F(0)) for label in system["inequality_labels"]]
    pi = [equality_weights.get(label, F(0)) for label in system["equality_labels"]]
    if set(inequality_weights) - set(system["inequality_labels"]):
        raise AssertionError("missing hard-coded inequality label")
    if set(equality_weights) - set(system["equality_labels"]):
        raise AssertionError("missing hard-coded equality label")
    if any(weight < 0 for weight in nu):
        raise AssertionError("dual inequality multiplier is negative")
    for coordinate, objective_coefficient in enumerate(system["objective"]):
        lhs = -sum(
            (weight * row[coordinate] for weight, row in zip(nu, system["inequalities"])),
            F(0),
        )
        lhs += sum(
            (weight * row[coordinate] for weight, row in zip(pi, system["equalities"])),
            F(0),
        )
        if lhs != objective_coefficient:
            raise AssertionError(("dual stationarity", coordinate, lhs, objective_coefficient))
    dual_value = sum(
        (weight * rhs for weight, rhs in zip(pi, system["equality_rhs"])), F(0)
    ) - sum(
        (weight * rhs for weight, rhs in zip(nu, system["inequality_rhs"])), F(0)
    )
    if dual_value != optimum:
        raise AssertionError("rooted primal and dual values differ")
    return primal, optimum, len(inequality_weights), len(equality_weights)


def audit_symbolic_identity():
    rows = []
    for p in range(1, 9):
        for k in range(2, 9):
            P = p * (k - 1)
            D = k * (p + 1)
            n = p + k + 1
            # Parameterize the two nonnegative slacks used in the proof.
            for h, s in ((F(0), F(0)), (F(1, 19), F(0)), (F(0), F(1, 23)), (F(1, 17), F(1, 29))):
                a = F(1)
                b = a + h
                c = P * a - s
                if c < b:
                    continue
                total = c + (k - 1) * b + (p + 1) * a
                lhs = (P - 1) * total - D * (c - b)
                rhs = (k * P + p + 1) * (b - a) + n * (P * a - c)
                if lhs != rhs or rhs < 0:
                    raise AssertionError("mixed block-star polynomial identity failed")
            rows.append({"p": p, "k": k, "n": n, "denominator": D})
    price_rows = 0
    penalty_rows = 0
    for g in range(1, 7):
        for m in range(1, 7):
            n = 1 + g + m
            for P in (F(1), F(3, 2), F(2), F(7, 3), F(4), F(6), F(9)):
                for h, s in ((F(0), F(0)), (F(1, 31), F(0)), (F(0), F(1, 37))):
                    a = F(1)
                    b = a + h
                    c = P * a - s
                    if c < b:
                        continue
                    total = c + g * b + m * a
                    Dp = P + n - 1
                    lhs = (P - 1) * total - Dp * (c - b)
                    rhs = (g * (P - 1) + Dp) * (b - a) + n * (P * a - c)
                    if lhs != rhs or rhs < 0:
                        raise AssertionError("rooted facet-price identity failed")
                    price_rows += 1
                for excess, slack in ((F(1, 13), F(0)), (F(2, 17), F(1, 41))):
                    a = F(1)
                    b = a + F(1, 43)
                    c = P * a + excess - slack
                    if c < b:
                        continue
                    total = c + g * b + m * a
                    Dp = P + n - 1
                    lhs = (P - 1) * total - Dp * (c - b) + n * excess
                    rhs = (
                        (g * (P - 1) + Dp) * (b - a)
                        + n * (P * a + excess - c)
                    )
                    if lhs != rhs or rhs < 0:
                        raise AssertionError("multistage penalty identity failed")
                    penalty_rows += 1
    return rows, price_rows, penalty_rows


def audit_facet_prices():
    data = json.loads(MIXED_PROJECTION.read_text())
    selections = {case["name"]: (tuple(case["x"]), tuple(case["z"])) for case in CASES}
    selections["neutral_rectangle_control"] = (NEUTRAL_X, NEUTRAL_Z)
    rows = []
    for case in data["cases"]:
        for rooted in case["roots"]:
            root = rooted["root"]
            for cut_index, cut in enumerate(rooted["cuts"]):
                loads = tuple(F(q) for q in cut["player_loads"])
                delta = F(cut["root_excess_delta"])
                if delta <= 0 or max(loads[i] for i in range(len(loads)) if i != root) != 1:
                    raise AssertionError("mixed cut is not in normalized rooted-packing form")
                deficit = sum(
                    (1 - loads[i] for i in range(len(loads)) if i != root), F(0)
                )
                deficit_support = tuple(
                    i for i in range(len(loads)) if i != root and loads[i] < 1
                )
                x, z = selections[case["name"]]
                loss_aligned = all(x[i] >= z[i] for i in deficit_support)
                first_floor_aligned = loss_aligned and all(
                    x[i] == min(x) for i in deficit_support
                )
                price = deficit / delta
                n = case["n"]
                threshold = F((n * n) // 4 - n + 1)
                if price > threshold:
                    raise AssertionError("extreme mixed cut exceeds the facet-price threshold")
                rows.append(
                    {
                        "case": case["name"],
                        "root": root,
                        "cut": cut_index,
                        "deficit_weight": str(deficit),
                        "root_excess": str(delta),
                        "effective_price": str(price),
                        "dimensional_threshold": str(threshold),
                        "deficit_support": deficit_support,
                        "loss_aligned": loss_aligned,
                        "first_floor_aligned": first_floor_aligned,
                    }
                )
    if len(rows) != 9:
        raise AssertionError("mixed-projection cut count changed")
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if any(sum(generator, F(0)) != 24 for generator in GENERATORS):
        raise AssertionError("generator total changed")
    if any(VALUES[1 << i] != 0 for i in range(N)):
        raise AssertionError("singleton normalization failed")
    for generator in GENERATORS:
        if any(coalition_sum(generator, S) < VALUES[S] for S in range(1 << N)):
            raise AssertionError("generator left the core")
    for point in (X, Z):
        if sum(point, F(0)) != 24:
            raise AssertionError("selection total changed")
        if any(coalition_sum(point, S) < VALUES[S] for S in range(1 << N)):
            raise AssertionError("selection left the core")
    if tuple(
        S for S in range(1, FULL) if coalition_sum(X, S) == VALUES[S]
    ) != FULL_X_TIGHT:
        raise AssertionError("full Lmin tight family changed")
    if tuple(
        S for S in range(1, FULL) if coalition_sum(Z, S) == VALUES[S]
    ) != FULL_Z_TIGHT:
        raise AssertionError("full Lmax tight family changed")
    for entry in LMIN_CERTIFICATES:
        audit_staged_identity(X, "min", entry)
    for entry in LMAX_CERTIFICATES:
        audit_staged_identity(Z, "max", entry)

    overlap = sum((min(a, b) for a, b in zip(X, Z)), F(0))
    overlap_coordinates = tuple(min(a, b) for a, b in zip(X, Z))
    roots = tuple(i for i, q in enumerate(overlap_coordinates) if q == max(overlap_coordinates))
    if overlap != 22 or roots != (3,):
        raise AssertionError("control overlap/root changed")
    primal, root_optimum, dual_inequalities, dual_equalities = audit_root_primal_dual()
    grid, price_rows, penalty_rows = audit_symbolic_identity()
    facet_prices = audit_facet_prices()
    report = {
        "status": "exact mixed block-star boundary audit",
        "human_theorem": (
            "a k-hinge Lmin block-star packet, one common z-to-x hinge, and a "
            "root-zero witness imply O/T >= n/[k(p+1)] >= n/floor(n^2/4)"
        ),
        "symbolic_identity_grid": {
            "p_range": "1..8",
            "k_range": "2..8",
            "parameter_rows": len(grid),
            "identity": (
                "[p(k-1)-1]T-k(p+1)(c-b)="
                "[kp(k-1)+p+1](b-a)+n[p(k-1)a-c]"
            ),
            "general_facet_price_rows": price_rows,
            "multistage_penalty_rows": penalty_rows,
            "general_identity": (
                "(P-1)T-(P+n-1)(c-b)="
                "[g(P-1)+P+n-1](b-a)+n(Pa-c)"
            ),
        },
        "rooted_facet_price_audit": {
            "source": str(MIXED_PROJECTION.relative_to(COOPGAMES)),
            "extreme_cuts": len(facet_prices),
            "all_prices_within_dimensional_threshold": True,
            "loss_aligned_cuts": sum(row["loss_aligned"] for row in facet_prices),
            "first_floor_aligned_cuts": sum(
                row["first_floor_aligned"] for row in facet_prices
            ),
            "rows": facet_prices,
            "scope": "coefficient audit only; payoff-stratum/sign alignment is separate",
        },
        "three_generator_control": {
            "generators": [[str(q) for q in row] for row in GENERATORS],
            "lmin": [str(q) for q in X],
            "lmax": [str(q) for q in Z],
            "actual_overlap": str(overlap),
            "actual_overlap_ratio": str(overlap / 24),
            "unique_maximum_overlap_root": roots[0],
            "lmin_staged_identities": len(LMIN_CERTIFICATES),
            "lmax_staged_identities": len(LMAX_CERTIFICATES),
            "lower_envelope_exact_and_singleton_normalized": True,
        },
        "rooted_relaxation": {
            "root": 3,
            "uses_every_proper_coalition_tight_at_each_selection": True,
            "optimum": str(root_optimum),
            "target": "7/12",
            "primal_lmin": [str(q) for q in primal[:N]],
            "primal_lmax": [str(q) for q in primal[N:2 * N]],
            "primal_witness": [str(q) for q in primal[2 * N:]],
            "hard_coded_dual_nonzero_inequalities": dual_inequalities,
            "hard_coded_dual_nonzero_equalities": dual_equalities,
            "primal_dual_checked_without_optimization": True,
        },
        "scope": (
            "the theorem covers this mixed block-star branch in every dimension; "
            "the n=7 discovery screen is not a census or a proof of universal root selection"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
