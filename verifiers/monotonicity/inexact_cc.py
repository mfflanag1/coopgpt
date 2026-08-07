"""Measure the C-C CONTAINMENTS (not the retired identifications) on
inexact-bump failures, split by the localization hypotheses."""
import json, glob, sys, time
from fractions import Fraction as F
sys.path.insert(0,"/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad")
import audit, z3
from hunt2 import boundaries
def parseS(s,n):
    return s if isinstance(s,int) else sum(1<<(int(t)-1) for t in s.strip('{}').split(','))
def local_exact(n,v2,S):
    full=(1<<n)-1
    x=[z3.Real(f"x{i}") for i in range(n)]
    base=[z3.Sum(x)==audit.to_z3(v2[full])]+[
        z3.Sum([x[i] for i in range(n) if T>>i&1])>=audit.to_z3(v2[T]) for T in range(1,full)]
    for j in range(n):
        if S>>j&1: continue
        T=S|(1<<j)
        if T==full: continue
        o=z3.Optimize(); o.add(base)
        h=o.minimize(z3.Sum([x[i] for i in range(n) if T>>i&1]))
        if o.check()!=z3.sat or audit.rat(o.lower(h))!=v2[T]: return False
    return True
recs=[]
for f in glob.glob('h[2345]_*.json'):
    d=json.load(open(f))
    for c in d.get('cases',[])+d.get('ce',[]): c['_n']=c.get('n',d.get('n')); recs.append(c)
tab={}; tot={'n':0,'both':0,'left':0,'right':0}
t0=time.time()
for c in recs:
    if c.get('exact',True): continue
    if time.time()-t0>420: break
    n=c['_n']; w=[F(q) for q in c['w']]; phi=[F(q) for q in c['phi']]
    phi2=[F(q) for q in c['phi2']]; S=parseS(c['S'],n); d=F(c['d'])
    W=[i for i in range(n) if S>>i&1 and phi2[i]<phi[i]]
    if not W: continue
    Wm=sum(1<<i for i in W)
    sl=[(j,H) for j,(H,s) in enumerate(boundaries(n,w,phi)) if s>0]
    if not sl: continue
    Hstar=max(sl)[1]
    left=(Wm & ~Hstar)==0; right=(Hstar & ~S)==0
    tot['n']+=1; tot['left']+=left; tot['right']+=right; tot['both']+=(left and right)
    w2=list(w); w2[S]=w[S]+d
    k="LE" if local_exact(n,w2,S) else "notLE"
    t=tab.setdefault(k,{'n':0,'both':0})
    t['n']+=1; t['both']+=(left and right)
print("inexact-bump failures, C-C containments:",json.dumps(tot,indent=1))
print("pct both:", round(100*tot['both']/max(tot['n'],1),1))
for k,t in tab.items():
    print("%-6s both %d/%d = %.1f%%"%(k,t['both'],t['n'],100*t['both']/max(t['n'],1)))
