"""Warm-up: verify (*) numerically on freshly harvested CFG games.

CFG: Lmin strata (3,2); Lmax strata (1,4) with min(Lmax) = 0.
Checks per CFG game: f({j}) >= T/8, mu = T/8, M = T/4, ratio = 1/2, j poor.
"""
import json, random, sys
from fractions import Fraction as F
SCR="/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad"
sys.path.insert(0, SCR)
import audit, lmax as lmaxmod

def run(trials, seed):
    rng = random.Random(seed); n=5; full=31
    st = {"games":0,"cfg":0,"star_ok":0,"ratio_half":0,"mu_T8":0,"M_T4":0,"j_poor":0}
    bad=[]
    for _ in range(trials):
        tot = rng.choice([4,5,6,8,12,16])
        gens = audit.rand_gens(n, rng, rng.randint(2,6), tot, tot)
        v = audit.envelope(n, gens)
        w,_ = audit.normalize(n, v)
        if w[full] == 0: continue
        st["games"] += 1
        x = audit.lmin(n,w); z = lmaxmod.lmax(n,w)
        sx = [len(b) for b in audit.strata(x)]; sz_ = [len(b) for b in audit.strata(z)]
        if not (sx==[3,2] and sorted(sz_)==[1,4] and min(z)==0): continue
        st["cfg"] += 1
        T = w[full]
        j = [i for i in range(n) if z[i]==0]
        if len(j)!=1: continue
        j = j[0]
        fj = T - w[full ^ (1<<j)]
        mu = min(x); M = max(z)
        ratio = sum(abs(x[i]-z[i]) for i in range(n))/T
        st["star_ok"] += (fj >= F(T,8))
        st["mu_T8"]   += (mu == F(T,8))
        st["M_T4"]    += (M == F(T,4))
        st["ratio_half"] += (ratio == F(1,2))
        st["j_poor"]  += (x[j] == mu)
        if fj < F(T,8):
            bad.append({"v":[str(q) for q in w],"j":j,"f_j":str(fj),"T":str(T)})
    return st, bad

if __name__ == "__main__":
    trials = int(sys.argv[1]) if len(sys.argv)>1 else 400
    seed = int(sys.argv[2]) if len(sys.argv)>2 else 5
    st, bad = run(trials, seed)
    print(json.dumps(st, indent=1))
    print("VIOLATIONS of (*):", len(bad))
    json.dump({"stats":st,"violations":bad}, open(f"{SCR}/sel/o2/warmup_{seed}.json","w"), indent=1)
