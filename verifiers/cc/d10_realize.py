"""d10: extract a lab SAT model and try to realize it as a genuine game.

Why a SAT model should already BE a counterexample.  Lemma L is not only
necessary for leximin-maximality of a core point, it is sufficient:

  Let phi in core(v) satisfy Lemma L at every cut, and suppose y in core(v) has
  sort(y) >lex sort(phi).  Put delta = y - phi.  Then delta(N) = 0 and
  delta(T) >= 0 at every phi-tight T, so delta lies in the tangent cone D.
  If some i in B_1 had delta_i < 0 then min y < min phi and y would be worse;
  so delta|B_1 >= 0.  If delta|B_1 != 0, that is exactly a direction forbidden
  by Lemma L at cut 1.  Otherwise every player outside B_1 must satisfy
  y_i > phi_1 (equality would put an extra entry at level phi_1 and make y
  worse at position |B_1|+1), the first |B_1| sorted entries agree, and the
  argument repeats on the next stratum.  Contradiction at some cut.

So core + exv + exv2 + cert + cert2 is a COMPLETE description: any model of it
is a real exact game with a real leximin pair.  This driver therefore rebuilds
v from the model and re-derives everything from scratch with the independent
toolkit -- exactness by z3 optimisation, Lmin by two algorithms.

usage: d10_realize.py <n> <target> <gaps 3,4> <cstar> [groups]
"""
import sys, json
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L
import d2_lab as lab
import z3

n = int(sys.argv[1])
target = sys.argv[2]
gaps = tuple(int(x) for x in sys.argv[3].split(","))
cstar = int(sys.argv[4])
groups = sys.argv[5].split(",") if len(sys.argv) > 5 else lab.ALLGROUPS
FULL = (1 << n) - 1

s, H = lab.build(n, gaps, cstar, target, groups)
s.set("timeout", 900000)
print("solving shape gaps=%s c*=%d target=%s ..." % (gaps, cstar, target), flush=True)
r = s.check()
print("z3:", r)
if r != z3.sat:
    raise SystemExit(0)
m = s.model()


def val(e):
    q = m.eval(e, model_completion=True)
    return L.rat(q)


v = [F(0)] * (1 << n)
for T in L.masks(n):
    v[T] = val(H["v"][T])
v[FULL] = F(1)
phi = [val(H["phi"][i]) for i in range(n)]
ph2 = [val(H["ph2"][i]) for i in range(n)]
S = [T for T in H["isS"] if z3.is_true(m.eval(H["isS"][T]))][0]
al = val(H["al"])
print("model S =", L.nm(n, S), " alpha =", al)
print("model v =", [str(q) for q in v])
print("model phi  =", [str(q) for q in phi])
print("model phi' =", [str(q) for q in ph2])

# clear denominators so the game is integral (scaling changes nothing)
den = 1
for q in list(v) + [al]:
    den = den * q.denominator // __import__("math").gcd(den, q.denominator)
V = [q * den for q in v]
AL = al * den
print("\nscaled by %d -> integral game" % den)
print("v =", [str(q) for q in V])

print("\n--- independent re-derivation from v alone ---")
ok, bad = L.exactness_report(n, V)
print("v exact:", ok, bad[:4])
if not ok:
    print("MODEL IS NOT AN EXACT GAME -- encoding of exv is at fault")
    raise SystemExit(0)
PHI = L.lmin(n, V, both=True)
print("Lmin(v) recomputed =", [str(q) for q in PHI])
print("   matches model phi:", PHI == [q * den for q in phi])
W2 = L.bumped(V, S, AL)
ok2, bad2 = L.exactness_report(n, W2)
print("v' exact:", ok2, bad2[:4])
PHI2 = L.lmin(n, W2, both=True) if ok2 else None
print("Lmin(v') recomputed =", None if PHI2 is None else [str(q) for q in PHI2])
if PHI2 is not None:
    print("   matches model phi':", PHI2 == [q * den for q in ph2])

if ok and ok2 and PHI is not None and PHI2 is not None:
    Hs, js = L.hstar(n, V, PHI)
    Wl = [i for i in L.members(n, S) if PHI2[i] < PHI[i]]
    Wm = sum(1 << i for i in Wl)
    print("\n--- verdict on the REALIZED game ---")
    print("strata:", [[i + 1 for i in b] for b in L.strata(n, PHI)])
    print("suffix slacks:", [(L.nm(n, Hj), str(sl))
                             for _, Hj, sl in L.suffixes(n, V, PHI)])
    print("H* =", None if Hs is None else L.nm(n, Hs), " S =", L.nm(n, S),
          " W =", L.nm(n, Wm))
    print("violation:", bool(Wl))
    if Hs is not None and Wl:
        print("C-C LEFT  (W subset H*):", (Wm & ~Hs) == 0)
        print("C-C RIGHT (H* subset S):", (Hs & ~S) == 0)
