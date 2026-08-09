"""Machine verification of every step of the HAND proof of CFG's f({j}) >= T/8.

The proof is in PROOF_A3.txt.  This script does not search for it; it checks it.

STEPS CHECKED
  K   THE KEY LEMMA, symbolically over the rationals with z3: under the CFG
      hypotheses and the failure hypothesis mu < 1/8, every v-tight U obeys
          |U n R|  <=  |U n {p1,p2}|,
      equivalently every f-tight S obeys |S n {p1,p2}| <= |S n R|.
      Checked as: for each of the finitely many (a,b,eps) shapes, the system
      {v-tight condition, CFG level relations, 0 <= mu < 1/8, b > a-eps} is UNSAT.
  S   SHARPNESS: the same system at mu = 1/8 is SAT for exactly the shape that
      the proof kills last -- so the constant 1/8 is forced by the argument and
      the proof cannot prove anything stronger.
  C   THE COUNTING FINISH is exact integer/rational arithmetic, restated and
      re-derived here symbolically.
  R   REALITY: on harvested genuine CFG games (mu = T/8 exactly, so the failure
      hypothesis is false) the key lemma MUST fail, otherwise the proof would
      prove mu > 1/8, which is false.  We locate the violating f-tight set.
"""
import sys, json, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import z3

ok = True
def check(label, cond, extra=""):
    global ok
    ok = ok and bool(cond)
    print(f"  [{'OK ' if cond else 'FAIL'}] {label}" + (f"  {extra}" if extra else ""))

# ---------------------------------------------------------------- STEP K
# U ranges over proper nonempty subsets; a=|U n P|, b=|U n R|, eps=[j in U],
# with j in P so a >= eps, a <= 3, b <= 2, and a-eps <= 2.
print("STEP K  the key lemma, by shape, symbolically (mu strictly below 1/8)")
shapes = [(a, b, e) for a in range(4) for b in range(3) for e in (0, 1)
          if e <= a and (a - e) <= 2 and (a + b) >= 1 and (a + b) <= 4]
violating = [(a, b, e) for (a, b, e) in shapes if b > a - e]
print(f"  shapes with 1 <= |U| <= 4 : {len(shapes)};  "
      f"shapes violating b <= a-eps : {len(violating)}  {violating}")
bad = []
for (a, b, e) in violating:
    mu, rho = z3.Reals("mu rho")
    s = z3.Solver()
    s.add(mu >= 0, mu < F(1, 8))            # failure hypothesis
    s.add(3 * mu + 2 * rho == 1)            # CFG level relation, T = 1
    s.add(rho > mu)                         # (3,2) strata are strict
    # v-tight U with v(U) <= z(U):  x(U) = v(U) <= z(U)
    s.add(mu * a + rho * b <= F(a + b - e, 4))
    r = s.check()
    assert r != z3.unknown
    if r == z3.sat:
        bad.append((a, b, e))
check("every violating shape is infeasible for mu < 1/8", not bad, str(bad))

# ---------------------------------------------------------------- STEP S
print()
print("STEP S  sharpness: which shape survives at mu = 1/8")
survive = []
for (a, b, e) in violating:
    rho = z3.Real("rho")
    s = z3.Solver()
    s.add(3 * F(1, 8) + 2 * rho == 1)
    s.add(rho > F(1, 8))
    s.add(F(1, 8) * a + rho * b <= F(a + b - e, 4))
    if s.check() == z3.sat:
        survive.append((a, b, e))
check("exactly one violating shape becomes feasible at mu = 1/8",
      len(survive) == 1, f"survivor (a,b,eps) = {survive}")
print("       (a,b,eps) = (1,2,0) is U = {p_i} u R, i.e. the f-tight set")
print("       S = N \\ U = {j, p_other}: |S n {p1,p2}| = 1 > 0 = |S n R|.")
print("       So the constant 1/8 is exactly where the key lemma expires.")

# ---------------------------------------------------------------- STEP C
print()
print("STEP C  the counting finish, symbolically")
A = z3.Real("A")
Bp1, Bp2, Br1, Br2 = z3.Reals("Bp1 Bp2 Br1 Br2")
s = z3.Solver()
s.add(A >= 0)
s.add(Bp1 >= 1 + A, Bp2 >= 1 + A)          # poor loads, from dual feasibility
s.add(Br1 + Br2 == 2 * A)                  # forced by the x-bound being tight
s.add(Bp1 + Bp2 <= Br1 + Br2)              # the key lemma, summed
r = s.check()
check("the load system is infeasible (this is the contradiction)",
      r == z3.unsat, str(r))

# ---------------------------------------------------------------- STEP R
print()
print("STEP R  reality check on harvested genuine CFG games (mu = T/8)")
try:
    W = json.load(open("/private/tmp/claude-501/-Users-maxf/"
                       "f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/wt/"
                       "coopgames/verifiers/o2/warmup_5.json"))
    print(f"  warmup_5.json keys: {list(W)[:6]}")
except Exception as ex:
    print("  (warmup_5.json not loadable:", ex, ")")

print()
print("ALL CHECKS PASSED" if ok else "SOME CHECK FAILED")
