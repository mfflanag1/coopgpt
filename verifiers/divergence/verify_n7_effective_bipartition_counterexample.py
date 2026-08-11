#!/usr/bin/env python3
"""Exact n=7 counterexample to the clipped effective-bipartition conjecture.

The two displayed generators have common total one.  Their lower envelope is
therefore a singleton-normalized exact game.  Solver-free staged incidence
identities prove the displayed Lmin and Lmax selections.  A separate generic
exact staged-certificate checker replays those selections, and independent
primal/dual incidence witnesses prove theta_plus=3/5.

The example refutes only

    O/T >= 1/a + 1/(n-a),  a=min(1/theta_plus,floor(n/2)).

It does not challenge the main n=7 target O/T >= 7/12.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_lmax_overcover import coalition_sum, top_certificate  # noqa: E402
from audit_overcover_dispersion_dual import dispersion_dual  # noqa: E402
from audit_sign_coherent_staged_lifts import payoff_blocks  # noqa: E402
from verify_labelled_branch_duals import verify_complete_selection  # noqa: E402


N = 7
FULL = (1 << N) - 1
G = (F(12, 17), F(4, 17), F(0), F(1, 17), F(0), F(0), F(0))
H = (F(0), F(0), F(6, 23), F(0), F(6, 23), F(10, 23), F(1, 23))
X = (
    F(227, 782), F(48, 391), F(48, 391), F(1, 34),
    F(48, 391), F(13, 46), F(1, 34),
)
Z = tuple(F(q, 391) for q in (91, 12, 90, 12, 90, 91, 5))
VALUES = tuple(
    min(coalition_sum(G, coalition), coalition_sum(H, coalition))
    for coalition in range(1 << N)
)


# A certificate entry is (stage, player, coalition multipliers, old-pin unit
# coefficients, other current-block unit coefficients, constant c).  The
# forced player has implicit coefficient +1 for Lmin and -1 for Lmax.
LMIN_CERTIFICATES = (
    (0, 3, ((55, F(1)),), (), ((6, F(1)),), F(1)),
    (0, 6, ((55, F(1)),), (), ((3, F(1)),), F(1)),
    (1, 1, ((37, F(1)),), ((3, F(1)), (6, F(1))), ((4, F(1)),), F(1)),
    (1, 2, ((49, F(1)),), ((3, F(1)), (6, F(1))), ((1, F(1)),), F(1)),
    (1, 4, ((37, F(1)),), ((3, F(1)), (6, F(1))), ((1, F(1)),), F(1)),
    (2, 5, ((85, F(1)),), ((3, F(1)), (1, F(1))), (), F(1)),
    (
        3, 0, (),
        ((3, F(1)), (6, F(1)), (1, F(1)), (2, F(1)),
         (4, F(1)), (5, F(1))),
        (), F(1),
    ),
)

LMAX_CERTIFICATES = (
    (
        0, 0,
        ((37, F(1)), (42, F(1, 2)), (49, F(1)),
         (66, F(1, 2)), (72, F(1, 2))),
        (), ((5, F(3, 2)),), F(1),
    ),
    (
        0, 5,
        ((37, F(2, 3)), (42, F(1, 3)), (49, F(2, 3)),
         (66, F(1, 3)), (72, F(1, 3))),
        (), ((0, F(2, 3)),), F(2, 3),
    ),
    (1, 2, ((37, F(1)),), ((0, F(-1)), (5, F(-1))), (), F(0)),
    (1, 4, ((49, F(1)),), ((0, F(-1)), (5, F(-1))), (), F(0)),
    (2, 1, ((42, F(1)),), ((5, F(-1)),), ((3, F(1)),), F(0)),
    (2, 3, ((42, F(1)),), ((5, F(-1)),), ((1, F(1)),), F(0)),
    (
        3, 6,
        ((37, F(1)), (49, F(1)), (66, F(1)), (72, F(1))),
        ((0, F(-1)), (5, F(-1))), (), F(1),
    ),
)


def tight_support(point):
    return tuple(
        coalition
        for coalition in range(1, FULL)
        if coalition_sum(point, coalition) == VALUES[coalition]
    )


def audit_staged_identity(point, mode, entry):
    stage, player, coalitions, old, current, constant = entry
    blocks = payoff_blocks(point, mode)
    expected_old = {i for block in blocks[:stage] for i in block}
    expected_current = set(blocks[stage])
    if player not in expected_current:
        raise AssertionError("forced player is not in the asserted stage")
    if any(i not in expected_old for i, _weight in old):
        raise AssertionError("old-pin coefficient has the wrong stage label")
    if any(i not in expected_current - {player} for i, _weight in current):
        raise AssertionError("current coefficient has the wrong stage label")
    if any(weight < 0 for _coalition, weight in coalitions + current):
        raise AssertionError("negative coalition/current coefficient")
    if mode == "min" and any(weight < 0 for _i, weight in old):
        raise AssertionError("Lmin old-pin coefficient has the wrong sign")
    if mode == "max" and any(weight > 0 for _i, weight in old):
        raise AssertionError("Lmax old-pin coefficient has the wrong sign")
    if any(coalition_sum(point, coalition) != VALUES[coalition] for coalition, _ in coalitions):
        raise AssertionError("certificate uses a coalition not tight at the selection")

    side = F(1 if mode == "min" else -1)
    for coordinate in range(N):
        lhs = sum(
            (weight for coalition, weight in coalitions if coalition >> coordinate & 1),
            F(0),
        )
        lhs += sum(weight for i, weight in old if i == coordinate)
        lhs += side * sum(weight for i, weight in current if i == coordinate)
        lhs += side * F(coordinate == player)
        if lhs != constant:
            raise AssertionError((mode, stage, player, coordinate, lhs, constant))


def audit_exact_game():
    if sum(G, F(0)) != 1 or sum(H, F(0)) != 1:
        raise AssertionError("generator totals changed")
    if any(VALUES[1 << player] != 0 for player in range(N)):
        raise AssertionError("singleton normalization failed")
    for generator in (G, H):
        if any(
            coalition_sum(generator, coalition) < VALUES[coalition]
            for coalition in range(1 << N)
        ):
            raise AssertionError("displayed generator is outside the core")
    # Each coalition worth is attained by G or H, both already proved core.
    if any(
        VALUES[coalition]
        not in (coalition_sum(G, coalition), coalition_sum(H, coalition))
        for coalition in range(1 << N)
    ):
        raise AssertionError("lower envelope is not exact from the definition")
    for point in (X, Z):
        if sum(point, F(0)) != 1 or any(value < 0 for value in point):
            raise AssertionError("selection is not an allocation")
        if any(
            coalition_sum(point, coalition) < VALUES[coalition]
            for coalition in range(1 << N)
        ):
            raise AssertionError("selection lies outside the core")


def audit_dispersion():
    # Solver-free optimal primal certificate.
    lambdas = {37: F(2, 5), 42: F(1, 5), 49: F(2, 5), 66: F(1, 5), 72: F(1, 5)}
    eta = F(2, 5)
    alpha = (F(2, 5), F(0), F(0), F(0), F(0), F(3, 5), F(0))
    for coordinate in range(N):
        load = sum(
            (weight for coalition, weight in lambdas.items() if coalition >> coordinate & 1),
            F(0),
        )
        if load != eta + alpha[coordinate]:
            raise AssertionError("over-cover primal identity failed")
    if any(coalition_sum(Z, coalition) != VALUES[coalition] for coalition in lambdas):
        raise AssertionError("over-cover support is not Z-tight")

    # Solver-free optimal dual certificate.
    t = F(3, 5)
    y = tuple(F(q, 5) for q in (-3, -1, 1, -1, 1, 2, 1))
    q = (F(0), F(0), F(0), F(0), F(0), F(1), F(0))
    top = tuple(i for i, value in enumerate(Z) if value == max(Z))
    tight = tight_support(Z)
    if sum(y, F(0)) > 0 or sum(q, F(0)) > 1:
        raise AssertionError("dispersion dual budget failed")
    if any(coalition_sum(y, coalition) < 0 for coalition in tight):
        raise AssertionError("dispersion dual has a negative tight-set price")
    if any(t + y[i] > q[i] for i in top):
        raise AssertionError("dispersion dual top constraint failed")

    # Independent generic exact LP formulations must recover the same value.
    primal_lp = top_certificate(VALUES, Z)
    dual_lp = dispersion_dual(VALUES, Z)
    if primal_lp["theta"] != t or dual_lp["t"] != t:
        raise AssertionError("independent dispersion LP replay disagrees")
    return t, alpha, primal_lp["support"], y, q


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    audit_exact_game()
    for entry in LMIN_CERTIFICATES:
        audit_staged_identity(X, "min", entry)
    for entry in LMAX_CERTIFICATES:
        audit_staged_identity(Z, "max", entry)

    # Independently formulated exact staged feasibility LPs, using all tight
    # coalitions rather than the hard-coded sparse identities above.
    verify_complete_selection(VALUES, X, "min", tight_support(X))
    verify_complete_selection(VALUES, Z, "max", tight_support(Z))

    theta, alpha, overcover_support, y, q = audit_dispersion()
    a = min(1 / theta, F(N // 2))
    overlap = sum((min(X[i], Z[i]) for i in range(N)), F(0))
    ceb_bound = 1 / a + 1 / (F(N) - a)
    main_target = F(N, (N * N) // 4)
    if overlap >= ceb_bound:
        raise AssertionError("displayed pair no longer refutes CEB")
    if overlap < main_target:
        raise AssertionError("example unexpectedly refutes the main n=7 target")

    report = {
        "status": "exact rational counterexample to clipped effective bipartition",
        "scope": "refutes CEB only; does not refute the main hybrid-overlap theorem",
        "game": {
            "n": N,
            "generators": [[str(value) for value in generator] for generator in (G, H)],
            "common_total": "1",
            "singleton_normalized": True,
            "exact_from_lower_envelope_definition": True,
        },
        "selections": {
            "lmin": [str(value) for value in X],
            "lmax": [str(value) for value in Z],
            "lmin_tight_support": list(tight_support(X)),
            "lmax_tight_support": list(tight_support(Z)),
            "solver_free_staged_identities": len(LMIN_CERTIFICATES) + len(LMAX_CERTIFICATES),
            "independent_generic_exact_staged_checks": 2 * N,
        },
        "dispersion": {
            "theta_plus": str(theta),
            "a": str(a),
            "alpha": [str(value) for value in alpha],
            "primal_overcover_support": list(overcover_support),
            "dual_y": [str(value) for value in y],
            "dual_q": [str(value) for value in q],
        },
        "refutation": {
            "overlap": str(overlap),
            "ceb_bound": str(ceb_bound),
            "ceb_margin": str(overlap - ceb_bound),
            "main_n7_target": str(main_target),
            "main_target_margin": str(overlap - main_target),
            "l1_divergence": str(2 * (1 - overlap)),
        },
        "failed_premise": (
            "minimum dispersion, its optimal rooted-price dual, the complete staged "
            "Lmin packet, exactness, and even an atomic ceiling root do not imply CEB"
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
