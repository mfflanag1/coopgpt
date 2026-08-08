"""The (4,1) Lmin regime at the sharper target ratio <= 1/3.

Discharges the target named in the task brief: "(4,1) Lmin regime, target
ratio <= 1/3".  Runs closecfg2 (full multi-stage ladders) with target 1/3 on
exactly the (4,1) configurations that the arithmetic triage leaves open at
1/3, with both controls.

usage: python3 run41.py <shard> <nshards>
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

TARGET = F(1, 3)


def main():
    sh, nsh = int(sys.argv[1]), int(sys.argv[2])
    src = json.load(open(f"{HERE}/arith22_1_3.json"))["results"]
    todo = [x for x in src if x["verdict"] == "open" and x["lmin"] == [4, 1]]
    mine = [x for i, x in enumerate(todo) if i % nsh == sh]
    print(f"(4,1) regime, target 1/3: shard {sh}/{nsh}, "
          f"{len(mine)} of {len(todo)} open configurations", flush=True)
    ineqs = inequalities(5)
    out = []
    for i, cfgd in enumerate(mine):
        r, c, tbl = tuple(cfgd["lmin"]), tuple(cfgd["lmax"]), cfgd["tbl"]
        t0 = time.time()
        try:
            res = closecfg2.check2(r, c, tbl, TARGET, ineqs, controls=True)
            res["error"] = None
        except Exception as e:
            res = {"lmin": list(r), "lmax": list(c), "tbl": tbl,
                   "error": f"{type(e).__name__}: {e}"}
        res["seconds"] = round(time.time() - t0, 1)
        res["mu_hi_arith"] = cfgd.get("mu_hi")
        out.append(res)
        json.dump(out, open(f"{HERE}/run41_{sh}.json", "w"), indent=1)
        print(f"  [{sh}] {i+1}/{len(mine)} lmax={c} tbl={tbl} "
              f"feasible={res.get('feasible')} "
              f"dropctl={res.get('control_drop_pinning_feasible')} "
              f"posctl={res.get('control_positive_feasible')} "
              f"err={res['error']} {res['seconds']}s", flush=True)
    print(f"RUN41 SHARD {sh} DONE: "
          f"{sum(1 for x in out if x.get('feasible'))} feasible of {len(out)}")


if __name__ == "__main__":
    main()
