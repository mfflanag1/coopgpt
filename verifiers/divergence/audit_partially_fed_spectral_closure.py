#!/usr/bin/env python3
r"""Exact controls for partially fed spectral closure (PXC80).

The wide many-generator probe refuted both the feeding implication and
the five-mechanism selection disjunction as first stated: seeded
envelopes of four to eight generators produce uniform-top packet
violations whose co-stars of one omission type are all Lmax-slack, and
among them roots that escape reserve, direct, the fully fed (PXC75)
hypotheses, the (PXC78) hypotheses, and the chosen-family certificate
simultaneously.  The repair is a strictly weaker feeding hypothesis with
the same conclusion: if the decorated co-stars of at least two omission
types are Lmax-tight, the symmetric over-cover on those rows alone is
feasible and its dispersion bound collapses to the same
`theta<=(k-1)/(g(k-1)-1)` for every number of fed types, so the (PXC75)
chain holds verbatim.  This driver replays the escape controls exactly,
checks the dispersion identity across the fed-type count, and pins the
chain closures.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path


COOPGAMES = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COOPGAMES / "src"))

from audit_costar_saturation_dichotomy import coalition_sum  # noqa: E402
from audit_lmax_overcover import top_certificate  # noqa: E402
from audit_menu_relaxed_root_exchange import ordered_saturated_roots  # noqa: E402
from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from audit_spectral_label_currency import spectral_decomposition  # noqa: E402
from audit_spectral_or_reserve import margins, selectors  # noqa: E402


CONTROLS = (
    ("escape_six_generator", (
        (0, 4, 4, 4, 0, 0, 0), (7, 0, 0, 0, 2, 2, 1), (7, 0, 0, 0, 1, 2, 2),
        (0, 3, 4, 5, 0, 0, 0), (7, 0, 0, 0, 2, 2, 1), (7, 0, 0, 0, 2, 1, 2),
    ), {
        "x": ["9/2", "5/4", "5/4", "5/4", "5/4", "5/4", "5/4"],
        "z": ["12/5", "12/5", "12/5", "12/5", "4/5", "4/5", "4/5"],
        "packet_margin": "-1/5",
        "fed_types": 2,
        "theta": "2/5",
        "chain": "327/40",
        "chain_closes": True,
        "bound": "171/20",
    }),
    ("feeding_counterexample_five_generator", (
        (0, 4, 4, 4, 0, 0, 0), (7, 0, 0, 0, 3, 1, 1), (0, 4, 5, 3, 0, 0, 0),
        (8, 0, 0, 0, 2, 1, 1), (7, 0, 0, 0, 2, 1, 2),
    ), {
        "x": ["13/3", "4/3", "4/3", "4/3", "4/3", "1", "4/3"],
        "z": ["12/5", "12/5", "12/5", "12/5", "4/5", "4/5", "4/5"],
        "packet_margin": "-1/5",
        "fed_types": 2,
        "theta": "2/5",
        "chain": "239/30",
        "chain_closes": True,
        "bound": "127/15",
    }),
)


def dispersion_identity():
    """The symmetric cover denominator is g(k-1)-1 for every |F|>=2."""
    for g in range(2, 8):
        for k in range(2, 8):
            for fed in range(2, g + 1):
                denominator = ((k - 1) * (g - fed + 1)
                               + fed * k - k - fed)
                if denominator != g * (k - 1) - 1:
                    raise AssertionError("dispersion identity failed")
                if (fed - 1) * k - fed < 0:
                    raise AssertionError("cover weight lost nonnegativity")


def pair_graph_feasibility():
    """PXC81: demands 1 per column, supplies k-1 per touched row.

    Gale's condition over column subsets J reduces to: every column has
    an edge, and at least two rows are touched, because a proper subset
    has |J| <= k-1 <= (k-1)|N(J)| once N(J) is nonempty, while J equal
    to all columns needs 2(k-1) >= k, i.e. k >= 2.  Verified here by
    brute force on all bipartite graphs with g, k <= 4.
    """
    import itertools
    for g in range(2, 5):
        for k in range(2, 5):
            cells = [(a, j) for a in range(g) for j in range(k)]
            for mask in range(1 << (g * k)):
                edges = [cells[i] for i in range(g * k) if mask >> i & 1]
                columns = {j for _a, j in edges}
                rows = {a for a, _j in edges}
                simple = (columns == set(range(k)) and len(rows) >= 2)
                gale = all(
                    (k - 1) * len({a for a, j in edges if j in J}) >= len(J)
                    for size in range(1, k + 1)
                    for J in itertools.combinations(range(k), size)
                )
                if simple != gale:
                    raise AssertionError(
                        f"pair-graph characterization failed at {edges}"
                    )


def audit_control(name, generators, expected):
    generators = tuple(
        tuple(F(value) for value in generator) for generator in generators
    )
    n = len(generators[0])
    values = lower_envelope(generators)
    x, z = selectors(values, n)
    roots = ordered_saturated_roots(values, x, z)
    if len(roots) != 1:
        raise AssertionError(f"{name}: root count changed")
    root, gainers, outsiders, _dec = roots[0]
    g = len(gainers)
    k = len(outsiders)
    M = max(z)
    if not (z[root] == M and all(z[a] == M for a in gainers)
            and all(z[j] < M for j in outsiders)):
        raise AssertionError(f"{name}: top uniformity changed")
    if any(x[i] > M for i in range(n) if i != root):
        raise AssertionError(f"{name}: nonroot Lmin cap changed")
    fed_types = 0
    for a in gainers:
        if all(
            coalition_sum(z, coalition) == values[coalition]
            for j in outsiders
            for coalition in [(1 << root) | (1 << j)
                              | sum(1 << b for b in gainers if b != a)]
        ):
            fed_types += 1
    if fed_types < 2:
        raise AssertionError(f"{name}: fed-type count fell below two")
    delta = g * (k - 1) - 1
    certificate = top_certificate(values, z)
    theta = F(certificate["theta"])
    if theta > F(k - 1, delta):
        raise AssertionError(f"{name}: partial cover feasibility failed")
    spec = spectral_decomposition("p", values, x, z)
    total = sum(x, F(0))
    bound = F(spec["sharpened_spectral_bound_ratio"]) * total
    f = min(x)
    residual = sum((z[j] for j in outsiders), F(0)) - sum(
        (max(z[j] - f, F(0)) for j in outsiders), F(0)
    )
    chain = ((M - f) * F(delta, k - 1) + (g + 1) * f + residual
             + M - x[root])
    if bound < chain:
        raise AssertionError(f"{name}: partially fed chain failed")
    target = F(n, (n * n) // 4) * total
    packet = margins(values, x, z)["packet_margin"]
    observed = {
        "x": [str(value) for value in x],
        "z": [str(value) for value in z],
        "packet_margin": str(packet),
        "fed_types": fed_types,
        "theta": str(theta),
        "chain": str(chain),
        "chain_closes": chain >= target,
        "bound": str(bound),
    }
    mismatches = {
        key: (observed[key], expected[key])
        for key in expected
        if observed[key] != expected[key]
    }
    if mismatches:
        raise AssertionError(f"{name} drifted: {mismatches!r}")
    return {"name": name, **observed, "target": str(target)}


CONDITION_FAILURE_CONTROLS = (
    ("single_column_graph_g3k4", ((5, 5, 5), 8, (4, 1, 1, 1)),
     "-1/14", "219/70"),
    ("single_column_graph_g4k3_low", ((5, 5, 5, 5), 5, (13, 1, 1)),
     "-1/3", "8/3"),
    ("single_column_graph_g4k3_high", ((5, 5, 5, 5), 13, (5, 1, 1)),
     "-1/3", "8/3"),
)


def audit_condition_failure(name, shape, packet_expected, family_expected):
    """Uniform-top violations whose pair graph fails (PXC81) yet which
    the direct arm and the chosen family both close."""
    from audit_spectral_or_reserve import family_instance
    from audit_direct_ceiling_common_hinge_trichotomy import (
        has_direct_packet,
    )
    from audit_chosen_family_costar_closure import best_family_margin
    a, H, w = shape
    generators = family_instance(a, H, w)
    n = len(generators[0])
    values = lower_envelope(generators)
    x, z = selectors(values, n)
    roots = ordered_saturated_roots(values, x, z)
    if len(roots) != 1:
        raise AssertionError(f"{name}: root count changed")
    root, gainers, outsiders, _dec = roots[0]
    packet = margins(values, x, z)["packet_margin"]
    if str(packet) != packet_expected or packet >= 0:
        raise AssertionError(f"{name}: packet margin changed")
    edges = [
        (a_, j) for a_ in gainers for j in outsiders
        if coalition_sum(
            z, (1 << root) | (1 << j)
            | sum(1 << b for b in gainers if b != a_)
        ) == values[(1 << root) | (1 << j)
                    | sum(1 << b for b in gainers if b != a_)]
    ]
    columns = {j for _a, j in edges}
    if columns == set(outsiders):
        raise AssertionError(f"{name}: pair condition no longer fails")
    if not has_direct_packet(x, z, F(n, (n * n) // 4)):
        raise AssertionError(f"{name}: direct arm no longer closes")
    floor = min(x)
    if any(z[j] > floor for j in set(outsiders) - columns):
        raise AssertionError(f"{name}: uncovered outsider above the floor")
    family = best_family_margin(values, x, z, root, gainers, outsiders)
    if family is None or str(family) != family_expected or family < 0:
        raise AssertionError(f"{name}: chosen-family margin changed")
    return {"name": name, "packet_margin": packet_expected,
            "uncovered_outsiders": len(set(outsiders) - columns),
            "chosen_family_margin": family_expected}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    dispersion_identity()
    pair_graph_feasibility()
    rows = [audit_control(name, generators, expected)
            for name, generators, expected in CONTROLS]
    failure_rows = [
        audit_condition_failure(name, shape, packet, family)
        for name, shape, packet, family in CONDITION_FAILURE_CONTROLS
    ]
    summary = {
        "controls": len(rows),
        "chain_closures": sum(row["chain_closes"] for row in rows),
        "dispersion_identity": "g(k-1)-1 for all fed counts >= 2",
        "condition_failure_controls": len(failure_rows),
    }
    payload = {
        "claim": (
            "two fed omission types suffice: the partial symmetric cover "
            "has the same dispersion bound as the fully fed case and the "
            "PXC75 chain closes the wide-probe escape controls"
        ),
        "summary": summary,
        "rows": rows,
        "condition_failure_rows": failure_rows,
    }
    rendered = json.dumps(payload, indent=2, default=str) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
