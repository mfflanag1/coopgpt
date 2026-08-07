"""m=5, h=2 (n=7): how many split (P)-types are indecomposable?"""
import sys, json; sys.path.insert(0,'/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad')
sys.path.insert(0,'/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/sel')
import catalogue, sbcheck
from enum_packets import enumerate_packets
n=7; m=5; H=sum(1<<i for i in range(m,n))
pks=enumerate_packets(n,H)
full={}; split={}
for p in pks:
    k=catalogue.canon(n,p["lam"])
    (full if (len(p["traces"])==1 and p["traces"][0]==H) else split).setdefault(k,p)
print(f"n=7 (m,h)=(5,2): {len(pks)} packets, {len(full)} full-trace types, {len(split)} split types", flush=True)
res={"full_trace_types":len(full),"split_types":len(split),"split_indecomposable":[]}
cnt=0
for k,p in split.items():
    ind,E=sbcheck.is_indecomposable(n,list(p["lam"]))
    if ind:
        cnt+=1
        res["split_indecomposable"].append(catalogue.pretty(n,p["lam"]))
        print("  INDECOMPOSABLE split:", catalogue.pretty(n,p["lam"]), flush=True)
print(f"  split types indecomposable: {cnt} / {len(split)}", flush=True)
res["count"]=cnt
json.dump(res,open('/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/sel/m5.json','w'),indent=1)
