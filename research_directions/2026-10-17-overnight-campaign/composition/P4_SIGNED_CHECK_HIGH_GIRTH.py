from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json, random

counts={'projective_graphs':0,'circulant_graphs':0,'exact_star_identities':0,'degree_upper_profiles':0}

def graph(n,edges):
    adj=[set() for _ in range(n)]
    for u,v in edges:adj[u].add(v);adj[v].add(u)
    return adj

def verify_high_girth(adj,d):
    n=len(adj)
    assert all(len(a)==d for a in adj)
    for v in range(n):
        for u in adj[v]:
            assert not adj[v]&adj[u]
        for u in range(v):assert len(adj[v]&adj[u])<=1
    edges=[(u,v) for u in range(n) for v in adj[u] if u<v]
    assert Q(len(edges),d)==Q(n,2)
    assert Q(n,2)+len(edges)==Q(n*(d+1),2)
    # A star layer centered at v can have arbitrary positive leaf weights.
    rng=random.Random(420+n)
    for z in range(120):
        v=rng.randrange(n);cap=Q(rng.randrange(1,10),rng.randrange(1,5))
        ws={u:Q(rng.randrange(0,10),rng.randrange(1,5)) for u in adj[v]}
        def value(S):
            return min(cap,sum((w for u,w in ws.items() if u in S),Q(0))) if v in S else Q(0)
        grand=value(set(range(n)))
        lhs=sum((value(adj[u]|{u}) for u in range(n)),Q(0))
        rhs=grand+sum((value({u,w}) for u,w in edges),Q(0))
        assert lhs==rhs
        counts['exact_star_identities']+=1
    return {'vertices':n,'degree':d,'edges':len(edges),'distortion_lower':str(Q(d+1,2))}

families=[]
for q in (2,3,5):
    points=[(1,a,b) for a in range(q) for b in range(q)]+[(0,1,b) for b in range(q)]+[(0,0,1)]
    r=len(points);assert r==q*q+q+1
    edges=[(i,r+j) for i,p in enumerate(points) for j,l in enumerate(points) if sum(a*b for a,b in zip(p,l))%q==0]
    info=verify_high_girth(graph(2*r,edges),q+1);info.update(family='projective',q=q);families.append(info)
    counts['projective_graphs']+=1
for d in range(1,6):
    m=2**(d+1);shifts=[2**k for k in range(d)]
    edges=[(x,m+(x+s)%m) for x in range(m) for s in shifts]
    info=verify_high_girth(graph(2*m,edges),d);info.update(family='circulant');families.append(info)
    counts['circulant_graphs']+=1

# Exact dual enumeration on independent small graphs; no numerical LP is used.
examples=[(4,[(0,1),(1,2),(2,3)]),(5,[(i,(i+1)%5) for i in range(5)]),(6,[(i,(i+1)%6) for i in range(6)]),(5,[(0,i) for i in range(1,5)]),(3,[(0,1),(1,2),(0,2)]),(4,[(0,1),(0,2),(1,2),(0,3)]),(4,[(i,j) for i in range(4) for j in range(i)])]
rng=random.Random(8545)
for n,edges in examples:
    adj=graph(n,edges);delta=max(map(len,adj))
    covers=[p for p in product((Q(0),Q(1,2),Q(1)),repeat=n) if all(p[u]+p[v]>=1 for u,v in edges)]
    for _ in range(250):
        capacities=[Q(rng.randrange(0,20),rng.randrange(1,7)) for _ in range(n)]
        F=min(sum((a*b for a,b in zip(capacities,p)),Q(0)) for p in covers)
        H=sum((min(capacities[v],sum((capacities[u] for u in adj[v]),Q(0))) for v in range(n)),Q(0))/2
        assert F<=H<=Q(delta+1,2)*F
        counts['degree_upper_profiles']+=1
result={'status':'PASS','counts':counts,'families':families,'scope':'Exact finite replay; all-capacity, arbitrary-layer and growing-family claims are analytic in the companion note.'}
Path(__file__).with_name('P4_SIGNED_HIGH_GIRTH_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
