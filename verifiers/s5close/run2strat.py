"""Re-run, under the FULL multi-stage ladders of closecfg2, the 17 arithmetically
open configurations whose Lmin has at most two strata -- the ones that carry
Theorem T1.

The single-stage pass (batch.py / closecfg.py) already returned UNSAT for all
17, and UNSAT under a weaker hypothesis set implies UNSAT under a stronger one,
so T1 does not depend on this run.  Its purpose is the CLASSIFICATION: with the
full ladders the positive control (C-pos) separates the configurations that are
merely BOUNDED from the ones that are outright IMPOSSIBLE, and only the full
ladders give that split correctly.

usage: python3 run2strat.py <shard> <nshards>
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

TARGET = F(1, 2)


def main():
    sh, nsh = int(sys.argv[1]), int(sys.argv[2])
    src = json.load(open(f"{HERE}/arith22_1_2.json"))["results"]
    todo = [x for x in src if x["verdict"] == "open" and len(x["lmin"]) <= 2]
    mine = [x for i, x in enumerate(todo) if i % nsh == sh]
    print(f"two-stratum Lmin, target 1/2, full ladders: shard {sh}/{nsh}, "
          f"{len(mine)} of {len(todo)}", flush=True)
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
        json.dump(out, open(f"{HERE}/run2strat_{sh}.json", "w"), indent=1)
        print(f"  [{sh}] {i+1}/{len(mine)} lmin={r} lmax={c} tbl={tbl} "
              f"feasible={res.get('feasible')} "
              f"dropctl={res.get('control_drop_pinning_feasible')} "
              f"posctl={res.get('control_positive_feasible')} "
              f"stages={res.get('stages')} err={res['error']} "
              f"{res['seconds']}s", flush=True)
    print(f"RUN2STRAT SHARD {sh} DONE: "
          f"{sum(1 for x in out if x.get('feasible'))} feasible of {len(out)}")


if __name__ == "__main__":
    main()
