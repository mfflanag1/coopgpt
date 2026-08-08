"""How far do lemmas L1 and L2 get on their own, with no LP and no game data.

Discharges: the two corollaries reported as PROVED in PROOF.txt sections L1-L2,
and quantifies how many of the 2961 (Lmin-shape, Lmax-shape, overlap) triples
each lemma kills by itself.

 F1 (from L1)  the Lmax top stratum has >= 2 players, so every configuration
               whose Lmax composition ends in 1 is impossible.
 F2 (from L2)  mu >= min_{i in P} Lmax_i, where P is the Lmin bottom stratum;
               combined with mu <= T/5 this says the Lmin bottom stratum must
               contain a player whose Lmax payoff is at most T/5.  Applied to
               the (1,4)-with-zero Lmax shape it forces the starved player to
               be Lmin-POOR, settling the hypothesis left open as scope item
               E3 of records/S5PROOF.txt and in paper5 section sec:scope.

F2 is applied here as an exact feasibility test on the level variables only
(no v, no anchors): levels ordered and summing to 1, plus mu >= min_{i in P} z_i.
"""
from __future__ import annotations
import json
import sys
from fractions import Fraction as F

import z3

HERE = sys.path[0]
sys.path.insert(0, HERE)
import arith22

N = 5


def f2_kills(r, c, tbl):
    """True if levels + (mu >= min_{i in P} z_i) is already infeasible."""
    A, B = len(r), len(c)
    m = [z3.Real(f"m{k}") for k in range(A)]
    Mv = [z3.Real(f"M{l}") for l in range(B)]
    s = z3.Solver()
    s.add(m[0] >= 0, Mv[0] >= 0)
    s.add(z3.Sum([arith22.q(r[k]) * m[k] for k in range(A)]) == 1)
    s.add(z3.Sum([arith22.q(c[l]) * Mv[l] for l in range(B)]) == 1)
    s += [m[k] < m[k + 1] for k in range(A - 1)]
    s += [Mv[l] < Mv[l + 1] for l in range(B - 1)]
    # the Lmax levels present in the Lmin bottom stratum (row 0)
    lv = [l for l in range(B) if tbl[0][l]]
    s.add(z3.Or([m[0] >= Mv[l] for l in lv]))        # mu >= min over them
    res = s.check()
    assert res in (z3.sat, z3.unsat)
    return res == z3.unsat


def main():
    comps = arith22.compositions(N)
    tot = f1 = f2 = both = 0
    killed14 = []
    for r in comps:
        for c in comps:
            for tbl in arith22.tables(r, c):
                tot += 1
                a = (c[-1] == 1)
                b = f2_kills(r, c, tbl)
                f1 += a
                f2 += b
                both += (a or b)
                if b and not a and c == (1, 4):
                    killed14.append((r, c, tbl))
    print(f"{tot} configurations")
    print(f"  killed by F1 (Lmax top stratum singleton) : {f1}")
    print(f"  killed by F2 (mu >= min_P Lmax)           : {f2}")
    print(f"  killed by F1 or F2                        : {both}")
    print(f"  (1,4)-Lmax configurations killed by F2 alone: {len(killed14)}")
    for r, c, tbl in killed14:
        print(f"     lmin={r} lmax={c} tbl={tbl}")
    json.dump({"total": tot, "F1": f1, "F2": f2, "F1_or_F2": both,
               "lmax14_killed_by_F2": [[list(r), list(c), t]
                                       for r, c, t in killed14]},
              open(f"{HERE}/l2filter.json", "w"), indent=1)


if __name__ == "__main__":
    main()
