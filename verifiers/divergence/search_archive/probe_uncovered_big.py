#!/usr/bin/env python3
"""Bipartite-pairing angle: what does an uncovered outsider force?

At a uniform-top packet violation, PXC81 feasibility fails iff some
outsider j lies in no Lmax-tight pair (or only one omission type
appears).  Probe: over all uniform-top violations in the two-generator
family grid, record for each UNCOVERED outsider j the exact identities
available -- z_j vs f=min x, x_j vs z_j, the PXC71 row-loss of its rows,
whether the direct arm / chosen family close -- hunting an implication
"uncovered outsider => [structure] => direct or chosen-family".
"""
import json
import sys
from fractions import Fraction as F
from pathlib import Path

REPO = Path("/private/tmp/coop-hybrid-20260812/coopgames")
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "verifiers" / "divergence"))

from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from audit_spectral_or_reserve import selectors, margins, family_instance  # noqa: E402
from audit_costar_saturation_dichotomy import coalition_sum  # noqa: E402
from audit_menu_relaxed_root_exchange import ordered_saturated_roots  # noqa: E402
from audit_direct_ceiling_common_hinge_trichotomy import has_direct_packet  # noqa: E402
from audit_chosen_family_costar_closure import best_family_margin  # noqa: E402


def grid():
    for g in (2, 3, 4, 5):
        for a in range(2, 9):
            for k in (2, 3, 4, 5):
                if 1 + g + k > 9:
                    continue
                total_a = g * a
                for H in range(2, total_a):
                    rest = total_a - H
                    if rest < k:
                        continue
                    import itertools
                    for w in itertools.combinations_with_replacement(
                        range(1, rest + 1), k
                    ):
                        if sum(w) != rest:
                            continue
                        yield (tuple([a] * g), H,
                               tuple(sorted(w, reverse=True)))


def main():
    rows = []
    seen = set()
    for a_vec, H, w in grid():
        key = (a_vec, H, w)
        if key in seen:
            continue
        seen.add(key)
        n = 1 + len(a_vec) + len(w)
        gen1 = tuple([F(0)] + [F(q) for q in a_vec] + [F(0)] * len(w))
        gen2 = tuple([F(H)] + [F(0)] * len(a_vec) + [F(q) for q in w])
        if sum(gen1, F(0)) != sum(gen2, F(0)):
            continue
        generators = (gen1, gen2)
        values = lower_envelope(generators)
        x, z = selectors(values, n)
        if x is None or z is None or x == z:
            continue
        for root, gainers, outsiders, _dec in ordered_saturated_roots(
            values, x, z
        ):
            m = margins(values, x, z)
            if m["packet_margin"] >= 0:
                continue
            M = max(z)
            if not (z[root] == M and all(z[a] == M for a in gainers)
                    and all(z[j] < M for j in outsiders)):
                continue
            edges = [
                (a_, j) for a_ in gainers for j in outsiders
                if coalition_sum(
                    z, (1 << root) | (1 << j)
                    | sum(1 << b for b in gainers if b != a_)
                ) == values[(1 << root) | (1 << j)
                            | sum(1 << b for b in gainers if b != a_)]
            ]
            columns = {j for _a, j in edges}
            types = {a_ for a_, _j in edges}
            condition = (columns == set(outsiders) and len(types) >= 2)
            uncovered = sorted(set(outsiders) - columns)
            f = min(x)
            direct = has_direct_packet(x, z, F(n, (n * n) // 4))
            family = best_family_margin(values, x, z, root, gainers,
                                        outsiders)
            rows.append({
                "shape": f"a={a_vec} H={H} w={w}",
                "condition": condition,
                "uncovered": [
                    {"j": j, "z_j": str(z[j]), "x_j": str(x[j]),
                     "zj_le_f": z[j] <= f, "xj_eq_zj": x[j] == z[j]}
                    for j in uncovered
                ],
                "n_types": len(types),
                "f": str(f),
                "direct": direct,
                "chosen_family": None if family is None else str(family),
                "family_closes": family is not None and family >= 0,
                "packet_margin": str(m["packet_margin"]),
            })
    fails = [r for r in rows if not r["condition"]]
    print(f"violations: {len(rows)}, condition failures: {len(fails)}")
    for r in fails:
        print(json.dumps(r))
    # candidate implications over ALL condition failures
    impl_zf = all(u["zj_le_f"] for r in fails for u in r["uncovered"])
    impl_xz = all(u["xj_eq_zj"] for r in fails for u in r["uncovered"])
    impl_closed = all(r["direct"] or r["family_closes"] for r in fails)
    print(f"IMPL uncovered => z_j <= f: {impl_zf}")
    print(f"IMPL uncovered => x_j == z_j: {impl_xz}")
    print(f"IMPL failure => direct or family: {impl_closed}")
    # covered-violation contrast
    holds = [r for r in rows if r["condition"]]
    print(f"condition holds at {len(holds)}; "
          f"direct at {sum(r['direct'] for r in holds)}; "
          f"family at {sum(r['family_closes'] for r in holds)}")


if __name__ == "__main__":
    main()
