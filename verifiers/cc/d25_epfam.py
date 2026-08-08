"""d25: DESIGNED exact-partition search at n = 6 by the family trick.

Random exact-partition bases are cheap (355 of 400 games) but admissible exact
windows inside them are scarce (8 per 2488 prefiltered coalitions), so random
volume buys very little.  The trick that produced thousands of violations in the
C-C^ round applies here too:

  Phase 1  hunt until a handful of exact-partition bases that DO carry a window
           are found, and record them.
  Phase 2  perturb each such base's generator rows, keeping the common total and
           the zero pattern so exactness and singleton-normalization stay free,
           keep the perturbations that are still at exact partition, and scan
           every admissible exact bump in them for a monotonicity failure.

Bump sizes come from the exact window endpoint (Lemma WIN), so every bump tried
is exact by construction.

usage: d25_epfam.py <n> <phase1_budget_s> <phase2_budget_s> <seed>
"""
import sys, time, json, random
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L

n = int(sys.argv[1])
b1 = float(sys.argv[2])
b2 = float(sys.argv[3])
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
FULL = (1 << n) - 1
rng = random.Random(seed)


def rand_rows(total, nr):
    rows = []
    for _ in range(nr):
        z = rng.randint(1, max(1, n // 2))
        zeros = set(rng.sample(range(n), z))
        free = [k for k in range(n) if k not in zeros]
        cs = sorted(rng.randint(0, total) for _ in range(len(free) - 1))
        r = [0] * n
        for k, q in zip(free, [b - a for a, b in zip([0] + cs, cs + [total])]):
            r[k] = q
        rows.append(tuple(r))
    if not all(any(r[k] == 0 for r in rows) for k in range(n)):
        return None
    if len(set(rows)) != len(rows):
        return None
    return rows


def analyse(rows, st, hits):
    """Returns True if the base is at exact partition and carries a window."""
    v = L.envelope(n, [tuple(F(q) for q in r) for r in rows])
    if v[FULL] == 0:
        return False
    phi = L.lmin_staged(n, v)
    if phi is None:
        return False
    st["games"] += 1
    suf = L.suffixes(n, v, phi)
    if not suf or any(s != 0 for _, _, s in suf):
        return False
    st["expart"] += 1
    got = False
    for S in range(1, FULL):
        if bin(S).count("1") < 2:
            continue
        sS = L.slack(n, v, phi, S)
        g = L.g_of(n, v, S)
        if g is None or g <= sS:
            continue
        amax = L.alpha_exact_max(n, v, S)
        if amax is None or amax <= sS:
            continue
        st["windows"] += 1
        got = True
        for k in range(1, 9):
            al = sS + (amax - sS) * F(k, 8)
            st["bumps"] += 1
            w = L.bumped(v, S, al)
            p2 = L.lmin_staged(n, w)
            if p2 is None:
                continue
            Wl = [i for i in L.members(n, S) if p2[i] < phi[i]]
            if not Wl:
                continue
            ok, _ = L.exactness_report(n, w)
            if not ok:
                continue
            assert L.lmin_ladder(n, w) == p2
            st["viol"] += 1
            rec = dict(n=n, rows=[list(r) for r in rows], S=L.nm(n, S),
                       alpha=str(al), phi=[str(q) for q in phi],
                       phi2=[str(q) for q in p2],
                       W=L.nm(n, sum(1 << i for i in Wl)),
                       suffixes=[[L.nm(n, Hj), str(s)] for _, Hj, s in suf])
            hits.append(rec)
            print("*** EXACT-PARTITION FAILURE ***", json.dumps(rec), flush=True)
    return got


st = dict(games=0, expart=0, windows=0, bumps=0, viol=0,
          seeds_found=0, perturbed=0, perturb_expart=0)
hits = []
seeds = []
t0 = time.time()
print("phase 1: hunting exact-partition bases that carry a window", flush=True)
while time.time() - t0 < b1:
    rows = rand_rows(rng.choice([6, 8, 12, 18, 24, 30]), rng.randint(2, 4))
    if rows is None:
        continue
    if analyse(rows, st, hits):
        seeds.append(rows)
        st["seeds_found"] += 1
        print("  window-bearing exact-partition base #%d: %s"
              % (len(seeds), rows), flush=True)
print("  phase 1 done: %d seed bases, %s" % (len(seeds), st), flush=True)

print("\nphase 2: families around those bases", flush=True)


def perturb(rows, spread):
    out = []
    for r in rows:
        nz = [k for k in range(n) if r[k] != 0]
        if len(nz) < 2:
            out.append(tuple(r))
            continue
        absorb = max(nz, key=lambda k: r[k])
        new = list(r)
        for k in nz:
            if k == absorb:
                continue
            new[k] = r[k] + rng.randint(-spread, spread)
            if new[k] <= 0:
                return None
        new[absorb] = sum(r) - sum(new[k] for k in nz if k != absorb)
        if new[absorb] <= 0:
            return None
        out.append(tuple(new))
    if len({sum(r) for r in out}) != 1:
        return None
    if any(all(r[k] != 0 for r in out) for k in range(n)):
        return None
    if len(set(out)) != len(out):
        return None
    return out


t1 = time.time()
while seeds and time.time() - t1 < b2:
    base = rng.choice(seeds)
    rows = perturb(base, rng.choice([1, 2, 3]))
    if rows is None:
        continue
    st["perturbed"] += 1
    before = st["expart"]
    analyse(rows, st, hits)
    if st["expart"] > before:
        st["perturb_expart"] += 1
    if st["perturbed"] % 400 == 0:
        print("  t=%.0fs %s" % (time.time() - t0, st), flush=True)

json.dump(dict(stats=st, seeds=[[list(r) for r in s] for s in seeds],
               hits=hits), open("epfam_%d_%d.json" % (n, seed), "w"), indent=1)
print(json.dumps(st, indent=1))
print("exact-partition monotonicity failures found:", len(hits))
