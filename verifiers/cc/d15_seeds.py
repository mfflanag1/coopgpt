"""d15: solver-robustness cross-check for the UNSAT verdicts.

The n=5 theorems rest on z3 returning unsat.  z3 is exact over LRA, but a single
configuration is a single point of failure, so the same shapes are re-solved
with different random seeds and with the constraints permuted (shuffling the
assertion order changes the search completely).  Any disagreement would void
the corresponding theorem.

usage: d15_seeds.py <target> <shapes as "1,3:3 4:4"> [--timeout=SEC]
"""
import sys, time, random
import z3
import d2_lab as lab

target = sys.argv[1]
shapes = []
for tok in sys.argv[2].split():
    g, c = tok.split(":")
    shapes.append((tuple(int(x) for x in g.split(",")), int(c)))
tmo = 900000
for a in sys.argv[3:]:
    if a.startswith("--timeout="):
        tmo = int(float(a.split("=")[1]) * 1000)
groups = lab.ALLGROUPS if target in ("right", "left", "control") else \
    ["core", "sup", "exv", "exv2", "cert", "cert2", "worse", "hmin"]
print("target=%s groups=%s" % (target, ",".join(groups)), flush=True)
for gaps, cstar in shapes:
    for seed in (0, 1, 7, 12345):
        s, H = lab.build(len(gaps) and 5, gaps, cstar, target, groups)
        cs = list(s.assertions())
        random.Random(seed).shuffle(cs)
        s2 = z3.Solver()
        s2.set("timeout", tmo, "random_seed", seed, "smt.random_seed", seed)
        for c in cs:
            s2.add(c)
        t0 = time.time()
        r = s2.check()
        print("  gaps=%-12s c*=%d  seed=%-6d %-7s (%.0fs)"
              % (str(gaps), cstar, seed, r, time.time() - t0), flush=True)
