"""THE THREE-DIMENSIONAL NORMAL FORM for PART at m = 3, and the cone-level
case enumeration that the hand proof of Theorem D is built on.

Discharges: the combinatorial half of PROOF_M3.txt.  Everything here is about
CONES ONLY -- no game values appear -- so each answer is a statement about set
systems and holds at every boundary of every exact game.

THE NORMAL FORM (proved in PROOF_M3.txt Lemma N).  Let v be exact and
singleton-normalized on N = {a,b,c,f,g} with a PART(1,2) configuration at
H = {f,g}: S1 = af and S2 = bcg tight.  By block rigidity every core point has
x(af) = v(af) and x(bcg) = v(bcg), so writing

      u = x_a - phi_a,   v_b = x_b - phi_b,   v_c = x_c - phi_c,

the core is a 3-dimensional polytope K in (u, v_b, v_c) containing the origin,
with x_f - phi_f = -u and x_g - phi_g = -(v_b + v_c).  The thirty coalition
functionals d(T) collapse onto TWENTY linear forms, ten up to sign:

  +-u, +-v_b, +-v_c, +-(v_b+v_c), +-(u+v_b), +-(u+v_c),
  +-(u+v_b+v_c), +-(u-v_b), +-(u-v_c), +-(u-v_b-v_c)

and d(af) = d(bcg) = 0 identically.  The forms that are ABSENT are exactly
those separating b from c with opposite signs -- v_b - v_c, u+v_b-v_c,
u-v_b+v_c -- which is the combinatorial trace of S2 holding b and c together.

Twelve of the twenty can be phi-TIGHT; the other eight are excluded outright:
  d(f) = d(bcfg) = -u          f tight would give phi_f = 0;  bcfg by Lemma 3
  d(g) = d(afg) = -(v_b+v_c)   g tight would give phi_g = 0;  afg by Lemma 3
  d(cfg) = -(u+v_b)            Lemma 3
  d(bfg) = -(u+v_c)            Lemma 3
  d(fg)  = -(u+v_b+v_c)        H is slack
  d(b) = d(abf) = v_b          phi_b > 0 (Lemma 6);  abf by the crossing budget
  d(c) = d(acf) = v_c          phi_c > 0 (Lemma 6);  acf by the crossing budget
  d(a) = d(abcg) = u           phi_a > 0 (Lemma 6);  abcg by the crossing budget
Note every excluded form is one whose sign would have been useful: the eight
exclusions are precisely the eight forms that are nonpositive somewhere on the
nonnegative orthant and are NOT in the surviving list.

THE TWELVE SURVIVORS (constraint "d in D" reads nu . d >= 0):
   1 ab        nu = ( 1, 1, 0)
   2 ac        nu = ( 1, 0, 1)
   3 bc|abcf   nu = ( 0, 1, 1)
   4 abc       nu = ( 1, 1, 1)
   5 bf        nu = (-1, 1, 0)      numeric: phi_b <= phi_a
   6 cf        nu = (-1, 0, 1)      numeric: phi_c <= phi_a
   7 bcf       nu = (-1, 1, 1)      numeric: phi_f <= phi_g
   8 ag        nu = ( 1,-1,-1)      numeric: phi_a <= phi_b + phi_c
   9 bg|abfg   nu = ( 0, 0,-1)
  10 cg|acfg   nu = ( 0,-1, 0)
  11 abg       nu = ( 1, 0,-1)      numeric: phi_a <= phi_c
  12 acg       nu = ( 1,-1, 0)      numeric: phi_a <= phi_b

LEMMA 4 (proved by hand) says at least one of 5, 6, 7 is tight.

WHAT THIS SCRIPT COMPUTES.  For each stratification, the MINIMAL subsets of
{1..12} for which the leximin cone conditions hold.  Those minimal subsets are
the complete case list the hand proof must close, and they are reported with
the numeric implications each one carries.

Usage: python3 normalform.py
"""
from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction as F

sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import z3

# constraint id -> (normal vector in (u,v_b,v_c), source sets, numeric note)
CONS = {
    1:  ((1, 1, 0),   "ab",        None),
    2:  ((1, 0, 1),   "ac",        None),
    3:  ((0, 1, 1),   "bc|abcf",   None),
    4:  ((1, 1, 1),   "abc",       None),
    5:  ((-1, 1, 0),  "bf",        "B<=A"),
    6:  ((-1, 0, 1),  "cf",        "C<=A"),
    7:  ((-1, 1, 1),  "bcf",       "F<=G"),
    8:  ((1, -1, -1), "ag",        "A<=B+C"),
    9:  ((0, 0, -1),  "bg|abfg",   None),
    10: ((0, -1, 0),  "cg|acfg",   None),
    11: ((1, 0, -1),  "abg",       "A<=C"),
    12: ((1, -1, 0),  "acg",       "A<=B"),
}

PLAYERS = ["a", "b", "c", "f", "g"]


def dvec(uvw):
    """(u,v_b,v_c) -> the 5-vector (d_a,d_b,d_c,d_f,d_g)."""
    u, vb, vc = uvw
    return [u, vb, vc, -u, -(vb + vc)]


def leximin_ok(active, blocks):
    """No d in the cone with d|B_<t = 0, d|B_t >= 0, d|B_t != 0, for any t."""
    u, vb, vc = z3.Real("u"), z3.Real("vb"), z3.Real("vc")
    base = []
    for i in active:
        nu = CONS[i][0]
        base.append(nu[0] * u + nu[1] * vb + nu[2] * vc >= 0)
    d = dvec((u, vb, vc))
    pre = []
    for t, blk in enumerate(blocks):
        s = z3.Solver()
        s.add(base)
        for l in pre:
            s.add(d[l] == 0)
        for c in blk:
            s.add(d[c] >= 0)
        s.add(z3.Or([d[c] > 0 for c in blk]))
        r = s.check()
        assert r != z3.unknown
        if r == z3.sat:
            return False
        pre = pre + blk
    return True


def strat_list():
    """(blocks, tag) for every stratification, blocks in player indices
    a=0,b=1,c=2,f=3,g=4.  L-shapes up to the b<->c relabelling."""
    Lshapes = [
        ([[0, 1, 2]],            "abc"),
        ([[0], [1, 2]],          "a|bc"),
        ([[1, 2], [0]],          "bc|a"),
        ([[0, 1], [2]],          "ab|c"),
        ([[2], [0, 1]],          "c|ab"),
        ([[0], [1], [2]],        "a|b|c"),
        ([[1], [0], [2]],        "b|a|c"),
        ([[1], [2], [0]],        "b|c|a"),
    ]
    out = []
    for lb, ltag in Lshapes:
        for hb, htag in (([[3, 4]], "fg"), ([[3], [4]], "f|g"),
                         ([[4], [3]], "g|f")):
            out.append((lb + hb, f"{ltag} < {htag}"))
    return out


def minimal_sets(blocks):
    """All MINIMAL subsets of {1..12} for which leximin holds."""
    ids = list(CONS)
    ok = []
    for r in range(0, len(ids) + 1):
        for combo in itertools.combinations(ids, r):
            st = set(combo)
            if any(prev <= st for prev in ok):
                continue
            if leximin_ok(st, blocks):
                ok.append(st)
        if ok and r >= max(len(s) for s in ok):
            pass
    return ok


def main():
    out = []
    print("MINIMAL TIGHT-CONSTRAINT SETS MAKING LEXIMIN HOLD")
    print("(Lemma 4 forces at least one of 5=bf, 6=cf, 7=bcf; sets that miss")
    print(" all three are struck out as vacuous.)")
    print()
    for blocks, tag in strat_list():
        ms = minimal_sets(blocks)
        live = [s for s in ms if s & {5, 6, 7}]
        dead = len(ms) - len(live)
        print(f"{tag:14s}  minimal sets: {len(ms):3d}   "
              f"surviving Lemma 4: {len(live):3d}   (killed by Lemma 4: {dead})")
        for s in sorted(live, key=lambda z: (len(z), sorted(z))):
            names = "+".join(CONS[i][1] for i in sorted(s))
            nums = [CONS[i][2] for i in sorted(s) if CONS[i][2]]
            print(f"      {sorted(s)}  = {names}"
                  + (f"   [{', '.join(nums)}]" if nums else ""))
        out.append({"tag": tag,
                    "minimal": [sorted(s) for s in ms],
                    "surviving": [sorted(s) for s in live]})
    json.dump(out, open("/private/tmp/claude-501/-Users-maxf/"
                        "f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23/"
                        "normalform.json", "w"), indent=1)


if __name__ == "__main__":
    main()
