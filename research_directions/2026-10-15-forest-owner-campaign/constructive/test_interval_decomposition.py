import random,json
r=random.Random(128)
def path_value(cap,weights):
    # Integral optimum exists for this bipartite incidence matrix.
    state={0:0}
    for k,w in enumerate(weights):
        nxt={}
        for prev,score in state.items():
            for x in range(min(cap[k]-prev,cap[k+1])+1):
                nxt[x]=max(nxt.get(x,-1),score+w*x)
        state=nxt
    return max(state.values())
for z in range(100000):
    n=r.randrange(3,12)
    w=[r.randrange(1,10) for _ in range(n-1)]
    cap=[r.randrange(5) for _ in range(n)]
    pos=[0]
    for k,v in enumerate(w):pos.append(pos[-1]+v*(1 if k%2==0 else -1))
    knots=sorted(set(pos));total=0
    for lo,hi in zip(knots,knots[1:]):
        t=(lo+hi)/2
        active=[int(min(pos[k],pos[k+1])<t<max(pos[k],pos[k+1])) for k in range(n-1)]
        total+=(hi-lo)*path_value(cap,active)
    actual=path_value(cap,w)
    if total!=actual:
        print(json.dumps({'case':z,'weights':w,'capacities':cap,'positions':pos,'weighted':actual,'integrated':total}));break
else:print('NO FAILURE')
