"""d1: DESIGNED counterexample hunt for C-C, aimed at the region the earlier
harvests could not reach.

Design decisions (this is a targeted search, not a volume search):
  * PRIORITY TARGET for the right inclusion: only bumped coalitions S with
    H* NOT contained in S are candidates.  Every violation there refutes C-C
    right outright.  Earlier harvests enumerated S at random and are believed
    to be dominated by S = N minus one poor player.
  * PRIORITY TARGET for the left inclusion: any violation whose loser set W
    meets N \\ H*.
  * Generator regimes are varied deliberately (row count, total, sparsity,
    n) rather than by raising volume: campaign law says 1041/1041 random
    evidence proves nothing.

Every candidate that produces W != empty is certified: v' exactness on all
proper coalitions by exact z3 optimisation, and phi' by two independent
leximin algorithms with a z3 UNSAT uniqueness proof.

usage: d1_hunt.py <regime> <trials> <seed> [budget_seconds]
"""
import sys, time, json, random, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L

REGIMES = {
    #  name        n  rows  totals            hi_frac  zeros_per_row
    "A": dict(n=6, rows=2, totals=[20, 30, 40], zmin=1, zmax=3),
    "B": dict(n=6, rows=3, totals=[18, 24, 30], zmin=2, zmax=3),
    "C": dict(n=6, rows=4, totals=[24, 36], zmin=2, zmax=4),
    "D": dict(n=5, rows=2, totals=[12, 20, 30], zmin=1, zmax=2),
    "E": dict(n=5, rows=3, totals=[12, 18, 24], zmin=1, zmax=3),
    "F": dict(n=7, rows=2, totals=[28, 42], zmin=2, zmax=4),
    "G": dict(n=7, rows=3, totals=[28, 42], zmin=2, zmax=4),
    "H": dict(n=6, rows=2, totals=[60, 90], zmin=1, zmax=3),
}


def gen_rows(n, nrows, total, zmin, zmax, rng):
    """Nonnegative integer rows with a common total and a controlled number of zeros;
    every coordinate must vanish in some row (then the envelope is
    singleton-normalized and exact for free)."""
    for _ in range(40):
        rows = []
        for _ in range(nrows):
            z = rng.randint(zmin, min(zmax, n - 1))
            zeros = set(rng.sample(range(n), z))
            free = [i for i in range(n) if i not in zeros]
            cuts = sorted(rng.randint(0, total) for _ in range(len(free) - 1))
            parts = [b - a for a, b in zip([0] + cuts, cuts + [total])]
            r = [0] * n
            for i, p in zip(free, parts):
                r[i] = p
            rows.append(tuple(F(q) for q in r))
        if all(any(r[i] == 0 for r in rows) for i in range(n)):
            if len(set(rows)) == len(rows):
                return rows
    return None


def alphas(s, amax, k=8):
    """Bump sizes inside the admissible window (s, amax].  Every one of these is
    an EXACT bump by construction (lib12.alpha_exact_max)."""
    out = [amax]
    for t in range(1, k):
        out.append(s + (amax - s) * F(t, k))
    return sorted(set(q for q in out if q > s))


def main():
    reg = sys.argv[1]
    trials = int(sys.argv[2])
    seed = int(sys.argv[3])
    budget = float(sys.argv[4]) if len(sys.argv) > 4 else 1500.0
    R = REGIMES[reg]
    n = R["n"]
    full = (1 << n) - 1
    rng = random.Random(seed)
    t0 = time.time()
    st = dict(regime=reg, seed=seed, games=0, slack_bases=0, S_offHstar=0,
              S_onHstar=0, prefilter=0, windows=0, bumps=0,
              viol_exact=0, viol_inexact=0,
              cc_left=0, cc_right=0, cc_both=0,
              viol_exact_offHstar=0, viol_exact_S_notNminus1=0,
              aux_frozen_above=0, aux_outsider_below=0)
    hits = []
    for tr in range(trials):
        if time.time() - t0 > budget:
            print("BUDGET STOP at trial", tr, flush=True)
            break
        if tr % 200 == 0:
            print("  trial %d  t=%.0fs  %s" % (tr, time.time() - t0,
                  {k: v for k, v in st.items() if isinstance(v, int) and v}), flush=True)
        rows = gen_rows(n, R["rows"], rng.choice(R["totals"]),
                        R["zmin"], R["zmax"], rng)
        if rows is None:
            continue
        v = L.envelope(n, rows)
        if v[full] == 0 or not L.is_sing_norm(n, v):
            continue
        phi = L.lmin_staged(n, v)
        if phi is None:
            continue
        st["games"] += 1
        H, js = L.hstar(n, v, phi)
        if H is None:
            continue
        st["slack_bases"] += 1
        for S in range(1, full):
            if bin(S).count("1") < 2:
                continue
            off = (H & ~S) != 0
            st["S_offHstar" if off else "S_onHstar"] += 1
            sS = L.slack(n, v, phi, S)
            g = L.g_of(n, v, S)
            if g is None or g <= sS:
                continue
            st["prefilter"] += 1
            amax = L.alpha_exact_max(n, v, S)
            if amax is None or amax <= sS:
                continue
            st["windows"] += 1
            for a in alphas(sS, amax):
                if time.time() - t0 > budget:
                    break
                st["bumps"] += 1
                w = L.bumped(v, S, a)
                phi2 = L.lmin_staged(n, w)
                if phi2 is None:
                    continue
                W = [i for i in L.members(n, S) if phi2[i] < phi[i]]
                if not W:
                    continue
                ok, bad = L.exactness_report(n, w)
                if not ok:
                    st["viol_inexact"] += 1
                    continue
                # certified exact-domain violation
                assert L.lmin_ladder(n, w) == phi2, "leximin algorithms disagree"
                st["viol_exact"] += 1
                Wm = sum(1 << i for i in W)
                left = (Wm & ~H) == 0
                right = (H & ~S) == 0
                st["cc_left"] += left
                st["cc_right"] += right
                st["cc_both"] += (left and right)
                if off:
                    st["viol_exact_offHstar"] += 1
                if bin(full ^ S).count("1") > 1:
                    st["viol_exact_S_notNminus1"] += 1
                losers = [i for i in range(n) if phi2[i] < phi[i]]
                lam = max(phi[i] for i in losers)
                st["aux_frozen_above"] += all(phi2[i] == phi[i] for i in range(n)
                                              if phi[i] > lam)
                ins = [phi[i] for i in W]
                outs = [phi[i] for i in losers if not S >> i & 1]
                st["aux_outsider_below"] += (not outs) or (max(outs) < min(ins))
                rec = dict(regime=reg, n=n, rows=[[str(q) for q in r] for r in rows],
                           S=S, Sname=L.nm(n, S), alpha=str(a),
                           phi=[str(q) for q in phi], phi2=[str(q) for q in phi2],
                           W=L.nm(n, Wm), Hstar=L.nm(n, H), jstar=js,
                           left=left, right=right,
                           strata=[[i + 1 for i in b] for b in L.strata(n, phi)],
                           suffix_slacks=[(L.nm(n, Hj), str(s))
                                          for _, Hj, s in L.suffixes(n, v, phi)],
                           n_outsiders=bin(full ^ S).count("1"))
                hits.append(rec)
                if not (left and right):
                    print("\n*** C-C FAILURE ***", json.dumps(rec, indent=1), flush=True)
    st["elapsed"] = round(time.time() - t0, 1)
    out = dict(stats=st, hits=hits)
    with open("hunt_%s_%d.json" % (reg, seed), "w") as f:
        json.dump(out, f, indent=1)
    print("\nREGIME", reg, "seed", seed, json.dumps(st, indent=1))


if __name__ == "__main__":
    main()
