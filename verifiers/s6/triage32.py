"""Task #32 Phase 1(2): the full A3-FREE hand-net triage over the entire n=6
configuration universe.  levels + L1'' + L7 + L7' + L11 + L12, target 2/3.
Nothing here assumes A3 (false on the M-side at n>=6)."""
import json, sys
from fractions import Fraction as F
sys.path.insert(0,'.')
import nsix
N=6; R=F(2,3)
nsh, sh = int(sys.argv[1]), int(sys.argv[2])
comps=nsix.compositions(N)
univ=[(r,c,t) for r in comps for c in comps for t in nsix.tables(r,c)]
mine=[u for i,u in enumerate(univ) if i%nsh==sh]
tally={"L1-excluded":0,"killed":0,"survives":0}; surv=[]
for i,(r,c,t) in enumerate(mine):
    k=nsix.handnet(N,r,c,t,R); tally[k]+=1
    if k=="survives": surv.append([list(r),list(c),t])
    if (i+1)%500==0:
        print(f"  [{sh}] {i+1}/{len(mine)} {tally}", flush=True)
        json.dump({"tally":tally,"survivors":surv}, open(f"triage32_{sh}.json","w"))
json.dump({"tally":tally,"survivors":surv}, open(f"triage32_{sh}.json","w"))
print(f"SHARD {sh} DONE {tally}")
