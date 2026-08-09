"""d32: EXHAUSTIVE confirmation of the corrected rigidity condition.

d31 enumerated every SET partition, which is wasteful: two partitions with the
same block-size profile differ by a relabelling of players, and relabelling
carries generators, Lmin and Lmax along with it, so rho depends only on the
PROFILE.  One representative per integer partition therefore covers everything,
and the sweep becomes exhaustive over profiles rather than a sample of them.

CONDITION UNDER TEST
    Lmin = Lmax  <=>  every block has size <= 2  OR  at most one block size >= 2
    (equivalently: fails iff some block >= 3 AND some other block >= 2)

For each profile of n into k >= 3 parts, n = 5..9.
"""
import sys, random, itertools, json
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L

rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
TR = int(sys.argv[2]) if len(sys.argv) > 2 else 60
NMAX = int(sys.argv[3]) if len(sys.argv) > 3 else 8

def int_partitions(n, maxpart=None):
    if maxpart is None: maxpart = n
    if n == 0: yield (); return
    for p in range(min(n, maxpart), 0, -1):
        for rest in int_partitions(n - p, p):
            yield (p,) + rest

def spread(total, m):
    if m == 1: return [total]
    cuts = sorted(rng.randint(1, total - 1) for _ in range(m - 1))
    return [b - a for a, b in zip([0] + cuts, cuts + [total])]

def blocks_of(sizes):
    bl, i = [], 0
    for s in sizes:
        bl.append(list(range(i, i + s))); i += s
    return bl

print("%-3s %-18s %-8s %6s %8s %9s %s" % ("n","profile","predict","games","nonzero","best rho","verdict"))
rows_out, bad = [], 0
for n in range(5, NMAX + 1):
    for sizes in int_partitions(n):
        if len(sizes) < 3: continue
        bl = blocks_of(sizes)
        pred = "BREAKS" if (max(sizes) >= 3 and sum(1 for s in sizes if s >= 2) >= 2) else "rigid"
        games = nz = 0; best = F(0); ex = None
        for _ in range(TR):
            total = rng.choice([6, 8, 12, 16, 20])
            rows = []; ok = True
            for b in bl:
                parts = spread(total, len(b))
                if any(q <= 0 for q in parts): ok = False; break
                r = [0]*n
                for i, q in zip(b, parts): r[i] = q
                rows.append(tuple(r))
            if not ok or len(set(rows)) != len(rows): continue
            v = L.envelope(n, [tuple(F(q) for q in r) for r in rows])
            if v[(1<<n)-1] == 0: continue
            a = L.lmin_staged(n, v); b2 = L.lmax_staged(n, v)
            if a is None or b2 is None: continue
            games += 1; r_ = L.rho(n, v, a, b2)
            if r_ > 0:
                nz += 1
                if r_ > best: best = r_; ex = [list(q) for q in rows]
        got = "BREAKS" if nz else "rigid"
        agree = (pred == got)
        if not agree: bad += 1
        print("%-3d %-18s %-8s %6d %8d %9s %s" % (n, str(sizes), pred, games, nz, best,
              "ok" if agree else "*** MISMATCH ***"), flush=True)
        rows_out.append(dict(n=n, profile=list(sizes), predicted=pred, games=games,
                             nonzero=nz, best=str(best), agree=agree, example=ex))
json.dump(dict(mismatches=bad, rows=rows_out), open("profiles.json","w"), indent=1)
print("\nprofiles tested: %d   MISMATCHES: %d" % (len(rows_out), bad))
