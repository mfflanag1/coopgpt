"""r12 toolkit: exact-rational cooperative-game utilities for the C-C containment work.

Everything is Fraction / z3-Real exact.  No floats anywhere.

Conventions
-----------
n players 0..n-1, coalitions are bitmasks 1..FULL where FULL = 2^n - 1.
v is a list of Fractions indexed by mask, v[0] = 0.
"Lmin" = the leximin-maximal core element (unique), computed two independent ways.
"""
from fractions import Fraction as F
import itertools
import z3


# ---------------------------------------------------------------- basics
def masks(n):
    return range(1, (1 << n) - 1)


def members(n, T):
    return [i for i in range(n) if T >> i & 1]


def nm(n, T):
    return "{" + ",".join(str(i + 1) for i in members(n, T)) + "}"


def xsum(x, n, T):
    return sum(x[i] for i in members(n, T))


def envelope(n, gens):
    """Lower envelope of common-total nonnegative rows: an exact game (paper4 Lemma)."""
    full = (1 << n) - 1
    total = sum(gens[0])
    for g in gens:
        assert sum(g) == total, "rows must share a common total"
        assert all(q >= 0 for q in g), "rows must be nonnegative"
    v = [F(0)] * (1 << n)
    for T in range(1, full):
        v[T] = min(sum(g[i] for i in members(n, T)) for g in gens)
    v[full] = F(total)
    return v


def is_sing_norm(n, v):
    return all(v[1 << i] == 0 for i in range(n))


def to_z3(q):
    q = F(q)
    return z3.RealVal("%d/%d" % (q.numerator, q.denominator))


def rat(e):
    e = z3.simplify(e)
    if z3.is_int_value(e):
        return F(e.as_long())
    if z3.is_rational_value(e):
        return F(e.numerator_as_long(), e.denominator_as_long())
    raise RuntimeError("non-rational %r" % (e,))


def core_constraints(n, v, x):
    full = (1 << n) - 1
    return [z3.Sum(x) == to_z3(v[full])] + [
        z3.Sum([x[i] for i in members(n, T)]) >= to_z3(v[T]) for T in masks(n)]


def core_min(n, v, T, x=None, base=None):
    """min_{core(v)} x(T); None if core empty.  Exact."""
    if x is None:
        x = [z3.Real("x%d" % i) for i in range(n)]
        base = core_constraints(n, v, x)
    o = z3.Optimize()
    o.add(base)
    h = o.minimize(z3.Sum([x[i] for i in members(n, T)]))
    if o.check() != z3.sat:
        return None
    return rat(o.lower(h))


def core_max(n, v, T, x=None, base=None):
    if x is None:
        x = [z3.Real("x%d" % i) for i in range(n)]
        base = core_constraints(n, v, x)
    o = z3.Optimize()
    o.add(base)
    h = o.maximize(z3.Sum([x[i] for i in members(n, T)]))
    if o.check() != z3.sat:
        return None
    return rat(o.upper(h))


def exactness_report(n, v):
    """(is_exact, list of coalitions where min_core x(T) != v(T)).  Exact, z3-certified."""
    x = [z3.Real("e%d" % i) for i in range(n)]
    base = core_constraints(n, v, x)
    s = z3.Solver()
    s.add(base)
    if s.check() != z3.sat:
        return False, ["EMPTY CORE"]
    bad = []
    for T in masks(n):
        m = core_min(n, v, T, x, base)
        if m != v[T]:
            bad.append((T, m, v[T]))
    return (not bad), bad


# ---------------------------------------------------------------- leximin
def lmin_staged(n, v):
    """Leximin-maximal core point by staged max-min with pinning (algorithm 1)."""
    full = (1 << n) - 1
    x = [z3.Real("a%d" % i) for i in range(n)]
    base = core_constraints(n, v, x)
    pinned, free = {}, set(range(n))
    while free:
        t = z3.Real("t")
        o = z3.Optimize()
        o.add(base)
        for j, val in pinned.items():
            o.add(x[j] == to_z3(val))
        for i in free:
            o.add(x[i] >= t)
        h = o.maximize(t)
        if o.check() != z3.sat:
            return None
        lvl = rat(o.upper(h))
        newly = []
        for i in sorted(free):
            o2 = z3.Optimize()
            o2.add(base)
            for j, val in pinned.items():
                o2.add(x[j] == to_z3(val))
            for k in free:
                o2.add(x[k] >= to_z3(lvl))
            h2 = o2.maximize(x[i])
            assert o2.check() == z3.sat
            if rat(o2.upper(h2)) == lvl:
                newly.append(i)
        assert newly, "stage pinned nobody"
        for i in newly:
            pinned[i] = lvl
            free.discard(i)
    return [pinned[i] for i in range(n)]


def lmin_ladder(n, v, check_unique=True):
    """Leximin-maximal core point by the Sigma_m ladder (algorithm 2, independent)."""
    full = (1 << n) - 1
    x = [z3.Real("b%d" % i) for i in range(n)]
    base = core_constraints(n, v, x)
    fixed = []
    for m in range(1, n + 1):
        s = z3.Real("s%d" % m)
        o = z3.Optimize()
        o.add(base + fixed + [s <= z3.Sum([x[i] for i in A])
                              for A in itertools.combinations(range(n), m)])
        h = o.maximize(s)
        if o.check() != z3.sat:
            return None
        best = rat(o.upper(h))
        fixed.append(z3.And([z3.Sum([x[i] for i in A]) >= to_z3(best)
                             for A in itertools.combinations(range(n), m)]))
    o = z3.Optimize()
    o.add(base + fixed)
    assert o.check() == z3.sat
    mdl = o.model()
    pt = [rat(mdl.eval(x[i], model_completion=True)) for i in range(n)]
    if check_unique:
        sv = z3.Solver()
        sv.add(base + fixed)
        sv.add(z3.Or([x[i] != to_z3(pt[i]) for i in range(n)]))
        assert sv.check() == z3.unsat, "ladder optimum not unique"
    return pt


def lmin(n, v, both=False):
    p = lmin_staged(n, v)
    if both:
        q = lmin_ladder(n, v)
        assert p == q, ("leximin algorithms disagree", p, q)
    return p


# ---------------------------------------------------------------- structure
def strata(n, phi):
    """Blocks of equal payoff, poorest first, as index lists."""
    order = sorted(range(n), key=lambda i: phi[i])
    blocks, cur = [], [order[0]]
    for i in order[1:]:
        if phi[i] == phi[cur[0]]:
            cur.append(i)
        else:
            blocks.append(cur)
            cur = [i]
    blocks.append(cur)
    return blocks


def suffixes(n, v, phi):
    """[(j, H_j mask, slack)] for j = 1..k-1, poorest cut first."""
    B = strata(n, phi)
    out = []
    for j in range(len(B) - 1):
        H = sum(1 << i for b in B[j + 1:] for i in b)
        out.append((j + 1, H, xsum(phi, n, H) - v[H]))
    return out


def hstar(n, v, phi):
    """(mask, j*) of the innermost slack richer suffix, or (None, None)."""
    sl = [(j, H) for j, H, s in suffixes(n, v, phi) if s > 0]
    if not sl:
        return None, None
    j, H = max(sl)
    return H, j


def slack(n, v, phi, T):
    return xsum(phi, n, T) - v[T]


def tight_sets(n, v, phi):
    return [T for T in masks(n) if xsum(phi, n, T) == v[T]]


# ---------------------------------------------------------------- bumps
def bumped(v, S, alpha):
    w = list(v)
    w[S] = v[S] + alpha
    return w


def alpha_feasible_max(n, v, S):
    """max alpha with core(v^{S,alpha}) nonempty = max_{core(v)} x(S) - v(S)."""
    m = core_max(n, v, S)
    return None if m is None else m - v[S]


def alpha_exact_max(n, v, S):
    """Exact right endpoint of the admissible bump window.

    For T != S proper, min_{core(v^{S,a})} x(T) is nondecreasing in a, and equals
    v(T) iff a <= beta_T := max{x(S) : x in core(v), x(T) = v(T)} - v(S).
    Hence v^{S,a} is exact for every a in [0, alpha_ex] with
    alpha_ex = min_{T != S} beta_T, and inexact for a > alpha_ex.
    Returns None if some T admits no core point with x(T) = v(T) (v not exact).
    """
    x = [z3.Real("f%d" % i) for i in range(n)]
    base = core_constraints(n, v, x)
    best = None
    for T in masks(n):
        if T == S:
            continue
        o = z3.Optimize()
        o.add(base)
        o.add(z3.Sum([x[i] for i in members(n, T)]) == to_z3(v[T]))
        h = o.maximize(z3.Sum([x[i] for i in members(n, S)]))
        if o.check() != z3.sat:
            return None
        b = rat(o.upper(h)) - v[S]
        if best is None or b < best:
            best = b
    return best


def alpha_exact_argmin(n, v, S):
    """(alpha_ex, T*, x*) where T* attains the minimum in alpha_exact_max and x*
    is an optimal core point for it (used to read off the binding structure)."""
    x = [z3.Real("k%d" % i) for i in range(n)]
    base = core_constraints(n, v, x)
    best = None
    for T in masks(n):
        if T == S:
            continue
        o = z3.Optimize()
        o.add(base)
        o.add(z3.Sum([x[i] for i in members(n, T)]) == to_z3(v[T]))
        h = o.maximize(z3.Sum([x[i] for i in members(n, S)]))
        if o.check() != z3.sat:
            return None, None, None
        b = rat(o.upper(h)) - v[S]
        if best is None or b < best[0]:
            m = o.model()
            pt = [rat(m.eval(x[i], model_completion=True)) for i in range(n)]
            best = (b, T, pt)
    return best


def g_of(n, v, S):
    out = [v[S | (1 << j)] - v[S] for j in range(n) if not S >> j & 1]
    return min(out) if out else None


def violation_record(n, v, phi, S, alpha, verify_exact=True, two_algos=True):
    """Full audited record of one bump.  Returns dict or None if not a violation."""
    w = bumped(v, S, alpha)
    if verify_exact:
        ok, bad = exactness_report(n, w)
        if not ok:
            return None
    phi2 = lmin(n, w, both=two_algos)
    if phi2 is None:
        return None
    W = [i for i in members(n, S) if phi2[i] < phi[i]]
    if not W:
        return None
    H, js = hstar(n, v, phi)
    Wm = sum(1 << i for i in W)
    return dict(n=n, v=v, w=w, S=S, alpha=alpha, phi=phi, phi2=phi2,
                W=Wm, Hstar=H, jstar=js,
                losers=sum(1 << i for i in range(n) if phi2[i] < phi[i]),
                gainers=sum(1 << i for i in range(n) if phi2[i] > phi[i]),
                left=(H is not None and (Wm & ~H) == 0),
                right=(H is not None and (H & ~S) == 0))
