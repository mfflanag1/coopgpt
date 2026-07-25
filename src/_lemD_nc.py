import random, sys, time
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from hunt_exact_points import rand_point_sum, game_from_points
from lemD import star_holds, core_max_xS, xS, residual_cover, max_exact_bump
def members(S,n): return [i for i in range(n) if S>>i&1]
n=int(sys.argv[1]); seed=int(sys.argv[2]); log=sys.argv[3]
def out(s):
    with open(log,'a') as f: f.write(s+'\n')
rng=random.Random(seed); N=(1<<n)-1; t0=time.time(); nc=0; certok=0; g3ok=0; g3fail=0; certfail=0
out(f"=== nc-collector n={n} seed={seed} @ {time.strftime('%H:%M:%S')} ===")
while True:
    kk=rng.randint(2,3); c=rng.randint(n,6*n)
    g=game_from_points(n,[rand_point_sum(n,c,rng) for _ in range(kk)])
    phi=leximin_core_exact(g)
    if phi is None: continue
    for S in range(1,N):
        if bin(S).count("1")<2: continue
        if core_max_xS(g,S)<=xS(phi,S,n): continue
        h,_,_=star_holds(g,phi,S)
        if h: continue
        rc=residual_cover(g,phi,S)
        if not rc['lambda']: continue
        sig=rc['mu']; r=rc['r']
        Tstar=[k for k in members(S,n) if r[k]<sig]
        if len(set(r[k] for k in Tstar))<2: continue  # only NON-constant on T*
        nc+=1
        Wm=0
        for U in rc['lambda']: Wm|=U
        Tmask=Wm&S; P=N&~S
        cert = g.v[Wm] >= xS(phi,P,n)+g.v[Tmask]
        if cert: certok+=1
        else: certfail+=1
        # GOAL3
        slackT=xS(phi,Tmask,n)-g.v[Tmask]
        vals=sorted(set(r[k] for k in Tstar),reverse=True); rhos=vals+[F(0)]
        lhs=F(0)
        for l in range(len(vals)):
            Dl=0
            for k in Tstar:
                if r[k]>=vals[l]: Dl|=1<<k
            lhs+=(rhos[l]-rhos[l+1])*(xS(phi,Dl,n)-g.v[Dl])
        if lhs<=sig*slackT: g3ok+=1
        else:
            g3fail+=1
            out("GOAL3 FAIL "+str([str(u) for u in g.v])+" S="+str(members(S,n))+" r="+str({k:str(v) for k,v in r.items()}))
        d=max_exact_bump(g,S); slack=xS(phi,S,n)-g.v[S]
        lemD = d<=slack
        out(f"[nc {nc}] S={members(S,n)} rTstar={sorted(str(r[k]) for k in Tstar)} sig={sig} cert={cert} GOAL3={lhs<=sig*slackT} lemD={lemD}")
        if not lemD: out("*** LEMMA D COUNTEREX *** "+str([str(u) for u in g.v]))
    if nc and nc%5==0:
        out(f"[prog] nonconst={nc} cert_ok={certok} cert_fail={certfail} GOAL3_ok={g3ok} GOAL3_fail={g3fail} t={time.time()-t0:.0f}s")
