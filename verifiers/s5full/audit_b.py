"""End-to-end audit of the (b) witness: is it a REAL game in CFG with no
nu-attaining triple, or another certificate-not-realizable case?"""
import json, sys
from fractions import Fraction as F
SCR="/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad"
sys.path.insert(0,SCR); sys.path.insert(0,SCR+"/sel/s5full")
import audit, lmax as lmaxmod
d=json.load(open(f"{SCR}/sel/s5full/checks2.json"))
w=d["b_witness"]
if not w: print("no witness"); sys.exit()
v=[F(q) for q in w["v"]]; N,FULL=5,31
print("v =",[str(q) for q in v]); print("LP mu =",w["mu"])
print("singleton-normalized:",all(v[1<<i]==0 for i in range(N)))
ex=audit.is_exact(N,v); print("exact (vertex enumeration):",ex)
if ex:
    phi=audit.lmin(N,v); psi=lmaxmod.lmax(N,v)
    st=lambda p:[len(b) for b in audit.strata(p)]
    print("Lmin =",[str(q) for q in phi]," strata",st(phi))
    print("Lmax =",[str(q) for q in psi]," strata",st(psi))
    T=v[FULL]; mu=min(phi); M=max(psi)
    nu=max(F(v[S],bin(S).count("1")) for S in range(1,FULL+1))
    trip=[S for S in range(1,FULL+1) if bin(S).count("1")==3 and F(v[S],3)==nu]
    ratio=sum(abs(phi[i]-psi[i]) for i in range(N))/T
    print(f"mu={mu} M={M} nu={nu} ratio={ratio}")
    print("nu-attaining triples:",[ "".join('abcde'[i] for i in range(N) if S>>i&1) for S in trip])
    cfg=(st(phi)==[3,2] and sorted(st(psi))==[1,4] and min(psi)==0)
    print("in CFG:",cfg)
    print("VERDICT:", "hypothesis 2 CAN fail in a real CFG game" if (cfg and not trip)
          else "certificate NOT realizable as CFG (LP model only)")
