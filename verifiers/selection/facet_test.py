"""Is a packet system a FACET of the exact cone exactly when it is full-trace?

Enumerates every abstract packet system with delta>0 for the given (m,h) --
using only the forced structural constraints of sel/enum_packets.py -- and
classifies each permutational type with the independent classifier sbcheck.
"""
from __future__ import annotations

import json
import sys

SCR = "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad"
sys.path.insert(0, SCR)
sys.path.insert(0, SCR + "/sel")
import catalogue
import sbcheck
from enum_packets import enumerate_packets, nm


def main():
    cases = [(5, 4, 1), (5, 3, 2), (6, 5, 1), (6, 4, 2), (6, 3, 3), (6, 2, 4)]
    if len(sys.argv) > 1:
        cases = [tuple(int(x) for x in a.split(",")) for a in sys.argv[1:]]
    out = []
    for n, m, h in cases:
        table, _ = catalogue.index(n) if n <= 6 else (None, None)
        Hmask = sum(1 << i for i in range(m, n))
        pks = enumerate_packets(n, Hmask)
        by = {}
        for p in pks:
            by.setdefault(catalogue.canon(n, p["lam"]), []).append(p)
        print(f"\n=== n={n} (m,h)=({m},{h}) : {len(pks)} packets, {len(by)} types ===")
        rec = []
        for key, grp in sorted(by.items(), key=lambda kv: -len(kv[1])):
            p = grp[0]
            ft = all(g["full_trace"] for g in grp)
            anyft = any(g["full_trace"] for g in grp)
            verdict, wit = sbcheck.classify(n, list(p["lam"]))
            rows = table.get(key) if table else None
            kind = "FULL-TRACE" if ft else ("MIXED" if anyft else "SPLIT")
            print(f"  {kind:10s} {catalogue.pretty(n, p['lam']):46s} "
                  f"{verdict:34s} rows={rows if rows else '-'}")
            rec.append({"system": catalogue.pretty(n, p["lam"]), "kind": kind,
                        "verdict": verdict, "rows": rows, "count": len(grp)})
        agree = all((r["kind"] == "FULL-TRACE") ==
                    r["verdict"].startswith("indecomposable") for r in rec)
        print(f"  full-trace <=> facet-defining : {agree}")
        out.append({"n": n, "m": m, "h": h, "types": rec, "equivalence": agree})
    with open(f"{SCR}/sel/facet_test.json", "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
