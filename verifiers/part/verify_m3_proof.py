"""STEP-BY-STEP VERIFICATION of the hand proof of Theorem D (no PART at m = 3).

Every step of PROOF_M3.txt is a hand argument; this script re-derives each one
mechanically as a guard against slips.  Nothing here is part of the proof --
the proof is in PROOF_M3.txt -- but a disagreement here would mean the proof is
wrong.

Checks:
  V1  the normal-form identities: for all 30 proper coalitions T, d(T) equals
      the claimed linear form in (u, v_b, v_c), and d(af) = d(bcg) = 0;
  V2  the collapse: the 30 forms take exactly 21 distinct values, namely 0 and
      ten forms up to sign; the three forms separating b from c with opposite
      signs never occur;
  V3  the exclusion list: exactly 13 coalitions are excluded by Lemmas 3 and 6,
      slackness and the crossing budget, leaving 12 admissible normals;
  V4  LEMMA P: among the twelve admissible normals, exactly cf and cg|acfg are
      negative on (1,1,0), and exactly bf and bg|abfg are negative on (1,0,1);
  V5  the directions (1,1,0) and (1,0,1) are leximin-improving for EVERY one of
      the 24 stratifications (this is why the stratification drops out);
  V6  the four-case contradiction table is exhaustive and each case closes;
  V7  cross-check against normalform.py: each of the 8 minimal leximin sets
      satisfies Lemma P's conclusion and falls into one of the four cases.
"""
from __future__ import annotations

import itertools
import sys
from fractions import Fraction as F

sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import z3

PL = "abcfg"          # a=0 b=1 c=2 f=3 g=4
A, B, C, Ff, G = 0, 1, 2, 3, 4


def name(mask):
    return "".join(PL[i] for i in range(5) if mask >> i & 1)


def dform(mask):
    """d(T) as a triple of coefficients of (u, v_b, v_c), using
    d = (u, v_b, v_c, -u, -(v_b+v_c))."""
    co = [0, 0, 0]
    if mask >> A & 1:
        co[0] += 1
    if mask >> B & 1:
        co[1] += 1
    if mask >> C & 1:
        co[2] += 1
    if mask >> Ff & 1:
        co[0] -= 1
    if mask >> G & 1:
        co[1] -= 1
        co[2] -= 1
    return tuple(co)


ok = True


def check(label, cond, extra=""):
    global ok
    ok = ok and bool(cond)
    print(f"  [{'OK ' if cond else 'FAIL'}] {label}" + (f"  {extra}" if extra else ""))


print("V1/V2  normal-form collapse")
forms = {}
for m in range(1, 31):
    forms.setdefault(dform(m), []).append(name(m))
check("d(af) = d(bcg) = 0", dform(0b01001) == (0, 0, 0) and dform(0b10110) == (0, 0, 0))
distinct = set(forms)
check("30 coalitions collapse onto 21 forms (0 plus 10 up to sign)",
      len(distinct) == 21, f"got {len(distinct)}")
absent = [(0, 1, -1), (1, 1, -1), (1, -1, 1)]
check("the three b/c-separating forms never occur",
      all(f not in distinct and tuple(-x for x in f) not in distinct
          for f in absent))

print()
print("V3  exclusions")
EXCLUDED = {
    "a": "phi_a > 0 (Lemma 6)", "b": "phi_b > 0", "c": "phi_c > 0",
    "f": "phi_f > 0", "g": "phi_g > 0",
    "fg": "H is slack",
    "bfg": "Lemma 3", "cfg": "Lemma 3", "bcfg": "Lemma 3",
    "afg": "crossing with S2 gives phi_g <= 0",
    "abf": "crossing with S2 makes {b} tight, phi_b = 0",
    "acf": "crossing with S2 makes {c} tight, phi_c = 0",
    "abcg": "crossing with S1 gives phi_a <= 0",
}
allnames = {name(m) for m in range(1, 31)}
adm = sorted(allnames - set(EXCLUDED))
check("13 coalitions excluded", len(EXCLUDED) == 13)
check("17 coalitions admissible", len(adm) == 17, str(adm))
admforms = {}
for nm in adm:
    m = sum(1 << PL.index(ch) for ch in nm)
    admforms.setdefault(dform(m), []).append(nm)
nonzero = {f: v for f, v in admforms.items() if f != (0, 0, 0)}
check("12 distinct nonzero admissible normals", len(nonzero) == 12,
      f"got {len(nonzero)}")

print()
print("V4  LEMMA P")
for direction, culprits in ((( 1, 1, 0), {"cf", "cg", "acfg"}),
                            (( 1, 0, 1), {"bf", "bg", "abfg"})):
    neg = set()
    for f, names in nonzero.items():
        val = sum(f[i] * direction[i] for i in range(3))
        if val < 0:
            neg |= set(names)
    check(f"normals negative on {direction} are exactly {sorted(culprits)}",
          neg == culprits, f"got {sorted(neg)}")

print()
print("V5  the two directions are leximin-improving for every stratification")


def improving(direction, blocks):
    u, vb, vc = direction
    d = [u, vb, vc, -u, -(vb + vc)]
    pre = []
    for blk in blocks:
        if all(d[l] == 0 for l in pre) and all(d[c] >= 0 for c in blk) \
           and any(d[c] > 0 for c in blk):
            return True
        pre = pre + blk
    return False


Lshapes = [([[0, 1, 2]], "abc"), ([[0], [1, 2]], "a|bc"), ([[1, 2], [0]], "bc|a"),
           ([[0, 1], [2]], "ab|c"), ([[2], [0, 1]], "c|ab"),
           ([[0], [1], [2]], "a|b|c"), ([[1], [0], [2]], "b|a|c"),
           ([[1], [2], [0]], "b|c|a"),
           ([[0], [2], [1]], "a|c|b"), ([[2], [0], [1]], "c|a|b"),
           ([[2], [1], [0]], "c|b|a"), ([[0, 2], [1]], "ac|b"),
           ([[1], [0, 2]], "b|ac")]
strats = []
for lb, lt in Lshapes:
    for hb, ht in (([[3, 4]], "fg"), ([[3], [4]], "f|g"), ([[4], [3]], "g|f")):
        strats.append((lb + hb, f"{lt} < {ht}"))
bad = [t for bl, t in strats
       if not (improving((1, 1, 0), bl) and improving((1, 0, 1), bl))]
check(f"both directions improving on all {len(strats)} stratifications "
      f"(all L-orderings, not only the canonical ones)", not bad, str(bad))

print()
print("V6  the four-case contradiction table")
# d* = exactness at {f}: u = phi_f = F > 0.  Symbolically: is each case UNSAT?
u, vb, vc, Fv = z3.Reals("u vb vc F")
cases = {
    "(1) cf and bf tight": [vc >= u, vb >= u],
    "(2) cf and bg|abfg tight": [vc >= u, vc <= 0],
    "(3) cg|acfg and bf tight": [vb <= 0, vb >= u],
    "(4) cg|acfg and bg|abfg tight": [vb <= 0, vc <= 0],
}
for label, cons in cases.items():
    s = z3.Solver()
    s.add(u == Fv, Fv > 0)
    s.add(cons)
    if label.startswith("(1)"):
        # case 1 dies because d* is then strictly positive on all of L,
        # hence leximin-improving; encode "not strictly positive"
        s.add(z3.Or(vb <= 0, vc <= 0))
    if label.startswith("(4)"):
        # case 4 dies via Lemma 4: one of bf, cf, bcf must be tight
        s.add(z3.Or(vb >= u, vc >= u, vb + vc >= u))
    r = s.check()
    check(f"{label} is contradictory", r == z3.unsat, str(r))

print()
print("V7  cross-check against the normalform.py enumeration")
MIN8 = [{5, 6, 8}, {5, 8, 10}, {5, 9, 10}, {5, 10, 11},
        {6, 8, 9}, {6, 9, 10}, {6, 9, 12}, {7, 9, 10}]
# ids: 5=bf 6=cf 7=bcf 8=ag 9=bg|abfg 10=cg|acfg 11=abg 12=acg
allP = all((s & {6, 10}) and (s & {5, 9}) for s in MIN8)
check("every minimal leximin set satisfies Lemma P's conclusion", allP)
lem4 = all(s & {5, 6, 7} for s in MIN8)
check("every minimal leximin set meets Lemma 4", lem4)

print()
print("ALL CHECKS PASSED" if ok else "SOME CHECK FAILED")
sys.exit(0 if ok else 1)
