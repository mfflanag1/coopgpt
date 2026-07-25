import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, residual_cover, core_min_xT
def members(S,n): return [i for i in range(n) if S>>i&1]
def subgame(g, Wm):
    mem=members(Wm,g.n); k=len(mem)
    v2=[F(0)]*(1<<k)
    for bits in range(1,1<<k):
        SS=0
        for i in range(k):
            if bits>>i&1: SS|=1<<mem[i]
        v2[bits]=g.v[SS]
    return Game(k,v2),mem
def is_exact(gg):
    for T in range(1,gg.N):
        if core_min_xT(gg,T)!=gg.v[T]: return False
    return True
n=int(sys.argv[1]); seed=int(sys.argv[2]); cap=int(sys.argv[3])
rng=random.Random(seed*17); N=(1<<n)-1; t0=time.time()
sf=0; Wexact=0; Wnotexact=0; philex=0; philexno=0
while time.time()-t0<cap:
    kk=rng.randint(2,3); c=rng.randint(n,6*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        if core_max_xS(g,S)<=xS(phi,S,n): continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        sf+=1
        rc=residual_cover(g,phi,S)
        if not rc['lambda']: continue
        Wm=0
        for U in rc['lambda']: Wm|=U
        gW,memW=subgame(g,Wm)
        if is_exact(gW): Wexact+=1
        else: Wnotexact+=1
        # is phi|_{T*} the leximin of T*-subgame with INFLATED grand value phi(T*)?
        Tmask=Wm&S
        if bin(Tmask).count("1")>=2:
            gT,memT=subgame(g,Tmask)
            # inflate grand value to phi(T*)
            v2=list(gT.v); v2[gT.N]=xS(phi,Tmask,g.n); gTinf=Game(gT.n,v2)
            lex=leximin_core_exact(gTinf)
            if lex is not None:
                phiT=[phi[i] for i in memT]
                if lex==phiT: philex+=1
                else: philexno+=1
    if sf and sf%20==0:
        print(f"[prog] sf={sf} Wexact={Wexact} Wnotexact={Wnotexact} phiT=lexInflated:{philex} no:{philexno} t={time.time()-t0:.0f}s",flush=True)
print(f"n={n} seed={seed}: sf={sf} W-subgame exact:{Wexact} not:{Wnotexact} | phi|T*=leximin(inflated T*):{philex} no:{philexno}",flush=True)
