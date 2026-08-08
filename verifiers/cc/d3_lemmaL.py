"""d3: verify Lemma L (the leximin optimality certificate) computationally,
with a positive control and a drop-the-hypothesis negative control.

Lemma L.  phi leximin-maximal on core(v), strata B_1 < ... < B_k, richer
suffixes H_j.  Then for every j there are lambda_T >= 0 supported on proper
phi-tight coalitions and nu with
    sum_{T ni i} lambda_T = nu      (i in H_j)
    sum_{T ni i} lambda_T <= nu - 1 (i in B_j).

POSITIVE control : the certificate must exist at every cut of a true Lmin.
NEGATIVE control : for a core point that is NOT leximin-maximal, some cut must
                   fail to have a certificate (otherwise the lemma is vacuous).
"""
import sys, random, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L
import z3


def cert_exists(n, v, x, cut_H, cut_B):
    """Is there a Lemma-L certificate at the cut (H, B) for allocation x?"""
    tight = [T for T in L.masks(n) if L.xsum(x, n, T) == v[T]]
    lam = {T: z3.Real("L%d" % T) for T in tight}
    nu = z3.Real("nu")
    s = z3.Solver()
    for T in tight:
        s.add(lam[T] >= 0)
    for i in range(n):
        cover = z3.Sum([lam[T] for T in tight if T >> i & 1]) if tight else z3.RealVal(0)
        if cut_H >> i & 1:
            s.add(cover == nu)
        elif cut_B >> i & 1:
            s.add(cover <= nu - 1)
    return s.check() == z3.sat


def all_cuts_ok(n, v, x):
    """Check Lemma L at every cut of the payoff order of x.  Returns list of results."""
    B = L.strata(n, x)
    out = []
    for j in range(len(B)):
        H = sum(1 << i for b in B[j + 1:] for i in b)
        Bj = sum(1 << i for i in B[j])
        out.append(cert_exists(n, v, x, H, Bj))
    return out


CASES = [
    ("notsuffix", 6, [(0, 11, 0, 7, 0, 0), (0, 10, 0, 4, 3, 1), (2, 0, 1, 0, 15, 0)]),
    ("notstratum", 6, [(0, 15, 0, 14, 0, 0), (0, 9, 0, 9, 6, 5), (4, 0, 4, 0, 21, 0)]),
]
print("POSITIVE CONTROL on the two paper4 games")
for name, n, rows in CASES:
    v = L.envelope(n, [tuple(F(q) for q in r) for r in rows])
    phi = L.lmin_staged(n, v)
    res = all_cuts_ok(n, v, phi)
    print("  %-11s cuts %s   all certificates exist: %s" % (name, res, all(res)))
    assert all(res), "Lemma L FAILED on a genuine Lmin -- derivation is wrong"

print("\nPOSITIVE CONTROL on random exact games (every cut of a true Lmin)")
rng = random.Random(7)
tot = ok = 0
for t in range(120):
    n = rng.choice([4, 5, 5, 6])
    total = rng.choice([12, 18, 24])
    rows = []
    for _ in range(rng.randint(2, 3)):
        zeros = set(rng.sample(range(n), rng.randint(1, 3)))
        free = [i for i in range(n) if i not in zeros]
        cuts = sorted(rng.randint(0, total) for _ in range(len(free) - 1))
        r = [0] * n
        for i, p in zip(free, [b - a for a, b in zip([0] + cuts, cuts + [total])]):
            r[i] = p
        rows.append(tuple(F(q) for q in r))
    if not all(any(r[i] == 0 for r in rows) for i in range(n)):
        continue
    v = L.envelope(n, rows)
    if v[(1 << n) - 1] == 0:
        continue
    phi = L.lmin_staged(n, v)
    if phi is None:
        continue
    res = all_cuts_ok(n, v, phi)
    tot += 1
    ok += all(res)
    if not all(res):
        print("  LEMMA L FAILURE", n, [str(q) for q in v], [str(q) for q in phi], res)
print("  %d/%d games: certificate at every cut" % (ok, tot))

print("\nNEGATIVE CONTROL: core points that are not leximin-maximal")
bad_total = bad_fail = 0
rng = random.Random(11)
for name, n, rows in CASES:
    v = L.envelope(n, [tuple(F(q) for q in r) for r in rows])
    phi = L.lmin_staged(n, v)
    gens = [tuple(F(q) for q in r) for r in rows]
    for g in gens:
        y = list(g)
        if y == phi:
            continue
        res = all_cuts_ok(n, v, y)
        bad_total += 1
        bad_fail += (not all(res))
        print("  %-11s y=%s  cuts %s  -> certificate fails somewhere: %s"
              % (name, [str(q) for q in y], res, not all(res)))
print("  %d/%d non-leximin core points are detected (certificate fails)"
      % (bad_fail, bad_total))
