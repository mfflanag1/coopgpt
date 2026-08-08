"""d26: minimal unsat core for the EXACT-PARTITION theorem at n = 5.

Minimal hypotheses (d23 ablation): core + exv2 + cert2 + expart.  That is a
much smaller vocabulary than either half of C-C needed, so the core may be
short enough to read off a hand proof.  S is fixed (players inside a stratum
are interchangeable, a symmetry of every hypothesis) and z3's core is then
minimized greedily to an irredundant set.

usage: d26_epcore.py <gaps e.g. 1> <S mask>
"""
import sys, itertools
import z3

n = 5
FULL = 31
props = list(range(1, FULL))
gaps = tuple(int(x) for x in sys.argv[1].split(","))
S = int(sys.argv[2])


def bits(T):
    return [i for i in range(n) if T >> i & 1]


def nm(T):
    return "{" + ",".join(str(i + 1) for i in bits(T)) + "}"


def make():
    C = []
    v = {T: z3.Real("v_%d" % T) for T in props}
    v[FULL] = z3.RealVal(1)
    phi = [z3.Real("p_%d" % i) for i in range(n)]
    ph2 = [z3.Real("q_%d" % i) for i in range(n)]
    al = z3.Real("alpha")

    def tot(x, T):
        return z3.Sum([x[i] for i in bits(T)])

    for i in range(n):
        C.append(("norm_%d" % (i + 1), v[1 << i] == 0))
    C.append(("alpha_pos", al > 0))
    for c in range(1, n):
        C.append(("shape_%d%d" % (c, c + 1),
                  phi[c - 1] < phi[c] if c in gaps else phi[c - 1] == phi[c]))
    v2 = {T: (v[T] + al if T == S else v[T]) for T in props}
    v2[FULL] = z3.RealVal(1)
    # core
    C.append(("eff_phi", tot(phi, FULL) == v[FULL]))
    C.append(("eff_phi2", tot(ph2, FULL) == v2[FULL]))
    for T in props:
        C.append(("core_phi_%s" % nm(T), tot(phi, T) >= v[T]))
        C.append(("core_phi2_%s" % nm(T), tot(ph2, T) >= v2[T]))
    # exact partition: every richer suffix tight
    for c in gaps:
        H = sum(1 << i for i in range(c, n))
        C.append(("expart_%s" % nm(H), tot(phi, H) == v[H]))
    # exactness of v'
    for T in props:
        z = [z3.Real("z%d_%d" % (T, i)) for i in range(n)]
        C.append(("exv2_%s_eff" % nm(T), z3.Sum(z) == v2[FULL]))
        for U in props:
            C.append(("exv2_%s_core_at_%s" % (nm(T), nm(U)), tot(z, U) >= v2[U]))
        C.append(("exv2_%s_attains" % nm(T), tot(z, T) == v2[T]))
    # Lemma L for phi', shape-free (one certificate per attained level)
    for m in range(n):
        lam = {T: z3.Real("L%d_%d" % (m, T)) for T in props}
        nu = z3.Real("nu%d" % m)
        for T in props:
            C.append(("cert2_%d_nonneg_%s" % (m, nm(T)), lam[T] >= 0))
            C.append(("cert2_%d_support_%s" % (m, nm(T)),
                      z3.Implies(lam[T] > 0, tot(ph2, T) == v2[T])))
        for i in range(n):
            cov = z3.Sum([lam[T] for T in props if T >> i & 1])
            C.append(("cert2_%d_rich_%d" % (m, i + 1),
                      z3.Implies(ph2[i] > ph2[m], cov == nu)))
            C.append(("cert2_%d_level_%d" % (m, i + 1),
                      z3.Implies(ph2[i] == ph2[m], cov <= nu - 1)))
    # the failure
    C.append(("failure_in_S",
              z3.Or([ph2[i] < phi[i] for i in bits(S)])))
    return C


def unsat_with(sub):
    s = z3.Solver()
    s.set("timeout", 300000)
    for _, c in sub:
        s.add(c)
    return s.check() == z3.unsat


C = make()
print("gaps=%s  S=%s   full system: %d assertions" % (gaps, nm(S), len(C)))
if not unsat_with(C):
    print("SATISFIABLE -- this shape/S admits a failure; nothing to minimize")
    raise SystemExit(0)
s = z3.Solver()
s.set(unsat_core=True)
for lab, c in C:
    s.assert_and_track(c, lab)
assert s.check() == z3.unsat
cur = [(l, c) for l, c in C if l in {str(x) for x in s.unsat_core()}]
print("z3 core: %d; minimizing..." % len(cur))
changed = True
while changed:
    changed = False
    for k in range(len(cur) - 1, -1, -1):
        if unsat_with(cur[:k] + cur[k + 1:]):
            cur = cur[:k] + cur[k + 1:]
            changed = True
print("\nMINIMAL (irredundant) core: %d assertions" % len(cur))
for lab, _ in sorted(cur):
    print("   ", lab)
