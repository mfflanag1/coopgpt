"""Harvest genuine PARTITION-configuration witnesses at n=6 (split (1,3)/(3,1)).

Discharges: supplies the POSITIVE CONTROL for the decisive encodings --
a real exact game whose Lmin carries a PART(1,3) configuration.  Every
driver must accept it.

Method copied in spirit from verifiers/zp/hunt_partition.py: sample inside the
affine slice where a coalition's total is frozen, so that complementary tight
pairs are common.

Usage: python3 harvest.py N SEED BUDGET_S OUT.json
"""
from __future__ import annotations

import itertools
import json
import random
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import lib23 as L


def compose(rng, k, tot):
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
    stat = {"n": n, "games": 0, "h2_slack": 0, "splits": {}}
    t0 = time.time()
    while time.time() - t0 < budget:
        k = rng.randint(2, n - 2)
        S_players = rng.sample(range(n), k)
        total = rng.randint(n, 26)
        cS = rng.randint(1, total - 1)
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
            continue
        try:
            v = L.envelope(n, gens)
            w, _ = L.normalize(n, v)
            if w[FULL] <= 0:
                continue
            phi = L.lmin(n, w)
        except (AssertionError, RuntimeError):
            continue
        if phi is None:
            continue
        stat["games"] += 1
        blocks = L.strata(phi)
        for j in range(len(blocks) - 1):
            H = sum(1 << i for b in blocks[j + 1:] for i in b)
            if bin(H).count("1") != 2:
                continue
            if sum(phi[i] for i in range(n) if H >> i & 1) <= w[H]:
                continue
            stat["h2_slack"] += 1
            tight = L.tight_family(n, w, phi)
            Hs = L.bits(n, H)
            for S1, S2 in itertools.permutations(tight, 2):
                if S1 & H != (1 << Hs[0]) or S2 & H != (1 << Hs[1]):
                    continue
                if (S1 | S2) != FULL or (S1 & S2) != 0:
                    continue
                p = bin(S1 & ~H).count("1")
                q = bin(S2 & ~H).count("1")
                key = f"n{n}m{n-2}split({p},{q})"
                stat["splits"][key] = stat["splits"].get(key, 0) + 1
                if key not in found:
                    found[key] = {
                        "n": n, "m": n - 2, "split": [p, q],
                        "gens": [[int(x) for x in g] for g in gens],
                        "w": [str(x) for x in w],
                        "phi": [str(x) for x in phi],
                        "H": L.nm(n, H), "Hmask": H,
                        "S1": L.nm(n, S1), "S1mask": S1,
                        "S2": L.nm(n, S2), "S2mask": S2,
                        "tight": [L.nm(n, T) for T in tight],
                        "tightmasks": tight,
                        "s_H": str(sum(phi[i] for i in range(n)
                                       if H >> i & 1) - w[H])}
                    print("FOUND", key, found[key]["phi"], found[key]["H"],
                          found[key]["S1"], found[key]["S2"], flush=True)
    stat["elapsed"] = round(time.time() - t0, 1)
    json.dump({"stat": stat, "found": found}, open(out, "w"), indent=1)
    print(json.dumps(stat))


if __name__ == "__main__":
    main()
