"""EXTERNAL POSITIVE CONTROL: do genuine games satisfy the encoded hypotheses?

Campaign law demands, for every finite check, a positive control on a KNOWN
GENUINE GAME.  The z3-internal control in closecfg2 (negate the failure
hypothesis, must be SAT) only shows the hypothesis set is self-consistent.
This script is the real thing: every harvested exact game is relabelled into
the canonical layout of its own configuration and every hypothesis of
closecfg2.Prog2 is evaluated on it numerically, in exact rational arithmetic.

Checked per game:
  H1  singleton-normalized, v >= 0, v(N)=T
  H2  Lmin in Core;  H3  Lmax in Core
  H4  v(S) <= M|S| and T - v(N\\S) >= mu|S| for all S
  H4a a ceiling anchor exists, has >= 2 players and lies in the Lmax top
      stratum
  H4b a floor anchor exists and lies in the Lmin bottom stratum
  H5* every floor stage k: some vertex of the stage-k dual polyhedron has
      objective <= 0
  H6* every ceiling stage l: likewise
A single failure anywhere would mean the corresponding UNSAT verdict is
vacuous.  Output poscontrol.json.
"""
from __future__ import annotations
import json
import sys
from fractions import Fraction as F

HERE = sys.path[0]
sys.path.insert(0, HERE)
sys.path.insert(0, HERE + "/lib")
import audit
import stages

N, FULL = 5, 31
SZ = [bin(S).count("1") for S in range(32)]


def relabel(v, perm):
    """perm[newindex] = oldindex."""
    inv = {o: n for n, o in enumerate(perm)}
    w = [F(0)] * 32
    for S in range(32):
        Sp = sum(1 << inv[i] for i in range(N) if S >> i & 1)
        w[Sp] = v[S]
    return w


def stage_ok(v, lev, masks, idx, ceiling):
    """Evaluate the stage certificate numerically; None if the stage is vacuous.

    lev[i] = the pinned value of player i on the relevant side."""
    B = len(masks)
    if ceiling:
        other = 0
        for j in range(idx + 1, B):
            other |= masks[j]
    else:
        other = 0
        for j in range(idx):
            other |= masks[j]
    Fm = FULL ^ other
    Dl = masks[idx]
    if bin(Fm).count("1") < 2 or Dl == Fm:
        return None
    val = lambda m: sum(lev[i] for i in range(N) if m >> i & 1)
    Tl = 1 - val(other)
    L = lev[[i for i in range(N) if Dl >> i & 1][0]]     # the stage level
    caps = {}
    for A in stages.subsets(Fm):
        if A in (0, Fm):
            continue
        if ceiling:
            caps[A] = min(F(SZ[A]) * L + val(Bm) - v[A | Bm]
                          for Bm in stages.subsets(other))
        else:
            comp = Fm ^ A
            caps[A] = min(Tl - (v[comp | Bm] - val(Bm)) - F(SZ[A]) * L
                          for Bm in stages.subsets(other))
    c = (F(bin(Fm).count("1")) * L - Tl if ceiling
         else Tl - F(bin(Fm).count("1")) * L)
    best = None
    for al, be in stages.pinverts_ground(Fm, Dl):
        obj = al * c + sum(b * caps[A] for A, b in be)
        if best is None or obj < best:
            best = obj
    return best is not None and best <= 0


def check_game(rec):
    v0 = [F(t) for t in rec["v"]]
    T = F(rec["T"])
    v0 = [t / T for t in v0]                     # normalize T = 1
    x0 = [F(t) / T for t in rec["lmin"]]
    z0 = [F(t) / T for t in rec["lmax"]]
    sx, sz = audit.strata(x0), audit.strata(z0)
    ri = {i: k for k, b in enumerate(sx) for i in b}
    ci = {i: l for l, b in enumerate(sz) for i in b}
    A, B = len(sx), len(sz)
    tbl = [[0] * B for _ in range(A)]
    for i in range(N):
        tbl[ri[i]][ci[i]] += 1
    perm = [i for k in range(A) for l in range(B) for i in range(N)
            if ri[i] == k and ci[i] == l]
    v = relabel(v0, perm)
    x = [x0[i] for i in perm]
    z = [z0[i] for i in perm]
    rowmask = [sum(1 << n for n, i in enumerate(perm) if ri[i] == k)
               for k in range(A)]
    colmask = [sum(1 << n for n, i in enumerate(perm) if ci[i] == l)
               for l in range(B)]
    mu, M = min(x), max(z)
    out = {"lmin": [len(b) for b in sx], "lmax": [len(b) for b in sz],
           "tbl": tbl, "ratio": rec["ratio"]}
    fail = []
    if not (v[0] == 0 and all(v[1 << i] == 0 for i in range(N)) and v[FULL] == 1
            and all(v[S] >= 0 for S in range(32))):
        fail.append("H1")
    xS = lambda S: sum(x[i] for i in range(N) if S >> i & 1)
    zS = lambda S: sum(z[i] for i in range(N) if S >> i & 1)
    if any(v[S] > xS(S) for S in range(1, FULL)):
        fail.append("H2")
    if any(v[S] > zS(S) for S in range(1, FULL)):
        fail.append("H3")
    if any(v[S] > F(SZ[S]) * M or 1 - v[FULL ^ S] < F(SZ[S]) * mu
           for S in range(1, FULL)):
        fail.append("H4")
    D1, P = colmask[B - 1], rowmask[0]
    if not any(v[S] == F(SZ[S]) * M and SZ[S] >= 2 and (S & ~D1) == 0
               for S in range(1, FULL + 1)):
        fail.append("H4a")
    if not any(1 - v[FULL ^ S] == F(SZ[S]) * mu and (S & ~P) == 0
               for S in range(1, FULL + 1)):
        fail.append("H4b")
    st = {}
    for k in range(A):
        r = stage_ok(v, x, rowmask, k, ceiling=False)
        if r is not None:
            st[f"floor{k}"] = r
            if not r:
                fail.append(f"floor{k}")
    for l in range(B):
        r = stage_ok(v, z, colmask, l, ceiling=True)
        if r is not None:
            st[f"ceil{l}"] = r
            if not r:
                fail.append(f"ceil{l}")
    out["stages"] = st
    out["failures"] = fail
    return out


def main():
    d = json.load(open(f"{HERE}/harvest.json"))
    recs = d["records"]
    res = []
    bad = 0
    for i, r in enumerate(recs):
        a = check_game(r)
        res.append(a)
        if a["failures"]:
            bad += 1
            print(f"  FAILURE game {i}: lmin={a['lmin']} lmax={a['lmax']} "
                  f"tbl={a['tbl']} -> {a['failures']}", flush=True)
        if (i + 1) % 200 == 0:
            print(f"  {i+1}/{len(recs)} games, {bad} failures", flush=True)
    ncfg = len({(str(a["lmin"]), str(a["lmax"]), str(a["tbl"])) for a in res})
    nstage = sum(len(a["stages"]) for a in res)
    print(f"POSITIVE CONTROL: {len(res)} genuine exact games over {ncfg} "
          f"configurations, {nstage} stage certificates evaluated, "
          f"{bad} hypothesis failures (must be 0)")
    json.dump({"games": len(res), "configurations": ncfg,
               "stage_certificates": nstage, "failures": bad,
               "detail": res}, open(f"{HERE}/poscontrol.json", "w"), indent=1)


if __name__ == "__main__":
    main()
