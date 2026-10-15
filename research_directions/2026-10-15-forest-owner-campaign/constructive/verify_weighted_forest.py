from random import Random
import json

def tree_value(n, edges, cap, weights):
    adj=[[] for _ in range(n)]
    for k,(u,v) in enumerate(edges):
        adj[u].append((v,k));adj[v].append((u,k))
    def walk(v,parent):
        children=[]
        for ch,k in adj[v]:
            if ch!=parent:children.append((ch,k,walk(ch,v)))
        # best[t] for total capacity allocated to child edges exactly t.
        best={0:0}
        for ch,k,sub in children:
            nxt={}
            for used,score in best.items():
                for x in range(min(cap[ch],cap[v]-used)+1):
                    val=score+weights[k]*x+sub[x]
                    nxt[used+x]=max(nxt.get(used+x,-1),val)
            best=nxt
        return [max(score for used,score in best.items() if used<=cap[v]-parentx)
                for parentx in range(cap[v]+1)]
    return walk(0,-1)[0]

r=Random(26321);checks=0;thresholds=0
for z in range(20000):
    n=r.randrange(2,20)
    edges=[(r.randrange(v),v) for v in range(1,n)]
    weights=[r.randrange(1,15) for _ in edges]
    cap=[r.randrange(5) for _ in range(n)]
    parity=[0]*n;positions=[0]*n
    for k,(p,v) in enumerate(edges):
        parity[v]=1-parity[p]
        positions[v]=positions[p]+weights[k]*(1 if parity[v] else -1)
    knots=sorted(set(positions));integrated=0
    for lo,hi in zip(knots,knots[1:]):
        mid=(lo+hi)/2
        active=[int(min(positions[u],positions[v])<mid<max(positions[u],positions[v]))
                for u,v in edges]
        # Inactive edges have profit zero, not forbidden: zero edges can always
        # be discarded, so they do not alter the active-edge value optimum.
        integrated+=(hi-lo)*tree_value(n,edges,cap,active)
        thresholds+=1
    actual=tree_value(n,edges,cap,weights)
    if actual!=integrated:raise RuntimeError((edges,weights,cap,positions,actual,integrated))
    checks+=1
print(json.dumps({'status':'PASS','exact_integer_tree_profiles':checks,
 'threshold_optimizations':thresholds,'max_vertices':19,
 'scope':'finite branching-tree corroboration; full real-capacity proof in WEIGHTED_FOREST_REDUCTION.txt'},indent=2))
