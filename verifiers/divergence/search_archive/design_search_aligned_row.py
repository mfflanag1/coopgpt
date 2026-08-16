#!/usr/bin/env python3
"""Design search: ordered saturated ceiling roots without an aligned co-star row.

Family: lower envelopes of k additive nonnegative integer generators with a
common total (exact by construction) and zero singletons (each player is off
the support of some generator).  For every ordered saturated ceiling root of
the exact Lmin/Lmax selector pair, test:
  (E) existence of an Lmax-tight aligned co-star row,
  (B) the unit-exchange bound D - d_max <= ell_r,
  (Q) the exact equality D - d_max = ell_r.
Any root failing (E) or (B), or satisfying (E) with strict inequality in (Q),
is a discovery and is printed in full.
"""
import argparse
import json
import random
import sys
import time
from fractions import Fraction as F
from pathlib import Path

REPO = Path("/private/tmp/coop-hybrid-20260812/coopgames")
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "verifiers" / "divergence"))

from tugame import Game, exact_lp_min  # noqa: E402
from certified_float_lp import certified_lp_min  # noqa: E402
from certified_leximin import leximin_core_certified  # noqa: E402
from leximin import leximin_core_exact  # noqa: E402
from audit_pxc52_coloured_charge import lower_envelope  # noqa: E402
from audit_menu_relaxed_root_exchange import ordered_saturated_roots  # noqa: E402
from audit_costar_saturation_dichotomy import coalition_sum  # noqa: E402


def lp(c, A, b, Aeq, beq):
    optimum, point, _info = certified_lp_min(c, A, b, Aeq, beq)
    if optimum is None:
        optimum, point = exact_lp_min(c, A, b, Aeq, beq)
    return optimum, point


def leximax_core_certified(game):
    n, N, v = game.n, game.N, game.v
    fixed = {}

    def core_rows(nv):
        A, b = [], []
        for coalition in range(1, N):
            row = [F(0)] * nv
            for player in range(n):
                if coalition >> player & 1:
                    row[player] = F(-1)
            A.append(row)
            b.append(-v[coalition])
        return A, b

    def solve_ceiling(free):
        nv = n + 1
        A, b = core_rows(nv)
        for player in free:
            row = [F(0)] * nv
            row[player] = F(1)
            row[n] = F(-1)
            A.append(row)
            b.append(F(0))
        Aeq = [[F(1)] * n + [F(0)]]
        beq = [v[N]]
        for player, value in fixed.items():
            row = [F(0)] * nv
            row[player] = F(1)
            Aeq.append(row)
            beq.append(value)
        objective = [F(0)] * nv
        objective[n] = F(1)
        return lp(objective, A, b, Aeq, beq)

    def min_player(player, free, ceiling):
        A, b = core_rows(n)
        for other in free:
            row = [F(0)] * n
            row[other] = F(1)
            A.append(row)
            b.append(ceiling)
        Aeq = [[F(1)] * n]
        beq = [v[N]]
        for other, value in fixed.items():
            row = [F(0)] * n
            row[other] = F(1)
            Aeq.append(row)
            beq.append(value)
        objective = [F(0)] * n
        objective[player] = F(1)
        optimum, _ = lp(objective, A, b, Aeq, beq)
        return optimum

    free = list(range(n))
    while free:
        optimum, _ = solve_ceiling(free)
        if optimum is None or optimum == "unbounded":
            return None
        ceiling = optimum
        pinned = [
            player
            for player in free
            if min_player(player, free, ceiling) == ceiling
        ]
        if not pinned:
            raise RuntimeError("certified Lmax stage found no pinned player")
        for player in pinned:
            fixed[player] = ceiling
            free.remove(player)
    return [fixed[player] for player in range(n)]


def composition(rng, support, total):
    """Random positive integer weights on the support summing to total."""
    k = len(support)
    cuts = sorted(rng.sample(range(1, total), k - 1)) if k > 1 else []
    parts = []
    previous = 0
    for cut in cuts + [total]:
        parts.append(cut - previous)
        previous = cut
    return dict(zip(support, parts))


def random_generators(rng, n, k, total):
    """k nonneg integer generators, common total, zero singleton envelope."""
    while True:
        supports = []
        for _ in range(k):
            size = rng.randint(1, n - 1)
            supports.append(tuple(sorted(rng.sample(range(n), size))))
        if any(all(p in s for s in supports) for p in range(n)):
            continue
        generators = []
        for s in supports:
            weights = composition(rng, s, total)
            generators.append(tuple(F(weights.get(p, 0)) for p in range(n)))
        return tuple(generators)


def structured_generators(rng, n, total):
    """Sharp-family-shaped designs: heavy root, light block, uneven hinge."""
    players = list(range(n))
    rng.shuffle(players)
    root = players[0]
    light_count = rng.randint(0, min(3, n - 3))
    light = players[1 : 1 + light_count]
    hinge = players[1 + light_count :]
    light_weights = {p: rng.randint(1, 3) for p in light}
    heavy = total - sum(light_weights.values())
    if heavy <= max(light_weights.values(), default=0):
        return None
    g = [F(0)] * n
    g[root] = F(heavy)
    for p, w in light_weights.items():
        g[p] = F(w)
    h = [F(0)] * n
    hinge_weights = composition(rng, tuple(hinge), total)
    for p, w in hinge_weights.items():
        h[p] = F(w)
    generators = [tuple(g), tuple(h)]
    if rng.random() < 0.5:
        size = rng.randint(2, n - 1)
        support = tuple(sorted(rng.sample(range(n), size)))
        weights = composition(rng, support, total)
        generators.append(tuple(F(weights.get(p, 0)) for p in range(n)))
    return tuple(generators)


def audit_game(generators, tag, findings, stats):
    n = len(generators[0])
    values = lower_envelope(generators)
    game = Game(n, list(values))
    x, _certificate = leximin_core_certified(game)
    if x is None:
        x = leximin_core_exact(game)
        stats["selector_fallbacks"] += 1
    z = leximax_core_certified(game)
    if x is None or z is None:
        stats["selector_failures"] += 1
        return
    x = tuple(F(q) for q in x)
    z = tuple(F(q) for q in z)
    stats["games"] += 1
    if x == z:
        return
    stats["divergent"] += 1
    total_check = sum(x, F(0))
    if sum(min(a, b) for a, b in zip(x, z)) < F(n, (n * n) // 4) * total_check:
        findings.append({"kind": "TARGET_VIOLATION", "tag": tag,
                         "generators": [[str(q) for q in g] for g in generators],
                         "x": [str(q) for q in x], "z": [str(q) for q in z]})
        print(json.dumps(findings[-1]), flush=True)
    from audit_carrier_separator_payment import full_tight_support
    from audit_ceiling_root_gainer_exclusion import rooted_packing
    ceiling = max(z)
    gainer_set = {p for p in range(n) if z[p] > x[p]}
    support = tuple(full_tight_support(values, x))
    for root in range(n):
        if z[root] != ceiling or x[root] < ceiling or root in gainer_set:
            continue
        stats["funnel_candidate_roots"] += 1
        rooted, nu, _w, _c = rooted_packing(support, n, root)
        omitted = {
            c: tuple(p for p in gainer_set if not (c >> p & 1)) for c in rooted
        }
        if any(len(v_) >= 2 for v_ in omitted.values()):
            stats["funnel_multiomission"] += 1
            continue
        g = len(gainer_set)
        if g < 2:
            stats["funnel_single_gainer"] += 1
            continue
        outsiders = [p for p in range(n) if p not in gainer_set and p != root]
        ming = min(x[p] for p in gainer_set)
        ordered = all(x[root] >= x[p] for p in gainer_set) and all(
            ming >= x[p] for p in outsiders
        )
        saturated = nu == F(g, g - 1)
        if not ordered:
            stats["funnel_unordered"] += 1
            continue
        if not saturated:
            stats["funnel_ordered_not_saturated"] += 1
            findings.append(
                {
                    "kind": "ordered_not_saturated",
                    "tag": tag,
                    "generators": [[str(q) for q in g_] for g_ in generators],
                    "x": [str(q) for q in x],
                    "z": [str(q) for q in z],
                    "root": root,
                    "packing_value": str(nu),
                    "gainers": sorted(gainer_set),
                }
            )
            print(json.dumps(findings[-1]), flush=True)
            continue
        stats["funnel_ordered_saturated"] += 1
    try:
        roots = ordered_saturated_roots(values, x, z)
    except AssertionError as error:
        stats["root_enum_failures"] += 1
        findings.append(
            {
                "kind": "root_enumeration_assertion",
                "tag": tag,
                "generators": [[str(q) for q in g] for g in generators],
                "error": str(error),
            }
        )
        return
    if not roots:
        return
    stats["games_with_roots"] += 1
    for root, gainers, outsiders, _decoration in roots:
        stats["roots"] += 1
        outsiders_all = outsiders
        g = len(gainers)
        gains = {p: z[p] - x[p] for p in gainers}
        total_gain = sum(gains.values(), F(0))
        d_max = max(gains.values())
        maxg = [p for p in gainers if gains[p] == d_max]
        ell = x[root] - z[root]
        strict = [j for j in outsiders if x[j] > z[j]]
        full = (1 << n) - 1
        aligned = []
        for c in range(1, full):
            if coalition_sum(z, c) != values[c]:
                continue
            if not (c >> root & 1):
                continue
            if any(c >> j & 1 for j in strict):
                continue
            for a in maxg:
                if c >> a & 1:
                    continue
                if any(not (c >> b & 1) for b in gainers if b != a):
                    continue
                aligned.append(c)
        bound_ok = total_gain - d_max <= ell
        equality = total_gain - d_max == ell
        if aligned:
            stats["roots_with_aligned_row"] += 1
        if equality:
            stats["roots_with_equality"] += 1
        mu = F((g - 1) * n, g * (n - g))
        total = sum(x, F(0))
        slack63 = (F(n, g * (n - g)) - F(n, (n * n) // 4)) * total
        penalty = total_gain - d_max - ell
        margin63 = mu * _decoration + slack63 - penalty
        if margin63 >= 0:
            stats["roots_pxc63b"] += 1
        spectral_margin = None
        if margin63 < 0:
            from audit_spectral_label_currency import spectral_decomposition
            try:
                spec = spectral_decomposition("s", values, x, z)
                spectral_margin = (
                    F(spec["sharpened_spectral_bound_ratio"])
                    - F(spec["target_ratio"])
                ) * total
            except AssertionError:
                spectral_margin = None
            if spectral_margin is not None and spectral_margin >= 0:
                stats["roots_spectral_rescued"] += 1
        pxc75 = None
        if margin63 < 0:
            M_top = max(z)
            top_uniform = z[root] == M_top and all(
                z[p] == M_top for p in gainers
            ) and all(z[j] < M_top for j in outsiders_all)
            fed = True
            for a_g in gainers:
                for j_o in outsiders_all:
                    cl = (1 << root) | (1 << j_o)
                    for b_g in gainers:
                        if b_g != a_g:
                            cl |= 1 << b_g
                    zc = sum(z[p_] for p_ in range(n) if cl >> p_ & 1)
                    if zc != values[cl]:
                        fed = False
                        break
                if not fed:
                    break
            hw = all(x[p_] <= M_top for p_ in range(n) if p_ != root)
            pxc75 = top_uniform and fed and hw
            if pxc75:
                stats["violations_pxc75_covered"] += 1
        interesting = margin63 < 0 and (
            (spectral_margin is None or spectral_margin < 0)
            or pxc75 is False
        )
        if interesting:
            findings.append(
                {
                    "kind": "combined_or_uncovered",
                    "margin63": str(margin63),
                    "spectral_margin": str(spectral_margin),
                    "pxc75_covered": pxc75,
                    "decoration_mass": str(_decoration),
                    "tag": tag,
                    "generators": [[str(q) for q in g] for g in generators],
                    "x": [str(q) for q in x],
                    "z": [str(q) for q in z],
                    "root": root,
                    "gainers": list(gainers),
                    "strict_outsiders": strict,
                    "D_minus_dmax": str(total_gain - d_max),
                    "ell_r": str(ell),
                    "aligned_rows": aligned,
                }
            )
            print(json.dumps(findings[-1]), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260815)
    parser.add_argument("--n", type=int, default=7)
    parser.add_argument("--rounds", type=int, default=400)
    parser.add_argument("--total", type=int, default=12)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    findings = []
    stats = {
        "games": 0,
        "divergent": 0,
        "games_with_roots": 0,
        "roots": 0,
        "roots_with_aligned_row": 0,
        "roots_with_equality": 0,
        "roots_pxc63b": 0,
        "roots_spectral_rescued": 0,
        "violations_pxc75_covered": 0,
        "selector_failures": 0,
        "selector_fallbacks": 0,
        "root_enum_failures": 0,
        "funnel_candidate_roots": 0,
        "funnel_multiomission": 0,
        "funnel_single_gainer": 0,
        "funnel_ordered_not_saturated": 0,
        "funnel_unordered": 0,
        "funnel_ordered_saturated": 0,
    }
    start = time.time()
    for round_index in range(args.rounds):
        if round_index % 3 == 2:
            k = 2 if round_index % 2 == 0 else 3
            generators = random_generators(rng, args.n, k, args.total)
            tag = f"random[{round_index}]k{k}"
        else:
            generators = structured_generators(rng, args.n, args.total)
            if generators is None:
                continue
            tag = f"structured[{round_index}]k{len(generators)}"
        audit_game(generators, tag, findings, stats)
        if (round_index + 1) % 25 == 0:
            print(
                f"[{round_index + 1}/{args.rounds}] {time.time() - start:.0f}s "
                + json.dumps(stats),
                flush=True,
            )
    payload = {"stats": stats, "findings": findings, "seed": args.seed,
               "n": args.n, "rounds": args.rounds, "total": args.total}
    if args.output:
        args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
