"""Scan random exact games for the two configurations the ZP descent turns on.

At an h=2 slack boundary H = {f,g} with poorer side L, look at pairs of
phi-tight sets S1, S2 with S1 & H = {f}, S2 & H = {g}:

  ZP config        : S1 ^ S2 = {e} (one poorer player) and S1 u S2 = N.
                     Profile (p,q) = (|S1 ^ L \\ e|, |S2 ^ L \\ e|), p+q = m-1.
  PARTITION config : S1 ^ S2 = empty and S1 u S2 = N.

Falsifiable predictions of the descent theorem (zp/PROOF.txt):
  P1  no ZP config with profile (p,0) or (0,q) ever occurs, at any n;
  P2  no ZP config of any profile occurs when m = 3;
  P3  partition configs are the only surviving branch, so if they never occur
      either, every ZP config is impossible.

Usage: python3 scan.py N SEED TRIALS BUDGET_S OUT.json
"""
from __future__ import annotations

import itertools
import json
import random
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad")

import audit

BASE = "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/census7/zp"


def nm(n, mask):
    return "".join("abcdefg"[i] for i in range(n) if mask >> i & 1) or "0"


def gens_uniform(n, rng, npts, total):
    return audit.rand_gens(n, rng, npts, total, total)


def gens_two(n, rng, npts, total):
    """Two-row envelopes: the highest-slack-yield style from the campaign."""
    return audit.rand_gens(n, rng, 2, total, total)


def gens_sparse(n, rng, npts, total):
    out = []
    for _ in range(npts):
        k = rng.randint(1, max(2, n - 2))
        who = rng.sample(range(n), k)
        cuts = sorted(rng.randint(0, total) for _ in range(k - 1))
        parts = [b - a for a, b in zip([0] + cuts, cuts + [total])]
        g = [0] * n
        for i, p in zip(who, parts):
            g[i] = p
        out.append(tuple(F(q) for q in g))
    return out


def gens_zero(n, rng, npts, total):
    """Force one player to zero in every row: makes phi_min = 0 likely, which
    is what the ZP configuration requires."""
    z = rng.randrange(n)
    out = []
    for _ in range(npts):
        g = [rng.randint(0, total) for _ in range(n)]
        g[z] = 0
        s = sum(g)
        if s == 0:
            g[(z + 1) % n] = total
            s = total
        g = [q * total // s for q in g]
        g[(z + 1) % n] += total - sum(g)
        if any(q < 0 for q in g):
            continue
        out.append(tuple(F(q) for q in g))
    while len(out) < npts:
        g = [0] * n
        g[(z + 1) % n] = total
        out.append(tuple(F(q) for q in g))
    return out


MODES = {"uniform": gens_uniform, "two": gens_two, "sparse": gens_sparse,
         "zero": gens_zero}


def main():
    n = int(sys.argv[1])
    seed, trials, budget, outpath = (int(sys.argv[2]), int(sys.argv[3]),
                                     float(sys.argv[4]), sys.argv[5])
    FULL = (1 << n) - 1
    stat = {"n": n, "games": 0, "h2_slack": 0, "zp": {}, "partition": {},
            "zp_examples": [], "partition_examples": [], "modes": {}}
    t0 = time.time()
    per_mode = budget / len(MODES)
    for km, (mode, gf) in enumerate(MODES.items(), 1):
        rng = random.Random(seed * 7919 + (hash(mode) % 10007))
        deadline = t0 + per_mode * km
        done = 0
        for _ in range(trials):
            if time.time() > deadline:
                break
            done += 1
            total = rng.randint(n, 30)
            npts = rng.randint(2, 5)
            gens = gf(n, rng, npts, total)
            if len({sum(g) for g in gens}) != 1:
                continue
            try:
                v = audit.envelope(n, gens)
                w, _ = audit.normalize(n, v)
                if w[FULL] <= 0:
                    continue
                phi = audit.lmin(n, w)
            except (AssertionError, RuntimeError):
                continue
            if phi is None:
                continue
            stat["games"] += 1
            blocks = audit.strata(phi)
            for j in range(len(blocks) - 1):
                H = sum(1 << i for b in blocks[j + 1:] for i in b)
                if bin(H).count("1") != 2:
                    continue
                if sum(phi[i] for i in range(n) if H >> i & 1) <= w[H]:
                    continue
                stat["h2_slack"] += 1
                m = n - 2
                tight = [S for S in range(1, FULL)
                         if sum(phi[i] for i in range(n) if S >> i & 1) == w[S]]
                Hs = [i for i in range(n) if H >> i & 1]
                for S1, S2 in itertools.permutations(tight, 2):
                    if S1 & H != (1 << Hs[0]) or S2 & H != (1 << Hs[1]):
                        continue
                    if (S1 | S2) != FULL:
                        continue
                    inter = S1 & S2
                    if inter == 0:
                        pp = bin(S1 & ~H).count("1")
                        qq = bin(S2 & ~H).count("1")
                        key = f"n{n}m{m}split({pp},{qq})"
                        stat["partition"][key] = \
                            stat["partition"].get(key, 0) + 1
                        if len(stat["partition_examples"]) < 6:
                            stat["partition_examples"].append({
                                "n": n, "m": m,
                                "gens": [[int(q) for q in g] for g in gens],
                                "phi": [str(q) for q in phi],
                                "H": nm(n, H), "S1": nm(n, S1),
                                "S2": nm(n, S2)})
                    elif bin(inter).count("1") == 1 and not (inter & H):
                        p = bin(S1 & ~H & ~inter).count("1")
                        q = bin(S2 & ~H & ~inter).count("1")
                        key = f"n{n}m{m}profile({p},{q})"
                        stat["zp"][key] = stat["zp"].get(key, 0) + 1
                        if len(stat["zp_examples"]) < 8:
                            stat["zp_examples"].append({
                                "n": n, "m": m, "profile": [p, q],
                                "gens": [[int(q2) for q2 in g] for g in gens],
                                "phi": [str(q2) for q2 in phi],
                                "H": nm(n, H), "S1": nm(n, S1),
                                "S2": nm(n, S2), "e": nm(n, inter)})
        stat["modes"][mode] = done
    stat["elapsed"] = round(time.time() - t0, 1)
    json.dump(stat, open(outpath, "w"), indent=1)
    print(json.dumps({k: v for k, v in stat.items()
                      if k not in ("zp_examples", "partition_examples")}))


if __name__ == "__main__":
    main()
