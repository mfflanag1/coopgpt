"""Independent adversarial audit of the n<=4 Lmin/Lmax bridge.

Nothing here imports the project's code.  Lmin is recomputed with z3.Optimize
(exact LRA), exact games are generated as lower envelopes of common-total
allocations (which is *exactly* the class of exact games: v is exact iff it is
the lower envelope of its own core, and any lower envelope of common-total
points is exact).
"""
from fractions import Fraction as F
import itertools, random, sys
import z3


def envelope(n, gens):
    full = (1 << n) - 1
    total = sum(gens[0])
    v = [F(0)] * (1 << n)
    for S in range(1, full):
        v[S] = min(sum(g[i] for i in range(n) if S >> i & 1) for g in gens)
    v[full] = F(total)
    return v


def normalize(n, v):
    full = (1 << n) - 1
    m = [v[1 << i] for i in range(n)]
    w = [F(0)] * (1 << n)
    for S in range(1, full + 1):
        w[S] = v[S] - sum(m[i] for i in range(n) if S >> i & 1)
    return w, m


def solve(A, b):
    """Exact Gaussian elimination; None if singular."""
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
                f = M[r][c]
                M[r] = [M[r][j] - f * M[c][j] for j in range(k + 1)]
    return [M[r][k] for r in range(k)]


def core_vertices(n, v):
    full = (1 << n) - 1
    rows = [([F(1)] * n, F(v[full]))]
    ineq = [([F(1) if S >> i & 1 else F(0) for i in range(n)], F(v[S]))
            for S in range(1, full)]
    verts = set()
    for combo in itertools.combinations(range(len(ineq)), n - 1):
        A = [rows[0][0]] + [ineq[c][0] for c in combo]
        b = [rows[0][1]] + [ineq[c][1] for c in combo]
        x = solve(A, b)
        if x is None:
            continue
        if all(sum(a[i] * x[i] for i in range(n)) >= rhs for a, rhs in ineq):
            verts.add(tuple(x))
    return sorted(verts)


def is_exact(n, v, verts=None):
    """Definition-level exactness by exact rational vertex enumeration."""
    full = (1 << n) - 1
    if verts is None:
        verts = core_vertices(n, v)
    if not verts:
        return False
    for S in range(1, full):
        lo = min(sum(x[i] for i in range(n) if S >> i & 1) for x in verts)
        if lo != v[S]:
            return False
    return True


def to_z3(q):
    q = F(q)
    return z3.RealVal(f"{q.numerator}/{q.denominator}")


def rat(e):
    e = z3.simplify(e)
    if z3.is_int_value(e):
        return F(e.as_long())
    if z3.is_rational_value(e):
        return F(e.numerator_as_long(), e.denominator_as_long())
    raise RuntimeError(f"non-rational optimum {e!r}")


def lmin(n, v):
    """Leximin-above-singleton-floors core point, via staged exact optimization."""
    full = (1 << n) - 1
    x = [z3.Real(f"x{i}") for i in range(n)]
    m = [F(v[1 << i]) for i in range(n)]
    base = [z3.Sum(x) == to_z3(v[full])] + [
        z3.Sum([x[i] for i in range(n) if S >> i & 1]) >= to_z3(v[S])
        for S in range(1, full)
    ]
    pinned, free = {}, set(range(n))
    while free:
        t = z3.Real("t")
        o = z3.Optimize()
        o.add(base)
        for j, val in pinned.items():
            o.add(x[j] == to_z3(val))
        for i in free:
            o.add(x[i] - to_z3(m[i]) >= t)
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
                o2.add(x[k] - to_z3(m[k]) >= to_z3(lvl))
            h2 = o2.maximize(x[i])
            assert o2.check() == z3.sat
            if rat(o2.upper(h2)) == m[i] + lvl:
                newly.append(i)
        assert newly, "stage pinned nobody"
        for i in newly:
            pinned[i] = m[i] + lvl
            free.discard(i)
    return [pinned[i] for i in range(n)]


def strata(phi):
    """Blocks of equal payoff, poorest to richest, as player-index lists."""
    order = sorted(range(len(phi)), key=lambda i: phi[i])
    blocks, cur = [], [order[0]]
    for i in order[1:]:
        if phi[i] == phi[cur[0]]:
            cur.append(i)
        else:
            blocks.append(cur)
            cur = [i]
    blocks.append(cur)
    return blocks


def check_rst(n, w, phi):
    """Richer-suffix tightness.  Returns list of violations."""
    blocks = strata(phi)
    bad = []
    for j in range(len(blocks) - 1):
        H = sum(1 << i for b in blocks[j + 1:] for i in b)
        val = sum(phi[i] for i in range(n) if H >> i & 1)
        if val != w[H]:
            bad.append((j, H, val, w[H]))
    return bad


def rand_gens(n, rng, npts, total, hi):
    gens = []
    for _ in range(npts):
        while True:
            p = [rng.randint(0, hi) for _ in range(n - 1)]
            last = total - sum(p)
            if 0 <= last <= hi:
                gens.append(tuple(F(q) for q in p + [last]))
                break
    return gens


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    rng = random.Random(seed)
    full = (1 << n) - 1
    stats = {"games": 0, "rst_violations": 0, "lmax_mismatch": 0,
             "mono_pairs": 0, "mono_violations": 0, "compositions": {}}
    examples = []
    for _ in range(trials):
        total = rng.choice([8, 12, 16, 20])
        npts = rng.randint(2, 5)
        gens = rand_gens(n, rng, npts, total, total)
        v = envelope(n, gens)
        w, _ = normalize(n, v)
        if w[full] == 0:
            continue
        phi = lmin(n, w)
        if phi is None:
            continue
        stats["games"] += 1
        comp = tuple(len(b) for b in strata(phi))
        stats["compositions"][comp] = stats["compositions"].get(comp, 0) + 1
        bad = check_rst(n, w, phi)
        if bad:
            stats["rst_violations"] += 1
            examples.append(("RST", list(map(str, w)), list(map(str, phi)), bad))
            print("RST VIOLATION", [str(q) for q in w], [str(q) for q in phi], bad)

        # coalitional monotonicity on the exact domain, non-singleton bumps
        for S in range(1, full):
            if bin(S).count("1") == 1:
                continue
            for d in (F(1), F(2), F(1, 2)):
                w2 = list(w)
                w2[S] = w[S] + d
                if not is_exact(n, w2):
                    continue
                if any(w2[1 << i] != 0 for i in range(n)):
                    continue
                phi2 = lmin(n, w2)
                if phi2 is None:
                    continue
                stats["mono_pairs"] += 1
                drops = {i: (phi[i], phi2[i]) for i in range(n)
                         if S >> i & 1 and phi2[i] < phi[i]}
                if drops:
                    stats["mono_violations"] += 1
                    print("MONO VIOLATION n=%d S=%d d=%s" % (n, S, d))
                    print("  w =", [str(q) for q in w])
                    print("  phi =", [str(q) for q in phi],
                          "phi' =", [str(q) for q in phi2], drops)
                    examples.append(("MONO", list(map(str, w)), S, str(d),
                                     list(map(str, phi)), list(map(str, phi2))))
    print("n=%d" % n, stats)


if __name__ == "__main__":
    main()
