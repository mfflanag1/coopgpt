"""Split-configuration existence sweep over ALL stratifications, with the
stratification enumerated by DFS so that a failing prefix prunes its extensions.
"""
from __future__ import annotations

import itertools
import json
import sys

SCR = "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad"
sys.path.insert(0, SCR)
sys.path.insert(0, SCR + "/sel")
import exists as E




def stage_free(n, F, pinned, B):
    import numpy as np
    Aub = [[-a for a in E.row(n, T)] for T in F]
    bub = [0.0] * len(F)
    for i in B:
        e = [0.0] * n; e[i] = -1.0
        Aub.append(e); bub.append(0.0)
    e = [0.0] * n
    for i in B:
        e[i] = -1.0
    Aub.append(e); bub.append(-1.0)
    Aeq = [[1.0] * n]
    beq = [0.0]
    for i in pinned:
        e = [0.0] * n; e[i] = 1.0
        Aeq.append(e); beq.append(0.0)
    r = E._feas(np.zeros(n), np.array(Aub), np.array(bub), np.array(Aeq),
                np.array(beq), [(-50, 50)] * n)
    return not r.success


def strat_dfs(n, F, remaining, pinned, Hlist, acc, out):
    """Enumerate stratifications of the poor side that survive stage by stage."""
    if not remaining:
        for hs in Hlist:
            st = acc + hs
            ok = True
            p2 = list(pinned)
            for B in hs:
                if not stage_free(n, F, p2, B):
                    ok = False
                    break
                p2 = p2 + list(B)
            if ok:
                out.append(st)
        return
    for k in range(1, len(remaining) + 1):
        for B in itertools.combinations(remaining, k):
            if not stage_free(n, F, pinned, list(B)):
                continue
            rest = [x for x in remaining if x not in B]
            strat_dfs(n, F, rest, pinned + list(B), Hlist, acc + [list(B)], out)


def main():
    n = 5
    Hmask = 0b11000
    Lmask = 0b00111
    p, q = 4, 3
    Lp = [0, 1, 2]
    full = (1 << n) - 1
    maxextra = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    which = int(sys.argv[2]) if len(sys.argv) > 2 else -1
    reps = [(0b001, 0b001), (0b001, 0b010), (0b001, 0b011),
            (0b001, 0b111), (0b011, 0b011), (0b011, 0b101)]
    Hlist = [[[3, 4]], [[3], [4]], [[4], [3]]]
    pool = [S for S in range(1, full) if S != Hmask]
    out = []
    for idx, (A1, A2) in enumerate(reps):
        if which >= 0 and idx != which:
            continue
        T1 = (1 << p) | A1
        T2 = (1 << q) | A2
        r = {i: ((A1 >> i & 1) + (A2 >> i & 1)) for i in Lp}
        b = max(r.values())
        delta = 1 + sum(b - r[i] for i in Lp) - b
        extras = [S for S in pool if S not in (T1, T2)]
        cnt = {"F": 0, "slack": 0, "cover": 0, "strat": 0}
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
                sts = []
                strat_dfs(n, F, Lp, [], Hlist, [], sts)
                cnt["strat"] += len(sts)
                for st in sts:
                    phi = E.normalizable(n, F, st)
                    if phi is not None:
                        found = {"F": [E.nm(n, S) for S in F],
                                 "strata": [[E.nm(n, 1 << i) for i in B] for B in st],
                                 "phi": [round(x, 6) for x in phi]}
                        break
                if found:
                    break
            if found:
                break
        print(f"  A1={E.nm(n,A1):4s} A2={E.nm(n,A2):4s} b={b} delta={delta}  {cnt}  "
              f"{'FOUND ' + str(found) if found else 'none up to %d extras' % maxextra}",
              flush=True)
        out.append({"A1": E.nm(n, A1), "A2": E.nm(n, A2), "b": b, "delta": delta,
                    "counts": cnt, "found": found})
    tag = f"_{which}" if which >= 0 else ""
    with open(f"{SCR}/sel/complete2{tag}.json", "w") as fh:
        json.dump({"maxextra": maxextra, "orbits": out}, fh, indent=1)


if __name__ == "__main__":
    main()
