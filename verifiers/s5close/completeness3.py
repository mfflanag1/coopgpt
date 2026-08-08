"""Positive control WITH TEETH for the independent (Theorem A + Theorem B)
encoding, in the ceiling/leximax setting.

Task #23's Theorem B was controlled on the FLOOR/leximin side only.  The mirror
derived in farkas.py is new, so closecfg3 needs its own controls before any of
its verdicts count.  farkas.py supplies the pointwise ones (true Lmax accepted,
Lmin-as-Lmax and the Lmin/Lmax midpoint rejected, on 1050 games).  This supplies
the end-to-end one: on the eight configurations where a genuine game above a
target is known, closecfg3 must return SAT and its witness must audit as a real
exact game in that very configuration.

If the mirror were mis-derived in the strengthening direction, these would come
out UNSAT and every closecfg3 UNSAT elsewhere would be worthless.
"""
from __future__ import annotations
import json
import sys
import time
from fractions import Fraction as F

HERE = sys.path[0]
sys.path.insert(0, HERE)
sys.path.insert(0, HERE + "/lib")
import closecfg3
import audit22
from completeness import CASES as C1
from completeness2 import CASES as C2


def main():
    out = []
    for r, c, tbl, obs, tgt in list(C1) + list(C2):
        t0 = time.time()
        res = closecfg3.check3(r, c, tbl, F(tgt))
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
        json.dump(out, open(f"{HERE}/completeness3.json", "w"), indent=1)
    ok = all(x["feasible"] and (x.get("audit") or {}).get("verdict")
             == "REALIZABLE-COUNTEREXAMPLE" for x in out)
    print("INDEPENDENT ENCODING REALIZES ITS CONFIGURATIONS" if ok
          else "SOME CASE FAILED -- see completeness3.json")


if __name__ == "__main__":
    main()
