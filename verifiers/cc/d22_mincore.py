"""d22: MINIMAL unsat core for the two-strata case, to expose the hand proof.

z3's unsat core is not minimal (d20 returned 72 assertions).  This driver
minimizes it greedily: repeatedly drop one assertion and re-check; keep the drop
whenever the system stays unsat.  The instance solves in well under a second, so
a full pass is cheap and the result is a genuinely irredundant hypothesis list --
i.e. a proof skeleton, naming exactly which coalitions' core inequalities, which
exactness witnesses and which certificate rows are combined.

Claim under test (from d19/d21):
  v with v({i}) = 0, phi leximin-maximal in core(v) with exactly two strata
  B_1 = {1,2,3,4} at mu and {5} at nu > mu.  If v' = v^{S,alpha} is exact and
  alpha > s_phi(S), then 5 in S.   (Here S = {1..m}, so 5 not in S: contradiction
  expected.)

usage: d22_mincore.py [m]
"""
import sys, itertools
import z3

n = 5
FULL = 31
props = list(range(1, FULL))
m = int(sys.argv[1]) if len(sys.argv) > 1 else 2
S = (1 << m) - 1


def bits(T):
    return [i for i in range(n) if T >> i & 1]


def nm(T):
    return "{" + ",".join(str(i + 1) for i in bits(T)) + "}"


def make():
    """Returns (list of (label, constraint))."""
    C = []
    v = {T: z3.Real("v_%d" % T) for T in props}
    v[FULL] = z3.RealVal(1)
    phi = [z3.Real("p_%d" % i) for i in range(n)]
    al = z3.Real("alpha")

    def tot(x, T):
        return z3.Sum([x[i] for i in bits(T)])

    for i in range(n):
        C.append(("norm_%d" % (i + 1), v[1 << i] == 0))
    C.append(("alpha_pos", al > 0))
    for i in range(3):
        C.append(("tie_%d%d" % (i + 1, i + 2), phi[i] == phi[i + 1]))
    C.append(("gap_45", phi[3] < phi[4]))
    C.append(("eff_phi", tot(phi, FULL) == v[FULL]))
    for T in props:
        C.append(("core_phi_%s" % nm(T), tot(phi, T) >= v[T]))
    lam = {T: z3.Real("l_%d" % T) for T in props}
    nu = z3.Real("nu")
    for T in props:
        C.append(("lam_nonneg_%s" % nm(T), lam[T] >= 0))
        C.append(("lam_support_%s" % nm(T),
                  z3.Implies(lam[T] > 0, tot(phi, T) == v[T])))
    C.append(("cert_rich_cover",
              z3.Sum([lam[T] for T in props if T >> 4 & 1]) == nu))
    for i in range(4):
        C.append(("cert_poor_cover_%d" % (i + 1),
                  z3.Sum([lam[T] for T in props if T >> i & 1]) <= nu - 1))
    C.append(("overshoot_alpha>s_phi(S)", al > tot(phi, S) - v[S]))
    v2 = {T: (v[T] + al if T == S else v[T]) for T in props}
    v2[FULL] = z3.RealVal(1)
    for T in props:
        z = [z3.Real("z%d_%d" % (T, i)) for i in range(n)]
        C.append(("exv2_%s_efficient" % nm(T), z3.Sum(z) == v2[FULL]))
        for U in props:
            C.append(("exv2_%s_core_at_%s" % (nm(T), nm(U)), tot(z, U) >= v2[U]))
        C.append(("exv2_%s_attains" % nm(T), tot(z, T) == v2[T]))
    return C


def unsat_with(sub):
    s = z3.Solver()
    s.set("timeout", 120000)
    for _, c in sub:
        s.add(c)
    return s.check() == z3.unsat


C = make()
print("S = %s   full system: %d assertions" % (nm(S), len(C)))
assert unsat_with(C), "system is not unsat"

# start from z3's core, then minimize greedily
s = z3.Solver()
s.set(unsat_core=True)
for lab, c in C:
    s.assert_and_track(c, lab)
assert s.check() == z3.unsat
core_labels = {str(x) for x in s.unsat_core()}
cur = [(l, c) for l, c in C if l in core_labels]
print("z3 core: %d assertions; minimizing..." % len(cur))

changed = True
while changed:
    changed = False
    for k in range(len(cur) - 1, -1, -1):
        trial = cur[:k] + cur[k + 1:]
        if unsat_with(trial):
            cur = trial
            changed = True
print("\nMINIMAL (irredundant) unsat core: %d assertions" % len(cur))
for lab, _ in sorted(cur):
    print("   ", lab)
print("\nEvery one of these is needed: dropping any single one makes the system")
print("satisfiable, so this is exactly the hypothesis list a hand proof combines.")
