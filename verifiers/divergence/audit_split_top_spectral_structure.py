#!/usr/bin/env python3
r"""Exact controls for split-top spectral structure (PXC77).

The one audited violation class outside the two-stratum theorem has a
split top: the heavy gainer joins the root at the Lmax ceiling, the
remaining gainers form a sub-top stratum, and the Lmax-tight menu is
built from double co-stars containing the root, the heavy gainer, all
sub-top gainers but one, and one outsider.  On this class the canonical
over-cover concentrates its largest weight on the heavy gainer rather
than the root, both spectral currencies vanish, so the sharpened bound
equals the actual-top bound, and the bound is exactly tight at the
canonical control.  This driver enumerates the split family
`a=(2a',a',a')` with a root-heavy second generator on a fixed grid,
checks the structural hypotheses instance by instance, and pins the
closures; the canonical clean control is replayed with its exact
dispersion, over-cover weights, and tight spectral value.  These are
exact finite structure facts.  On the class-A geometry --- exactly one
heavy gainer, double co-stars and the heavy-block row Lmax-tight ---
the mixed over-cover is feasible, the dispersion obeys
`theta<=s(k-1)/(sk+k-s)` (PXC78a), and the PXC75-style chain (PXC78)
closes every audited class-A root, both packet violations included; the
class-B/C sub-geometries stay outside the theorem.
"""

from __future__ import annotations

import argparse
import itertools
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


def split_partial_cover_infeasibility():
    """PXC82: no pair-supported cover with an unfed sub-top type.

    In the single-heavy split-top geometry, any over-cover supported on
    the fed double co-stars (t of the s sub-top omitted types) plus the
    heavy-block row is infeasible whenever t < s: an unfed type lies in
    every fed row and not in the heavy block, so its ambient equality
    forces coverage(u) = L = coverage(r), hence alpha_r = 0 and every
    fed type weight w_c = L - eta = 0, so L = eta = 0 and the
    normalization alpha_r + alpha_h = 1 fails.  Feasible exactly when
    t = s and (s-1)k >= s (the PXC78 cover).  Checked by exact LP.
    """
    from exactlp import exact_linprog

    for s_count in range(2, 6):
        for k in range(2, 5):
            for t in range(1, s_count + 1):
                m = t * k
                nu_i, eta_i, ar_i, ah_i = m, m + 1, m + 2, m + 3
                width = m + 4
                eqs, rhs = [], []
                base = [F(0)] * width
                for c in range(t):
                    for j in range(k):
                        base[c * k + j] = F(1)
                row = list(base)
                row[eta_i], row[ar_i] = F(-1), F(-1)
                eqs.append(row)
                rhs.append(F(0))
                row = list(base)
                row[nu_i], row[eta_i], row[ah_i] = F(1), F(-1), F(-1)
                eqs.append(row)
                rhs.append(F(0))
                for c in range(t):
                    row = list(base)
                    for j in range(k):
                        row[c * k + j] = F(0)
                    row[eta_i] = F(-1)
                    eqs.append(row)
                    rhs.append(F(0))
                if t < s_count:
                    row = list(base)
                    row[eta_i] = F(-1)
                    eqs.append(row)
                    rhs.append(F(0))
                for j in range(k):
                    row = [F(0)] * width
                    for c in range(t):
                        row[c * k + j] = F(1)
                    row[nu_i], row[eta_i] = F(1), F(-1)
                    eqs.append(row)
                    rhs.append(F(0))
                row = [F(0)] * width
                row[ar_i] = row[ah_i] = F(1)
                eqs.append(row)
                rhs.append(F(1))
                ineqs, irhs = [], []
                for variable in range(width):
                    row = [F(0)] * width
                    row[variable] = F(-1)
                    ineqs.append(row)
                    irhs.append(F(0))
                status, _value, _solution = exact_linprog(
                    [F(0)] * width, ineqs, irhs, eqs, rhs
                )
                expected = ("optimal"
                            if t == s_count and (s_count - 1) * k >= s_count
                            else "infeasible")
                if status != expected:
                    raise AssertionError(
                        f"partial cover s={s_count} k={k} t={t}: "
                        f"{status} != {expected}"
                    )


CLASS_B_CONTROL = (
    (0, 10, 5, 5, 0, 0, 0), (12, 0, 0, 0, 4, 2, 2),
    (0, 10, 4, 6, 0, 0, 0), (0, 9, 6, 5, 0, 0, 0),
    (0, 9, 5, 6, 0, 0, 0), (13, 0, 0, 0, 4, 1, 2),
)


def audit_class_b_control():
    """PXC84 on the first class-B violation found by design search.

    Split-top packet violation with a slack heavy-block row (class B).
    The top pair {r,h} is Lmax-tight, and any tight row R with
    r in R, R a subset of the top stratum T, is by itself an
    over-cover with ambient level zero: theta <= 1/|R|.  With the
    surplus hypothesis sum_R x >= |R| M and the nonroot Lmin cap, the
    master chain B >= (M-f)/theta + |T| f + z(N-T) -
    sum_{N-T}(z_i-f)_+ + M - x_r holds -- the (PXC75) argument
    verbatim with |T| in place of g+1.  Pinned exactly."""
    from audit_spectral_or_reserve import selectors as _selectors
    generators = tuple(
        tuple(F(value) for value in generator)
        for generator in CLASS_B_CONTROL
    )
    n = len(generators[0])
    values = lower_envelope(generators)
    x, z = _selectors(values, n)
    if [str(value) for value in x] != ["6", "4", "2", "2", "2", "2", "2"]:
        raise AssertionError("class-B control: x drifted")
    if [str(value) for value in z] !=             ["9/2", "9/2", "4", "4", "1", "1", "1"]:
        raise AssertionError("class-B control: z drifted")
    roots = ordered_saturated_roots(values, x, z)
    if len(roots) != 1:
        raise AssertionError("class-B control: root count changed")
    root, gainers, outsiders, _dec = roots[0]
    M = max(z)
    tops = [i for i in range(n) if z[i] == M]
    if sorted(tops) != [0, 1]:
        raise AssertionError("class-B control: top stratum changed")
    hb = sum(1 << a for a in tops if a != root)         + sum(1 << j for j in outsiders)
    if coalition_sum(z, hb) == values[hb]:
        raise AssertionError("class-B control: heavy block now tight")
    pair = (1 << root) | (1 << 1)
    if coalition_sum(z, pair) != values[pair]:
        raise AssertionError("class-B control: top pair no longer tight")
    packet = margins(values, x, z)["packet_margin"]
    if str(packet) != "-1":
        raise AssertionError("class-B control: packet margin drifted")
    cert = top_certificate(values, z)
    theta = F(cert["theta"])
    if theta != F(1, 2):
        raise AssertionError("class-B control: dispersion drifted")
    surplus = x[root] + x[1] - 2 * M
    if surplus != 1:
        raise AssertionError("class-B control: surplus drifted")
    f = min(x)
    nontop = [i for i in range(n) if z[i] < M]
    residual = sum(z[i] for i in nontop)         - sum(max(z[i] - f, F(0)) for i in nontop)
    chain = 2 * (M - f) + 2 * f + residual + M - x[root]
    total = sum(x, F(0))
    target = F(n, (n * n) // 4) * total
    spec = spectral_decomposition("b", values, x, z)
    bound = F(spec["sharpened_spectral_bound_ratio"]) * total
    if str(chain) != "29/2" or chain < target or bound < chain:
        raise AssertionError("class-B control: PXC84 chain failed")
    return {
        "name": "class_b_top_pair",
        "packet_margin": "-1",
        "theta": "1/2",
        "surplus": "1",
        "chain": "29/2",
        "bound": str(bound),
        "chain_closes": True,
    }


def split_instance(heavy, light, count_light, H, w):
    a = (heavy,) + (light,) * count_light
    g = len(a)
    k = len(w)
    generator_one = tuple([F(0)] + [F(q) for q in a] + [F(0)] * k)
    generator_two = tuple([F(H)] + [F(0)] * g + [F(q) for q in w])
    if sum(generator_one, F(0)) != sum(generator_two, F(0)):
        return None
    return (generator_one, generator_two)


def audit_instance(generators):
    n = len(generators[0])
    values = lower_envelope(generators)
    x, z = selectors(values, n)
    if x == z:
        return None
    roots = ordered_saturated_roots(values, x, z)
    if len(roots) != 1:
        return None
    root, gainers, outsiders, _decoration = roots[0]
    ceiling = max(z)
    top_gainers = tuple(a for a in gainers if z[a] == ceiling)
    sub_gainers = tuple(a for a in gainers if z[a] < ceiling)
    if z[root] != ceiling or not top_gainers or not sub_gainers:
        return None
    sub_values = {z[a] for a in sub_gainers}
    if len(sub_values) != 1:
        return None
    sub_level = sub_values.pop()
    if not all(z[j] < sub_level for j in outsiders):
        return None
    # double co-stars: root + all top gainers + all sub gainers but one +
    # one outsider, all Lmax-tight
    fed = True
    for omitted in sub_gainers:
        for outsider in outsiders:
            coalition = (1 << root) | (1 << outsider)
            for a in top_gainers:
                coalition |= 1 << a
            for a in sub_gainers:
                if a != omitted:
                    coalition |= 1 << a
            if coalition_sum(z, coalition) != values[coalition]:
                fed = False
    # heavy-block row {h} u O for the single-heavy geometry
    heavy_block = None
    if len(top_gainers) == 1:
        coalition = 1 << top_gainers[0]
        for j in outsiders:
            coalition |= 1 << j
        heavy_block = coalition_sum(z, coalition) == values[coalition]
    cert = top_certificate(values, z)
    theta = F(cert["theta"])
    alpha = [F(value) for value in cert["alpha"]]
    heavy_weighted = all(
        alpha[a] >= alpha[root] for a in top_gainers
    )
    # PXC78 chain on the class-A geometry
    s_count = len(sub_gainers)
    k_count = len(outsiders)
    pxc78 = None
    if heavy_block and fed and s_count >= 2 and k_count >= 2:
        denominator = s_count * k_count + k_count - s_count
        theta_bound = F(s_count * (k_count - 1), denominator)
        if theta > theta_bound:
            raise AssertionError("class-A over-cover feasibility failed")
        M = ceiling
        f = min(x)
        total = sum(x, F(0))
        if any(x[i] > M for i in range(n) if i != root):
            pxc78 = None
        else:
            residual_bound = s_count * f + sum(
                min(z[j], f) for j in outsiders
            )
            chain = (
                (M - f) / theta_bound + 2 * f + residual_bound + M - x[root]
            )
            spec_pre = spectral_decomposition("c", values, x, z)
            bound_pre = F(spec_pre["sharpened_spectral_bound_ratio"]) * total
            if bound_pre < chain:
                raise AssertionError("class-A spectral chain failed")
            target_pre = F(spec_pre["target_ratio"]) * total
            pxc78 = {
                "theta_bound": str(theta_bound),
                "chain": str(chain),
                "chain_closes": chain >= target_pre,
            }
    spec = spectral_decomposition("t", values, x, z)
    total = sum(x, F(0))
    bound = F(spec["sharpened_spectral_bound_ratio"]) * total
    target = F(spec["target_ratio"]) * total
    currencies_zero = (
        F(spec["top_selection_currency_ratio"]) == 0
        and F(spec["label_currency_ratio"]) == 0
    )
    packet = margins(values, x, z)["packet_margin"]
    overlap = sum(min(a, b) for a, b in zip(x, z))
    return {
        "generators": [
            [str(value) for value in generator] for generator in generators
        ],
        "n": n,
        "root": root,
        "top_gainers": list(top_gainers),
        "sub_gainers": list(sub_gainers),
        "double_costars_fed": fed,
        "heavy_block_row": heavy_block,
        "pxc78": pxc78,
        "theta": str(theta),
        "heavy_weighted": heavy_weighted,
        "currencies_zero": currencies_zero,
        "bound": str(bound),
        "target": str(target),
        "bound_closes": bound >= target,
        "bound_tight": bound == overlap,
        "packet_margin": str(packet),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    split_partial_cover_infeasibility()
    class_b_row = audit_class_b_control()
    rows = []
    for light in range(2, 6):
        heavy = 2 * light
        for count_light in (2,):
            total = heavy + count_light * light
            for k in (2, 3):
                for H in range(2, total - k + 1):
                    rest = total - H
                    for w in itertools.combinations_with_replacement(
                        range(1, rest + 1), k
                    ):
                        if sum(w) != rest:
                            continue
                        generators = split_instance(
                            heavy, light, count_light, H,
                            tuple(sorted(w, reverse=True)),
                        )
                        if generators is None:
                            continue
                        row = audit_instance(generators)
                        if row is not None:
                            rows.append(row)

    canonical = audit_instance(split_instance(6, 3, 2, 8, (2, 1, 1)))
    if canonical is None:
        raise AssertionError("canonical split-top control left the class")
    expected_canonical = {
        "theta": "4/7",
        "heavy_weighted": True,
        "currencies_zero": True,
        "double_costars_fed": True,
        "bound": "9",
        "target": "7",
        "bound_closes": True,
        "bound_tight": True,
        "packet_margin": "-5/7",
    }
    for key, value in expected_canonical.items():
        if canonical[key] != value:
            raise AssertionError(
                f"canonical[{key!r}] = {canonical[key]!r} != {value!r}"
            )

    summary = {
        "grid_split_top_instances": len(rows),
        "grid_double_costars_fed": sum(row["double_costars_fed"] for row in rows),
        "grid_heavy_weighted": sum(row["heavy_weighted"] for row in rows),
        "grid_currencies_zero": sum(row["currencies_zero"] for row in rows),
        "grid_bound_closes": sum(row["bound_closes"] for row in rows),
        "grid_bound_tight": sum(row["bound_tight"] for row in rows),
        "grid_packet_violations": sum(
            F(row["packet_margin"]) < 0 for row in rows
        ),
        "grid_class_a": sum(row["pxc78"] is not None for row in rows),
        "grid_class_a_chain_closes": sum(
            row["pxc78"]["chain_closes"]
            for row in rows
            if row["pxc78"] is not None
        ),
        "grid_class_bc_packet_closed": sum(
            F(row["packet_margin"]) >= 0
            for row in rows
            if row["pxc78"] is None
        ),
    }
    expected = {
        "grid_split_top_instances": 31,
        "grid_double_costars_fed": 11,
        "grid_heavy_weighted": 22,
        "grid_currencies_zero": 14,
        "grid_bound_closes": 31,
        "grid_bound_tight": 14,
        "grid_packet_violations": 2,
        "grid_class_a": 11,
        "grid_class_a_chain_closes": 11,
        "grid_class_bc_packet_closed": 20,
    }
    for key, value in expected.items():
        if summary[key] != value:
            raise AssertionError(
                f"summary[{key!r}] = {summary[key]!r} != {value!r}"
            )

    payload = {
        "class_b_top_pair": class_b_row,
        "claim": (
            "split-top roots carry heavy-gainer-weighted over-covers with "
            "vanishing spectral currencies; the sharpened bound closes and "
            "is exactly tight at the canonical control"
        ),
        "summary": summary,
        "canonical": canonical,
        "rows": rows,
    }
    rendered = json.dumps(payload, indent=2, default=str) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
