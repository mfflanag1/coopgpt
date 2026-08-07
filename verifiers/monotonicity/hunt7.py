"""Task #15: can a monotonicity failure occur at an EXACT-PARTITION base?

Exact partition at phi means every richer suffix H_j is phi-tight, i.e. no
slack boundary exists and H* is undefined.  Conjecture mono:conj:cc assumes
H* exists; the whole harvest so far bumped only slack-bearing bases, so this
class was never tested.

Theorem A (mono:thm:loss) forces any losing coalition other than S to be
phi-slack, so at an exact-partition base the losers cannot form a richer
suffix -- but a loser set that is slack WITHOUT being a suffix is not yet
excluded.  This run looks for one.

Classes tracked separately:
  EP2   exact partition with at least two payoff strata (the real case)
  EP1   a single payoff stratum (no boundary at all; vacuously exact
        partition, and the degenerate subcase)
"""
from __future__ import annotations
import json, random, sys, time
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad")
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/route3")
import audit
from hunt2 import boundaries, nm, core_expr, dmax
from probeA_sweep import exact_lp


def run(n, seed, budget, totals, npts, out):
    FULL = (1 << n) - 1
    rng = random.Random(seed)
    st = {"n": n, "seed": seed, "games": 0, "slack_bases": 0, "EP1": 0, "EP2": 0,
          "studied": 0, "prefilter": 0, "windows": 0, "bumps": 0,
          "viol_exact": 0, "viol_inexact": 0, "hits": [], "elapsed": 0}
    end = time.time() + budget
    while time.time() < end:
        total = rng.choice(totals)
        gens = audit.rand_gens(n, rng, rng.choice(npts), total, total)
        v = audit.envelope(n, [tuple(g) for g in gens])
        w, _ = audit.normalize(n, v)
        if w[FULL] == 0:
            continue
        phi = audit.lmin(n, w)
        if phi is None:
            continue
        st["games"] += 1
        bnd = boundaries(n, w, phi)
        if any(s > 0 for _, s in bnd):
            st["slack_bases"] += 1
            continue                      # slack-bearing: already covered
        cls = "EP1" if not bnd else "EP2"
        st[cls] += 1
        st["studied"] += 1
        x, base = core_expr(n, w)
        for S in range(1, FULL):
            if time.time() > end or bin(S).count("1") < 2:
                continue
            sS = sum(phi[i] for i in range(n) if S >> i & 1) - w[S]
            g = min(w[S | (1 << j)] - w[S] for j in range(n) if not S >> j & 1)
            if g <= sS:
                continue                  # Theorem B prefilter
            st["prefilter"] += 1
            dm = dmax(n, w, S, x, base)
            if dm is None:
                continue
            if dm > sS:
                st["windows"] += 1
            for d in sorted({dm, sS + (dm - sS) / 2, sS + (dm - sS) / 4,
                             sS + 3 * (dm - sS) / 4, dm * 2}):
                if d <= sS or d <= 0:
                    continue
                w2 = list(w); w2[S] = w[S] + d
                st["bumps"] += 1
                ex = exact_lp(n, w2)
                phi2 = audit.lmin(n, w2)
                if phi2 is None:
                    continue
                W = [i for i in range(n) if S >> i & 1 and phi2[i] < phi[i]]
                if not W:
                    continue
                Wm = sum(1 << i for i in W)
                st["viol_exact" if ex else "viol_inexact"] += 1
                if ex:
                    rec = {"n": n, "cls": cls,
                           "gens": [[str(q) for q in gg] for gg in gens],
                           "w": [str(q) for q in w], "S": S, "Sname": nm(n, S),
                           "d": str(d), "s_phi_S": str(sS), "d_max": str(dm),
                           "phi": [str(q) for q in phi],
                           "phi2": [str(q) for q in phi2], "W": nm(n, Wm),
                           "boundaries": [[nm(n, H), str(s)] for H, s in bnd],
                           "s_phi_W": str(sum(phi[i] for i in range(n)
                                              if Wm >> i & 1) - w[Wm])}
                    st["hits"].append(rec)
                    print("*** EXACT-PARTITION FAILURE ***",
                          json.dumps(rec), flush=True)
    st["elapsed"] = round(budget - (end - time.time()), 1)
    with open(out, "w") as fh:
        json.dump(st, fh, indent=1)
    print(json.dumps({k: y for k, y in st.items() if k != "hits"}))


if __name__ == "__main__":
    n, seed, budget = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
    totals = [int(t) for t in sys.argv[4].split(",")]
    npts = [int(t) for t in sys.argv[5].split(",")]
    run(n, seed, budget, totals, npts,
        f"/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/"
        f"scratchpad/ca/h7_n{n}_{seed}.json")
