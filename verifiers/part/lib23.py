"""Shared exact-arithmetic helpers for task #23 (PART(p,q) conjecture).

Discharges: nothing on its own.  Provides the primitives every driver uses.

Everything is exact rational (fractions.Fraction) or exact LRA (z3).

KEY ENCODING FACT USED THROUGHOUT
---------------------------------
A game v is EXACT iff for every coalition S there is a core point z^S with
z^S(S) = v(S).  That is a purely EXISTENTIAL linear condition, so exactness
can be encoded with no catalogue, no vertex enumeration and no reliance on
the completeness of the Studeny-Kratochvil list -- at any n.  We use it in
place of the 280/7006 min-semi-balanced inequalities of verifiers/zp/
exactcone.py; the catalogue cone is used only as an independent
cross-check at n=5.
"""
from __future__ import annotations

import itertools
from fractions import Fraction as F

import z3

LETTERS = "abcdefgh"


def nm(n, mask):
    return "".join(LETTERS[i] for i in range(n) if mask >> i & 1) or "0"


def bits(n, mask):
    return [i for i in range(n) if mask >> i & 1]


def to_z3(q):
    q = F(q)
    return z3.RealVal(f"{q.numerator}/{q.denominator}")


def rat(e):
    e = z3.simplify(e)
    if z3.is_int_value(e):
        return F(e.as_long())
    if z3.is_rational_value(e):
        return F(e.numerator_as_long(), e.denominator_as_long())
    raise RuntimeError(f"non-rational value {e!r}")


# ---------------------------------------------------------------- exact games

def envelope(n, gens):
    """Lower envelope of common-total allocations: always an exact game."""
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


def core_min(n, w, S):
    """min over core of x(S), by exact LP (z3 Optimize)."""
    full = (1 << n) - 1
    x = [z3.Real(f"x{i}") for i in range(n)]
    o = z3.Optimize()
    o.add(z3.Sum(x) == to_z3(w[full]))
    for T in range(1, full):
        o.add(z3.Sum([x[i] for i in range(n) if T >> i & 1]) >= to_z3(w[T]))
    h = o.minimize(z3.Sum([x[i] for i in range(n) if S >> i & 1]))
    assert o.check() == z3.sat
    return rat(o.lower(h))


def is_exact_lp(n, w):
    """Definition-level exactness WITHOUT vertex enumeration: check
    min_{core} x(S) == w[S] for every proper S, by exact LP."""
    full = (1 << n) - 1
    for S in range(1, full):
        if core_min(n, w, S) != w[S]:
            return False, S
    return True, None


def lmin(n, w):
    """Leximin core point (staged exact optimization), singleton floors 0."""
    full = (1 << n) - 1
    x = [z3.Real(f"x{i}") for i in range(n)]
    m = [F(w[1 << i]) for i in range(n)]
    base = [z3.Sum(x) == to_z3(w[full])] + [
        z3.Sum([x[i] for i in range(n) if S >> i & 1]) >= to_z3(w[S])
        for S in range(1, full)]
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
    """Blocks of equal payoff, poorest first, as index lists."""
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


def tight_family(n, w, phi):
    full = (1 << n) - 1
    return [T for T in range(1, full)
            if sum(phi[i] for i in range(n) if T >> i & 1) == w[T]]


# ------------------------------------------------- ordered set partitions

def all_ordered_partitions(elements):
    """Every ordered set partition, no canonicalisation."""
    elements = list(elements)
    if not elements:
        yield []
        return
    for r in range(1, len(elements) + 1):
        for first in itertools.combinations(elements, r):
            rest = [e for e in elements if e not in first]
            for tail in all_ordered_partitions(rest):
                yield [list(first)] + tail
