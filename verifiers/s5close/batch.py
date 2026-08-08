"""Batch runner for closecfg.check over the configurations left open by the
arithmetic triage (arith22.py).

Discharges: the exhaustive sweep behind "every configuration obeys ratio <= R".
Shards by index so several processes can run in parallel; each shard
checkpoints after every configuration.

usage: python3 batch.py <target> <nshards> <shard> [--controls]
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
import closecfg


def main():
    target = F(sys.argv[1])
    nsh, sh = int(sys.argv[2]), int(sys.argv[3])
    controls = "--controls" in sys.argv
    tag = str(target).replace("/", "_")
    src = json.load(open(f"{HERE}/arith22_{tag}.json"))
    todo = [x for x in src["results"] if x["verdict"] == "open"]
    mine = [x for i, x in enumerate(todo) if i % nsh == sh]
    print(f"target={target} shard {sh}/{nsh}: {len(mine)} of {len(todo)} open "
          f"configurations{' (with controls)' if controls else ''}", flush=True)
    ineqs = inequalities(5)
    out, path = [], f"{HERE}/batch_{tag}_{sh}.json"
    for i, cfgd in enumerate(mine):
        r = tuple(cfgd["lmin"])
        c = tuple(cfgd["lmax"])
        tbl = cfgd["tbl"]
        t0 = time.time()
        try:
            res = closecfg.check(r, c, tbl, target, ineqs, controls=controls)
            res["error"] = None
        except Exception as e:                     # record, never swallow
            res = {"lmin": list(r), "lmax": list(c), "tbl": tbl,
                   "target": str(target), "error": f"{type(e).__name__}: {e}"}
        res["seconds"] = round(time.time() - t0, 1)
        res["mu_hi_arith"] = cfgd.get("mu_hi")
        out.append(res)
        json.dump(out, open(path, "w"), indent=1)
        print(f"  [{sh}] {i+1}/{len(mine)} lmin={r} lmax={c} tbl={tbl} "
              f"feasible={res.get('feasible')} err={res['error']} "
              f"{res['seconds']}s", flush=True)
    nf = sum(1 for x in out if x.get("feasible"))
    print(f"SHARD {sh} DONE: {len(out)} configurations, {nf} FEASIBLE, "
          f"{sum(1 for x in out if x['error'])} errors")


if __name__ == "__main__":
    main()
