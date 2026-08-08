"""d24: (a) the two free structural lemmas about exact partition, verified;
        (b) a DESIGNED search for exact-partition monotonicity failures at
            n = 5, 6, 7.

LEMMA EP1.  If x in core(v) and every richer suffix H_j of x is x-tight, then x
is the leximin-maximal element of core(v).
PROOF.  Lemma L's certificate at cut j is witnessed by lambda = 1_{H_j}, nu = 1:
the cover is 1 = nu on H_j and 0 <= nu - 1 on B_j.  At the top cut take
lambda = 0, nu = 1.  Lemma L is sufficient, so x = Lmin(v).                 []
So at exact partition "phi = Lmin(v)" costs nothing -- it follows from core
membership plus tightness of the suffixes.

LEMMA EP2.  If v({i}) = 0 for all i, phi is at exact partition and has k >= 2
strata, then the top stratum B_k has at least two players.
PROOF.  H_{k-1} = B_k is tight, so phi(B_k) = v(B_k).  If B_k = {r} then
phi_r = v({r}) = 0; but phi_r > phi_i >= v({i}) = 0 for i in B_{k-1}, so
phi_r > 0.  Contradiction.                                                  []
This is exactly why the lab finds no admissible exact bump at any gap pattern
containing the cut n-1: those shapes have a singleton top stratum and cannot be
at exact partition at all.

The search below discards single-stratum games (no cut) and, per EP2, is not
restricted further -- non-exact-partition bases are simply filtered out.

usage: d24_ep.py <n> <budget_s> <seed>
"""
import sys, time, json, random, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L

# ------------------------------------------------------------------ (a)
print("(a) verifying EP1 and EP2 on random exact games")
import d3_lemmaL as LL
rng = random.Random(5)
ep_seen = ep1_ok = ep2_ok = games = 0
while games < 400:
    n0 = rng.choice([4, 5, 5, 6])
    total = rng.choice([6, 8, 12, 18])
    rows = []
    for _ in range(rng.randint(2, 3)):
        zeros = set(rng.sample(range(n0), rng.randint(1, 3)))
        free = [k for k in range(n0) if k not in zeros]
        cs = sorted(rng.randint(0, total) for _ in range(len(free) - 1))
        r = [0] * n0
        for k, q in zip(free, [b - a for a, b in zip([0] + cs, cs + [total])]):
            r[k] = q
        rows.append(tuple(F(q) for q in r))
    if not all(any(r[k] == 0 for r in rows) for k in range(n0)):
        continue
    v = L.envelope(n0, rows)
    if v[(1 << n0) - 1] == 0:
        continue
    phi = L.lmin_staged(n0, v)
    if phi is None:
        continue
    games += 1
    suf = L.suffixes(n0, v, phi)
    if not suf or any(s != 0 for _, _, s in suf):
        continue
    ep_seen += 1
    ep1_ok += all(LL.all_cuts_ok(n0, v, phi))         # EP1: certificate at every cut
    ep2_ok += len(L.strata(n0, phi)[-1]) >= 2          # EP2: top stratum >= 2
print("  %d games, %d at exact partition;  EP1 holds %d/%d,  EP2 holds %d/%d"
      % (games, ep_seen, ep1_ok, ep_seen, ep2_ok, ep_seen))
assert ep_seen and ep1_ok == ep_seen and ep2_ok == ep_seen

# ------------------------------------------------------------------ (b)
n = int(sys.argv[1])
budget = float(sys.argv[2])
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
FULL = (1 << n) - 1
rng = random.Random(seed)
t0 = time.time()
st = dict(games=0, expart=0, prefilter=0, windows=0, bumps=0, exact_bumps=0,
          viol=0)
hits = []
print("\n(b) designed exact-partition search at n=%d" % n, flush=True)
while time.time() - t0 < budget:
    total = rng.choice([6, 8, 12, 18, 24, 30])
    rows = []
    for _ in range(rng.randint(2, 4)):
        z = rng.randint(1, max(1, n // 2))
        zeros = set(rng.sample(range(n), z))
        free = [k for k in range(n) if k not in zeros]
        cs = sorted(rng.randint(0, total) for _ in range(len(free) - 1))
        r = [0] * n
        for k, q in zip(free, [b - a for a, b in zip([0] + cs, cs + [total])]):
            r[k] = q
        rows.append(tuple(F(q) for q in r))
    if not all(any(r[k] == 0 for r in rows) for k in range(n)):
        continue
    if len(set(rows)) != len(rows):
        continue
    v = L.envelope(n, rows)
    if v[FULL] == 0:
        continue
    phi = L.lmin_staged(n, v)
    if phi is None:
        continue
    st["games"] += 1
    suf = L.suffixes(n, v, phi)
    if not suf or any(s != 0 for _, _, s in suf):
        continue                                   # not at exact partition
    st["expart"] += 1
    for S in range(1, FULL):
        if bin(S).count("1") < 2:
            continue
        sS = L.slack(n, v, phi, S)
        g = L.g_of(n, v, S)
        if g is None or g <= sS:
            continue
        st["prefilter"] += 1
        amax = L.alpha_exact_max(n, v, S)
        if amax is None or amax <= sS:
            continue
        st["windows"] += 1
        for k in range(1, 9):
            al = sS + (amax - sS) * F(k, 8)
            st["bumps"] += 1
            w = L.bumped(v, S, al)
            p2 = L.lmin_staged(n, w)
            if p2 is None:
                continue
            st["exact_bumps"] += 1
            Wl = [i for i in L.members(n, S) if p2[i] < phi[i]]
            if not Wl:
                continue
            ok, _ = L.exactness_report(n, w)
            if not ok:
                continue
            assert L.lmin_ladder(n, w) == p2
            st["viol"] += 1
            rec = dict(n=n, rows=[[str(q) for q in r] for r in rows],
                       S=L.nm(n, S), alpha=str(al),
                       phi=[str(q) for q in phi], phi2=[str(q) for q in p2],
                       W=L.nm(n, sum(1 << i for i in Wl)),
                       suffixes=[[L.nm(n, Hj), str(s)] for _, Hj, s in suf])
            hits.append(rec)
            print("*** EXACT-PARTITION FAILURE ***", json.dumps(rec), flush=True)
    if st["expart"] % 200 == 0 and st["expart"]:
        print("  t=%.0fs %s" % (time.time() - t0, st), flush=True)
json.dump(dict(stats=st, hits=hits), open("ep_%d_%d.json" % (n, seed), "w"),
          indent=1)
print(json.dumps(st))
print("exact-partition monotonicity failures found:", len(hits))
