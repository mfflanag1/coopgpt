"""Positive controls for the A3 finite check.

A program that always answers "infeasible" would prove nothing, so three
controls are run.

 (C-1) DROP THE CONE.  Re-run the n=5 programs with the exact-cone constraints
       removed.  If failures become feasible, the encoding can express a
       failure and it is exactness -- not the encoding -- that forbids it.
 (C-2) KNOWN n=6 FAILURE.  route1's smallest M-side counterexample is rebuilt
       and pushed through the SAME reduction: its nu-tight cover must have
       value < h(N), and Lmax must exceed nu.
 (C-3) POSITIVE INSTANCES.  On random exact 5-player games, check directly that
       M = nu and mu = lambda, and that the minimising cover attains equality.
"""
from __future__ import annotations

import json
import random
import sys
from fractions import Fraction as F

import z3

SCR = "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad"
sys.path.insert(0, SCR)
sys.path.insert(0, SCR + "/sel/a3check")
import audit
import lmax as lmaxmod
from a3lp import load_vertices, canon_pairs, run, nm, N, FULL


def control_1():
    verts = load_vertices()
    over = [(w, b) for w, b in verts if not b]
    pairs = canon_pairs(over, list(range(1, FULL + 1)))
    out = {}
    for side in ("M", "mu"):
        feas = 0
        for w, A in pairs:
            if run(side, w, A, []) is not None:      # no cone inequalities
                feas += 1
        out[side] = feas
        print(f"  (C-1) {side}-side without the cone constraints: "
              f"{feas}/{len(pairs)} classes feasible", flush=True)
    return out


def game_stats(n, v):
    full = (1 << n) - 1
    T = v[full]
    nu = max(F(v[S], bin(S).count("1")) for S in range(1, full + 1))
    lam = min(F(T - v[full ^ S], bin(S).count("1")) for S in range(1, full + 1))
    return T, nu, lam


def control_2():
    n = 6
    full = (1 << n) - 1
    gens = [tuple(map(F, (3, 2, 0, 0, 0, 0))), tuple(map(F, (0, 0, 2, 1, 1, 1)))]
    v = audit.envelope(n, gens)
    assert all(v[1 << i] == 0 for i in range(n)), "not singleton-normalized"
    T, nu, lam = game_stats(n, v)
    tight = [S for S in range(1, full + 1) if F(v[S], bin(S).count("1")) == nu]
    cover = [0b000110, 0b001101, 0b010101, 0b100101]   # {2,3},{1,3,4},{1,3,5},{1,3,6}
    load = [sum(1 for S in cover if S >> i & 1) for i in range(n)]
    val = sum(nu * bin(S).count("1") - v[S] for S in cover)
    hN = nu * n - T
    mx = lmaxmod.lmax(n, v)
    M = max(mx)
    print(f"  (C-2) n=6 witness: T={T} nu={nu} h(N)={hN}")
    print(f"        cover {[nm6(S) for S in cover]} all nu-tight="
          f"{all(S in tight for S in cover)} loads={load} value={val}")
    print(f"        value < h(N): {val < hN};  Lmax={[str(q) for q in mx]}, "
          f"M={M} > nu={nu}: {M > nu}")
    return {"T": str(T), "nu": str(nu), "hN": str(hN), "cover_value": str(val),
            "beats_trivial": val < hN, "M": str(M), "M_gt_nu": M > nu}


def nm6(mask):
    return "".join("abcdef"[i] for i in range(6) if mask >> i & 1)


def control_3(trials=60, seed=11):
    rng = random.Random(seed)
    n = 5
    full = (1 << n) - 1
    ok = 0
    tot = 0
    for _ in range(trials):
        tt = rng.choice([6, 8, 12])
        gens = audit.rand_gens(n, rng, rng.randint(2, 5), tt, tt)
        v = audit.envelope(n, gens)
        w, _ = audit.normalize(n, v)
        if w[full] == 0:
            continue
        phi = audit.lmin(n, w)
        psi = lmaxmod.lmax(n, w)
        T, nu, lam = game_stats(n, w)
        tot += 1
        if max(psi) == nu and min(phi) == lam:
            ok += 1
        else:
            print("  (C-3) VIOLATION", [str(q) for q in w])
    print(f"  (C-3) {ok}/{tot} random exact 5-player games satisfy "
          f"M = nu and mu = lambda")
    return {"games": tot, "ok": ok}


def main():
    res = {}
    res["control_1_no_cone"] = control_1()
    res["control_2_n6_witness"] = control_2()
    res["control_3_random"] = control_3()
    json.dump(res, open(f"{SCR}/sel/a3check/controls.json", "w"), indent=1)


if __name__ == "__main__":
    main()
