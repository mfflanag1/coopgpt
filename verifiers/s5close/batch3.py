"""Independent re-derivation over ALL 2961 configurations with closecfg3.

Because the Theorem A / Theorem B encoding needs no lazy cut loop and no vertex
disjunctions, it is fast enough to run on the whole universe rather than only
on the residue the arithmetic triage leaves.  So this pass does not inherit the
triage's case split at all: it re-derives every configuration from scratch,
including the 1953 that L1' calls impossible and the 800 the arithmetic closes.

Verdicts are compared against the closecfg2 pipeline afterwards (compare3.py).

usage: python3 batch3.py <target> <nshards> <shard> [--controls] [--no-anchors]
"""
from __future__ import annotations
import json
import sys
import time
from fractions import Fraction as F

HERE = sys.path[0]
sys.path.insert(0, HERE)
sys.path.insert(0, HERE + "/lib")
import arith22
import closecfg3


def main():
    target = F(sys.argv[1])
    nsh, sh = int(sys.argv[2]), int(sys.argv[3])
    controls = "--controls" in sys.argv
    anchors = "--no-anchors" not in sys.argv
    todo = []
    for r in arith22.compositions(5):
        for c in arith22.compositions(5):
            for tbl in arith22.tables(r, c):
                todo.append((r, c, tbl))
    mine = [t for i, t in enumerate(todo) if i % nsh == sh]
    tag = str(target).replace("/", "_") + ("" if anchors else "_noanch")
    print(f"target={target} anchors={anchors} shard {sh}/{nsh}: "
          f"{len(mine)} of {len(todo)} configurations", flush=True)
    out, path = [], f"{HERE}/batch3_{tag}_{sh}.json"
    t0 = time.time()
    for i, (r, c, tbl) in enumerate(mine):
        try:
            res = closecfg3.check3(r, c, tbl, target, controls=controls,
                                   anchors=anchors)
            res["error"] = None
        except Exception as e:
            res = {"lmin": list(r), "lmax": list(c), "tbl": tbl,
                   "error": f"{type(e).__name__}: {e}"}
        out.append(res)
        if (i + 1) % 25 == 0 or i + 1 == len(mine):
            json.dump(out, open(path, "w"), indent=1)
            print(f"  [{sh}] {i+1}/{len(mine)} feasible so far "
                  f"{sum(1 for x in out if x.get('feasible'))} "
                  f"({round(time.time()-t0)}s)", flush=True)
    json.dump(out, open(path, "w"), indent=1)
    print(f"SHARD3 {sh} DONE: {len(out)} configurations, "
          f"{sum(1 for x in out if x.get('feasible'))} FEASIBLE, "
          f"{sum(1 for x in out if x.get('error'))} errors")


if __name__ == "__main__":
    main()
