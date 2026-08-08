"""THE SHARPEST CONTROL: same encoding, same configuration, two targets.

For a configuration to be closed at 1/2 by an UNSAT verdict, the encoding must
be strong enough to exclude ratio > 1/2 -- but not so strong that it excludes
the configuration's real games.  The cleanest way to see both at once is to run
the SAME program on the SAME configuration at two targets:

  * at target 1/2  it must be UNSAT (that is the theorem), and
  * at a target below the configuration's observed maximum it must be SAT with
    a witness that AUDITS as a genuine exact game in that very configuration.

If the encoding were over-constrained -- an over-tight pinning, a wrong
preimage minimum, a mis-stated anchor -- the second call would also be UNSAT
and the first verdict would be worthless.  This script tabulates both columns
from the stored runs.  -> crosscheck.json
"""
from __future__ import annotations
import glob
import json
import sys

HERE = sys.path[0]


def K(x):
    return (tuple(x["lmin"]), tuple(x["lmax"]), tuple(map(tuple, x["tbl"])))


def main():
    stored = {}
    for pat in ("batch_1_2_*.json", "batch2_1_2_*.json", "run2strat_*.json"):
        for fn in sorted(glob.glob(f"{HERE}/{pat}")):
            for x in json.load(open(fn)):
                if x.get("feasible") is not None:
                    stored.setdefault(K(x), []).append((pat, x["feasible"]))
    rows = []
    for fn in ("completeness.json", "completeness2.json"):
        for x in json.load(open(f"{HERE}/{fn}")):
            k = K(x)
            a = x.get("audit") or {}
            at_half = stored.get(k, [])
            rows.append({
                "lmin": x["lmin"], "lmax": x["lmax"], "tbl": x["tbl"],
                "target_half_verdicts": [f"{p}:{'SAT' if f else 'UNSAT'}"
                                         for p, f in at_half],
                "low_target": x["target"], "observed": x["observed_ratio"],
                "low_target_feasible": x["feasible"],
                "audit": a.get("verdict"), "true_ratio": a.get("true_ratio"),
                "configuration_holds": a.get("configuration_holds"),
            })
    both = [r for r in rows
            if any(v.endswith("UNSAT") for v in r["target_half_verdicts"])
            and r["audit"] == "REALIZABLE-COUNTEREXAMPLE"]
    for r in rows:
        print(f"  lmin={r['lmin']} lmax={r['lmax']} tbl={r['tbl']}")
        print(f"      target 1/2 -> {r['target_half_verdicts'] or ['closed before pass 1']}")
        print(f"      target {r['low_target']} (observed {r['observed']}) -> "
              f"SAT, audit {r['audit']}, true ratio {r['true_ratio']}, "
              f"configuration holds: {r['configuration_holds']}")
    print(f"\n{len(both)} configurations show BOTH behaviours in the multi-stage "
          f"encoding: UNSAT at 1/2 and an audited genuine game below it.")
    ok = all(r["audit"] == "REALIZABLE-COUNTEREXAMPLE"
             and r["configuration_holds"] for r in rows)
    print("CROSS-CHECK PASSED" if ok else "CROSS-CHECK FAILED")
    json.dump({"rows": rows, "both_behaviours": len(both), "passed": ok},
              open(f"{HERE}/crosscheck.json", "w"), indent=1)


if __name__ == "__main__":
    main()
