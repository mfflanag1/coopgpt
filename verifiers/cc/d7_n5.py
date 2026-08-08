"""d7: find a REAL five-player exact-domain monotonicity failure.

Needed as the faithfulness control for the n=5 lab: if the lab's UNSAT is to
mean anything, the encoding must admit genuine violations, and the cheapest
proof of that is to exhibit one and check it satisfies every encoded condition.

Designed generator: the BT shape of paper4's family with the sixth player
deleted, swept over integers, plus random two- and three-row envelopes.

usage: d7_n5.py <budget_s> [seed]
"""
import sys, time, json, random, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L

N = 5
FULL = 31
budget = float(sys.argv[1])
seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
rng = random.Random(seed)
t0 = time.time()
st = dict(games=0, slack=0, prefilter=0, windows=0, bumps=0, viol=0, viol_inexact=0)
hits = []


def try_game(rows, tag):
    if any(q < 0 for r in rows for q in r):
        return
    tot = sum(rows[0])
    if any(sum(r) != tot for r in rows) or tot <= 0:
        return
    if any(min(r[k] for r in rows) != 0 for k in range(N)):
        return
    v = L.envelope(N, [tuple(F(q) for q in r) for r in rows])
    phi = L.lmin_staged(N, v)
    if phi is None:
        return
    st["games"] += 1
    H, js = L.hstar(N, v, phi)
    if H is None:
        return
    st["slack"] += 1
    for S in range(1, FULL):
        if bin(S).count("1") < 2:
            continue
        sS = L.slack(N, v, phi, S)
        g = L.g_of(N, v, S)
        if g is None or g <= sS:
            continue
        st["prefilter"] += 1
        amax = L.alpha_exact_max(N, v, S)
        if amax is None or amax <= sS:
            continue
        st["windows"] += 1
        for al in [amax, sS + (amax - sS) / 2, sS + (amax - sS) / 4,
                   sS + (amax - sS) * F(3, 4)]:
            if al <= sS:
                continue
            st["bumps"] += 1
            w = L.bumped(v, S, al)
            phi2 = L.lmin_staged(N, w)
            if phi2 is None:
                continue
            Wl = [k for k in L.members(N, S) if phi2[k] < phi[k]]
            if not Wl:
                continue
            ok, bad = L.exactness_report(N, w)
            if not ok:
                st["viol_inexact"] += 1
                continue
            assert L.lmin_ladder(N, w) == phi2
            st["viol"] += 1
            Wm = sum(1 << k for k in Wl)
            rec = dict(tag=tag, rows=[list(r) for r in rows],
                       v=[str(q) for q in v], S=L.nm(N, S), Smask=S,
                       alpha=str(al), alpha_ex=str(amax), s_phi_S=str(sS),
                       phi=[str(q) for q in phi], phi2=[str(q) for q in phi2],
                       W=L.nm(N, Wm), Wmask=Wm, Hstar=L.nm(N, H), HstarMask=H,
                       strata=[[k + 1 for k in b] for b in L.strata(N, phi)],
                       suffixes=[[L.nm(N, Hj), str(s)]
                                 for _, Hj, s in L.suffixes(N, v, phi)],
                       left=(Wm & ~H) == 0, right=(H & ~S) == 0)
            hits.append(rec)
            print("VIOLATION", json.dumps(rec), flush=True)


print("phase 1: BT shape at n=5,  A=(0,a,0,b,0) B=(0,c,0,e,f) C=(h,0,i,0,j)",
      flush=True)
for T in range(6, 34):
    if time.time() - t0 > budget * 0.6:
        break
    for a in range(1, T):
        for c in range(0, T + 1):
            for e in range(0, T - c + 1):
                f = T - c - e
                for h in range(0, T + 1):
                    for i in range(0, T - h + 1):
                        j = T - h - i
                        if time.time() - t0 > budget * 0.6:
                            break
                        try_game([(0, a, 0, T - a, 0), (0, c, 0, e, f),
                                  (h, 0, i, 0, j)], "BT5:T%d,a%d,c%d,e%d,h%d,i%d"
                                 % (T, a, c, e, h, i))
    print("  T=%d done t=%.0fs %s" % (T, time.time() - t0, st), flush=True)

print("phase 2: random 2- and 3-row envelopes", flush=True)
while time.time() - t0 < budget:
    total = rng.choice([12, 20, 30, 40])
    nr = rng.randint(2, 3)
    rows = []
    for _ in range(nr):
        z = rng.randint(1, 2)
        zeros = set(rng.sample(range(N), z))
        free = [k for k in range(N) if k not in zeros]
        cs = sorted(rng.randint(0, total) for _ in range(len(free) - 1))
        r = [0] * N
        for k, p in zip(free, [b - a for a, b in zip([0] + cs, cs + [total])]):
            r[k] = p
        rows.append(tuple(r))
    try_game(rows, "rand")

json.dump(dict(stats=st, hits=hits), open("n5_hits_%d.json" % seed, "w"), indent=1)
print(json.dumps(st))
print("distinct violations:", len(hits))
