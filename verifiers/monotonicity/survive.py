"""What survives after C-A and C-B are both refuted?
Re-runs every constructive family member (all violations, not just the
first) and tests the candidate invariants; merges with the 253 stored
exact-domain violations."""
import json, glob, re, sys, time
from fractions import Fraction as F
sys.path.insert(0,"/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad")
sys.path.insert(0,"/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/route3")
import audit
from hunt2 import boundaries, nm, core_expr, dmax
from probeA_sweep import exact_lp
N=6; FULL=63

def tests(n,w,phi,phi2,S):
    W=[i for i in range(n) if S>>i&1 and phi2[i]<phi[i]]
    if not W: return None
    Wm=sum(1<<i for i in W)
    blocks=audit.strata(phi); bnd=boundaries(n,w,phi)
    sl=[q for q,(H,s) in enumerate(bnd) if s>0]
    if not sl: return None
    jstar=max(sl); Hstar=bnd[jstar][0]; pred=sum(1<<q for q in blocks[jstar+1])
    sW=sum(phi[i] for i in range(n) if Wm>>i&1)-w[Wm]
    lvl=min(phi[i] for i in W)
    return {
      "CA":  Wm in [H for H,s in bnd if s>0],
      "CB":  Wm==pred,
      "single_stratum": any(Wm==sum(1<<q for q in b) for b in blocks),
      "W_sub_Hstar": (Wm & ~Hstar)==0,
      "S_sup_Hstar": (Hstar & ~S)==0,
      "ThmA": sum(phi[i]-phi2[i] for i in W)<=sW and sW>0,
      "PropD": all(sum(phi2[i]-phi[i] for i in range(n) if H>>i&1)>=0
                   for H,s in bnd if s==0 and H!=S),
      "frozen_above_paying": all(phi2[i]==phi[i] for i in range(n)
                                 if phi[i]>max(phi[q] for q in W)),
      "outsider_loser_below_W": all(phi[i]<lvl for i in range(n)
                                    if not S>>i&1 and phi2[i]<phi[i]),
      "W_upward_closed_in_S": all((phi2[i]<phi[i]) for i in range(n)
                                  if (S>>i&1) and phi[i]>lvl),
    }

agg={}
def add(r):
    for k,v in r.items(): agg[k]=agg.get(k,0)+bool(v)
    agg["n"]=agg.get("n",0)+1

# --- stored violations
def parseS(s,n):
    return s if isinstance(s,int) else sum(1<<(int(t)-1) for t in s.strip('{}').split(','))
recs=[]
for f in glob.glob('h[2345]_*.json'):
    d=json.load(open(f))
    for c in d.get('cases',[])+d.get('ce',[]): c['_n']=c.get('n',d.get('n')); recs.append(c)
for f in glob.glob('/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/route3/sweepA_*.json')+ \
         glob.glob('/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/route3/targetedA_*.json'):
    for c in json.load(open(f))['cases']: c['_n']=5; c['exact']=True; recs.append(c)
nstored=0
for c in recs:
    if not c.get('exact',True): continue
    n=c['_n']
    r=tests(n,[F(q) for q in c['w']],[F(q) for q in c['phi']],
            [F(q) for q in c['phi2']],parseS(c['S'],n))
    if r: add(r); nstored+=1
print("stored exact-domain violations:",nstored)

# --- constructive family members (recomputed, ALL violations)
params=[]
for f in sorted(glob.glob('fambox_*.log')):
    for ln in open(f):
        if ln.startswith('HIT '): params.append(eval(ln[ln.index('{'):ln.index('}')+1]))
print("family members:",len(params))
t0=time.time(); nfam=0; famstats={}
for p in params:
    if time.time()-t0>480: break
    A=(0,p['a'],0,p['b'],0,0); B=(0,p['c'],0,p['e'],p['f'],p['g']); C=(p['h'],0,p['i'],0,p['j'],0)
    gens=[tuple(F(q) for q in r) for r in (A,B,C)]
    w=audit.envelope(N,gens); phi=audit.lmin(N,w)
    if phi is None: continue
    x,base=core_expr(N,w)
    for S in range(1,FULL):
        if bin(S).count("1")<2: continue
        sS=sum(phi[q] for q in range(N) if S>>q&1)-w[S]
        g=min(w[S|(1<<q)]-w[S] for q in range(N) if not S>>q&1)
        if g<=sS: continue
        dm=dmax(N,w,S,x,base)
        if dm is None or dm<=sS: continue
        for d in sorted({dm,sS+(dm-sS)/2,sS+(dm-sS)/4,sS+3*(dm-sS)/4}):
            if d<=sS: continue
            w2=list(w); w2[S]=w[S]+d
            if not exact_lp(N,w2): continue
            phi2=audit.lmin(N,w2)
            if phi2 is None: continue
            r=tests(N,w,phi,phi2,S)
            if r:
                add(r); nfam+=1
                for k,v in r.items(): famstats[k]=famstats.get(k,0)+bool(v)
                famstats["n"]=famstats.get("n",0)+1
print("family violations tested:",nfam)
print("\nFAMILY ONLY:",json.dumps(famstats,indent=1))
print("\nALL EXACT-DOMAIN VIOLATIONS:",json.dumps(agg,indent=1))
json.dump({"family":famstats,"all":agg,"n_stored":nstored,"n_family":nfam},
          open("survive.json","w"),indent=1)
