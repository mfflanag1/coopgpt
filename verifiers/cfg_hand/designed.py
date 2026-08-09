"""DESIGNED search to settle constraint (ii), replacing random sampling.

By my own reduction, mu < lambda requires some cover vertex to violate
sum_S beta_S g(S) >= g(N).  Lemmas B, C and E1 use ONLY core membership, so
they apply to BALANCED games too -- hence for a balanced game the ONLY possible
violating vertex is the residual shape
    S1 = {p,x},  S2 = {p,q,y},  S3 = {p,q,z},
whose inequality is  f(S1) + f(S2) + f(S3) >= T + 3*lambda.

So: ask z3 directly for a game v that is singleton-normalized, has a NONEMPTY
CORE, and VIOLATES that one inequality.  Exactness is NOT imposed.
  SAT   -> constraint (ii) restored: core membership alone cannot prove (R).
  UNSAT -> core membership alone DOES prove (R): exactness is not where the
           content lives, and the round-4 localization reopens.
Either way this is decisive, unlike random sampling.

lambda enters as a variable bounded by lambda|S| <= f(S) for EVERY nonempty S
INCLUDING N (the convention the lead corrected).  Any lambda satisfying that is
<= the true lambda, and the violation only gets harder as lambda shrinks, so a
SAT model at this lambda is a fortiori a violation at the true lambda.
T = 1 by homogeneity; in-regime is automatic, since lambda <= f(N)/5 = 1/5.
"""
import sys, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import lib23 as L, z3
n, FULL = 5, 31
PROPER = [S for S in range(1, FULL)]
p, q, x, y, z_ = 0, 1, 2, 3, 4
S1 = (1 << p) | (1 << x)
S2 = (1 << p) | (1 << q) | (1 << y)
S3 = (1 << p) | (1 << q) | (1 << z_)

v = {S: z3.Real(f"v{S}") for S in range(1, FULL + 1)}
lam = z3.Real("lam")
yy = [z3.Real(f"y{i}") for i in range(n)]
s = z3.Solver()
s.set("timeout", 900000)
s.add(v[FULL] == 1)
for i in range(n):
    s.add(v[1 << i] == 0)
# nonempty core (balanced)
s.add(z3.Sum(yy) == 1)
for i in range(n):
    s.add(yy[i] >= 0)
for S in PROPER:
    s.add(z3.Sum([yy[i] for i in range(n) if S >> i & 1]) >= v[S])
# lambda valid for EVERY nonempty S including N
def f_(S):
    return 1 - (v[FULL ^ S] if S != FULL else 0)
for S in range(1, FULL + 1):
    s.add(lam * bin(S).count("1") <= f_(S))
s.add(lam > 0)
# the residual cover, VIOLATED
s.add(f_(S1) + f_(S2) + f_(S3) < 1 + 3 * lam)
r = s.check()
print(f"designed search verdict: {r}")
if r == z3.sat:
    m = s.model()
    w = [F(0)] * 32
    for S in range(1, FULL + 1):
        w[S] = L.rat(m.eval(v[S], model_completion=True))
    lamv = L.rat(m.eval(lam, model_completion=True))
    print(f"  lambda used = {lamv}")
    print(f"  v = {{{', '.join(f'{L.nm(n,S)}:{w[S]}' for S in PROPER if w[S] != 0)}}}")
    # audit
    lp = min(F(1 - w[FULL ^ S], bin(S).count("1")) for S in PROPER)
    lt = min(lp, F(1, 5))
    xx = [z3.Real(f"a{i}") for i in range(n)]; t = z3.Real("t")
    o = z3.Optimize()
    o.add(z3.Sum(xx) == 1)
    for S in PROPER:
        o.add(z3.Sum([xx[i] for i in range(n) if S >> i & 1]) >= L.to_z3(w[S]))
    for i in range(n):
        o.add(xx[i] >= 0, xx[i] >= t)
    h = o.maximize(t); assert o.check() == z3.sat
    mu = L.rat(o.upper(h))
    ex, _ = L.is_exact_lp(n, w)
    print(f"  AUDIT: lambda_proper={lp}  T/5=1/5  lambda_true={lt}  mu={mu}")
    print(f"         mu < lambda_true : {mu < lt}    in regime : {lp <= F(1,5)}")
    print(f"         exact : {ex}   (must be False)")
    print("  => CONSTRAINT (ii) RESTORED as a theorem" if (mu < lt and not ex)
          else "  => model does NOT audit; (ii) still unproven")
else:
    print("  NO balanced game violates the residual cover inequality.")
    print("  => CORE MEMBERSHIP ALONE PROVES (R).  Exactness is NOT where the")
    print("     content of mu = lambda lives.  Constraint (ii) is FALSE, and")
    print("     (R) should be provable from core membership by hand.")
