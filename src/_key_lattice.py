"""LATTICE CHECK for (KEY). At star-fail configs of exact games:
 (L1) is the tight-set family at phi closed under union & intersection?
 (L2) is W = union of cover coalitions TIGHT at phi (slack(W)=0)?
 (L3) slack(W) vs slack(T*): does (KEY)<=>slack(W)<=slack(T*) hold, and with equality?
Also report whether ANY two tight sets A,B have non-tight union (the direct obstruction).
Exact rational throughout.
"""
import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, residual_cover, tight_coalitions

def members(S,n): return [i for i in range(n) if S>>i&1]

n=int(sys.argv[1]); seed0=int(sys.argv[2]); trials=int(sys.argv[3])
log=sys.argv[4] if len(sys.argv)>4 else None
def out(s):
    print(s, flush=True)
    if log:
        with open(log,'a') as f: f.write(s+'\n')

rng=random.Random(seed0*2**20+13); N=(1<<n)-1; t0=time.time()
games=0; sf=0
# lattice-of-all-tight-sets stats
lat_closed_all=0; lat_broken_all=0
# W-specific
W_tight=0; W_nottight=0
# slack(W)<=slack(T*)
key_ok=0; key_bad=0; key_eq=0; key_strict=0
# does union-of-tight stay tight in general?
union_tight_pairs=0; union_nontight_pairs=0

out(f"=== KEY lattice n={n} seed0={seed0} trials={trials} @ {time.strftime('%H:%M:%S')} ===")

for t in range(trials):
    kk=rng.randint(2,4); c=rng.randint(n,7*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    games+=1
    tights=set(tight_coalitions(g,phi))
    # (L1) global lattice check on all tight sets (sample pairs; full if small)
    tl=list(tights)
    if len(tl)<=60:
        broke=False
        for i in range(len(tl)):
            for j in range(i,len(tl)):
                A,B=tl[i],tl[j]
                U=A|B; I=A&B
                # union tight?
                if U!=N and U!=0:
                    ut = (xS(phi,U,n)==g.v[U])
                    if ut: union_tight_pairs+=1
                    else: union_nontight_pairs+=1; broke=True
                # intersection tight?
                if I!=0 and I!=N:
                    it = (xS(phi,I,n)==g.v[I])
                    if not it: broke=True
        if broke: lat_broken_all+=1
        else: lat_closed_all+=1
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        pS=xS(phi,S,n)
        if core_max_xS(g,S)<=pS: continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        sf+=1
        rc=residual_cover(g,phi,S)
        if rc is None or not rc['lambda']: continue
        W=0
        for Uc in rc['lambda']: W|=Uc
        Tstar=W&S; P=N&~S
        # (L2) W tight?
        sW=xS(phi,W,n)-g.v[W]
        if sW==0: W_tight+=1
        else: W_nottight+=1
        # (L3) slack(W) vs slack(T*)
        sT=xS(phi,Tstar,n)-g.v[Tstar]
        if sW<=sT: key_ok+=1
        else:
            key_bad+=1
            out("*** KEY VIOLATION slack(W)>slack(T*) *** "
                +f"v={[str(u) for u in g.v]} S={members(S,n)} "
                +f"W={members(W,n)} Tstar={members(Tstar,n)} sW={sW} sT={sT}")
        if sW==sT: key_eq+=1
        else: key_strict+=1
    if games%50==0:
        out(f"[prog] games={games} sf={sf} | latClosed={lat_closed_all} latBroke={lat_broken_all} "
            f"unionTight={union_tight_pairs} unionNONtight={union_nontight_pairs} | "
            f"Wtight={W_tight} Wnottight={W_nottight} | KEYok={key_ok} KEYbad={key_bad} "
            f"(eq={key_eq} strict={key_strict}) t={time.time()-t0:.0f}s")

out(f"DONE n={n} seed0={seed0}: games={games} sf={sf}")
out(f"  ALL-tight-set lattice: closed={lat_closed_all} broken={lat_broken_all}")
out(f"  union-of-tight-pairs: tight={union_tight_pairs} NONtight={union_nontight_pairs}")
out(f"  W tight: {W_tight}  W NOT tight: {W_nottight}")
out(f"  KEY slack(W)<=slack(T*): ok={key_ok} bad={key_bad}  (equality={key_eq} strict={key_strict})")
