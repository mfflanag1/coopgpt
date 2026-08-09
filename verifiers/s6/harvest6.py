"""Task #32 Phase 1(3): a fresh n=6 harvest, exact rationals.

Games are lower envelopes of common-total nonnegative allocations, which are
exactly the exact games -- so no exactness TEST is needed (and none is run:
core-vertex enumeration at n=6 is C(62,5) systems and is forbidden by the
brief).  Lmin and Lmax are recomputed by staged exact optimization.

Records the ratio, the two stratum shapes and the overlap table, so the recon
can say which configurations actually carry which ratios, and whether anything
exceeds the conjectured s(6) = 2/3.
"""
import json, random, sys
from fractions import Fraction as F
HERE = sys.path[0]; sys.path.insert(0, HERE + "/lib")
import audit, lmax as lmaxmod
N = 6; FULL = (1 << N) - 1

def main():
    trials = int(sys.argv[1]); seed = int(sys.argv[2])
    rng = random.Random(seed); recs = []; best = F(0)
    for t in range(trials):
        tot = rng.choice([4,5,6,8,10,12,16,20,24])
        gens = audit.rand_gens(N, rng, rng.randint(2,6), tot, tot)
        v = audit.envelope(N, gens)
        w, _ = audit.normalize(N, v)
        if w[FULL] == 0: continue
        x = audit.lmin(N, w); z = lmaxmod.lmax(N, w)
        if x is None or z is None: continue
        T = w[FULL]
        ratio = sum(abs(x[i]-z[i]) for i in range(N))/T
        sx = audit.strata(x); sz = audit.strata(z)
        ri = {i:k for k,b in enumerate(sx) for i in b}
        ci = {i:l for l,b in enumerate(sz) for i in b}
        tbl = [[0]*len(sz) for _ in sx]
        for i in range(N): tbl[ri[i]][ci[i]] += 1
        if ratio > best:
            best = ratio
            print(f"  new max ratio {ratio}  lmin={[len(b) for b in sx]} "
                  f"lmax={[len(b) for b in sz]}", flush=True)
        if ratio > 0:
            recs.append({"v":[str(a) for a in w], "T":str(T),
                         "lmin":[str(a) for a in x], "lmax":[str(a) for a in z],
                         "ratio":str(ratio),
                         "lmin_shape":[len(b) for b in sx],
                         "lmax_shape":[len(b) for b in sz], "tbl":tbl})
        if (t+1) % 100 == 0:
            print(f"  {t+1}/{trials}, {len(recs)} positive-ratio, max {best}", flush=True)
            json.dump({"max":str(best),"records":recs},
                      open(f"{HERE}/harvest6_{seed}.json","w"), indent=1)
    json.dump({"max":str(best),"records":recs},
              open(f"{HERE}/harvest6_{seed}.json","w"), indent=1)
    print(f"DONE {trials} draws, {len(recs)} positive-ratio games, MAX RATIO {best}")
    print(f"  exceeds 2/3: {best > F(2,3)}")

main()
