"""Task #32 Phase 1, corrected timing: same CONFIGURATION (r,c,tbl) through both
encodings, with the full triple recorded so 'unknown' cases can be re-tested.

(The first attempt compared different tables for the same shape pair and was
therefore not a like-for-like test; this one is.)
"""
import json, random, sys, time
from fractions import Fraction as F
import z3
sys.path.insert(0,'.')
import nsix
from opt32 import pipeline2_shared
N=6; R=F(2,3); CAP=300000
comps=nsix.compositions(N)
live=[(r,c,t) for r in comps for c in comps for t in nsix.tables(r,c) if c[-1]!=1]
rng=random.Random(3232)
samp=rng.sample(live, 24)
rows=[]
for r,c,t in samp:
    rec={"lmin":list(r),"lmax":list(c),"tbl":t}
    for name,fn in (("orig", lambda: nsix.pipeline2(N,r,c,t,R)[0]),
                    ("shared", lambda: pipeline2_shared(N,r,c,t,R))):
        s=fn(); s.set("timeout",CAP)
        t0=time.time(); out=s.check(); dt=time.time()-t0
        rec[name]=str(out); rec[name+"_s"]=round(dt,1)
    rows.append(rec)
    print(f"  lmin={r} lmax={c} tbl={t}", flush=True)
    print(f"      orig {rec['orig']:8s} {rec['orig_s']:7.1f}s | "
          f"shared {rec['shared']:8s} {rec['shared_s']:7.1f}s", flush=True)
    json.dump(rows, open("time32b.json","w"), indent=1)
for k in ("orig","shared"):
    unk=sum(1 for x in rows if x[k]=="unknown")
    tot=sum(x[k+"_s"] for x in rows)
    print(f"{k}: {unk}/{len(rows)} unknown, mean {tot/len(rows):.1f}s, "
          f"max {max(x[k+'_s'] for x in rows):.1f}s")
