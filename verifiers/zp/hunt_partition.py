"""Targeted hunt for PARTITION configurations of a prescribed split.

Equivalence proved in PROOF.txt: a ZP configuration of profile (p,q) at m
poorer players exists iff a PARTITION configuration of split (p,q) exists at
m-1 (suspend/delete a null player).  So the resisting n=7 types reduce to:

    profile (4,0) at m=5  <->  split (4,0) at m=4   [impossible: {g} tight]
    profile (2,2) at m=5  <->  split (2,2) at m=4

A partition configuration needs two COMPLEMENTARY tight sets, and if phi is a
generator that is exactly the statement that every generator g has the same
total on S:  g(S) = phi(S).  Sampling directly inside that affine slice is far
more efficient than random games, which reach split (2,2) never.

Usage: python3 hunt_partition.py N SEED BUDGET_S OUT.json
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


def compose(rng, k, tot):
    """Random nonnegative integer composition of tot into k parts."""
    if k == 1:
        return [tot]
    cuts = sorted(rng.randrange(tot + 1) for _ in range(k - 1))
    return [b - a for a, b in zip([0] + cuts, cuts + [tot])]


def main():
    n = int(sys.argv[1])
    seed, budget, out = int(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    FULL = (1 << n) - 1
    rng = random.Random(seed)
    found = {}
    stat = {"n": n, "games": 0, "h2_slack": 0, "splits": {},
            "slice_tight": 0}
    t0 = time.time()
    while time.time() - t0 < budget:
        # choose the split S (the coalition whose total is frozen)
        k = rng.randint(2, n - 2)
        S_players = rng.sample(range(n), k)
        S = sum(1 << i for i in S_players)
        total = rng.randint(n, 26)
        cS = rng.randint(1, total - 1)          # frozen total on S
        npts = rng.randint(2, 5)
        gens = []
        for _ in range(npts):
            inS = compose(rng, k, cS)
            outS = compose(rng, n - k, total - cS)
            g = [0] * n
            for i, val in zip(S_players, inS):
                g[i] = val
            others = [i for i in range(n) if i not in S_players]
            for i, val in zip(others, outS):
                g[i] = val
            gens.append(tuple(F(q) for q in g))
        if any(min(g[i] for g in gens) != 0 for i in range(n)):
            continue                            # keep it singleton-normalized
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
            tight = [T for T in range(1, FULL)
                     if sum(phi[i] for i in range(n) if T >> i & 1) == w[T]]
            Hs = [i for i in range(n) if H >> i & 1]
            for S1, S2 in itertools.permutations(tight, 2):
                if S1 & H != (1 << Hs[0]) or S2 & H != (1 << Hs[1]):
                    continue
                if (S1 | S2) != FULL or (S1 & S2) != 0:
                    continue
                p = bin(S1 & ~H).count("1")
                q = bin(S2 & ~H).count("1")
                key = f"m{n-2}split({p},{q})"
                stat["splits"][key] = stat["splits"].get(key, 0) + 1
                if key not in found:
                    found[key] = {
                        "n": n, "m": n - 2, "split": [p, q],
                        "gens": [[int(x) for x in g] for g in gens],
                        "phi": [str(x) for x in phi],
                        "H": nm(n, H), "S1": nm(n, S1), "S2": nm(n, S2),
                        "v_H": str(w[H]),
                        "s_H": str(sum(phi[i] for i in range(n)
                                       if H >> i & 1) - w[H])}
                    print("FOUND", key, json.dumps(found[key]), flush=True)
    stat["elapsed"] = round(time.time() - t0, 1)
    json.dump({"stat": stat, "found": found}, open(out, "w"), indent=1)
    print(json.dumps(stat))


if __name__ == "__main__":
    main()
