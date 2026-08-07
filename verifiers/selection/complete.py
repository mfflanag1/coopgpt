"""Provably exhaustive case of the h=2 split exclusion at n=5.

Restriction: phi has ONE poor stratum (L) and ONE rich stratum (H).  Then the
leximin certificate is a single Lemma-1 cover, whose support can be taken to be
a basic solution of an n-dimensional system, hence has at most n = 5 members;
and the rich stratum needs no certificate (d(N)=0 with d|_L=0 forces
d_p + d_q = 0, so d|_H cannot be >= 0 and nonzero).

Shrinking the tight family F preserves the leximin certificate and only helps
slack and singleton-normalization, so WLOG

     F = (cover support) u {T1, T2},      |F| <= n + 2 = 7.

Enumerating every such F is therefore a COMPLETE decision procedure for this
stratification.  Run over the 6 symmetry orbits of (A1, A2) with delta > 0.
"""
from __future__ import annotations

import itertools
import json
import sys

SCR = "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad"
sys.path.insert(0, SCR)
sys.path.insert(0, SCR + "/sel")
import exists as E


def main():
    n = 5
    Hmask = 0b11000
    Lmask = 0b00111
    p, q = 4, 3
    Lp = [0, 1, 2]
    full = (1 << n) - 1
    maxextra = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    reps = [(0b001, 0b001), (0b001, 0b010), (0b001, 0b011),
            (0b001, 0b111), (0b011, 0b011), (0b011, 0b101)]
    strat = [[0, 1, 2], [3, 4]]
    pool = [S for S in range(1, full) if S != Hmask]
    out = []
    for A1, A2 in reps:
        T1 = (1 << p) | A1
        T2 = (1 << q) | A2
        r = {i: ((A1 >> i & 1) + (A2 >> i & 1)) for i in Lp}
        b = max(r.values())
        delta = 1 + sum(b - r[i] for i in Lp) - b
        extras = [S for S in pool if S not in (T1, T2)]
        cnt = {"F": 0, "slack": 0, "cover": 0, "lex": 0, "norm": 0}
        found = None
        for k in range(0, maxextra + 1):
            for combo in itertools.combinations(extras, k):
                F = [T1, T2] + list(combo)
                cnt["F"] += 1
                if not E.slack_dir(n, F, Hmask):
                    continue
                cnt["slack"] += 1
                if not E.poor_cover_ok(n, F, Lmask):
                    continue
                cnt["cover"] += 1
                if not E.leximin_ok(n, F, strat):
                    continue
                cnt["lex"] += 1
                phi = E.normalizable(n, F, strat)
                if phi is not None:
                    cnt["norm"] += 1
                    found = {"F": [E.nm(n, S) for S in F],
                             "phi": [round(x, 6) for x in phi]}
                    break
            if found:
                break
        print(f"  A1={E.nm(n,A1):4s} A2={E.nm(n,A2):4s} b={b} delta={delta}  {cnt}  "
              f"{'FOUND ' + str(found) if found else 'EXCLUDED'}", flush=True)
        out.append({"A1": E.nm(n, A1), "A2": E.nm(n, A2), "b": b, "delta": delta,
                    "counts": cnt, "found": found})
    with open(f"{SCR}/sel/complete.json", "w") as fh:
        json.dump({"maxextra": maxextra, "stratification": "L|H (one stratum each)",
                   "orbits": out}, fh, indent=1)


if __name__ == "__main__":
    main()
