"""Do the two independent pipelines agree on every configuration?

PIPELINE 1 (closecfg / closecfg2): 280-facet exactness + pinning ladders
           dualized over enumerated vertices, with reduced-game preimage minima.
PIPELINE 2 (closecfg3):            Theorem A exactness + Theorem B / mirror
           Farkas identities, no catalogue and no vertex enumeration.

They share only the configuration layout, the core memberships and the two A3
anchor disjunctions.  Anywhere they disagree, at least one is wrong.
"""
from __future__ import annotations
import glob
import json
import sys

HERE = sys.path[0]
sys.path.insert(0, HERE)
import arith22


def K(lmin, lmax, tbl):
    return (tuple(lmin), tuple(lmax), tuple(map(tuple, tbl)))


def load(pat):
    out = []
    for fn in sorted(glob.glob(f"{HERE}/{pat}")):
        d = json.load(open(fn))
        out += d if isinstance(d, list) else d.get("results", [])
    return out


def main():
    universe = set()
    for r in arith22.compositions(5):
        for c in arith22.compositions(5):
            for tbl in arith22.tables(r, c):
                universe.add(K(r, c, tbl))

    p1 = {}
    for x in json.load(open(f"{HERE}/arith22_1_2.json"))["results"]:
        k = K(x["lmin"], x["lmax"], x["tbl"])
        if x["verdict"] == "no-anchor":
            p1[k] = "L1-impossible"
        elif x["verdict"] == "closed":
            p1[k] = "UNSAT"
    for x in load("batch_1_2_*.json"):
        k = K(x["lmin"], x["lmax"], x["tbl"])
        p1[k] = "UNSAT" if x.get("feasible") is False else "SAT"
    for x in load("batch2_1_2_*.json"):          # pass 2 overrides pass 1
        k = K(x["lmin"], x["lmax"], x["tbl"])
        p1[k] = "UNSAT" if x.get("feasible") is False else "SAT"

    p2 = {}
    for x in load("batch3_1_2_[0-9]*.json"):      # NOT the _noanch files
        k = K(x["lmin"], x["lmax"], x["tbl"])
        p2[k] = ("L1-impossible" if x.get("error")
                 else ("UNSAT" if x["feasible"] is False else "SAT"))

    missing1 = universe - set(p1)
    missing2 = universe - set(p2)
    disagree = [(k, p1[k], p2[k]) for k in universe
                if k in p1 and k in p2 and p1[k] != p2[k]]
    both_unsat = sum(1 for k in universe if p1.get(k) == p2.get(k) == "UNSAT")
    both_l1 = sum(1 for k in universe
                  if p1.get(k) == p2.get(k) == "L1-impossible")
    print(f"universe {len(universe)}")
    print(f"  pipeline 1 covered {len(p1)}, missing {len(missing1)}")
    print(f"  pipeline 2 covered {len(p2)}, missing {len(missing2)}")
    print(f"  agree UNSAT          : {both_unsat}")
    print(f"  agree L1-impossible  : {both_l1}")
    print(f"  DISAGREEMENTS        : {len(disagree)}")
    for k, a, b in disagree[:10]:
        print(f"     {k}: pipeline1={a} pipeline2={b}")
    ok = (not disagree and not missing1 and not missing2
          and both_unsat + both_l1 == len(universe))
    json.dump({"universe": len(universe), "agree_unsat": both_unsat,
               "agree_L1_impossible": both_l1,
               "disagreements": [[list(map(list, k)), a, b]
                                 for k, a, b in disagree],
               "passed": ok},
              open(f"{HERE}/compare3.json", "w"), indent=1)
    print("PIPELINES AGREE ON EVERY CONFIGURATION" if ok
          else "MISMATCH -- see compare3.json")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
