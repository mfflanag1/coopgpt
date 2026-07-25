import random
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from hunt_sd import is_exact_game
from family_infeasible import is_family_feasible, certify_infeasible
n=4
A,B,C=3,5,6  # {0,1},{0,2},{1,2} balanced collection on players 0,1,2
def mk(vals):
    v=[F(0)]*16
    for S,x in vals.items(): v[S]=F(x)
    return Game(n,v)
def add(vals,bumps):
    d=dict(vals)
    for S,x in bumps: d[S]=d.get(S,0)+x
    return d
rng=random.Random(0)
star_tested=star_inf=lat_tested=lat_inf=0
for trial in range(400000):
    M=rng.randint(4,7); p=rng.randint(1,3)
    vals={15:M,3:p,5:p,6:p}
    for T in (7,11,13,14): vals[T]=rng.randint(p,M)
    for T in (9,10,12): vals[T]=rng.randint(0,M)
    base=mk(vals)
    if not is_balanced_game(base): continue
    d=rng.randint(1,3)
    bA,bB,bC=(A,d),(B,d),(C,d)
    sA=mk(add(vals,[bA])); sB=mk(add(vals,[bB])); sC=mk(add(vals,[bC]))
    top=mk(add(vals,[bA,bB,bC]))
    if is_balanced_game(top): continue
    if not all(is_balanced_game(g) for g in (sA,sB,sC)): continue
    games=[base,sA,sB,sC]; edges=[(0,1,A),(0,2,B),(0,3,C)]
    star_tested+=1
    feas,_=is_family_feasible(games,edges)
    if not feas:
        star_inf+=1
        cert=certify_infeasible(games,edges)
        if cert['infeasible']:
            print("STAR INFEASIBLE vals",vals,"d",d,"farkas",cert.get('farkas') is not None,
                  "exact_members",[is_exact_game(g) for g in games],flush=True)
    dAB=mk(add(vals,[bA,bB])); dAC=mk(add(vals,[bA,bC])); dBC=mk(add(vals,[bB,bC]))
    if all(is_balanced_game(g) for g in (dAB,dAC,dBC)):
        G=[base,sA,sB,sC,dAB,dAC,dBC]
        E=[(0,1,A),(0,2,B),(0,3,C),(1,4,B),(2,4,A),(1,5,C),(3,5,A),(2,6,C),(3,6,B)]
        lat_tested+=1
        feas2,_=is_family_feasible(G,E)
        if not feas2:
            lat_inf+=1
            cert=certify_infeasible(G,E)
            if cert['infeasible']:
                print("LATTICE INFEASIBLE vals",vals,"d",d,"farkas",cert.get('farkas') is not None,
                      "exact_members",[is_exact_game(g) for g in G],flush=True)
    if star_tested>6000 and lat_tested>3000: break
print("star_tested",star_tested,"star_inf",star_inf,"lat_tested",lat_tested,"lat_inf",lat_inf)
