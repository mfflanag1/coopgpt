"""Leximin / leximax-min core points computed with the home-grown exact simplex.

Variable layout for a stage: y = (x_0..x_{n-1}, t).  All variables >= 0, which is
valid because the game is singleton-normalized (so core points have x_i >= 0) and
t is a min/max of nonnegative numbers.
"""
from fractions import Fraction as F
from simplex import lp_max, lp_min


def _base_rows(n, v, pinned):
    """Rows of A y <= b for the core (variables y_0..y_{n-1}=x, y_n=t)."""
    full = (1 << n) - 1
    A, b = [], []
    e = lambda: [F(0)] * (n + 1)
    r = e();
    for i in range(n): r[i] = F(1)
    A.append(r[:]); b.append(F(v[full]))            #  sum x <= T
    r2 = [-q for q in r]; A.append(r2); b.append(-F(v[full]))   # -sum x <= -T
    for S in range(1, full):
        r = e()
        for i in range(n):
            if S >> i & 1:
                r[i] = F(-1)
        A.append(r); b.append(-F(v[S]))             # -x(S) <= -v(S)
    for j, val in pinned.items():
        r = e(); r[j] = F(1); A.append(r); b.append(F(val))
        r = e(); r[j] = F(-1); A.append(r); b.append(-F(val))
    return A, b


def lex_point_with_trace(n, v, mode):
    """Return the selected point and an exact trace of its lexicographic stages.

    ``mode='min'`` computes leximin and ``mode='max'`` computes leximax-min.
    The trace records the level, the coordinates newly forced to that level,
    and those still free after each stage.  Recording the *forced* coordinates
    matters when auditing packet certificates: a first-stage aggregate dual
    need not certify that every coordinate displayed at the trial level is
    individually pinned.
    """
    pinned, free = {}, set(range(n))
    trace = []
    guard = 0
    while free and guard <= n:
        guard += 1
        A, b = _base_rows(n, v, pinned)
        for i in free:
            r = [F(0)] * (n + 1)
            if mode == 'min':
                r[i] = F(-1); r[n] = F(1)           #  t - x_i <= 0
            else:
                r[i] = F(1); r[n] = F(-1)           #  x_i - t <= 0
            A.append(r); b.append(F(0))
        c = [F(0)] * (n + 1); c[n] = F(1)
        val, _ = (lp_max(c, A, b) if mode == 'min' else lp_min(c, A, b))
        assert not isinstance(val, str), f"stage LP {val}"
        lvl = val
        # pin the players forced to the level
        A2, b2 = _base_rows(n, v, pinned)
        for k in free:
            r = [F(0)] * (n + 1)
            if mode == 'min':
                r[k] = F(-1); A2.append(r); b2.append(-lvl)   # x_k >= lvl
            else:
                r[k] = F(1); A2.append(r); b2.append(lvl)     # x_k <= lvl
        newly = []
        for i in sorted(free):
            c2 = [F(0)] * (n + 1); c2[i] = F(1)
            v2, _ = (lp_max(c2, A2, b2) if mode == 'min' else lp_min(c2, A2, b2))
            assert not isinstance(v2, str), f"pin LP {v2}"
            if v2 == lvl:
                newly.append(i)
        assert newly, "stage pinned nobody"
        for i in newly:
            pinned[i] = lvl
            free.discard(i)
        trace.append({
            "level": lvl,
            "newly_pinned": tuple(newly),
            "remaining_free": tuple(sorted(free)),
        })
    assert not free, "guard exceeded"
    return [pinned[i] for i in range(n)], trace


def lex_point(n, v, mode):
    """mode='min' -> leximin;  mode='max' -> leximax-min."""
    point, _ = lex_point_with_trace(n, v, mode)
    return point


def sx_lmin(n, v):
    return lex_point(n, v, 'min')


def sx_lmax(n, v):
    return lex_point(n, v, 'max')
