"""COVERAGE AUDIT: is every one of the 2961 configurations actually accounted
for, by name, exactly once?

This is the bookkeeping step on which the main theorem rests, so it is checked
mechanically rather than by adding up numbers in a report.  It verifies:
  1. the configuration universe is the full set of (Lmin composition, Lmax
     composition, overlap table) triples;
  2. every triple lands in exactly one bucket -- impossible by L1', closed by
     the arithmetic, closed by the single-stage check, closed by the
     multi-stage check;
  3. the set of triples run in pass 1 is EXACTLY the arithmetic's open set;
  4. the set run in pass 2 is EXACTLY pass 1's feasible set;
  5. no run reported an error, and none is left feasible.
Any mismatch is printed and the exit status is nonzero.
"""
from __future__ import annotations
import glob
import json
import sys

HERE = sys.path[0]
sys.path.insert(0, HERE)
import arith22


def K(lmin, lmax, tbl):
    return (tuple(lmin), tuple(lmax), tuple(tuple(r) for r in tbl))


def load(pat):
    out = []
    for fn in sorted(glob.glob(f"{HERE}/{pat}")):
        d = json.load(open(fn))
        out += d if isinstance(d, list) else d.get("results", [])
    return out


def main():
    bad = []
    universe = set()
    for r in arith22.compositions(5):
        for c in arith22.compositions(5):
            for tbl in arith22.tables(r, c):
                universe.add(K(r, c, tbl))
    print(f"universe: {len(universe)} configurations")

    ar = json.load(open(f"{HERE}/arith22_1_2.json"))["results"]
    arK = {K(x["lmin"], x["lmax"], x["tbl"]): x for x in ar}
    if set(arK) != universe:
        bad.append(f"arith universe mismatch: {len(set(arK) ^ universe)} differ")
    impossible = {k for k, x in arK.items() if x["verdict"] == "no-anchor"}
    arclosed = {k for k, x in arK.items() if x["verdict"] == "closed"}
    aropen = {k for k, x in arK.items() if x["verdict"] == "open"}
    # the impossibility reason must be exactly L1' (Lmax top stratum singleton)
    mis = {k for k in impossible if k[1][-1] != 1}
    if mis:
        bad.append(f"{len(mis)} 'no-anchor' configurations are NOT explained "
                   f"by L1'")
    mis2 = {k for k in universe if k[1][-1] == 1} - impossible
    if mis2:
        bad.append(f"{len(mis2)} L1'-impossible configurations were not "
                   f"marked no-anchor")
    print(f"  impossible by L1' : {len(impossible)}")
    print(f"  closed by arith   : {len(arclosed)}")
    print(f"  open after arith  : {len(aropen)}")

    p1 = load("batch_1_2_*.json")
    p1K = {K(x["lmin"], x["lmax"], x["tbl"]): x for x in p1}
    if len(p1) != len(p1K):
        bad.append(f"pass 1 has duplicates: {len(p1)} records, {len(p1K)} keys")
    if set(p1K) != aropen:
        bad.append(f"pass 1 set != arith open set "
                   f"(missing {len(aropen - set(p1K))}, "
                   f"extra {len(set(p1K) - aropen)})")
    p1err = [k for k, x in p1K.items() if x.get("error")]
    p1feas = {k for k, x in p1K.items() if x.get("feasible")}
    p1unsat = {k for k, x in p1K.items() if x.get("feasible") is False}
    print(f"  pass 1 run {len(p1K)}: {len(p1unsat)} UNSAT, {len(p1feas)} "
          f"feasible, {len(p1err)} errors")
    if p1err:
        bad.append(f"pass 1 errors: {p1err[:3]}")

    p2 = load("batch2_1_2_*.json")
    p2K = {K(x["lmin"], x["lmax"], x["tbl"]): x for x in p2}
    if len(p2) != len(p2K):
        bad.append(f"pass 2 has duplicates: {len(p2)} records, {len(p2K)} keys")
    if set(p2K) != p1feas:
        bad.append(f"pass 2 set != pass 1 feasible set "
                   f"(missing {len(p1feas - set(p2K))}, "
                   f"extra {len(set(p2K) - p1feas)})")
    p2err = [k for k, x in p2K.items() if x.get("error")]
    p2feas = {k for k, x in p2K.items() if x.get("feasible")}
    p2unsat = {k for k, x in p2K.items() if x.get("feasible") is False}
    print(f"  pass 2 run {len(p2K)}: {len(p2unsat)} UNSAT, {len(p2feas)} "
          f"feasible, {len(p2err)} errors")
    if p2err:
        bad.append(f"pass 2 errors: {p2err[:3]}")
    if p2feas:
        bad.append(f"{len(p2feas)} configurations still feasible after pass 2")

    covered = impossible | arclosed | p1unsat | p2unsat
    missing = universe - covered
    overlap = (len(impossible) + len(arclosed) + len(p1unsat) + len(p2unsat)
               - len(covered))
    print(f"  covered: {len(covered)} = {len(impossible)} + {len(arclosed)} "
          f"+ {len(p1unsat)} + {len(p2unsat)}  (overlap {overlap})")
    if missing:
        bad.append(f"{len(missing)} configurations NOT covered, e.g. "
                   f"{list(missing)[:3]}")
    if overlap:
        bad.append(f"buckets overlap by {overlap}")

    out = {"universe": len(universe), "impossible_L1": len(impossible),
           "arith_closed": len(arclosed), "pass1_unsat": len(p1unsat),
           "pass2_unsat": len(p2unsat), "covered": len(covered),
           "missing": len(missing), "problems": bad}
    json.dump(out, open(f"{HERE}/coverage.json", "w"), indent=1)
    if bad:
        print("COVERAGE AUDIT FAILED:")
        for b in bad:
            print("  -", b)
        sys.exit(1)
    print("COVERAGE AUDIT PASSED: every configuration accounted for exactly "
          "once, no errors, none feasible.")


if __name__ == "__main__":
    main()
