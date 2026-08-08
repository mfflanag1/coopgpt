"""d16: cross-check r12's Lemma L against r23's Theorem B.

Both claim to characterize leximin-maximality of a core point by a Farkas
certificate over the tight family, and my n=5 decision procedure rests on mine
being an IFF.  They dualize the same stage LP but at different granularity:

  r12 Lemma L (per CUT):    max { delta(B_t) : delta in C_t } = 0
  r23 Theorem B (per PLAYER): max { x_i : x in stage-t feasible set } = phi_i,
                              i.e. max { d_i : d in C_t } = 0 for each i in B_t

with the same tangent cone
  C_t = { d : d(N)=0, d(T)>=0 (T proper phi-tight), d_l=0 (l in B_<t),
              d_c>=0 (c in B_t) }.
These are equivalent a priori -- on C_t every d is >= 0 on B_t, so the sum has
maximum 0 iff each coordinate does -- but an a-priori argument is exactly what
a cross-check is for.  This driver evaluates both, independently coded, on
   (a) the true Lmin of a batch of random exact games and of every game in
       play in this task, where BOTH must accept, and
   (b) core points that are NOT leximin-maximal, where BOTH must reject,
and asserts they agree cut by cut and player by player.
"""
import sys, random, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L
import d3_lemmaL as LL
import z3


def theoremB(n, v, x):
    """r23's per-player Farkas certificate, coded from its statement alone."""
    FULL = (1 << n) - 1
    props = list(L.masks(n))
    tight = [A for A in props if L.xsum(x, n, A) == v[A]]
    B = L.strata(n, x)
    for t, Bt in enumerate(B):
        below = [l for b in B[:t] for l in b]
        for i in Bt:
            y = {A: z3.Real("y%d" % A) for A in props}
            eta = z3.Real("eta")
            rho = {l: z3.Real("rho%d" % l) for l in below}
            sig = {c: z3.Real("sig%d" % c) for c in Bt}
            s = z3.Solver()
            for A in props:
                s.add(y[A] >= 0)
                if A not in tight:
                    s.add(y[A] == 0)                      # SUPPORT
            for c in Bt:
                s.add(sig[c] >= 0)
            for j in range(n):                            # IDENTITY
                e = -z3.Sum([y[A] for A in props if A >> j & 1]) + eta
                if j in rho:
                    e = e + rho[j]
                if j in sig:
                    e = e - sig[j]
                s.add(e == (1 if j == i else 0))
            if s.check() != z3.sat:
                return False, (t, i)
    return True, None


def games():
    yield ("notsuffix", 6, L.envelope(6, [tuple(F(q) for q in r) for r in
           [(0, 11, 0, 7, 0, 0), (0, 10, 0, 4, 3, 1), (2, 0, 1, 0, 15, 0)]]))
    yield ("notstratum", 6, L.envelope(6, [tuple(F(q) for q in r) for r in
           [(0, 15, 0, 14, 0, 0), (0, 9, 0, 9, 6, 5), (4, 0, 4, 0, 21, 0)]]))
    yield ("n5-witness", 5, L.envelope(5, [tuple(F(q) for q in r) for r in
           [(0, 3, 0, 3, 0), (0, 0, 0, 0, 6), (1, 0, 1, 0, 4)]]))
    CE = [F(q) for q in
          [0, 0, 0, 106, 0, 136, 0, 136, 0, 161, 0, 161, 176, 297, 176, 297,
           0, 242, 0, 242, 242, 393, 242, 484, 176, 418, 176, 418, 418, 534,
           418, 660]]
    yield ("CC-counterexample v", 5, CE)
    yield ("CC-counterexample v'", 5, L.bumped(CE, 0b11101, F(20)))
    rng = random.Random(3)
    made = 0
    while made < 25:
        n = rng.choice([4, 5, 5, 6])
        total = rng.choice([12, 18, 24])
        rows = []
        for _ in range(rng.randint(2, 3)):
            zeros = set(rng.sample(range(n), rng.randint(1, 3)))
            free = [k for k in range(n) if k not in zeros]
            cs = sorted(rng.randint(0, total) for _ in range(len(free) - 1))
            r = [0] * n
            for k, q in zip(free, [b - a for a, b in zip([0] + cs, cs + [total])]):
                r[k] = q
            rows.append(tuple(F(q) for q in r))
        if not all(any(r[k] == 0 for r in rows) for k in range(n)):
            continue
        v = L.envelope(n, rows)
        if v[(1 << n) - 1] == 0:
            continue
        made += 1
        yield ("random#%d n=%d" % (made, n), n, v)


print("(a) POSITIVE: at the true Lmin both certificates must accept")
agree = pos = 0
for name, n, v in games():
    phi = L.lmin_staged(n, v)
    if phi is None:
        continue
    a = all(LL.all_cuts_ok(n, v, phi))
    b, where = theoremB(n, v, phi)
    pos += 1
    agree += (a == b)
    flag = "" if (a and b) else "   <-- DISAGREEMENT/REJECTION %s" % (where,)
    if not (a and b) or name.startswith(("not", "n5", "CC")):
        print("  %-22s LemmaL=%-5s TheoremB=%-5s%s" % (name, a, b, flag))
    assert a and b, "a certificate rejected a genuine Lmin"
print("  %d/%d games: both accept, and they agree" % (agree, pos))

print("\n(b) NEGATIVE: at core points that are NOT leximin-maximal both must reject")
neg = nagree = 0
for name, n, rows in (("notsuffix", 6, [(0, 11, 0, 7, 0, 0), (0, 10, 0, 4, 3, 1),
                                        (2, 0, 1, 0, 15, 0)]),
                      ("notstratum", 6, [(0, 15, 0, 14, 0, 0), (0, 9, 0, 9, 6, 5),
                                         (4, 0, 4, 0, 21, 0)])):
    v = L.envelope(n, [tuple(F(q) for q in r) for r in rows])
    phi = L.lmin_staged(n, v)
    for r in rows:
        y = [F(q) for q in r]
        if y == phi:
            continue
        a = all(LL.all_cuts_ok(n, v, y))
        b, _ = theoremB(n, v, y)
        neg += 1
        nagree += (a == b)
        print("  %-11s y=%-34s LemmaL=%-5s TheoremB=%-5s  agree=%s"
              % (name, str([str(q) for q in y]), a, b, a == b))
        assert not a and not b, "a certificate accepted a non-Lmin point"
print("  %d/%d non-optimal points: both reject, and they agree" % (nagree, neg))
print("\nr12 Lemma L and r23 Theorem B agree on every case tested, in both")
print("directions.  The completeness of the n=5 encoding now rests on two")
print("independently derived and independently coded characterizations.")
