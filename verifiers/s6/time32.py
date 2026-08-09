"""Task #32 Phase 1(1,2): cost of the hand net and of pipeline 2 at n=6."""
import json, random, sys, time
from fractions import Fraction as F
sys.path.insert(0,'.')
import nsix, z3
N=6; R=F(2,3)
comps=nsix.compositions(N)
universe=[(r,c,t) for r in comps for c in comps for t in nsix.tables(r,c)]
print(f"universe {len(universe)}")
live=[u for u in universe if u[1][-1]!=1]
print(f"after L1'' : {len(live)}")
rng=random.Random(32)

# --- hand net timing on a random sample ---
samp=rng.sample(live, 200)
t0=time.time(); res={}
for r,c,t in samp:
    k=nsix.handnet(N,r,c,t,R); res[k]=res.get(k,0)+1
dt=time.time()-t0
print(f"HAND NET: {len(samp)} configurations in {dt:.1f}s "
      f"({1000*dt/len(samp):.0f} ms each) -> {res}")
kill=res.get('killed',0)/len(samp)
print(f"  kill rate on the post-L1'' set: {100*kill:.1f}%  "
      f"=> projected survivors {(1-kill)*len(live):.0f} of {len(live)}")
print(f"  projected full-triage wall time: {dt/len(samp)*len(live)/60:.1f} min single-core")

# --- pipeline 2 timing on a small sample (the expensive one) ---
samp2=rng.sample(live, 8)
print("\nPIPELINE 2 (Theorem A + Farkas), target 2/3:")
tot=0
for r,c,t in samp2:
    t0=time.time()
    s,_,_,_,_ = nsix.pipeline2(N,r,c,t,R)
    z3.set_param('timeout', 120000)
    out=s.check(); dt=time.time()-t0; tot+=dt
    print(f"   lmin={r} lmax={c} -> {out} in {dt:.1f}s")
print(f"   mean {tot/len(samp2):.1f}s per configuration")
json.dump({"universe":len(universe),"after_L1":len(live),
           "handnet_ms_each":1000*dt/len(samp),"handnet_kill_rate":kill,
           "pipeline2_mean_s":tot/len(samp2)}, open("time32.json","w"), indent=1)
