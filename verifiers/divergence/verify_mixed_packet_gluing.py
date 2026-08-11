#!/usr/bin/env python3
"""Exact proof objects for the first mixed-colour rooted packet.

The dimension-free theorem proved in the accompanying research note is a
one-line dot-product argument.  This verifier has the more modest job of
checking, over Q, that the advertised packet is an incidence identity and
that three support-minimal labelled Farkas certificates are coefficient
identities for their fixed hostile branches.  It is not an all-n search.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from verify_labelled_branch_duals import CASES, branch_system


def frac(value: str | int) -> F:
    return F(value)


CERTIFICATES = {
    "optimized_label_free_spectral_failure": {
        "optimum": "3/4",
        "root": 3,
        "inequalities": (
            (("nonnegative", 1, 2), "1"),
            (("nonnegative", 5, 2), "1/2"),
            (("nonnegative", 5, 5), "1/4"),
            (("nonnegative", 5, 6), "1/4"),
            (("tight", "x", 26, 5), "1/4"),
            (("tight", "x", 57, 5), "1/4"),
            (("tight", "z", 52, 0), "5/4"),
            (("tight", "z", 57, 0), "1/2"),
            (("tight", "z", 75, 5), "1/4"),
            (("stratum_order", 0, 4, 0), "3/4"),
            (("stratum_order", 1, 4, 5), "1/2"),
            (("stratum_order", 1, 5, 1), "1"),
        ),
        "equalities": (
            (("total", 1), "5/4"),
            (("total", 5), "-1/2"),
            (("witness_zero", 3), "-1/4"),
            (("stratum_equal", 0, 1, 2), "-5/4"),
            (("stratum_equal", 0, 4, 5), "-1/2"),
            (("stratum_equal", 1, 0, 3), "1/2"),
        ),
    },
    "actual_top_fixed_failure": {
        "optimum": "7/10",
        "root": None,
        "inequalities": (
            (("nonnegative", 1, 5), "21/10"),
            (("tight", "x", 21, 1), "2/5"),
            (("tight", "x", 47, 1), "7/10"),
            (("stratum_order", 0, 4, 1), "6/5"),
            (("stratum_order", 1, 0, 1), "3/5"),
        ),
        "equalities": (
            (("total", 0), "11/10"),
            (("total", 1), "-2/5"),
            (("stratum_equal", 0, 4, 5), "-2/5"),
            (("stratum_equal", 0, 4, 6), "-11/10"),
            (("stratum_equal", 0, 1, 3), "3/5"),
            (("stratum_equal", 1, 0, 2), "3/10"),
            (("stratum_equal", 1, 1, 3), "-3/10"),
            (("stratum_equal", 1, 5, 6), "7/5"),
        ),
    },
    "top_and_bottom_fixed_failure": {
        "optimum": "2/3",
        "root": None,
        "inequalities": (
            (("nonnegative", 1, 2), "7/3"),
            (("tight", "x", 59, 1), "2/3"),
            (("tight", "x", 115, 1), "4/3"),
            (("stratum_order", 0, 1, 6), "4/3"),
            (("stratum_order", 0, 6, 0), "1"),
            (("stratum_order", 1, 4, 0), "2/3"),
        ),
        "equalities": (
            (("total", 0), "2"),
            (("total", 1), "-4/3"),
            (("stratum_equal", 0, 1, 2), "-2"),
            (("stratum_equal", 0, 1, 3), "-1/3"),
            (("stratum_equal", 1, 4, 5), "1/3"),
            (("stratum_equal", 1, 1, 3), "2/3"),
        ),
    },
}


def coefficient_identity(case, certificate):
    system = branch_system(case)
    width = len(system["objective"])
    combined = [F(0)] * width
    constant = F(0)
    inequality_terms = []
    equality_terms = []

    inequality_index = {label: k for k, label in enumerate(system["inequality_labels"])}
    equality_index = {label: k for k, label in enumerate(system["equality_labels"])}

    for label, raw_multiplier in certificate["inequalities"]:
        multiplier = frac(raw_multiplier)
        assert multiplier > 0 and label in inequality_index
        k = inequality_index[label]
        # A y <= b contributes multiplier * (b-A y).
        for j, coefficient in enumerate(system["inequalities"][k]):
            combined[j] -= multiplier * coefficient
        constant += multiplier * system["inequality_rhs"][k]
        inequality_terms.append({"label": list(label), "multiplier": str(multiplier)})

    for label, raw_multiplier in certificate["equalities"]:
        multiplier = frac(raw_multiplier)
        assert label in equality_index
        k = equality_index[label]
        # E y = d contributes multiplier * (E y-d).
        for j, coefficient in enumerate(system["equalities"][k]):
            combined[j] += multiplier * coefficient
        constant -= multiplier * system["equality_rhs"][k]
        equality_terms.append({"label": list(label), "multiplier": str(multiplier)})

    optimum = frac(certificate["optimum"])
    assert combined == system["objective"]
    assert constant == -optimum
    return {
        "optimum": str(optimum),
        "identity": "objective - optimum = sum(nonnegative row slacks) + equality zeros",
        "coefficient_identity_verified": True,
        "inequality_terms": inequality_terms,
        "equality_terms": equality_terms,
        "uses_rooted_witness": certificate["root"] is not None,
        "root": certificate["root"],
    }


def incidence(mask: int, n: int) -> tuple[F, ...]:
    return tuple(F((mask >> i) & 1) for i in range(n))


def rank(matrix) -> int:
    rows = [list(map(F, row)) for row in matrix]
    if not rows:
        return 0
    pivot_row = 0
    for column in range(len(rows[0])):
        pivot = next((i for i in range(pivot_row, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = rows[pivot_row][column]
        rows[pivot_row] = [q / scale for q in rows[pivot_row]]
        for i in range(len(rows)):
            if i != pivot_row and rows[i][column]:
                scale = rows[i][column]
                rows[i] = [a - scale * b for a, b in zip(rows[i], rows[pivot_row])]
        pivot_row += 1
    return pivot_row


def coalition_sum(point, mask: int) -> F:
    return sum((point[i] for i in range(len(point)) if mask >> i & 1), F(0))


def verify_branch_input(case):
    n = len(case["x"])
    generators = (tuple(map(F, case["g"])), tuple(map(F, case["h"])))
    total = sum(generators[0], F(0))
    assert sum(generators[1], F(0)) == total > 0
    values = tuple(
        min(coalition_sum(generator, mask) for generator in generators)
        for mask in range(1 << n)
    )
    assert values[-1] == total
    assert all(values[1 << i] == 0 for i in range(n))
    for point, support in (
        (tuple(case["x"]), case["support_x"]),
        (tuple(case["z"]), case["support_z"]),
    ):
        assert sum(point, F(0)) == total
        assert all(
            coalition_sum(point, mask) >= values[mask]
            for mask in range(1, (1 << n) - 1)
        )
        assert all(coalition_sum(point, mask) == values[mask] for mask in support)
    return {
        "lower_envelope_exactness": "attained coalitionwise by one of the two core generators",
        "singleton_normalized": True,
        "advertised_support_tightness_verified": True,
    }


def mixed_packet():
    # The hard optimized branch uses x-tight 26,57 and z-tight 75.
    n, root = 7, 3
    coloured = (("x", 26, F(1)), ("x", 57, F(1)), ("z", 75, F(1)))
    singleton_slack = {2: F(2), 5: F(1), 6: F(1)}
    lhs = [F(0)] * n
    for _colour, coalition, weight in coloured:
        for i, bit in enumerate(incidence(coalition, n)):
            lhs[i] += weight * bit
    for i, weight in singleton_slack.items():
        lhs[i] += weight
    rhs = [F(2)] * n
    rhs[root] += 1
    assert lhs == rhs
    normalized_loads = [q / 2 for q in [F(2), F(2), F(0), F(3), F(2), F(1), F(1)]]
    assert max(normalized_loads[i] for i in range(n) if i != root) == 1
    active_rows = (0, 1, 4)
    active_matrix = [
        [incidence(mask, n)[i] for _colour, mask, _weight in coloured]
        for i in active_rows
    ]
    assert rank(active_matrix) == len(coloured)
    return {
        "n": n,
        "root": root,
        "coloured_tight_coalitions": [
            {"selection": colour, "coalition_mask": coalition, "weight": str(weight)}
            for colour, coalition, weight in coloured
        ],
        "nonroot_singleton_slack": {str(i): str(q) for i, q in singleton_slack.items()},
        "incidence_identity": "1_26+1_57+1_75+2e_2+e_5+e_6=2(1_N)+e_3",
        "incidence_identity_verified": True,
        "normalized_extreme_packet": {
            "coalition_weights": ["1/2", "1/2", "1/2"],
            "player_loads": [str(q) for q in normalized_loads],
            "offroot_load_ceiling": "1",
            "root_excess_delta": "1/2",
            "positive_coalition_support": 3,
            "support_bound_n_minus_1": 6,
            "independent_active_capacity_rows": list(active_rows),
            "vertex_rank_verified": True,
        },
        "witness_consequence": "v(26)+v(57)+v(75)<=2T",
        "selection_form": "x(26)+x(57)+z(75)<=2T",
        "common_coalitions": [57],
        "noncommon_coalitions": [26, 75],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = {case["name"]: case for case in CASES}
    report = {
        "status": "exact rational mixed-packet and fixed-branch Farkas proof objects",
        "mixed_packet": mixed_packet(),
        "branch_certificates": {
            name: {
                "input": verify_branch_input(cases[name]),
                **coefficient_identity(cases[name], certificate),
            }
            for name, certificate in CERTIFICATES.items()
        },
        "classification": {
            "optimized_label_free_spectral_failure": "one mixed-colour rooted packet plus direct and stratum rows",
            "actual_top_fixed_failure": "direct x-to-z and stratum rows; no witness packet",
            "top_and_bottom_fixed_failure": "direct x-to-z and stratum rows; no witness packet",
        },
        "scope": (
            "The incidence implication is dimension-free.  The three Farkas "
            "objects certify only their fixed labelled hostile branches and do "
            "not prove the universal hybrid-overlap conjecture."
        ),
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
