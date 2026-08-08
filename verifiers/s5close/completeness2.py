"""Positive control with teeth, at the EXTREMAL configurations.

completeness.py does this for the three-or-more-stratum configurations.  This
one does it where it matters most: CFG itself, which carries ratio exactly 1/2,
and the (3,2) x (1,2,2) configuration, which the harvest reaches at 4/9.  Run
just below each observed maximum, the program must be SAT and its witness must
audit as a genuine exact game in that very configuration above the target.

If the encoding were accidentally too strong -- an over-tight pinning, a wrong
preimage minimum, a mis-stated anchor -- these are the cases where it would
show, because here the true answer is known to be positive.
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
    ((3, 2), (1, 4), [[1, 2], [0, 2]], "1/2", "4/9"),        # CFG
    ((3, 2), (1, 2, 2), [[1, 2, 0], [0, 0, 2]], "4/9", "2/5"),
    ((4, 1), (1, 4), [[1, 3], [0, 1]], "1/3", "3/10"),
    ((4, 1), (2, 3), [[2, 2], [0, 1]], "1/3", "3/10"),
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
        json.dump(out, open(f"{HERE}/completeness2.json", "w"), indent=1)
    ok = all(x["feasible"] and (x.get("audit") or {}).get("verdict")
             == "REALIZABLE-COUNTEREXAMPLE" for x in out)
    print("EXTREMAL CONFIGURATIONS ARE REALIZED BY THE ENCODING" if ok
          else "SOME CASE FAILED -- see completeness2.json")


if __name__ == "__main__":
    main()
