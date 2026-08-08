"""Second pass: re-run, with the FULL multi-stage pinning ladders of
closecfg2, every configuration that survived the single-stage pass of batch.py.

usage: python3 batch2.py <target> <nshards> <shard> [--controls]
"""
from __future__ import annotations
import glob
import json
import sys
import time
from fractions import Fraction as F

HERE = sys.path[0]
sys.path.insert(0, HERE)
sys.path.insert(0, HERE + "/lib")
from cone import inequalities
import closecfg2


def main():
    target = F(sys.argv[1])
    nsh, sh = int(sys.argv[2]), int(sys.argv[3])
    controls = "--controls" in sys.argv
    tag = str(target).replace("/", "_")
    todo = []
    for fn in sorted(glob.glob(f"{HERE}/batch_{tag}_*.json")):
        todo += [x for x in json.load(open(fn)) if x.get("feasible")]
    todo.sort(key=lambda x: (x["lmin"], x["lmax"], x["tbl"]))
    mine = [x for i, x in enumerate(todo) if i % nsh == sh]
    print(f"target={target} shard {sh}/{nsh}: {len(mine)} of {len(todo)} "
          f"survivors", flush=True)
    ineqs = inequalities(5)
    out, path = [], f"{HERE}/batch2_{tag}_{sh}.json"
    for i, cfgd in enumerate(mine):
        r, c, tbl = tuple(cfgd["lmin"]), tuple(cfgd["lmax"]), cfgd["tbl"]
        t0 = time.time()
        try:
            res = closecfg2.check2(r, c, tbl, target, ineqs, controls=controls)
            res["error"] = None
        except Exception as e:
            res = {"lmin": list(r), "lmax": list(c), "tbl": tbl,
                   "target": str(target), "error": f"{type(e).__name__}: {e}"}
        res["seconds"] = round(time.time() - t0, 1)
        out.append(res)
        json.dump(out, open(path, "w"), indent=1)
        print(f"  [{sh}] {i+1}/{len(mine)} lmin={r} lmax={c} tbl={tbl} "
              f"feasible={res.get('feasible')} stages={res.get('stages')} "
              f"err={res['error']} {res['seconds']}s", flush=True)
    print(f"SHARD2 {sh} DONE: {len(out)} configurations, "
          f"{sum(1 for x in out if x.get('feasible'))} still FEASIBLE, "
          f"{sum(1 for x in out if x['error'])} errors")


if __name__ == "__main__":
    main()
