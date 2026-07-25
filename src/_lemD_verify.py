"""Broad verifier of the Lemma D certificate chain on exact games.
For every exact game and non-singleton proper S with room (phi(S)<max_core x(S)):
 if star_S fails, build W=union(cover), T*=W&S, R=S\W; assert P1,P2, compute delta,
 and confirm M^(T*)=v(S) (=> d*=0 => not binding-bumpable => Lemma D safe).
 Any binding-bumpable star-fail (d*>slack) => COUNTEREXAMPLE (saved)."""
import random, sys, time, json
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, residual_cover, exact_lp_min
def members(S,n): return [i for i in range(n) if S>>i&1]
def maxxS_Ttight(g,S,T):
    n,N,v=g.n,g.N,g.v
    A_ub,b_ub=[],[]
    for U in range(1,N):
        A_ub.append([-1 if U>>i&1 else 0 for i in range(n)]); b_ub.append(-v[U])
    A_eq=[[1]*n,[1 if T>>i&1 else 0 for i in range(n)]]; b_eq=[v[N],v[T]]
    c=[-1 if S>>i&1 else 0 for i in range(n)]
    opt,_=exact_lp_min(c,A_ub,b_ub,A_eq,b_eq)
    return None if opt is None or opt=='unbounded' else -opt
n=int(sys.argv[1]); seed=int(sys.argv[2]); log=sys.argv[3]
def out(s):
    with open(log,'a') as f: f.write(s+'\n')
rng=random.Random(seed*15485863); N=(1<<n)-1; t0=time.time()
sf=0; okcert=0; deltapos=0; deltazero=0; CX=0; anom=0
out(f"=== lemD VERIFY n={n} seed={seed} @ {time.strftime('%H:%M:%S')} ===")
while True:
    kk=rng.randint(2,4); c=rng.randint(n,7*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        pS=xS(phi,S,n)
        if core_max_xS(g,S)<=pS: continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        sf+=1
        rc=residual_cover(g,phi,S)
        if rc is None or not rc['lambda']:
            anom+=1; out("ANOM no-cover S="+str(members(S,n))+" "+json.dumps([str(u) for u in g.v])); continue
        W=0
        for U in rc['lambda']: W|=U
        Tstar=W&S; R=S&~W
        P1=((N^S)&~W)==0; union=((S|W)==N)
        delta=g.v[S]+g.v[W]-g.v[N]-g.v[Tstar]
        M=maxxS_Ttight(g,S,Tstar) if Tstar not in (0,S) else None
        # certificate valid iff M==v(S)
        good = (M==g.v[S])
        if good: okcert+=1
        if delta>0: deltapos+=1
        if delta==0: deltazero+=1
        if delta<0 or not P1 or not union or not good:
            out("ANOMALY "+json.dumps(dict(v=[str(u) for u in g.v],S=members(S,n),
                W=members(W,n),Tstar=members(Tstar,n),R=members(R,n),
                delta=str(delta),P1=P1,union=union,M=str(M),vS=str(g.v[S]),phiS=str(pS))))
            anom+=1
        # decisive counterexample check: binding-bumpable (d*>slack) AND star fails
        if M is not None and M>pS:   # d*_{T*}>slack => this cert insufficient; check real d*
            out("CERT_INSUFF M>phiS "+json.dumps(dict(S=members(S,n),M=str(M),phiS=str(pS))))
    if sf and sf%10==0:
        out(f"[prog] sf={sf} cert_ok(M=vS):{okcert} delta==0:{deltazero} delta>0:{deltapos} anom={anom} CX={CX} t={time.time()-t0:.0f}s")
