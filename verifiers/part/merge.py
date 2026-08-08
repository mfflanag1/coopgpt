"""ROUTE A: the rich-pair MERGE transfer lemma.

Discharges: the structural explanation of the threshold, and (if it holds) a
human proof that a PART configuration forces m >= 4.

THE CONSTRUCTION.  Let v be exact, singleton-normalized, phi = Lmin(v), with a
slack strict boundary H = {f,g} and a PART(p,q) pair S1, S2.  Merge f and g
into one player r and normalize:

    N'  = L u {r},
    w'(A)        = v(A)                     (A subset of L),
    w'(A u {r})  = v(A u H) - v(H).

FACTS PROVED BY HAND (see PROOF.txt):
  M1  w' is exact.               [the merge of a coordinate block of an exact
                                  game is exact: the projection of core(v)
                                  lies in core(w') and already attains every
                                  w'(B), so the two minima coincide]
  M2  w' is singleton-normalized.
  M3  psi := (phi|_L, s) with s = s_phi(H) lies in core(w').

WHAT IS TESTED HERE (the two remaining links, before attempting a proof):
  T1  s > max_{i in L} phi_i        -- {r} is the STRICT richer suffix of psi;
  T2  psi = Lmin(w')                -- the merge respects the leximin point.

If T1 and T2 hold at every PART configuration then the h=1 branch of the phase
theorem (paper4 Prop 4.3: a slack h=1 boundary forces m >= m_min(1) = 4)
applies to w' verbatim and yields m >= 4.  T1 must FAIL at slack h=2
boundaries that are not PART -- e.g. the (m,h)=(3,2) member of paper4
Prop family3, where phi = (1,1,2,3,3), s = 1 and max_L phi = 2 -- since those
do exist at m = 3.  So the test also has a built-in negative control.

Usage: python3 merge.py
"""
from __future__ import annotations

import itertools
import json
import random
import sys
from fractions import Fraction as F

sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import lib23 as L


def merged_game(n, w, Hmask):
    """Return (n', w') for the game with H merged into one player r, listed
    last.  Poorer players keep their relative order."""
    Ls = [i for i in range(n) if not (Hmask >> i & 1)]
    n2 = len(Ls) + 1
    r = n2 - 1
    FULL2 = (1 << n2) - 1
    vH = w[Hmask]
    w2 = [F(0)] * (1 << n2)
    for B in range(1, FULL2 + 1):
        A = sum(1 << Ls[k] for k in range(len(Ls)) if B >> k & 1)
        if B >> r & 1:
            w2[B] = w[A | Hmask] - vH
        else:
            w2[B] = w[A]
    return n2, w2, Ls


def test_config(n, w, phi, Hmask, label, verbose=True):
    Ls = [i for i in range(n) if not (Hmask >> i & 1)]
    s = sum(phi[i] for i in range(n) if Hmask >> i & 1) - w[Hmask]
    maxL = max(phi[i] for i in Ls)
    n2, w2, order = merged_game(n, w, Hmask)
    psi = [phi[i] for i in order] + [s]
    FULL2 = (1 << n2) - 1
    res = {"label": label, "m": len(Ls), "s": str(s), "max_L_phi": str(maxL),
           "T1_s_gt_maxL": s > maxL}
    # M2
    res["M2_normalized"] = all(w2[1 << i] == 0 for i in range(n2))
    # M1
    ex, bad = L.is_exact_lp(n2, w2)
    res["M1_exact"] = ex
    # M3 + T2
    incore = (sum(psi) == w2[FULL2]
              and all(sum(psi[i] for i in range(n2) if B >> i & 1) >= w2[B]
                      for B in range(1, FULL2)))
    res["M3_psi_in_core"] = incore
    lm = L.lmin(n2, w2)
    res["merged_lmin"] = [str(x) for x in lm] if lm else None
    res["T2_psi_is_lmin"] = (lm == psi)
    if verbose:
        print(f"  {label:34s} m={res['m']} s={res['s']:>6s} "
              f"maxLphi={res['max_L_phi']:>5s}  "
              f"M1={res['M1_exact']} M2={res['M2_normalized']} "
              f"M3={res['M3_psi_in_core']} "
              f"T1={res['T1_s_gt_maxL']} T2={res['T2_psi_is_lmin']}")
    return res


def part_configs(n, w, phi):
    """All (Hmask, p, q) PART configurations at slack h=2 strict boundaries."""
    FULL = (1 << n) - 1
    blocks = L.strata(phi)
    tight = L.tight_family(n, w, phi)
    out = []
    for j in range(len(blocks) - 1):
        H = sum(1 << i for b in blocks[j + 1:] for i in b)
        if bin(H).count("1") != 2:
            continue
        if sum(phi[i] for i in range(n) if H >> i & 1) <= w[H]:
            continue
        Hs = L.bits(n, H)
        for S1, S2 in itertools.permutations(tight, 2):
            if S1 & H != (1 << Hs[0]) or S2 & H != (1 << Hs[1]):
                continue
            if (S1 | S2) != FULL or (S1 & S2) != 0:
                continue
            out.append((H, bin(S1 & ~H).count("1"), bin(S2 & ~H).count("1")))
    return out


def slack_h2_boundaries(n, w, phi):
    blocks = L.strata(phi)
    out = []
    for j in range(len(blocks) - 1):
        H = sum(1 << i for b in blocks[j + 1:] for i in b)
        if bin(H).count("1") != 2:
            continue
        if sum(phi[i] for i in range(n) if H >> i & 1) <= w[H]:
            continue
        out.append(H)
    return out


def family3(m, h):
    """paper4 Prop 'three-poorer escape family': slack (m,h) boundary.
    Used as the NEGATIVE control -- it is a slack h=2 boundary that is NOT
    PART, and T1 must fail there when m = 3."""
    # players: p1,p2,p3, Q (m-3 of them), then H (h of them)
    n = m + h
    p1, p2, p3 = 0, 1, 2
    Q = list(range(3, m))
    Hs = list(range(m, m + h))
    r1, rh = Hs[0], Hs[-1]

    def vec(d):
        return tuple(F(d.get(i, 0)) for i in range(n))

    a = {p1: 2, p3: 3, r1: 5}
    for j in Q:
        a[j] = 1
    for k in Hs[1:-1]:
        a[k] = 3
    b = {p2: 2, p3: 1, r1: 4}
    for j in Q:
        b[j] = 1
    for k in Hs[1:]:
        b[k] = 3
    c = {rh: 3 * h + 4}
    for j in Q:
        c[j] = 1
    phid = {p1: 1, p2: 1, p3: 2}
    for j in Q:
        phid[j] = 1
    for k in Hs:
        phid[k] = 3
    gens = [vec(a), vec(b), vec(c), vec(phid)]
    for j in Q:
        d = dict(phid)
        d[p1] = d.get(p1, 0) + 1
        d[j] = d.get(j, 0) - 1
        gens.append(vec(d))
    tots = {sum(g) for g in gens}
    assert len(tots) == 1, tots
    v = L.envelope(n, gens)
    w, sh = L.normalize(n, v)
    assert all(x == 0 for x in sh), sh
    return n, w


def main():
    print("=" * 78)
    print("ROUTE A: rich-pair merge, tested at PART configurations")
    print("=" * 78)
    rows = []

    # ---- the PART(2,2) witness (n=6) and its n=7 suspension
    import audit_witness as AW
    gens = [tuple(F(x) for x in g) for g in AW.GENS22]
    v = L.envelope(6, gens)
    w, _ = L.normalize(6, v)
    phi = L.lmin(6, w)
    for (H, p, q) in part_configs(6, w, phi):
        rows.append(test_config(6, w, phi, H, f"witness PART({p},{q}) n=6"))

    # ---- harvested n=6 witnesses of the other splits
    try:
        data = json.load(open("/private/tmp/claude-501/-Users-maxf/"
                              "f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/"
                              "r23/witness_n6.json"))
        for key, wit in data["found"].items():
            g6 = [tuple(F(x) for x in row) for row in wit["gens"]]
            vv = L.envelope(6, g6)
            ww, _ = L.normalize(6, vv)
            pp = L.lmin(6, ww)
            for (H, p, q) in part_configs(6, ww, pp):
                rows.append(test_config(6, ww, pp, H,
                                        f"harvest PART({p},{q}) n=6"))
    except FileNotFoundError:
        pass

    # ---- random search for more PART configurations, n = 6 and 7
    print("\nrandom PART configurations:")
    rng = random.Random(7)
    seen = 0
    for n in (6, 7):
        tries = 0
        while seen < 200 and tries < 4000:
            tries += 1
            total = rng.randint(n, 22)
            k = rng.randint(2, n - 2)
            Sp = rng.sample(range(n), k)
            cS = rng.randint(1, total - 1)
            gs = []
            for _ in range(rng.randint(2, 5)):
                def comp(kk, tt):
                    cuts = sorted(rng.randrange(tt + 1) for _ in range(kk - 1))
                    return [b - a for a, b in zip([0] + cuts, cuts + [tt])]
                gg = [0] * n
                for i, val in zip(Sp, comp(k, cS)):
                    gg[i] = val
                oth = [i for i in range(n) if i not in Sp]
                for i, val in zip(oth, comp(n - k, total - cS)):
                    gg[i] = val
                gs.append(tuple(F(x) for x in gg))
            if any(min(g[i] for g in gs) != 0 for i in range(n)):
                continue
            try:
                vv = L.envelope(n, gs)
                ww, _ = L.normalize(n, vv)
                if ww[(1 << n) - 1] <= 0:
                    continue
                pp = L.lmin(n, ww)
            except (AssertionError, RuntimeError):
                continue
            if pp is None:
                continue
            cfgs = part_configs(n, ww, pp)
            if not cfgs:
                continue
            for (H, p, q) in cfgs[:1]:
                seen += 1
                rows.append(test_config(n, ww, pp, H,
                                        f"random PART({p},{q}) n={n}"))
            if seen >= 30:
                break

    # ---- NEGATIVE CONTROL: slack h=2 boundaries that are NOT PART
    print("\nNEGATIVE CONTROL -- slack h=2 boundaries with NO PART pair:")
    for m in (3, 4, 5):
        n, w3 = family3(m, 2)
        p3 = L.lmin(n, w3)
        for H in slack_h2_boundaries(n, w3, p3):
            cf = part_configs(n, w3, p3)
            test_config(n, w3, p3, H,
                        f"family3 m={m} h=2 (PART pairs: {len(cf)})")

    nT1 = sum(1 for r in rows if not r["T1_s_gt_maxL"])
    nT2 = sum(1 for r in rows if not r["T2_psi_is_lmin"])
    nM1 = sum(1 for r in rows if not r["M1_exact"])
    nM3 = sum(1 for r in rows if not r["M3_psi_in_core"])
    print("\n" + "=" * 78)
    print(f"PART configurations tested : {len(rows)}")
    print(f"  M1 (merge is exact)      failures: {nM1}")
    print(f"  M3 (psi in merged core)  failures: {nM3}")
    print(f"  T1 (s > max_L phi)       failures: {nT1}")
    print(f"  T2 (psi = Lmin of merge) failures: {nT2}")
    json.dump(rows, open("/private/tmp/claude-501/-Users-maxf/"
                         "f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23/"
                         "merge.json", "w"), indent=1)


if __name__ == "__main__":
    main()
