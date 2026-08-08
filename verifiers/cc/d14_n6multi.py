"""d14: designed hunt for a SIX-player C-C-left failure.

The n=5 counterexample's mechanism is now known: the base game needs at least
TWO slack richer suffixes, so that a loser can sit inside the outer slack
suffix but outside the inner one.  This driver therefore discards every
single-slack base game -- the regime the whole earlier harvest lived in -- and
only studies multi-slack bases.  Bump sizes come from the exact window
endpoint (Lemma WIN), so every bump tried is exact by construction.

usage: d14_n6multi.py <budget_s> <seed>
"""
import sys, time, json, random
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L

n = 6
FULL = 63
budget = float(sys.argv[1])
rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 0)
t0 = time.time()
st = dict(games=0, slack=0, multi=0, no_tight_suffix=0, prefilter=0, windows=0,
          bumps=0, viol=0, left_fail=0, right_fail=0)
hits = []
while time.time() - t0 < budget:
    total = rng.choice([20, 30, 40, 60])
    nr = rng.randint(2, 3)
    rows = []
    for _ in range(nr):
        z = rng.randint(1, 3)
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
    sl = [Hj for _, Hj, s in suf if s > 0]
    if not sl:
        continue
    st["slack"] += 1
    if len(sl) < 2:
        continue                      # single-slack bases are the known-clean regime
    st["multi"] += 1
    if all(s > 0 for _, _, s in suf):
        st["no_tight_suffix"] += 1
    H, js = L.hstar(n, v, phi)
    Hhat = sl[0]
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
            Wl = [i for i in L.members(n, S) if p2[i] < phi[i]]
            if not Wl:
                continue
            ok, _ = L.exactness_report(n, w)
            if not ok:
                continue
            assert L.lmin_ladder(n, w) == p2
            st["viol"] += 1
            Wm = sum(1 << i for i in Wl)
            lf = (Wm & ~H) != 0
            rf = (H & ~S) != 0
            st["left_fail"] += lf
            st["right_fail"] += rf
            if lf or rf:
                rec = dict(rows=[[str(q) for q in r] for r in rows],
                           S=L.nm(n, S), Smask=S, alpha=str(al),
                           phi=[str(q) for q in phi], phi2=[str(q) for q in p2],
                           W=L.nm(n, Wm), Hstar=L.nm(n, H), Hhat=L.nm(n, Hhat),
                           suffixes=[[L.nm(n, Hj), str(s)] for _, Hj, s in suf],
                           left_fail=bool(lf), right_fail=bool(rf),
                           W_in_Hhat=(Wm & ~Hhat) == 0,
                           Hhat_in_S=(Hhat & ~S) == 0)
                hits.append(rec)
                print("*** C-C FAILURE n=6 ***", json.dumps(rec), flush=True)
    if st["games"] % 500 == 0:
        print("  t=%.0fs %s" % (time.time() - t0, st), flush=True)
json.dump(dict(stats=st, hits=hits), open("n6multi.json", "w"), indent=1)
print(json.dumps(st))
