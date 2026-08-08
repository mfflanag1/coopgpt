"""d18: designed six-player MULTI-SLACK families around the two n=6
C-C-left counterexamples, tested against the repaired conjecture C-C^.

Random multi-slack bases are cheap to make but admissible exact windows inside
them are rare (24 windows per 4550 prefiltered coalitions in d14).  The BT
family trick applies: take a base game that IS known to carry a window and
perturb its generator rows, keeping the common total and the zero pattern so
that exactness and singleton-normalization stay free.  That produces designed
multi-slack violations in bulk instead of by luck.

Every violation found is tested for  W subset Hhat subset S  (C-C^) and for the
old  W subset H* subset S  (C-C).

usage: d18_fam6.py <budget_s> <seed>
"""
import sys, time, json, random, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L

n = 6
FULL = 63
BASES = [
    ("A", [(6, 7, 11, 0, 13, 3), (0, 22, 0, 10, 0, 8), (0, 0, 21, 0, 19, 0)]),
    ("B", [(3, 0, 37, 0, 0, 0), (5, 4, 22, 0, 5, 4), (0, 18, 0, 11, 11, 0)]),
]
budget = float(sys.argv[1])
rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 0)
t0 = time.time()
st = dict(tried=0, wellformed=0, slack=0, multi=0, windows=0, bumps=0, viol=0,
          cc_left_fail=0, cc_right_fail=0, cchat_left_fail=0, cchat_right_fail=0)
hits, breaks = [], []


def perturb(rows, spread):
    """Perturb nonzero entries, keep the common total and the zero pattern."""
    out = []
    for r in rows:
        nz = [k for k in range(n) if r[k] != 0]
        if len(nz) < 2:
            out.append(tuple(r))
            continue
        absorb = max(nz, key=lambda k: r[k])          # biggest entry absorbs
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
        return None                                    # need a zero in some row
    if len(set(out)) != len(out):
        return None
    return out


while time.time() - t0 < budget:
    name, base = rng.choice(BASES)
    rows = perturb(base, rng.choice([1, 2, 3, 5]))
    st["tried"] += 1
    if rows is None:
        continue
    st["wellformed"] += 1
    v = L.envelope(n, [tuple(F(q) for q in r) for r in rows])
    if v[FULL] == 0:
        continue
    phi = L.lmin_staged(n, v)
    if phi is None:
        continue
    suf = L.suffixes(n, v, phi)
    sl = [Hj for _, Hj, s in suf if s > 0]
    if not sl:
        continue
    st["slack"] += 1
    if len(sl) < 2:
        continue
    st["multi"] += 1
    H, js = L.hstar(n, v, phi)
    Hhat = sl[0]
    for S in range(1, FULL):
        if bin(S).count("1") < 2 or time.time() - t0 > budget * 1.4:
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
            rec = dict(base=name, rows=[list(r) for r in rows], S=L.nm(n, S),
                       Smask=S, alpha=str(al),
                       phi=[str(q) for q in phi], phi2=[str(q) for q in p2],
                       W=L.nm(n, Wm), Hstar=L.nm(n, H), Hhat=L.nm(n, Hhat),
                       suffixes=[[L.nm(n, Hj), str(s)] for _, Hj, s in suf],
                       cc_left=(Wm & ~H) == 0, cc_right=(H & ~S) == 0,
                       cchat_left=(Wm & ~Hhat) == 0,
                       cchat_right=(Hhat & ~S) == 0)
            st["cc_left_fail"] += not rec["cc_left"]
            st["cc_right_fail"] += not rec["cc_right"]
            st["cchat_left_fail"] += not rec["cchat_left"]
            st["cchat_right_fail"] += not rec["cchat_right"]
            hits.append(rec)
            if not (rec["cchat_left"] and rec["cchat_right"]):
                breaks.append(rec)
                print("*** C-C^ FAILURE ***", json.dumps(rec), flush=True)
    if st["multi"] % 100 == 0 and st["multi"]:
        print("  t=%.0fs %s" % (time.time() - t0, st), flush=True)

json.dump(dict(stats=st, breaks=breaks, hits=hits[:400]),
          open("fam6.json", "w"), indent=1)
print(json.dumps(st, indent=1))
print("C-C^ failures:", len(breaks))
