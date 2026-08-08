"""POSITIVE CONTROL WITH TEETH: does the encoding of closecfg2 actually FIND
real games when they exist, at a target the configuration is known to beat?

The controls in closecfg2 only show the hypothesis set is satisfiable.  This is
much stronger: for configurations where the harvest produced a genuine exact
game of ratio R_obs, the program is run at a target R < R_obs.  It MUST come
out SAT, and its witness MUST audit end-to-end as a genuine exact game in that
very configuration with ratio > R.  If it did, the encoding is not merely
sound but tight enough to realize the configurations it describes -- which is
what makes an UNSAT verdict elsewhere meaningful rather than an artefact of a
missing hypothesis.

The three cases below are the highest-ratio configurations in the harvest that
are NOT in the two-stratum-Lmin class of Theorem T1.
"""
from __future__ import annotations
import json
import sys
import time
from fractions import Fraction as F

HERE = sys.path[0]
sys.path.insert(0, HERE)
sys.path.insert(0, HERE + "/lib")
from cone import inequalities
import closecfg2
import audit22

CASES = [
    # (lmin, lmax, tbl, observed ratio, target strictly below it)
    ((2, 1, 2), (1, 1, 3), [[1, 1, 0], [0, 0, 1], [0, 0, 2]], "10/27", "1/3"),
    ((3, 1, 1), (1, 4), [[1, 2], [0, 1], [0, 1]], "1/3", "3/10"),
    ((1, 2, 2), (1, 4), [[1, 0], [0, 2], [0, 2]], "1/3", "3/10"),
    ((2, 1, 2), (1, 1, 1, 2), [[1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 2]],
     "1/4", "1/5"),
]


def main():
    ineqs = inequalities(5)
    out = []
    for r, c, tbl, obs, tgt in CASES:
        t0 = time.time()
        res = closecfg2.check2(r, c, tbl, F(tgt), ineqs)
        res["observed_ratio"] = obs
        res["seconds"] = round(time.time() - t0, 1)
        if res["feasible"]:
            res["audit"] = audit22.audit_one(res)
        out.append(res)
        a = res.get("audit") or {}
        print(f"  lmin={r} lmax={c} target={tgt} (observed {obs}): "
              f"feasible={res['feasible']} audit={a.get('verdict')} "
              f"true_ratio={a.get('true_ratio')} "
              f"cfg_holds={a.get('configuration_holds')} {res['seconds']}s",
              flush=True)
        json.dump(out, open(f"{HERE}/completeness.json", "w"), indent=1)
    ok = all(x["feasible"] and (x.get("audit") or {}).get("verdict")
             == "REALIZABLE-COUNTEREXAMPLE" for x in out)
    print("ENCODING REALIZES ITS CONFIGURATIONS" if ok
          else "SOME CASE FAILED -- see completeness.json")


if __name__ == "__main__":
    main()
