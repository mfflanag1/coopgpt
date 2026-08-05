"""Audit Remark 5: locate the one-packet systems (P) among semi-balanced types.

At the smallest realization of each minimal pair of the staircase, this script
rebuilds the game, recomputes Lmin exactly, enumerates every lifted packet of
the one-packet reduction theorem, and classifies the resulting incidence
system (P) as

    minimal semi-balanced?      no proper subsystem is semi-balanced,
    indecomposable?             no external set yields a decomposition,

using only the definitions of Studeny and Kratochvil (2022).  Indecomposable
min-semi-balanced systems are precisely the facet-defining ones, so this
separates "certifies the obstruction" from "defines a facet of the exact
cone".  The manuscript proof is symbolic; this is a bug audit of Remark 5 and
not a proof dependency.

Passing --catalogue-dir DIR, where DIR holds the n3/n4/n5/n6 CSV files of the
electronic catalogue

    http://gogo.utia.cas.cz/indecomposable-min-semi-balanced-catalogue/

additionally cross-checks the intrinsic classification against the published
permutational types.  Without it the intrinsic classification still runs.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import sys
from fractions import Fraction
from math import gcd
from pathlib import Path

import z3

from leximin import leximin_core_exact
from tugame import Game


if sys.flags.optimize:
    raise RuntimeError("run this exact verifier without Python -O")

LETTERS = "abcdefgh"


# --------------------------------------------------------------- the games

def _zero(n):
    return [Fraction(0)] * n


def family_unique_richest(m):
    """Proposition 6 with m poorer players 0..m-1 and richest player m."""
    n, r = m + 1, m
    rows = []
    g = _zero(n); g[3] = m - 1; g[r] = m - 1; rows.append(g)
    g = _zero(n); g[2] = m - 1; g[3] = m - 1; rows.append(g)
    g = _zero(n); g[0] = g[1] = g[2] = 1
    if m >= 5:
        g[4] = m - 4
    g[r] = m - 1; rows.append(g)
    phi = _zero(n)
    for i in range(m):
        phi[i] = Fraction(1)
    phi[r] = m - 2
    rows.append(phi)
    return n, rows, phi, 1 << r


def family_two_poorer(m, h):
    """Proposition 7: poorer 0..m-1, richer suffix m..m+h-1."""
    D, r, n = (h - 2) * (h - 3), h - 2, m + h
    p1, p2 = 0, 1
    Q = list(range(2, m))
    a, b = m, m + 1
    K = list(range(m + 2, n))
    H = list(range(m, n))
    rows = []

    g = _zero(n); g[p2] = D
    for j in Q:
        g[j] = D
    g[a] = g[b] = 3 * D
    for k in K:
        g[k] = (2 * r - 1) * (r - 1)
    rows.append(g)

    g = _zero(n); g[p1] = 4 * D
    for j in Q:
        g[j] = D
    for k in K:
        g[k] = 2 * (r * r - 1)
    rows.append(g)

    for drop in K:
        g = _zero(n); g[p1] = D
        for j in Q:
            g[j] = D
        g[a] = g[b] = 3 * D
        for k in K:
            if k != drop:
                g[k] = r * (2 * r - 1)
        rows.append(g)

    phi = _zero(n)
    for i in range(m):
        phi[i] = Fraction(D)
    for i in H:
        phi[i] = Fraction(2 * D)
    rows.append(phi)
    for j in Q:
        g = list(phi); g[p1] += D; g[j] -= D
        rows.append(g)

    return n, rows, phi, sum(1 << i for i in H)


def family_three_poorer(m, h):
    """Proposition 8: poorer 0..m-1, richer suffix m..m+h-1."""
    n = m + h
    p1, p2, p3 = 0, 1, 2
    Q = list(range(3, m))
    H = list(range(m, n))
    r1, rh = H[0], H[-1]
    rows = []

    g = _zero(n); g[p1] = 2; g[p3] = 3
    for j in Q:
        g[j] = 1
    g[r1] = 5
    for i in H:
        if i not in (r1, rh):
            g[i] = 3
    rows.append(g)

    g = _zero(n); g[p2] = 2; g[p3] = 1
    for j in Q:
        g[j] = 1
    g[r1] = 4
    for i in H:
        if i != r1:
            g[i] = 3
    rows.append(g)

    g = _zero(n)
    for j in Q:
        g[j] = 1
    g[rh] = 3 * h + 4
    rows.append(g)

    phi = _zero(n); phi[p1] = phi[p2] = Fraction(1); phi[p3] = Fraction(2)
    for j in Q:
        phi[j] = Fraction(1)
    for i in H:
        phi[i] = Fraction(3)
    rows.append(phi)
    for j in Q:
        g = list(phi); g[p1] += 1; g[j] -= 1
        rows.append(g)

    return n, rows, phi, sum(1 << i for i in H)


def lower_envelope(n, rows):
    full = (1 << n) - 1
    total = sum(rows[0])
    if any(sum(row) != total for row in rows):
        raise RuntimeError("generator totals disagree")
    v = [Fraction(0)] * (1 << n)
    for S in range(1, full):
        v[S] = min(sum(row[i] for i in range(n) if S >> i & 1) for row in rows)
    v[full] = Fraction(total)
    return v


# ------------------------------------------- vertices of the exact-cover polytope

def _solve_unique(A, rhs):
    """Exact solve of A x = rhs; None unless the solution is unique."""
    nc = len(A[0])
    work = [list(row) + [val] for row, val in zip(A, rhs)]
    piv, top = [], 0
    for col in range(nc):
        sel = next((i for i in range(top, len(work)) if work[i][col] != 0), None)
        if sel is None:
            continue
        work[top], work[sel] = work[sel], work[top]
        lead = work[top][col]
        work[top] = [q / lead for q in work[top]]
        for i in range(len(work)):
            if i != top and work[i][col] != 0:
                f = work[i][col]
                work[i] = [work[i][j] - f * work[top][j] for j in range(nc + 1)]
        piv.append(col)
        top += 1
    if len(piv) != nc:
        return None
    if any(row[nc] != 0 for row in work[top:]):
        return None
    x = [Fraction(0)] * nc
    for i, col in enumerate(piv):
        x[col] = work[i][nc]
    return x


def min_balanced_collections(members):
    """Vertices of the exact-cover polytope on `members`."""
    subsets = [sum(1 << i for i in c)
               for k in range(1, len(members) + 1)
               for c in itertools.combinations(members, k)]
    out = []
    for size in range(1, len(members) + 1):
        for coll in itertools.combinations(subsets, size):
            A = [[Fraction(bool(R >> i & 1)) for R in coll] for i in members]
            beta = _solve_unique(A, [Fraction(1)] * len(members))
            if beta is not None and all(x > 0 for x in beta):
                out.append((coll, dict(zip(coll, beta))))
    return out


# --------------------------------------------------------------- the packets

def lifted_packets(n, v, phi, Hmask):
    full = (1 << n) - 1
    poor = [i for i in range(n) if not Hmask >> i & 1]
    rich = [i for i in range(n) if Hmask >> i & 1]
    tight = [S for S in range(1, full)
             if sum(phi[i] for i in range(n) if S >> i & 1) == v[S]]
    packets = []
    for coll, beta in min_balanced_collections(rich):
        choices = []
        for R in coll:
            opts = [S for S in tight if S & Hmask == R]
            if not opts:
                choices = None
                break
            choices.append(opts)
        if choices is None:
            continue
        for lift in itertools.product(*choices):
            load = {i: sum(beta[R] for R, S in zip(coll, lift) if S >> i & 1)
                    for i in poor}
            b = max(load.values())
            u = {i: b - load[i] for i in poor}
            delta = 1 + sum(u.values()) - b
            if delta <= 0:
                continue
            lam = {}
            for R, S in zip(coll, lift):
                lam[S] = lam.get(S, Fraction(0)) + beta[R]
            for i in poor:
                if u[i]:
                    key = Hmask | (1 << i)
                    lam[key] = lam.get(key, Fraction(0)) + u[i]
            lam[Hmask] = lam.get(Hmask, Fraction(0)) - delta
            lam = {S: c for S, c in lam.items() if c != 0}
            scale = 1
            for c in lam.values():
                scale = scale * c.denominator // gcd(scale, c.denominator)
            lam = {S: int(c * scale) for S, c in lam.items()}
            common = 0
            for c in lam.values():
                common = gcd(common, abs(c))
            lam = {S: c // common for S, c in lam.items()}
            loads = [sum(c for S, c in lam.items() if S >> i & 1)
                     for i in range(n)]
            if len(set(loads)) != 1:
                raise RuntimeError("packet identity is not constant")
            if sum(1 for c in lam.values() if c < 0) != 1:
                raise RuntimeError("packet identity is not semi-conic")
            packets.append({"traces": coll, "lift": lift, "delta": delta,
                            "b": b, "lam": lam, "r": loads[0]})
    return packets, tight


# ------------------------------------------------- semi-balanced classification

def _constant_combination(n, sets, signs):
    """signs[k]: 1 strictly positive, -1 strictly negative, 0 nonnegative."""
    lam = [z3.Real(f"l{k}") for k in range(len(sets))]
    level = z3.Real("r")
    s = z3.Solver()
    for k, sign in enumerate(signs):
        s.add(lam[k] >= 1 if sign > 0 else
              lam[k] <= -1 if sign < 0 else lam[k] >= 0)
    for i in range(n):
        s.add(z3.Sum([lam[k] for k, S in enumerate(sets) if S >> i & 1]) == level)
    return s.check() == z3.sat


def _semi_balanced(n, sets):
    sets = list(sets)
    for neg in [None] + list(range(len(sets))):
        signs = [1] * len(sets)
        if neg is not None:
            signs[neg] = -1
        if _constant_combination(n, sets, signs):
            return True
    return False


def classify_system(n, sets):
    sets = list(sets)
    for size in range(1, len(sets)):
        for sub in itertools.combinations(sets, size):
            if _semi_balanced(n, sub):
                return "not minimal", list(sub)
    for E in range(1, (1 << n) - 1):
        if E in sets:
            continue
        if _constant_combination(n, sets + [E], [0] * len(sets) + [-1]):
            return "minimal but decomposable", E
    return "indecomposable min-semi-balanced", None


# ------------------------------------------------------------- the catalogue

def load_catalogue(directory, n):
    path = Path(directory) / f"n{n}.csv"
    if not path.exists():
        return None
    letters = LETTERS[:n]
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh, delimiter=";"))
    cols = [sum(1 << letters.index(ch) for ch in name) for name in rows[0][1:]]
    if cols[-1] != (1 << n) - 1:
        raise RuntimeError("unexpected catalogue column order")
    types = {}
    for raw in rows[1:]:
        vals = [int(x) for x in raw]
        # the CSV stores the negated coefficients of the proper subsets
        lam = {S: -c for S, c in zip(cols[:-1], vals[1:-1]) if c}
        level = vals[-1]
        loads = [sum(c for S, c in lam.items() if S >> i & 1) for i in range(n)]
        if loads != [level] * n or -level + sum(lam.values()) != vals[0]:
            raise RuntimeError("catalogue row fails its own standardization")
        types[canonical_type(n, lam)] = True
    return types


def canonical_type(n, lam):
    common = 0
    for c in lam.values():
        common = gcd(common, abs(c))
    reduced = {S: c // common for S, c in lam.items()}
    best = None
    for perm in itertools.permutations(range(n)):
        key = tuple(sorted(
            (sum(1 << perm[i] for i in range(n) if S >> i & 1), c)
            for S, c in reduced.items()))
        if best is None or key < best:
            best = key
    return best


# ------------------------------------------------------------------- driver

def name(n, mask):
    return "".join(LETTERS[i] for i in range(n) if mask >> i & 1)


def audit_case(label, builder, catalogue_dir):
    n, rows, phi_claim, Hmask = builder()
    v = lower_envelope(n, rows)
    game = Game(n, v)
    if any(game.v[1 << i] != 0 for i in range(n)):
        raise RuntimeError(f"{label}: game is not singleton-normalized")
    if any(not game.in_core(row) for row in rows):
        raise RuntimeError(f"{label}: a generator is outside the core")
    phi = leximin_core_exact(game)
    if list(phi) != list(phi_claim):
        raise RuntimeError(f"{label}: Lmin disagrees with the displayed row")
    slack = sum(phi[i] for i in range(n) if Hmask >> i & 1) - v[Hmask]
    if slack <= 0:
        raise RuntimeError(f"{label}: the boundary is not slack")

    packets, tight = lifted_packets(n, v, phi, Hmask)
    if not packets:
        raise RuntimeError(f"{label}: the one-packet theorem produced nothing")
    catalogue = (load_catalogue(catalogue_dir, n)
                 if catalogue_dir is not None else None)

    grouped = {}
    for packet in packets:
        grouped.setdefault(canonical_type(n, packet["lam"]), []).append(packet)

    types = []
    for key, group in grouped.items():
        verdict, witness = classify_system(n, list(group[0]["lam"]))
        listed = None if catalogue is None else key in catalogue
        if listed is not None and listed != verdict.startswith("indecomposable"):
            raise RuntimeError(
                f"{label}: catalogue lookup contradicts the classification")
        types.append({
            "system": {name(n, S): c for S, c in sorted(group[0]["lam"].items())},
            "common_load": group[0]["r"],
            "exceptional_coalition": name(n, Hmask),
            "traces": [name(n, R) for R in group[0]["traces"]],
            "lift": [name(n, S) for S in group[0]["lift"]],
            "delta": str(group[0]["delta"]),
            "packets_in_type": len(group),
            "classification": verdict,
            "decomposing_set": (name(n, witness)
                                if isinstance(witness, int) else None),
            "in_published_catalogue": listed,
        })
    types.sort(key=lambda t: -t["packets_in_type"])
    return {
        "case": label,
        "player_count": n,
        "richer_suffix": name(n, Hmask),
        "lmin": [str(q) for q in phi],
        "richer_suffix_slack": str(slack),
        "tight_proper_coalitions": sorted(name(n, S) for S in tight),
        "packet_count": len(packets),
        "packet_types": len(types),
        "facet_defining_types": sum(
            1 for t in types
            if t["classification"].startswith("indecomposable")),
        "types": types,
    }


CASES = {
    "4,1": ("unique-richest, five players",
            lambda: family_unique_richest(4)),
    "5,1": ("unique-richest, six players",
            lambda: family_unique_richest(5)),
    "3,2": ("three-poorer escape, five players",
            lambda: family_three_poorer(3, 2)),
    "3,3": ("three-poorer escape, six players",
            lambda: family_three_poorer(3, 3)),
    "4,2": ("three-poorer escape, six players",
            lambda: family_three_poorer(4, 2)),
    "2,4": ("two-poorer internal sacrifice, six players",
            lambda: family_two_poorer(2, 4)),
    "6,1": ("unique-richest, seven players",
            lambda: family_unique_richest(6)),
    "4,3": ("three-poorer escape, seven players",
            lambda: family_three_poorer(4, 3)),
    "3,4": ("two-poorer internal sacrifice, seven players",
            lambda: family_two_poorer(3, 4)),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--catalogue-dir",
        help="directory holding n3.csv..n6.csv from the published catalogue",
    )
    parser.add_argument("--cases", default=",".join(CASES),
                        help="comma-separated (m,h) pairs; default all")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    wanted = [c.strip() for c in args.cases.split(",") if c.strip()]
    keys, i = [], 0
    while i < len(wanted):
        keys.append(f"{wanted[i]},{wanted[i + 1]}")
        i += 2
    cases = [audit_case(f"(m,h)=({key})  {CASES[key][0]}",
                        CASES[key][1], args.catalogue_dir)
             for key in keys]

    payload = {
        "status": "one-packet systems classified as semi-balanced types",
        "claim": (
            "every system (P) is min-semi-balanced with exceptional coalition "
            "H, but need not be indecomposable, so it need not define a facet "
            "of the cone of exact games"
        ),
        "proof_scope": (
            "the manuscript proof is symbolic and dimension-free; this is a "
            "bug audit of Remark 5, not a proof dependency"
        ),
        "catalogue_consulted": args.catalogue_dir is not None,
        "case_count": len(cases),
        "non_facet_type_count": sum(
            case["packet_types"] - case["facet_defining_types"]
            for case in cases),
        "cases": cases,
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
