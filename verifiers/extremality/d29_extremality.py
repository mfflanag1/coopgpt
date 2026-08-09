"""d29: DESIGNED stress-test of two-generator extremality at n = 6, 7.

Conjecture under test (paper5 sec:scope item 3): s(n) = s_2(n), the
two-generator maximum, i.e.
        s(6) = 2/3   (attained by G(2,3)),      s(7) = 5/6   (G(2,4), G(3,3)).
A game with rho > those values refutes it.  We are hunting the refutation.

DESIGN, not volume.  The two-generator enumeration already covers the
G-family shape, and random harvests concentrate elsewhere; the regions below
are chosen to be where neither looks.  The n = 5 extremal class is
qualitatively unlike the n >= 6 one -- it has a STARVED Lmax (a player at
zero) and a (3,2)/(1,4) configuration, while G(p,k) has strictly positive
Lmax -- so the natural designed target is the hybrid: n = 6,7 games carrying
the n = 5 extremal's starvation together with the n >= 6 family's cap
structure.

  region A  STARVED-LMAX HYBRIDS.  Three or four generators, one of them
            concentrated on a single player (the n=5 extremal's shape), the
            rest spread; keep only games whose Lmax starves somebody.
  region B  G-PERTURBATIONS.  Start from G(p,k)'s two generators at the right
            n and add a third, or perturb entries, keeping the common total
            and the vanishing-coordinate property so exactness stays free.
  region C  DEEP FLOORS.  One generator concentrated on a large coalition and
            one on its complement, so a single cap forces a deep floor -- the
            mechanism G(p,k) exploits, pushed with more than two generators.
  region D  DISJOINT-SUPPORT MULTIGEN.  Generators with pairwise disjoint
            supports (G's two are disjoint); three or four of them, which the
            two-generator class cannot express at all.

Every game is an envelope of nonnegative common-total rows in which every
coordinate vanishes in some row, so exactness and singleton normalization are
free (paper5 lem:envelope).  Both selections are computed exactly; any game
with rho above the bound is re-derived with the independent second algorithm
for each selection before it is reported.

usage: d29_extremality.py <n> <budget_s> <seed>
"""
import sys, time, json, random
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L

n = int(sys.argv[1])
budget = float(sys.argv[2])
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
FULL = (1 << n) - 1
BOUND = {6: F(2, 3), 7: F(5, 6)}[n]
rng = random.Random(seed)
print("n=%d  hunting rho > %s (the two-generator maximum)" % (n, BOUND), flush=True)

st = {r: dict(tried=0, games=0, starved=0, best="0", ties=0, above=0)
      for r in "ABCD"}
hits, best_overall = [], (F(0), None)


def wellformed(rows):
    if any(q < 0 for r in rows for q in r):
        return False
    if len({sum(r) for r in rows}) != 1 or sum(rows[0]) <= 0:
        return False
    if any(min(r[k] for r in rows) != 0 for k in range(n)):
        return False
    return len(set(rows)) == len(rows)


def spread(total, slots):
    if slots == 1:
        return [total]
    cuts = sorted(rng.randint(0, total) for _ in range(slots - 1))
    return [b - a for a, b in zip([0] + cuts, cuts + [total])]


def gen_A(total):
    """starved-Lmax hybrid: one generator on a single player, others spread"""
    rows = []
    j = rng.randrange(n)
    r = [0] * n
    r[j] = total
    rows.append(tuple(r))
    for _ in range(rng.randint(2, 3)):
        z = rng.randint(1, n - 2)
        zeros = set(rng.sample(range(n), z))
        free = [k for k in range(n) if k not in zeros]
        r = [0] * n
        for k, q in zip(free, spread(total, len(free))):
            r[k] = q
        rows.append(tuple(r))
    return rows


def gen_B(total):
    """perturbation of a G(p,k) pair at this n, plus an optional third row"""
    ks = [k for k in range(2, n) if 1 <= n - 1 - k]
    k = rng.choice(ks)
    p = n - 1 - k
    if p < 1:
        return None
    T = p * k
    g = [p * (k - 1)] + [1] * p + [0] * k
    h = [0] * (p + 1) + [p] * k
    perm = list(range(n))
    rng.shuffle(perm)
    g = [g[perm[i]] for i in range(n)]
    h = [h[perm[i]] for i in range(n)]
    rows = [tuple(g), tuple(h)]
    if rng.random() < 0.7:                       # add a third generator
        z = rng.randint(1, n - 2)
        zeros = set(rng.sample(range(n), z))
        free = [q for q in range(n) if q not in zeros]
        r = [0] * n
        for q, val in zip(free, spread(T, len(free))):
            r[q] = val
        rows.append(tuple(r))
    return rows


def gen_C(total):
    """deep floor: a big coalition against its complement, plus extra rows"""
    sz = rng.randint(2, n - 2)
    Sset = set(rng.sample(range(n), sz))
    r1 = [0] * n
    for k, q in zip(sorted(Sset), spread(total, sz)):
        r1[k] = q
    r2 = [0] * n
    comp = [k for k in range(n) if k not in Sset]
    for k, q in zip(comp, spread(total, len(comp))):
        r2[k] = q
    rows = [tuple(r1), tuple(r2)]
    for _ in range(rng.randint(0, 2)):
        z = rng.randint(1, n - 2)
        zeros = set(rng.sample(range(n), z))
        free = [k for k in range(n) if k not in zeros]
        r = [0] * n
        for k, q in zip(free, spread(total, len(free))):
            r[k] = q
        rows.append(tuple(r))
    return rows


def gen_D(total):
    """three or four generators with pairwise disjoint supports"""
    nr = rng.randint(3, 4)
    if nr > n:
        return None
    parts = [[] for _ in range(nr)]
    order = list(range(n))
    rng.shuffle(order)
    for idx, pl in enumerate(order):
        parts[idx % nr].append(pl)
    rows = []
    for blk in parts:
        if not blk:
            return None
        r = [0] * n
        for k, q in zip(blk, spread(total, len(blk))):
            r[k] = q
        rows.append(tuple(r))
    return rows


GENS = dict(A=gen_A, B=gen_B, C=gen_C, D=gen_D)
t0 = time.time()
while time.time() - t0 < budget:
    reg = rng.choice("ABCD")
    total = rng.choice([6, 8, 10, 12, 15, 18, 20, 24, 30])
    rows = GENS[reg](total)
    st[reg]["tried"] += 1
    if rows is None or not wellformed(rows):
        continue
    v = L.envelope(n, [tuple(F(q) for q in r) for r in rows])
    if v[FULL] == 0:
        continue
    mn = L.lmin_staged(n, v)
    if mn is None:
        continue
    mx = L.lmax_staged(n, v)
    if mx is None:
        continue
    st[reg]["games"] += 1
    if min(mx) == 0:
        st[reg]["starved"] += 1
    r = L.rho(n, v, mn, mx)
    if r > F(st[reg]["best"]):
        st[reg]["best"] = str(r)
    if r == BOUND:
        st[reg]["ties"] += 1
    if r > best_overall[0]:
        best_overall = (r, rows)
    if r > BOUND:
        st[reg]["above"] += 1
        mn2 = L.lmin_ladder(n, v)
        mx2 = L.lmax_ladder(n, v)
        rec = dict(region=reg, n=n, rows=[list(q) for q in rows],
                   rho=str(r), bound=str(BOUND),
                   Lmin=[str(q) for q in mn], Lmax=[str(q) for q in mx],
                   second_algorithms_agree=(mn2 == mn and mx2 == mx))
        hits.append(rec)
        print("*** ABOVE THE TWO-GENERATOR BOUND ***", json.dumps(rec), flush=True)
    tot = sum(st[q]["games"] for q in "ABCD")
    if tot and tot % 2000 == 0:
        print("  t=%.0fs %s" % (time.time() - t0, json.dumps(st)), flush=True)

out = dict(n=n, bound=str(BOUND), stats=st,
           best_overall=dict(rho=str(best_overall[0]),
                             rows=[list(q) for q in best_overall[1]]
                             if best_overall[1] else None),
           hits=hits)
json.dump(out, open("extremal_%d_%d.json" % (n, seed), "w"), indent=1)
print(json.dumps(out["stats"], indent=1))
print("best rho found: %s   (bound %s)   games above: %d"
      % (best_overall[0], BOUND, len(hits)))
