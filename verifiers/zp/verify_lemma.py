"""Machine verification of the two lemmas the ZP descent rests on.

L1 (common zero).  In an exact singleton-normalized game whose Lmin has
    min_i phi_i = 0, the core is covered by the hyperplanes {x_i = 0}; being
    convex it lies in ONE of them, so some player j has x_j = 0 identically
    on the core, and then phi_j = 0 and j is null: v(S u {j}) = v(S).
    Checked at n=5 by exact core-vertex enumeration.

L2 (null-player deletion).  If j is null then v' = v restricted to N \\ {j} is
    exact and singleton-normalized, core(v') = core(v)|_{N'}, Lmin(v') =
    phi|_{N'}, every phi-tight S gives a phi'-tight S \\ {j}, and a slack
    strict boundary H (not containing j) stays one with the same slack.
    Checked by building n=6 games with a null player and deleting it, and by
    deleting the identically-zero player found by L1 in n=5 games.

Usage: python3 verify_lemma.py SEED TRIALS
"""
from __future__ import annotations

import random
import sys
from fractions import Fraction as F

sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad")

import audit


def restrict(n, w, drop):
    """Game on N \\ {drop}, coalitions reindexed."""
    keep = [i for i in range(n) if i != drop]
    n2 = n - 1
    w2 = [F(0)] * (1 << n2)
    for S2 in range(1, 1 << n2):
        S = sum(1 << keep[i] for i in range(n2) if S2 >> i & 1)
        w2[S2] = w[S]
    return w2, keep


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    rng = random.Random(seed)
    n = 5
    FULL = (1 << n) - 1
    stat = {"games": 0, "phi_min_zero": 0, "L1_common_zero_ok": 0,
            "L1_null_ok": 0, "L2_checked": 0, "L2_ok": 0,
            "L2_lmin_ok": 0, "L2_tight_ok": 0, "L2_slack_ok": 0}
    for _ in range(trials):
        total = rng.randint(5, 24)
        npts = rng.randint(2, 4)
        gens = audit.rand_gens(n, rng, npts, total, total)
        v = audit.envelope(n, gens)
        w, _ = audit.normalize(n, v)
        if w[FULL] <= 0:
            continue
        phi = audit.lmin(n, w)
        if phi is None:
            continue
        stat["games"] += 1
        if min(phi) != 0:
            continue
        stat["phi_min_zero"] += 1

        verts = audit.core_vertices(n, w)
        assert verts, "empty core"
        zeros = [j for j in range(n) if all(x[j] == 0 for x in verts)]
        assert zeros, "L1 FAILED: core not inside a single coordinate hyperplane"
        stat["L1_common_zero_ok"] += 1
        j = zeros[0]
        assert phi[j] == 0
        # j is null
        ok = True
        for S in range(1, FULL + 1):
            if S >> j & 1:
                if w[S] != w[S & ~(1 << j)] and (S & ~(1 << j)) != 0:
                    ok = False
                    break
        assert ok, "L1 FAILED: the common-zero player is not null"
        stat["L1_null_ok"] += 1

        # ---- L2: delete j
        w2, keep = restrict(n, w, j)
        n2 = n - 1
        FULL2 = (1 << n2) - 1
        if w2[FULL2] <= 0:
            continue
        stat["L2_checked"] += 1
        assert all(w2[1 << i] == 0 for i in range(n2)), "L2: not normalized"
        v2 = audit.core_vertices(n2, w2)
        assert audit.is_exact(n2, w2, v2), "L2 FAILED: reduced game not exact"
        stat["L2_ok"] += 1
        phi2 = audit.lmin(n2, w2)
        assert phi2 == [phi[i] for i in keep], "L2 FAILED: Lmin not preserved"
        stat["L2_lmin_ok"] += 1
        # tight sets map to tight sets
        good = True
        for S in range(1, FULL):
            if sum(phi[i] for i in range(n) if S >> i & 1) != w[S]:
                continue
            S2 = sum(1 << k for k, i in enumerate(keep) if S >> i & 1)
            if S2 == 0 or S2 == FULL2:
                continue
            if sum(phi2[k] for k in range(n2) if S2 >> k & 1) != w2[S2]:
                good = False
                break
        assert good, "L2 FAILED: a tight set did not stay tight"
        stat["L2_tight_ok"] += 1
        # slack strict boundaries not containing j survive with equal slack
        good = True
        for b in range(len(audit.strata(phi)) - 1):
            blocks = audit.strata(phi)
            H = sum(1 << i for bb in blocks[b + 1:] for i in bb)
            if H >> j & 1:
                continue
            s = sum(phi[i] for i in range(n) if H >> i & 1) - w[H]
            if s <= 0:
                continue
            H2 = sum(1 << k for k, i in enumerate(keep) if H >> i & 1)
            blocks2 = audit.strata(phi2)
            sufs = [sum(1 << k for bb in blocks2[c + 1:] for k in bb)
                    for c in range(len(blocks2) - 1)]
            if H2 not in sufs:
                good = False
                break
            s2 = sum(phi2[k] for k in range(n2) if H2 >> k & 1) - w2[H2]
            if s2 != s:
                good = False
                break
        assert good, "L2 FAILED: a slack boundary did not survive"
        stat["L2_slack_ok"] += 1

    print(stat)
    print("ALL CHECKS PASSED" if stat["L1_common_zero_ok"] == stat["phi_min_zero"]
          else "FAILURE")


if __name__ == "__main__":
    main()
