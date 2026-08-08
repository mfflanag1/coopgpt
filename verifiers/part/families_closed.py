"""TASK #29: CLOSED-FORM GENERATOR FAMILIES for PART(p,q), every (p,q).

Discharges Theorem G5/G6 of PROOF_FAMILY.txt.  Two explicit lower-envelope
families, uniform in (p,q), replacing the five audited instances plus padding.

Player order throughout: x_1..x_p | y_1..y_q | f, g.

FAMILY A  (p >= 2, q >= 2).  Common total m + 4; phi = 1 on L, 2 on H.
    A0   (1^p            | 1^q                  | 2, 2)      = phi
    A1   (2,2,1^{p-2}    | 0, 2, 1^{q-2}        | 0, 2)
    A2   (2,2,1^{p-2}    | 0, 4, 1^{q-2}        | 0, 0)
    A3_x (0 at x, 2 at one other, 1 elsewhere
                         | 0, 2, 1^{q-2}        | 2, 2)      one per x in P
    A4_j (2,2,1^{p-2}    | 0 at y_1 and y_j, 1 elsewhere | 0, 4)   j = 2..q

FAMILY B  (p = 1, q >= 3).  Put c = q - 1; common total 3q - 1; phi = 1 on L,
c on H.  Four rows only:
    B0   (1  | 1^q                    | c,     c)     = phi
    B1   (0  | q, q-1, 0^{q-2}        | 1+c,   0)
    B2   (1+c| 0, q-1, 0^{q-2}        | 0,     q)
    B3   (1  | 1, 0, 1^{q-2}          | c,     q)

The mirror of B (swap the two blocks) covers q = 1, p >= 3.  Families A, B and
mirror-B are disjoint and cover exactly {p,q >= 1, p+q >= 4}.

Each family is validated here end to end: exactness at definition level by
exact LP (n <= 7; for larger n the envelope lemma already proves it), Lmin
recomputed from scratch by staged exact optimization, strata, slack, the two
tight blocks and the split.

Usage: python3 families_closed.py
"""
from __future__ import annotations

import itertools
import sys
from fractions import Fraction as F

sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import lib23 as L

ok = True


def check(label, cond, extra=""):
    global ok
    ok = ok and bool(cond)
    print(f"  [{'OK ' if cond else 'FAIL'}] {label}" + (f"  {extra}" if extra else ""))


def familyA(p, q):
    """Rows of family A as integer lists, order x_1..x_p | y_1..y_q | f,g."""
    assert p >= 2 and q >= 2
    Pmid = [2, 2] + [1] * (p - 2)          # sums to p+2, each <= 2
    Qa = [0, 2] + [1] * (q - 2)            # sums to q
    Qb = [0, 4] + [1] * (q - 2)            # sums to q+2
    rows = []
    rows.append([1] * p + [1] * q + [2, 2])                    # A0 = phi
    rows.append(Pmid + Qa + [0, 2])                            # A1
    rows.append(Pmid + Qb + [0, 0])                            # A2
    for xi in range(p):                                        # A3_x
        Pr = [0] * p
        other = 0 if xi != 0 else 1
        for k in range(p):
            Pr[k] = 0 if k == xi else (2 if k == other else 1)
        rows.append(Pr + Qa + [2, 2])
    for j in range(1, q):                                      # A4_j, j=2..q
        Qr = [1] * q
        Qr[0] = 0
        Qr[j] = 0
        rows.append(Pmid + Qr + [0, 4])
    return rows


def familyB(q):
    """Rows of family B (p = 1), order a | y_1..y_q | f,g."""
    assert q >= 3
    c = q - 1
    rows = [
        [1] + [1] * q + [c, c],                                   # B0 = phi
        [0] + [q, q - 1] + [0] * (q - 2) + [1 + c, 0],            # B1
        [1 + c] + [0, q - 1] + [0] * (q - 2) + [0, q],            # B2
        [1] + [1, 0] + [1] * (q - 2) + [c, q],                    # B3
    ]
    return rows


def validate(rows, p, q, label, deep_exact=True):
    m = p + q
    n = m + 2
    f, g = n - 2, n - 1
    S1 = sum(1 << i for i in range(p)) | (1 << f)
    S2 = sum(1 << i for i in range(p, m)) | (1 << g)
    H = (1 << f) | (1 << g)
    FULL = (1 << n) - 1
    print(f"\n{label}: n={n}")
    tots = {sum(r) for r in rows}
    if len(tots) != 1:
        check("rows share a common total", False, str(sorted(tots)))
        return
    if any(x < 0 for r in rows for x in r):
        check("rows are nonnegative", False)
        return
    gens = [tuple(F(x) for x in r) for r in rows]
    v = L.envelope(n, gens)
    w, shift = L.normalize(n, v)
    check("singleton-normalized (every coordinate vanishes in some row)",
          all(x == 0 for x in shift))
    if deep_exact:
        ex, bad = L.is_exact_lp(n, w)
        check("EXACT at definition level (exact LP over the core)", ex,
              "" if ex else f"fails at {L.nm(n, bad)}")
    else:
        print("  [ -- ] exactness: by the envelope lemma (not re-run at this n)")
    phi = L.lmin(n, w)
    blocks = L.strata(phi)
    expected_lo = phi[0]
    check("Lmin has the two-stratum shape L < H",
          len(blocks) == 2
          and sorted(blocks[0]) == list(range(m))
          and sorted(blocks[1]) == [f, g],
          f"strata={[[L.LETTERS[i] for i in b] for b in blocks]}")
    slack = sum(phi[i] for i in range(n) if H >> i & 1) - w[H]
    check("H is slack", slack > 0, f"s = {slack}")
    tA = sum(phi[i] for i in range(n) if S1 >> i & 1) == w[S1]
    tB = sum(phi[i] for i in range(n) if S2 >> i & 1) == w[S2]
    check("S1 and S2 are Lmin-tight", tA and tB)
    check("S1, S2 partition N with traces {f}, {g}",
          (S1 | S2) == FULL and (S1 & S2) == 0
          and (S1 & H) == (1 << f) and (S2 & H) == (1 << g))
    print(f"       Lmin = {[str(x) for x in phi]}   s = {slack}   "
          f"v(N) = {w[FULL]}")
    return phi


print("=" * 78)
print("FAMILY A  (p >= 2, q >= 2)")
print("=" * 78)
for (p, q) in [(2, 2), (2, 3), (3, 2), (3, 3), (2, 4), (4, 2),
               (2, 5), (5, 2), (3, 4), (4, 3)]:
    validate(familyA(p, q), p, q, f"A({p},{q})", deep_exact=(p + q + 2 <= 7))

print()
print("=" * 78)
print("FAMILY B  (p = 1, q >= 3)")
print("=" * 78)
for q in (3, 4, 5, 6):
    validate(familyB(q), 1, q, f"B(1,{q})", deep_exact=(1 + q + 2 <= 7))

print()
print("=" * 78)
print("MIRROR OF B  (q = 1, p >= 3): swap the two blocks")
print("=" * 78)


def mirrorB(p):
    """Swap blocks: rows of B(1,p) reordered as y-block first, then a, then g,f."""
    q = p
    out = []
    for r in familyB(q):
        a, ys, ff, gg = r[0], r[1:1 + q], r[-2], r[-1]
        out.append(list(ys) + [a] + [gg, ff])
    return out


for p in (3, 4, 5, 6):
    validate(mirrorB(p), p, 1, f"mirrorB({p},1)", deep_exact=(p + 1 + 2 <= 7))

print()
print("ALL CHECKS PASSED" if ok else "SOME CHECK FAILED")
sys.exit(0 if ok else 1)
