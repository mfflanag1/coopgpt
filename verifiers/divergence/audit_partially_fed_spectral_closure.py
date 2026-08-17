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


TRIPLE_MENU_ESCAPE = (
    (0, 4, 4, 4, 4, 0, 0, 0), (11, 0, 0, 0, 0, 2, 2, 1),
    (10, 0, 0, 0, 0, 1, 4, 1), (11, 0, 0, 0, 0, 3, 2, 0),
    (10, 0, 0, 0, 0, 3, 1, 2), (0, 5, 3, 5, 3, 0, 0, 0),
    (12, 0, 0, 0, 0, 1, 1, 2), (12, 0, 0, 0, 0, 2, 1, 1),
)


def audit_triple_menu_escape():
    """The third refutation round: an eight-generator envelope whose
    uniform-top violation escapes reserve, direct, the pair-graph
    condition, the split-top hypotheses, and the chosen family at once,
    because its Lmax-tight menu consists of five rooted triples
    {r,a,b} -- no decorated co-star is tight at all.  The spectral
    certificate still closes it (bound 34/3 against target 8), so the
    spectral-or-reserve disjunction survives."""
    from audit_direct_ceiling_common_hinge_trichotomy import (
        has_direct_packet,
    )
    from audit_chosen_family_costar_closure import best_family_margin
    generators = tuple(
        tuple(F(value) for value in generator)
        for generator in TRIPLE_MENU_ESCAPE
    )
    n = len(generators[0])
    values = lower_envelope(generators)
    x, z = selectors(values, n)
    if [str(value) for value in x] != ["11/2"] + ["3/2"] * 7:
        raise AssertionError("triple-menu escape: x drifted")
    if [str(value) for value in z] != ["8/3"] * 5 + ["8/9"] * 3:
        raise AssertionError("triple-menu escape: z drifted")
    roots = ordered_saturated_roots(values, x, z)
    if len(roots) != 1:
        raise AssertionError("triple-menu escape: root count changed")
    root, gainers, outsiders, _dec = roots[0]
    packet = margins(values, x, z)
    if str(packet["packet_margin"]) != "-2/3":
        raise AssertionError("triple-menu escape: packet margin drifted")
    if str(packet["spectral_margin"]) != "10/3":
        raise AssertionError("triple-menu escape: spectral margin drifted")
    edges = [
        (a, j) for a in gainers for j in outsiders
        if coalition_sum(
            z, (1 << root) | (1 << j)
            | sum(1 << b for b in gainers if b != a)
        ) == values[(1 << root) | (1 << j)
                    | sum(1 << b for b in gainers if b != a)]
    ]
    if edges:
        raise AssertionError("triple-menu escape: pair graph not empty")
    tight = [
        coalition for coalition in range(1, (1 << n) - 1)
        if coalition_sum(z, coalition) == values[coalition]
    ]
    triples = sorted(
        tuple(p_ for p_ in range(n) if coalition >> p_ & 1)
        for coalition in tight
    )
    if triples != [(0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 3), (0, 3, 4)]:
        raise AssertionError("triple-menu escape: menu drifted")
    if has_direct_packet(x, z, F(n, (n * n) // 4)):
        raise AssertionError("triple-menu escape: direct arm now closes")
    family = best_family_margin(values, x, z, root, gainers, outsiders)
    if family is not None:
        raise AssertionError("triple-menu escape: chosen family now exists")
    # PXC83: a single tight rooted undecorated row {r} u P is an
    # over-cover with eta = 0 and theta = 1/(|P|+1); with the surplus
    # hypothesis x_r - M >= sum_P (M - x_a) the PXC75 chain closes.
    M = max(z)
    best = None
    for coalition in tight:
        members = {p_ for p_ in range(n) if coalition >> p_ & 1}
        if root not in members or not members <= set(gainers) | {root}:
            continue
        pset = members - {root}
        if not pset or pset == set(gainers):
            continue
        surplus = (x[root] - M) - sum(M - x[a] for a in pset)
        if surplus >= 0 and (best is None or len(pset) > best[0]):
            best = (len(pset), surplus)
    if best is None:
        raise AssertionError("triple-menu escape: no surplus rooted row")
    p_size, surplus = best
    if p_size != 2 or str(surplus) != "1/2":
        raise AssertionError("triple-menu escape: rooted row drifted")
    theta = F(1, p_size + 1)
    f = min(x)
    g = len(gainers)
    residual = sum(min(z[j], f) for j in outsiders)
    chain = (M - f) / theta + (g + 1) * f + residual + M - x[root]
    total = sum(x, F(0))
    target = F(n, (n * n) // 4) * total
    if str(chain) != "65/6" or chain < target:
        raise AssertionError("triple-menu escape: rooted chain failed")
    spec = spectral_decomposition("r", values, x, z)
    bound = F(spec["sharpened_spectral_bound_ratio"]) * total
    if bound < chain:
        raise AssertionError("triple-menu escape: chain exceeds the bound")
    return {
        "name": "triple_menu_escape",
        "menu": [list(row) for row in triples],
        "packet_margin": "-2/3",
        "spectral_margin": "10/3",
        "rooted_row_size": p_size,
        "rooted_surplus": str(surplus),
        "rooted_chain": str(chain),
        "rooted_chain_closes": True,
    }


def audit_family_rooted_control():
    """Extended-grid bridge correction: on the family instance
    a=(8,8,8,8), H=21, w=(9,2), the pair-graph condition fails and
    NEITHER the direct arm NOR the chosen family closes -- the first
    such instances on the two-generator family -- yet six rooted
    triples are Lmax-tight and the (PXC83) chain closes at 131/6
    against target 56/3.  The sharpened single-disjunct bridge
    (condition failure implies direct) is refuted at this scale; the
    six-mechanism disjunction is what survives."""
    from audit_direct_ceiling_common_hinge_trichotomy import (
        has_direct_packet,
    )
    from audit_chosen_family_costar_closure import best_family_margin
    a_vec, H, w = (8, 8, 8, 8), 21, (9, 2)
    g, k = len(a_vec), len(w)
    n = 1 + g + k
    gen1 = tuple([F(0)] + [F(q) for q in a_vec] + [F(0)] * k)
    gen2 = tuple([F(H)] + [F(0)] * g + [F(q) for q in w])
    values = lower_envelope((gen1, gen2))
    x, z = selectors(values, n)
    roots = ordered_saturated_roots(values, x, z)
    if len(roots) != 1:
        raise AssertionError("family rooted control: root count changed")
    root, gainers, outsiders, _dec = roots[0]
    packet = margins(values, x, z)["packet_margin"]
    if str(packet) != "-1/3":
        raise AssertionError("family rooted control: packet drifted")
    edges = [
        (a_, j) for a_ in gainers for j in outsiders
        if coalition_sum(
            z, (1 << root) | (1 << j)
            | sum(1 << b for b in gainers if b != a_)
        ) == values[(1 << root) | (1 << j)
                    | sum(1 << b for b in gainers if b != a_)]
    ]
    if {j for _a, j in edges} == set(outsiders):
        raise AssertionError("family rooted control: condition now holds")
    if has_direct_packet(x, z, F(n, (n * n) // 4)):
        raise AssertionError("family rooted control: direct now closes")
    family = best_family_margin(values, x, z, root, gainers, outsiders)
    if family is not None and family >= 0:
        raise AssertionError("family rooted control: family now closes")
    M = max(z)
    tops = {i for i in range(n) if z[i] == M}
    rooted = [
        frozenset(p_ for p_ in range(n) if coalition >> p_ & 1)
        for coalition in range(1, (1 << n) - 1)
        if coalition_sum(z, coalition) == values[coalition]
        and root in {p_ for p_ in range(n) if coalition >> p_ & 1}
        and {p_ for p_ in range(n) if coalition >> p_ & 1} <= tops
        and {p_ for p_ in range(n) if coalition >> p_ & 1} != tops
    ]
    if len(rooted) != 6:
        raise AssertionError("family rooted control: menu drifted")
    best = max(rooted, key=lambda R: sum(x[i] for i in R) - len(R) * M)
    surplus = sum(x[i] for i in best) - len(best) * M
    f = min(x)
    residual = sum(min(z[j], f) for j in outsiders)
    chain = (len(best)) * (M - f) + (len(gainers) + 1) * f         + residual + M - x[root]
    total = sum(x, F(0))
    target = F(n, (n * n) // 4) * total
    if str(surplus) != "1/2" or str(chain) != "131/6" or chain < target:
        raise AssertionError("family rooted control: chain drifted")
    return {"name": "family_rooted_control", "surplus": "1/2",
            "chain": "131/6", "target": str(target)}


ORDERED_UNSATURATED_WITNESS = (
    (0, 5, 5, 5, 5, 0, 0, 0), (5, 0, 0, 0, 0, 13, 1, 1),
    (0, 5, 6, 5, 4, 0, 0, 0), (0, 5, 6, 4, 5, 0, 0, 0),
    (5, 0, 0, 0, 0, 14, 0, 1), (6, 0, 0, 0, 0, 12, 0, 2),
)


def audit_ordered_unsaturated_witness():
    """First ordered-but-unsaturated ceiling root ever observed.

    Earlier searches found none in ~7,000 candidates; the n=8 probe
    around the condition-failure seeds produced seven.  The witness has
    an ordered ceiling root with rooted packing value 5/4, strictly
    below the saturation value g/(g-1) = 4/3 at g = 4, so the ordered
    geometry does not force saturation.  The target is safe: the
    overlap is 50/3 against 10.  Scope control for the saturated-arm
    theorems, which assume saturation."""
    from audit_carrier_separator_payment import full_tight_support
    from audit_ceiling_root_gainer_exclusion import rooted_packing
    generators = tuple(
        tuple(F(value) for value in generator)
        for generator in ORDERED_UNSATURATED_WITNESS
    )
    n = len(generators[0])
    values = lower_envelope(generators)
    x, z = selectors(values, n)
    ceiling = max(z)
    gset = {i for i in range(n) if z[i] > x[i]}
    if len(gset) != 4:
        raise AssertionError("unsaturated witness: gainer count changed")
    support = tuple(full_tight_support(values, x))
    found = None
    for root in range(n):
        if z[root] != ceiling or x[root] < ceiling or root in gset:
            continue
        _rooted, nu, _w, _c = rooted_packing(support, n, root)
        outsiders = [i for i in range(n)
                     if i not in gset and i != root]
        floor_g = min(x[a] for a in gset)
        ordered = (all(x[root] >= x[a] for a in gset)
                   and all(floor_g >= x[j] for j in outsiders))
        if ordered:
            found = (root, nu)
    if found is None:
        raise AssertionError("unsaturated witness: no ordered root")
    root, nu = found
    if str(nu) != "5/4":
        raise AssertionError("unsaturated witness: packing value drifted")
    overlap = sum(min(a, b) for a, b in zip(x, z))
    target = F(n, (n * n) // 4) * sum(x, F(0))
    if overlap < target:
        raise AssertionError("unsaturated witness: target violated")
    return {"name": "ordered_unsaturated_witness", "nu": "5/4",
            "overlap": str(overlap), "target": str(target)}


def strict_separation():
    """PXC85: at the Lmax point, z_i > z_j forces a z-tight coalition
    containing i and avoiding j (else the egalitarian transfer from i
    to j stays in the core and lexicographically improves the sorted
    vector).  Checked exhaustively on the pinned control games."""
    for generators in (TRIPLE_MENU_ESCAPE, ORDERED_UNSATURATED_WITNESS):
        generators = tuple(
            tuple(F(value) for value in generator)
            for generator in generators
        )
        n = len(generators[0])
        values = lower_envelope(generators)
        _x, z = selectors(values, n)
        tight = [coalition for coalition in range(1, (1 << n) - 1)
                 if coalition_sum(z, coalition) == values[coalition]]
        for i in range(n):
            for j in range(n):
                if i == j or z[i] <= z[j]:
                    continue
                if not any(coalition >> i & 1
                           and not coalition >> j & 1
                           for coalition in tight):
                    raise AssertionError(
                        f"strict separation failed at ({i},{j})"
                    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    dispersion_identity()
    pair_graph_feasibility()
    strict_separation()
    rows = [audit_control(name, generators, expected)
            for name, generators, expected in CONTROLS]
    failure_rows = [
        audit_condition_failure(name, shape, packet, family)
        for name, shape, packet, family in CONDITION_FAILURE_CONTROLS
    ]
    triple_row = audit_triple_menu_escape()
    unsaturated_row = audit_ordered_unsaturated_witness()
    family_rooted_row = audit_family_rooted_control()
    summary = {
        "controls": len(rows),
        "chain_closures": sum(row["chain_closes"] for row in rows),
        "dispersion_identity": "g(k-1)-1 for all fed counts >= 2",
        "condition_failure_controls": len(failure_rows),
        "triple_menu_escape": triple_row["name"],
        "ordered_unsaturated_witness": unsaturated_row["nu"],
        "family_rooted_control": family_rooted_row["chain"],
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
        "triple_menu_escape_row": triple_row,
        "ordered_unsaturated_witness_row": unsaturated_row,
        "family_rooted_control_row": family_rooted_row,
    }
    rendered = json.dumps(payload, indent=2, default=str) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
