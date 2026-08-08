"""d11: end-to-end adversarial audit of the C-C LEFT counterexample.

Nothing here trusts the lab.  The game is taken as a bare list of coalition
values and everything is re-derived four ways:

 1. exactness of v and of v' by exact z3 minimisation over the core;
 2. exactness of v and of v' AGAIN by exact rational core-vertex enumeration
    (an independent algorithm that shares no code path with 1);
 3. Lmin of both games by two independent algorithms (staged pinning and the
    Sigma_m ladder), each with a z3 UNSAT uniqueness proof;
 4. leximin-maximality of both allocations by an independent z3 UNSAT: no core
    point is leximin-better, encoded on the partial-sum ladder;
 5. leximin-maximality AGAIN by exhibiting a Lemma-L certificate at every cut
    (a positive certificate, checkable by hand).

usage: d11_audit.py            (audits the stored candidate)
"""
import sys, itertools, json
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L
import d3_lemmaL as LL
import z3

n = 5
FULL = 31
V = [0, 0, 0, 106, 0, 136, 0, 136, 0, 161, 0, 161, 176, 297, 176, 297,
     0, 242, 0, 242, 242, 393, 242, 484, 176, 418, 176, 418, 418, 534, 418, 660]
V = [F(q) for q in V]
S = 0b11101                      # {1,3,4,5}
ALPHA = F(20)

print("n = 5,  v given by mask (v(N) = %s)" % V[FULL])
for T in range(1, FULL + 1):
    if V[T]:
        print("   v(%-11s) = %s" % (L.nm(n, T), V[T]))
print("singleton-normalized:", L.is_sing_norm(n, V))
print("S =", L.nm(n, S), "  alpha =", ALPHA, "  v(S) =", V[S], "  v'(S) =", V[S] + ALPHA)
W2 = L.bumped(V, S, ALPHA)
print("v' differs from v at exactly one coalition:",
      [T for T in range(1, FULL + 1) if W2[T] != V[T]] == [S])


def vertex_exact(v):
    """Exactness by exact rational core-vertex enumeration (independent of z3)."""
    rows = [([F(1)] * n, v[FULL])]
    ineq = [([F(1) if T >> i & 1 else F(0) for i in range(n)], v[T])
            for T in L.masks(n)]
    verts = set()
    for combo in itertools.combinations(range(len(ineq)), n - 1):
        A = [rows[0][0]] + [ineq[c][0] for c in combo]
        b = [rows[0][1]] + [ineq[c][1] for c in combo]
        x = solve(A, b)
        if x is None:
            continue
        if all(sum(a[i] * x[i] for i in range(n)) >= r for a, r in ineq):
            verts.add(tuple(x))
    if not verts:
        return False, "empty core", 0
    bad = []
    for T in L.masks(n):
        lo = min(sum(x[i] for i in L.members(n, T)) for x in verts)
        if lo != v[T]:
            bad.append((L.nm(n, T), str(lo), str(v[T])))
    return (not bad), bad, len(verts)


def solve(A, b):
    k = len(A)
    M = [list(map(F, A[r])) + [F(b[r])] for r in range(k)]
    for c in range(k):
        p = next((r for r in range(c, k) if M[r][c] != 0), None)
        if p is None:
            return None
        M[c], M[p] = M[p], M[c]
        pv = M[c][c]
        M[c] = [q / pv for q in M[c]]
        for r in range(k):
            if r != c and M[r][c] != 0:
                fct = M[r][c]
                M[r] = [M[r][j] - fct * M[c][j] for j in range(k + 1)]
    return [M[r][k] for r in range(k)]


def no_better(v, x):
    """z3 UNSAT: no core point is leximin-strictly-better than x.
    Uses the ladder Sigma_m(y) = min_{|A|=m} y(A); sorted(y) >lex sorted(x) iff
    (Sigma_m(y)) >lex (Sigma_m(x))."""
    y = [z3.Real("Y%d" % i) for i in range(n)]
    s = z3.Solver()
    s.add(L.core_constraints(n, v, y))
    sx = [min(sum(x[i] for i in A) for A in itertools.combinations(range(n), m))
          for m in range(1, n + 1)]
    sy = []
    for m in range(1, n + 1):
        g = z3.Real("G%d" % m)
        A = list(itertools.combinations(range(n), m))
        for a in A:
            s.add(g <= z3.Sum([y[i] for i in a]))
        s.add(z3.Or([g == z3.Sum([y[i] for i in a]) for a in A]))
        sy.append(g)
    s.add(z3.Or([z3.And([sy[l] == L.to_z3(sx[l]) for l in range(m)] +
                        [sy[m] > L.to_z3(sx[m])]) for m in range(n)]))
    return s.check()


for name, g in (("v", V), ("v'", W2)):
    print("\n===== game %s =====" % name)
    ok1, bad1 = L.exactness_report(n, g)
    print("  exact (z3 minimisation over the core):", ok1, bad1[:3])
    ok2, bad2, nv = vertex_exact(g)
    print("  exact (independent rational vertex enumeration, %d vertices):" % nv,
          ok2, bad2[:3])
    assert ok1 and ok2 and ok1 == ok2
    ph = L.lmin(n, g, both=True)
    print("  Lmin =", [str(q) for q in ph], "(staged + ladder agree; ladder unique)")
    r = no_better(g, ph)
    print("  z3: some core point is leximin-better?", r, "(must be unsat)")
    assert r == z3.unsat
    cuts = LL.all_cuts_ok(n, g, ph)
    print("  Lemma-L certificate at every cut:", cuts, all(cuts))
    assert all(cuts)
    if name == "v":
        PHI = ph
    else:
        PHI2 = ph

print("\n===== verdict =====")
D = [PHI2[i] - PHI[i] for i in range(n)]
print("phi  =", [str(q) for q in PHI])
print("phi' =", [str(q) for q in PHI2])
print("Delta=", [str(q) for q in D])
print("strata of phi (poor->rich):", [[i + 1 for i in b] for b in L.strata(n, PHI)])
suf = L.suffixes(n, V, PHI)
print("richer suffixes / slacks:", [(L.nm(n, Hj), str(s)) for _, Hj, s in suf])
H, js = L.hstar(n, V, PHI)
Wl = [i for i in L.members(n, S) if PHI2[i] < PHI[i]]
Wm = sum(1 << i for i in Wl)
print("H* (innermost slack richer suffix) =", L.nm(n, H), "  j* =", js)
print("S =", L.nm(n, S), "  W =", L.nm(n, Wm),
      "  all strict losers =", L.nm(n, sum(1 << i for i in range(n) if D[i] < 0)),
      "  gainers =", L.nm(n, sum(1 << i for i in range(n) if D[i] > 0)))
print("s_phi(S) =", str(L.slack(n, V, PHI, S)), "  alpha =", ALPHA,
      "  rho =", str(ALPHA - L.slack(n, V, PHI, S)),
      "  alpha_ex =", str(L.alpha_exact_max(n, V, S)),
      "  g(S) =", str(L.g_of(n, V, S)))
print()
print("C-C RIGHT  H* subset S :", (H & ~S) == 0)
print("C-C LEFT   W subset H* :", (Wm & ~H) == 0, "   <-- REFUTED" if (Wm & ~H) else "")
print()
print("--- proved statements re-checked on this instance ---")
print("Theorem A  loss(W) <= s_phi(W):",
      sum(PHI[i] - PHI2[i] for i in Wl) <= L.slack(n, V, PHI, Wm),
      "  loss =", str(sum(PHI[i] - PHI2[i] for i in Wl)),
      " s_phi(W) =", str(L.slack(n, V, PHI, Wm)))
print("Prop D+ (phi-tight T => Delta(T) >= 0):",
      all(L.xsum(D, n, T) >= 0 for T in L.masks(n) if L.xsum(PHI, n, T) == V[T]))
print("Lemma C+ (phi'-tight T != S => Delta(T) <= 0):",
      all(L.xsum(D, n, T) <= 0 for T in L.masks(n)
          if T != S and L.xsum(PHI2, n, T) == W2[T]))
print("Delta(S) =", str(L.xsum(D, n, S)), " >= rho:",
      L.xsum(D, n, S) >= ALPHA - L.slack(n, V, PHI, S))
print("some outsider loses (Lemma reduce iii):",
      any(D[i] < 0 for i in range(n) if not S >> i & 1))
print()
print("--- the retired identifications on this instance ---")
print("C-A  (W is a slack richer suffix):",
      Wm in [Hj for _, Hj, s in suf if s > 0], " (W =", L.nm(n, Wm),
      "= the OUTER slack suffix H_1)")
print("aux: every player richer than the richest loser is frozen:",
      all(D[i] == 0 for i in range(n)
          if PHI[i] > max(PHI[k] for k in range(n) if D[k] < 0)))
print("aux: outsider losers strictly poorer than insider losers:",
      max([PHI[i] for i in range(n) if D[i] < 0 and not S >> i & 1] or [F(-1)])
      < min(PHI[i] for i in Wl))
