"""END-TO-END AUDIT of the harvested PART(2,2) witness, and construction of the
n=7 ZP(2,2) game from it by null-player suspension (PROOF.txt Lemma 4).

Discharges:
  * that PART(2,2) at m=4 is REALIZABLE, refuting PROOF.txt Conjecture 10;
  * that the n=7 zero-payoff profile (2,2) ("type B") is REALIZABLE, closing
    the ZP residue in the positive direction.

Nothing is taken from the harvester except the five generator rows.  The game,
its exactness, its Lmin, its strata, its tight family and the configuration are
all recomputed here from those rows in exact rational arithmetic.  Exactness is
checked at DEFINITION level (min over the core of x(S), by exact LP) -- no
vertex enumeration is performed at any n.

Usage: python3 audit_witness.py
"""
from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction as F

sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import lib23 as L

GENS22 = [[0, 0, 1, 4, 2, 1],
          [0, 0, 4, 4, 0, 0],
          [4, 0, 0, 0, 2, 2],
          [1, 0, 2, 3, 0, 2],
          [0, 1, 2, 3, 1, 1]]


def report_game(n, w, label):
    FULL = (1 << n) - 1
    print(f"\n=== {label} : n={n} ===")
    print("  v(N) =", w[FULL])
    print("  v    =", {L.nm(n, S): str(w[S])
                       for S in range(1, FULL + 1) if w[S] != 0})
    for i in range(n):
        assert w[1 << i] == 0, f"not singleton-normalized at {L.LETTERS[i]}"
    print("  singleton-normalized: yes")
    ex, bad = L.is_exact_lp(n, w)
    print(f"  EXACT (definition level, exact LP over the core): {ex}"
          + ("" if ex else f"  FAILS AT {L.nm(n, bad)}"))
    assert ex
    phi = L.lmin(n, w)
    print("  Lmin =", [str(x) for x in phi])
    blocks = L.strata(phi)
    print("  strata (poorest first) =",
          [[L.LETTERS[i] for i in b] for b in blocks])
    tight = L.tight_family(n, w, phi)
    print("  proper Lmin-tight coalitions =", [L.nm(n, T) for T in tight])
    return phi, blocks, tight


def check_part(n, w, phi, blocks, tight):
    FULL = (1 << n) - 1
    sufs = [sum(1 << i for b in blocks[j + 1:] for i in b)
            for j in range(len(blocks) - 1)]
    hits = []
    for H in sufs:
        if bin(H).count("1") != 2:
            continue
        s = sum(phi[i] for i in range(n) if H >> i & 1) - w[H]
        if s <= 0:
            continue
        Hs = L.bits(n, H)
        for S1, S2 in itertools.permutations(tight, 2):
            if S1 & H != (1 << Hs[0]) or S2 & H != (1 << Hs[1]):
                continue
            if (S1 | S2) != FULL or (S1 & S2) != 0:
                continue
            p = bin(S1 & ~H).count("1")
            q = bin(S2 & ~H).count("1")
            hits.append({"H": L.nm(n, H), "s_H": str(s), "S1": L.nm(n, S1),
                         "S2": L.nm(n, S2), "p": p, "q": q,
                         "m": n - 2})
    return hits


def check_zp(n, w, phi, blocks, tight):
    """ZP(p,q): S1 & S2 = {e} singleton in L, S1 | S2 = N."""
    FULL = (1 << n) - 1
    sufs = [sum(1 << i for b in blocks[j + 1:] for i in b)
            for j in range(len(blocks) - 1)]
    hits = []
    for H in sufs:
        if bin(H).count("1") != 2:
            continue
        s = sum(phi[i] for i in range(n) if H >> i & 1) - w[H]
        if s <= 0:
            continue
        Hs = L.bits(n, H)
        for S1, S2 in itertools.permutations(tight, 2):
            if S1 & H != (1 << Hs[0]) or S2 & H != (1 << Hs[1]):
                continue
            if (S1 | S2) != FULL:
                continue
            inter = S1 & S2
            if bin(inter).count("1") != 1 or inter & H:
                continue
            e = L.bits(n, inter)[0]
            p = bin(S1 & ~H & ~inter).count("1")
            q = bin(S2 & ~H & ~inter).count("1")
            hits.append({"H": L.nm(n, H), "s_H": str(s), "S1": L.nm(n, S1),
                         "S2": L.nm(n, S2), "e": L.LETTERS[e],
                         "phi_e": str(phi[e]), "p": p, "q": q, "m": n - 2})
    return hits


def main():
    out = {}

    # ---------------------------------------------------------------- n = 6
    n = 6
    gens = [tuple(F(x) for x in g) for g in GENS22]
    tot = {sum(g) for g in gens}
    assert len(tot) == 1, f"generators do not share a total: {tot}"
    print("generator rows (common total "
          f"{tot.pop()}):")
    for g in gens:
        print("   ", [str(x) for x in g])
    v = L.envelope(n, gens)
    w, shift = L.normalize(n, v)
    assert all(x == 0 for x in shift), shift
    phi, blocks, tight = report_game(n, w, "PART(2,2) witness")
    hits = check_part(n, w, phi, blocks, tight)
    print("  PARTITION configurations found:")
    for h in hits:
        print("    ", h)
    got22 = [h for h in hits if (h["p"], h["q"]) == (2, 2)]
    print(f"  >>> PART(2,2) at m=4 realized: {bool(got22)}")
    out["n6"] = {"w": [str(x) for x in w], "phi": [str(x) for x in phi],
                 "strata": [[L.LETTERS[i] for i in b] for b in blocks],
                 "tight": [L.nm(n, T) for T in tight],
                 "part_hits": hits}

    # ------------------------------- n = 7 : suspend a null player (Lemma 4)
    n7 = 7
    gens7 = [tuple(list(g) + [F(0)]) for g in gens]
    v7 = L.envelope(n7, gens7)
    w7, shift7 = L.normalize(n7, v7)
    assert all(x == 0 for x in shift7)
    # sanity: g is null
    FULL7 = (1 << n7) - 1
    nullok = all(w7[S | (1 << 6)] == w7[S] for S in range(1, FULL7))
    print(f"\n  player g adjoined as a NULL player: {nullok}")
    assert nullok
    phi7, blocks7, tight7 = report_game(n7, w7, "ZP(2,2) by suspension")
    zh = check_zp(n7, w7, phi7, blocks7, tight7)
    print("  ZERO-PAYOFF configurations found:")
    for h in zh:
        print("    ", h)
    got = [h for h in zh if (h["p"], h["q"]) == (2, 2)]
    print(f"  >>> ZP(2,2) at m=5 (n=7 'type B') realized: {bool(got)}")
    out["n7"] = {"w": [str(x) for x in w7], "phi": [str(x) for x in phi7],
                 "strata": [[L.LETTERS[i] for i in b] for b in blocks7],
                 "tight": [L.nm(n7, T) for T in tight7],
                 "zp_hits": zh}

    json.dump(out, open("/private/tmp/claude-501/-Users-maxf/"
                        "f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23/"
                        "audit_witness.json", "w"), indent=1)


if __name__ == "__main__":
    main()
