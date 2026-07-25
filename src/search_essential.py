import random, json, sys
from fractions import Fraction as F
from es_float import core_min_all, ega_float
from tugame import Game
from hunt_sd import exactify, is_exact_game
from eshunt import is_ES

def has_dummy(n, v):
    for i in range(n):
        b=1<<i
        if all(v[S|b]==v[S] for S in range((1<<n)) if not S>>i&1):
            return True
    return False

def rand_small(n,rng,hi):
    N=(1<<n)-1; v=[0.0]*(1<<n)
    for S in range(1,N): v[S]=float(rng.randint(0,hi))
    v[N]=float(rng.randint(hi,2*hi)); return v

rng=random.Random(int(sys.argv[1])); n=6; found=0
for t in range(300000):
    v=rand_small(n,rng,rng.choice([4,5,6]))
    ve=core_min_all(n,v)
    if ve is None: continue
    gm,infl=ega_float(n,ve)
    if infl is None or infl<=1e-5: continue
    g=Game(n,[F(x).limit_denominator(10**6) for x in v])
    ge=exactify(g)
    if ge is None or not is_exact_game(ge): continue
    es,gamma=is_ES(ge)
    if es: continue
    if has_dummy(n,ge.v): continue   # require every player essential
    found+=1
    print("ESSENTIAL n=6 exact non-ES: vN=",str(ge.v[ge.N]),"claims=",[str(x) for x in gamma],flush=True)
    json.dump({"n":n,"v":[str(x) for x in ge.v],"claims":[str(x) for x in gamma]},
              open(f"ESSENTIAL_es_n6.json","w"),indent=1)
    if found>=3: break
print("done found",found,flush=True)
