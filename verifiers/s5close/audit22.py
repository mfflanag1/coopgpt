"""END-TO-END AUDIT of every feasible model produced by closecfg/closecfg2.

Campaign law: a feasible certificate is NOT a counterexample until the game is
rebuilt from the model and its Lmin, Lmax, strata and ratio are recomputed from
scratch.  Three certificate-not-realizable incidents have already occurred in
this program (task #16's T/16 games, task #20's 5/12 game, and the o2 ablation
models); assume a fourth until proved otherwise.

For each witness this recomputes, with verifiers/lib code and nothing from the
solver:
  * singleton-normalization and v(N) = 1;
  * exactness, by exact rational core-vertex enumeration (audit.is_exact);
  * Lmin (audit.lmin) and Lmax (lmax.lmax) by staged exact optimization;
  * the two stratum shapes, the position of the Lmax zeros inside the Lmin
    strata, mu, M, and the ratio;
  * whether the configuration the program assumed actually holds.

VERDICT per witness:
  REALIZABLE-COUNTEREXAMPLE : configuration matches AND ratio > target
  NOT-REALIZABLE            : the model is a game, but not in this configuration
  NOT-A-GAME                : the model is not exact / not normalized
usage: python3 audit22.py <file.json> [...]
"""
from __future__ import annotations
import glob
import json
import sys
from fractions import Fraction as F

HERE = sys.path[0]
sys.path.insert(0, HERE + "/lib")
import audit
import lmax as lmaxmod

N, FULL = 5, 31


def audit_one(rec):
    w = rec.get("witness")
    if not w:
        return None
    v = [F(t) for t in w["v"]]
    out = {"lmin_cfg": rec["lmin"], "lmax_cfg": rec["lmax"], "tbl": rec["tbl"],
           "target": rec["target"], "claimed_ratio": w["ratio"],
           "v": w["v"]}
    out["normalized"] = (v[0] == 0 and all(v[1 << i] == 0 for i in range(N))
                         and v[FULL] == 1)
    verts = audit.core_vertices(N, v)
    out["core_vertices"] = len(verts)
    out["exact"] = bool(verts) and audit.is_exact(N, v, verts)
    if not (out["normalized"] and out["exact"]):
        out["verdict"] = "NOT-A-GAME"
        return out
    x = audit.lmin(N, v)
    z = lmaxmod.lmax(N, v)
    sx = [len(b) for b in audit.strata(x)]
    sz = [len(b) for b in audit.strata(z)]
    ratio = sum(abs(x[i] - z[i]) for i in range(N))
    out.update({
        "Lmin": [str(t) for t in x], "Lmax": [str(t) for t in z],
        "lmin_shape": sx, "lmax_shape": sz,
        "mu": str(min(x)), "M": str(max(z)), "true_ratio": str(ratio),
    })
    # does the assumed configuration hold?  compare shapes and the overlap table
    A, B = len(rec["lmin"]), len(rec["lmax"])
    match = (sx == rec["lmin"] and sz == rec["lmax"])
    if match:
        ri = {i: k for k, b in enumerate(audit.strata(x)) for i in b}
        ci = {i: l for l, b in enumerate(audit.strata(z)) for i in b}
        tbl = [[0] * B for _ in range(A)]
        for i in range(N):
            tbl[ri[i]][ci[i]] += 1
        out["true_tbl"] = tbl
        match = (tbl == rec["tbl"])
    out["configuration_holds"] = match
    out["exceeds_target"] = ratio > F(rec["target"])
    out["verdict"] = ("REALIZABLE-COUNTEREXAMPLE"
                      if match and out["exceeds_target"] else "NOT-REALIZABLE")
    return out


def main():
    files = []
    for pat in sys.argv[1:]:
        files += sorted(glob.glob(pat))
    recs = []
    for fn in files:
        d = json.load(open(fn))
        recs += d if isinstance(d, list) else d.get("results", [])
    wits = [r for r in recs if r.get("feasible") and r.get("witness")]
    print(f"{len(recs)} records, {len(wits)} feasible witnesses to audit",
          flush=True)
    res = []
    for i, r in enumerate(wits):
        a = audit_one(r)
        res.append(a)
        print(f"  [{i+1}/{len(wits)}] lmin={r['lmin']} lmax={r['lmax']} "
              f"tbl={r['tbl']} -> {a['verdict']} "
              f"(true shapes {a.get('lmin_shape')}/{a.get('lmax_shape')}, "
              f"true ratio {a.get('true_ratio')})", flush=True)
    ce = [a for a in res if a["verdict"] == "REALIZABLE-COUNTEREXAMPLE"]
    print(f"AUDIT DONE: {len(res)} witnesses, {len(ce)} realizable "
          f"counterexamples, "
          f"{sum(1 for a in res if a['verdict']=='NOT-REALIZABLE')} "
          f"not realizable, "
          f"{sum(1 for a in res if a['verdict']=='NOT-A-GAME')} not games")
    json.dump(res, open(f"{HERE}/audit22.json", "w"), indent=1)


if __name__ == "__main__":
    main()
