"""Minimal (n=5) refutation of C-A(a) when exactness of the BUMPED game is
dropped: v exact, v' = v + d.1_S only balanced, yet W is not a richer suffix."""
import sys, itertools
from fractions import Fraction as F
sys.path.insert(0,"/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad")
sys.path.insert(0,"/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/route3")
import audit, z3
from hunt2 import boundaries, nm
from probeA_sweep import exact_lp
from ce7 import lmin_ladder, exact_all
N=5; FULL=31
w=[F(q) for q in ["0","0","0","1","0","0","1","1","0","1","0","1","1","1","2","2",
                  "0","1","0","1","4","4","5","5","0","1","0","1","5","5","5","6"]]
S=0b10111; d=F(1)                       # S = {1,2,3,5}
w2=list(w); w2[S]=w[S]+d
print("v(N) =",w[FULL], " v(S) =",w[S], "-> v'(S) =",w2[S])
print("v exact:", exact_all(N,w), "  v' exact:", exact_all(N,w2))
print("singleton-normalized:", all(w[1<<i]==0 for i in range(N)), all(w2[1<<i]==0 for i in range(N)))
phi=audit.lmin(N,w); phi2=audit.lmin(N,w2)
lphi=lmin_ladder(N,w); lphi2=lmin_ladder(N,w2)
print("phi  =",[str(q) for q in phi], " ladder agrees:", lphi==phi)
print("phi' =",[str(q) for q in phi2]," ladder agrees:", lphi2==phi2)
W=[i for i in range(N) if S>>i&1 and phi2[i]<phi[i]]; Wm=sum(1<<i for i in W)
bnd=boundaries(N,w,phi)
print("S =",nm(N,S)," d =",str(d)," s_phi(S) =",
      str(sum(phi[i] for i in range(N) if S>>i&1)-w[S]))
print("boundaries (suffix, slack):",[(nm(N,H),str(s)) for H,s in bnd])
print("W =",nm(N,Wm)," is a richer suffix?", Wm in [H for H,_ in bnd],
      "  <-- C-A(a) demands True")
print("global losers:",nm(N,sum(1<<i for i in range(N) if phi2[i]<phi[i])))
print("s_phi(W) =",str(sum(phi[i] for i in range(N) if Wm>>i&1)-w[Wm]),
      " loss on W =",str(sum(phi[i]-phi2[i] for i in W)), " (Theorem A holds)")
print("corrected invariant W = H∩S for a slack suffix H?",
      any((H&S)==Wm and s>0 for H,s in bnd))
