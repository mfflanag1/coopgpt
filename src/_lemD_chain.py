"""End-to-end verifier of the Lemma D proof chain (exact rational).
For every exact game + non-singleton proper S with room (phi(S)<max_core x(S)):
 if star_S fails: build cover -> W,T*,P,R; verify each link of the proof:
   (C0) cover valid: r_k>=1 (k in S), r_j=0 (j not S), lambda>=0 on tight coalitions.
   (C1) 2-valued: r takes values {rho, sigma}, T*={r=rho}, R={r=sigma}, P=N\S subset W.
   (C2) v(W) >= phi(P)+v(T*)             [the key inequality]
   (C3) M^(T*) := max{x(S):core,x(T*)=v(T*)} <= phi(S)   [certificate caps x(S)]
   (C4) d*(S) <= slack  (Lemma D: S not binding-bumpable)  [decisive]
 Any star-fail with d*>slack => CERTIFIED LEMMA D COUNTEREXAMPLE (saved, reported).
"""
import random, sys, time, json
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import (star_holds, core_max_xS, xS, residual_cover, tight_coalitions,
                  max_exact_bump, exact_lp_min)
def members(S,n): return [i for i in range(n) if S>>i&1]
def M_Ttight(g,S,T):
    n,N,v=g.n,g.N,g.v
    A_ub,b_ub=[],[]
    for U in range(1,N):
        A_ub.append([-1 if U>>i&1 else 0 for i in range(n)]); b_ub.append(-v[U])
    A_eq=[[1]*n,[1 if T>>i&1 else 0 for i in range(n)]]; b_eq=[v[N],v[T]]
    c=[-1 if S>>i&1 else 0 for i in range(n)]
    opt,_=exact_lp_min(c,A_ub,b_ub,A_eq,b_eq)
    return None if opt is None or opt=='unbounded' else -opt
n=int(sys.argv[1]); seed0=int(sys.argv[2]); log=sys.argv[3]
def out(s):
    with open(log,'a') as f: f.write(s+'\n')
rng=random.Random(seed0*2**20+13); N=(1<<n)-1; t0=time.time()
games=0; sf=0; c1=0; c2=0; c3=0; c4=0; nottwoval=0; CX=0; badlink=0
out(f"=== lemD CHAIN n={n} seed0={seed0} @ {time.strftime('%H:%M:%S')} ===")
tights_ok=True
while True:
    kk=rng.randint(2,4); c=rng.randint(n,7*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    games+=1
    tights=set(tight_coalitions(g,phi))
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        pS=xS(phi,S,n)
        if core_max_xS(g,S)<=pS: continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        sf+=1
        rc=residual_cover(g,phi,S)
        if rc is None or not rc['lambda']:
            out("BADLINK no-cover S="+str(members(S,n))); badlink+=1; continue
        # C0 cover valid
        sig=rc['mu']; r=rc['r']
        cover_tight = all(U in tights for U in rc['lambda'])
        W=0
        for U in rc['lambda']: W|=U
        Tstar=W&S; R=S&~W; P=N&~S
        rvals=set(r.values())
        twoval = (len(rvals)<=2) and all((r[k]==sig or r[k]==min(rvals)) for k in r)
        rho = min(rvals)
        Tset=set(k for k in members(S,n) if r[k]<sig)
        # C1
        C1 = (twoval and Tset==set(members(Tstar,n)) and ((P & ~W)==0) and cover_tight
              and all(r[k]>=1 for k in members(S,n)))
        if C1: c1+=1
        else: nottwoval+=1
        # C2
        vW=g.v[W]; rhs=xS(phi,P,n)+g.v[Tstar]
        if vW>=rhs: c2+=1
        else: out("BADLINK C2 v(W)<phi(P)+v(T*) "+json.dumps([str(u) for u in g.v])+" S="+str(members(S,n))); badlink+=1
        # C3
        if Tstar not in (0,S):
            M=M_Ttight(g,S,Tstar)
            if M is not None and M<=pS: c3+=1
            else: out("BADLINK C3 M(T*)>phi(S) "+json.dumps([str(u) for u in g.v])+" S="+str(members(S,n))+" M="+str(M)); badlink+=1
        # C4 decisive: true d* <= slack
        d=max_exact_bump(g,S); slack=pS-g.v[S]
        if d<=slack: c4+=1
        else:
            CX+=1
            pay=dict(n=n,v=[str(u) for u in g.v],S=members(S,n),phi=[str(p) for p in phi],
                     dstar=str(d),slack=str(slack))
            out("*** LEMMA D COUNTEREXAMPLE (d*>slack) *** "+json.dumps(pay))
            json.dump(pay,open(f"../results/WITNESS_lemD_CX_n{n}_s{seed0}.json","w"),indent=1)
    if games%25==0:
        out(f"[prog] games={games} sf={sf} C1(2val):{c1} C2:{c2} C3:{c3} C4(d*<=slack):{c4} "
            f"not2val={nottwoval} badlink={badlink} CX={CX} t={time.time()-t0:.0f}s")
