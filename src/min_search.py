import random, json, sys
from fractions import Fraction as F
from es_float import core_min_all, ega_float
from tugame import Game
from hunt_sd import exactify, is_exact_game
from eshunt import is_ES

def rand_small(n, rng, hi):
    N=(1<<n)-1; v=[0.0]*(1<<n)
    for S in range(1,N): v[S]=float(rng.randint(0,hi))
    v[N]=float(rng.randint(hi,2*hi))
    return v

best=None
rng=random.Random(int(sys.argv[1]))
n=5
for t in range(200000):
    hi=rng.choice([3,4,5])
    v=rand_small(n,rng,hi)
    ve=core_min_all(n,v)
    if ve is None: continue
    gm,infl=ega_float(n,ve)
    if infl is None or infl<=1e-5: continue
    g=Game(n,[F(x).limit_denominator(10**6) for x in v])
    ge=exactify(g)
    if ge is None or not is_exact_game(ge): continue
    es,gamma=is_ES(ge)
    if es: continue
    vN=ge.v[ge.N]; supp=sum(1 for x in ge.v if x!=0)
    key=(vN,supp)
    if best is None or key<best[0]:
        best=(key,[str(x) for x in ge.v],[str(x) for x in gamma])
        print("new best vN=",str(vN),"supp=",supp,"claims=",best[2],flush=True)
        json.dump({"n":n,"v":best[1],"claims":best[2]},open("MIN_es_n5.json","w"),indent=1)
print("done best:",best[0] if best else None,flush=True)
