import random, sys
from fractions import Fraction as F
from tugame import Game
from hunt_exact_points import rand_point_sum, game_from_points
from leximin import leximin_core_float
from floatscreen import is_exact_float

def xS(x,S,n): return sum(x[i] for i in range(n) if S>>i&1)
n=int(sys.argv[1]) if len(sys.argv)>1 else 5
seed=int(sys.argv[2]) if len(sys.argv)>2 else 1
rng=random.Random(seed); N=(1<<n)-1
st={'bumps':0,'binding':0,'Sdrop':0,'outgain':0,'binding_Sdrop':0,'binding_outgain':0,'singleton_bumps':0,'singleton_jdrop':0}
exdrop=[]; exout=[]
tested=0
while st['bumps']<8000 and tested<40000:
    tested+=1
    k=rng.randint(2,3); c=rng.randint(n,7*n)
    pts=[rand_point_sum(n,c,rng) for _ in range(k)]
    g=game_from_points(n,pts); vf=[float(u) for u in g.v]
    x=leximin_core_float(n,vf)
    if x is None: continue
    for S in range(1,N):
        d=None
        for dd in range(1,7):
            v2=list(vf); v2[S]+=dd
            if is_exact_float(n,v2): d=dd
            else: break
        if d is None: continue
        v2=list(vf); v2[S]+=d
        y=leximin_core_float(n,v2)
        if y is None: continue
        st['bumps']+=1
        sing = bin(S).count('1')==1
        binding = xS(x,S,n) < g.v[S]+d-1e-9
        if binding: st['binding']+=1
        if sing:
            st['singleton_bumps']+=1
            j=[i for i in range(n) if S>>i&1][0]
            if y[j]<x[j]-1e-6: st['singleton_jdrop']+=1
            continue
        Sdrop=[i for i in range(n) if S>>i&1 and y[i]<x[i]-1e-6]
        outgain=[i for i in range(n) if not(S>>i&1) and y[i]>x[i]+1e-6]
        if Sdrop:
            st['Sdrop']+=1
            if binding: st['binding_Sdrop']+=1
            if len(exdrop)<4: exdrop.append(([str(u) for u in g.v],S,d))
        if outgain:
            st['outgain']+=1
            if binding: st['binding_outgain']+=1
            if len(exout)<4: exout.append((S,d,[(i,round(x[i],3),round(y[i],3)) for i in outgain]))
print(f'n={n} seed={seed}:',st)
print('S-DROP examples (would be violations):',exdrop)
print('OUTSIDER-GAIN examples:',exout)
