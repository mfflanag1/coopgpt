"""d27: at exact partition, does the internal-redistribution mechanism ever fire?

paper4's discussion says Theorem A rules out a loser set that is a richer
suffix, but NOT one that is "slack without being a suffix, which is the shape of
Example mono:ex:notstratum" -- there the tight top stratum keeps its total
exactly while one member pays and another is paid.  Lemma EP2 says that at
exact partition the top stratum ALWAYS has at least two players, so the
mechanism is structurally available at every exact-partition base, not only at
special ones.  This driver measures whether it ever actually fires.

For every admissible exact bump of an exact-partition base it records:
  * whether ANY player strictly loses (inside S or outside);
  * whether any phi-stratum redistributes INTERNALLY (a member up and a member
    down inside the same stratum) -- the mono:ex:notstratum mechanism;
  * whether the loser set is slack-but-not-a-suffix, the shape paper4 flags;
  * whether Delta is identically zero.

usage: d27_epredist.py <n> <budget_s> <seed>
"""
import sys, time, json, random
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L

n = int(sys.argv[1])
budget = float(sys.argv[2])
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
FULL = (1 << n) - 1
rng = random.Random(seed)
t0 = time.time()
st = dict(games=0, expart=0, windows=0, exact_bumps=0,
          delta_zero=0, any_loser=0, loser_inside_S=0,
          internal_redistribution=0, loser_set_is_suffix=0,
          loser_set_slack_not_suffix=0, top_stratum_moves=0)
examples = []


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
        rows.append(tuple(q for q in r))
    if not all(any(r[k] == 0 for r in rows) for k in range(n)):
        return None
    if len(set(rows)) != len(rows):
        return None
    return rows


while time.time() - t0 < budget:
    rows = rand_rows(rng.choice([6, 8, 12, 18, 24, 30]), rng.randint(2, 4))
    if rows is None:
        continue
    v = L.envelope(n, [tuple(F(q) for q in r) for r in rows])
    if v[FULL] == 0:
        continue
    phi = L.lmin_staged(n, v)
    if phi is None:
        continue
    st["games"] += 1
    suf = L.suffixes(n, v, phi)
    if not suf or any(s != 0 for _, _, s in suf):
        continue
    st["expart"] += 1
    B = L.strata(n, phi)
    sufmasks = {Hj for _, Hj, _ in suf}
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
        for k in range(1, 9):
            al = sS + (amax - sS) * F(k, 8)
            w = L.bumped(v, S, al)
            p2 = L.lmin_staged(n, w)
            if p2 is None:
                continue
            ok, _ = L.exactness_report(n, w)
            if not ok:
                continue
            st["exact_bumps"] += 1
            D = [p2[i] - phi[i] for i in range(n)]
            if all(q == 0 for q in D):
                st["delta_zero"] += 1
                continue
            losers = [i for i in range(n) if D[i] < 0]
            if losers:
                st["any_loser"] += 1
                Lm = sum(1 << i for i in losers)
                if Lm in sufmasks:
                    st["loser_set_is_suffix"] += 1
                elif L.slack(n, v, phi, Lm) > 0:
                    st["loser_set_slack_not_suffix"] += 1
            if any(i for i in L.members(n, S) if D[i] < 0):
                st["loser_inside_S"] += 1
            for b in B:
                if any(D[i] > 0 for i in b) and any(D[i] < 0 for i in b):
                    st["internal_redistribution"] += 1
                    if len(examples) < 6:
                        examples.append(dict(rows=[list(r) for r in rows],
                                             S=L.nm(n, S), alpha=str(al),
                                             phi=[str(q) for q in phi],
                                             phi2=[str(q) for q in p2],
                                             stratum=[i + 1 for i in b]))
                    break
            if any(D[i] != 0 for i in B[-1]):
                st["top_stratum_moves"] += 1
    if st["expart"] % 300 == 0 and st["expart"]:
        print("  t=%.0fs %s" % (time.time() - t0, st), flush=True)

json.dump(dict(stats=st, examples=examples),
          open("epredist_%d_%d.json" % (n, seed), "w"), indent=1)
print(json.dumps(st, indent=1))
for e in examples[:3]:
    print("internal-redistribution example:", json.dumps(e))
