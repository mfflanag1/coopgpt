"""Self-contained rerun: ALL 2287 cover vertices, not only the 995 strictly
over-covering ones.  This removes the reliance on route1's P10 (balanced covers
never beat the trivial one) from the n=5 conclusion."""
import json, sys
SCR="/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad"
sys.path.insert(0, SCR); sys.path.insert(0, SCR+"/sel/a3check")
from cone import inequalities
from a3lp import load_vertices, canon_pairs, run, nm, N, FULL

ineqs = inequalities(N)
verts = load_vertices()
pairs = canon_pairs(verts, list(range(1, FULL + 1)))
print(f"ALL {len(verts)} vertices x {FULL} anchors -> {len(pairs)} classes", flush=True)
res={}
for side in ("M","mu"):
    hits=[]
    for k,(w,A) in enumerate(pairs):
        out = run(side, w, A, ineqs)
        if out is not None:
            hits.append({"anchor": nm(A), "cover": {nm(S): str(x) for S,x in w.items()},
                         "v": [str(q) for q in out]})
            print("  FEASIBLE", side, nm(A), {nm(S):str(x) for S,x in w.items()}, flush=True)
        if (k+1)%400==0: print(f"  {side}: {k+1}/{len(pairs)}, {len(hits)} feasible", flush=True)
    res[side]=hits
    print(f"{side}-side: {len(hits)} feasible out of {len(pairs)} classes", flush=True)
json.dump({"n_classes":len(pairs),"M_hits":res["M"],"mu_hits":res["mu"]},
          open(f"{SCR}/sel/a3check/allverts.json","w"), indent=1)
