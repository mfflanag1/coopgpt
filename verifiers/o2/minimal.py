"""Minimal sufficient hypothesis subsets (pinning is always kept: it is the one
hypothesis whose removal restores feasibility)."""
import json, sys, itertools
from fractions import Fraction as F
import z3
SCR="/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad"
sys.path.insert(0,SCR); sys.path.insert(0,SCR+"/sel/a3check"); sys.path.insert(0,SCR+"/sel/o2")
from cone import inequalities
from o2main import load_pinverts, sz, nm, N, FULL, J, L, R
from ablate import prog
ineqs=inequalities(N); pins=load_pinverts()
subsets=[("pinning only", dict(z0=False,nu=False,x0=False,cone=False)),
         ("pinning + z0", dict(z0=True, nu=False,x0=False,cone=False)),
         ("pinning + x0", dict(z0=False,nu=False,x0=True, cone=False)),
         ("pinning + nu", dict(z0=False,nu=True, x0=False,cone=False)),
         ("pinning + z0 + x0", dict(z0=True,nu=False,x0=True,cone=False))]
out={}
for label,kw in subsets:
    cnt=0
    for Sstar in range(1,FULL+1):
        for pin in pins:
            if prog(Sstar,pin,ineqs,**kw): cnt+=1
    out[label]=cnt
    print(f"  {label:22s}: {cnt:6d} / {FULL*len(pins)} feasible"
          + ("   <-- SUFFICIENT" if cnt==0 else ""), flush=True)
json.dump(out, open(f"{SCR}/sel/o2/minimal.json","w"), indent=1)
