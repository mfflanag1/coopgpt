from fractions import Fraction as F
from itertools import combinations, permutations
import json

def require(ok,msg):
    if not ok:
        raise ValueError(msg)

def p4_values(x):
    a,b,c,d=map(F,x)
    return [a+c,b+d,b+c]

def paw_values(x):
    a,b,c,d=map(F,x)
    return [a+b,a+c,b+c+d,(a+b+c+d)/2]

require(p4_values((1,1,1,2))==[2,3,2],'P4 active hinge')
require(p4_values((1,1,2,1))==[3,2,3],'P4 inactive hinge')
require(paw_values((2,2,1,1))==[4,3,4,3],'paw active hinge')
require(paw_values((1,1,3,3))==[2,4,7,4],'paw inactive hinge')

def components(adj):
    unseen=set(range(len(adj)))
    result=[]
    while unseen:
        reached={unseen.pop()}
        frontier=list(reached)
        while frontier:
            v=frontier.pop()
            for w in list(unseen):
                if w in adj[v]:
                    unseen.remove(w); reached.add(w); frontier.append(w)
        result.append(reached)
    return result

def multipartite_components(adj):
    for comp in components(adj):
        for z in comp:
            nonneighbors=[v for v in comp if v!=z and v not in adj[z]]
            if any(v in adj[u] for u,v in combinations(nonneighbors,2)):
                return False
    return True

def forbidden(adj):
    for subset in combinations(range(len(adj)),4):
        degrees=sorted(sum(w in adj[v] for w in subset if w!=v) for v in subset)
        if degrees==[1,1,2,2] or degrees==[1,2,2,3]:
            return True
    return False

count=0
for n in range(1,7):
    edges=list(combinations(range(n),2))
    for mask in range(1<<len(edges)):
        adj=[set() for _ in range(n)]
        for k,(u,v) in enumerate(edges):
            if mask>>k&1:
                adj[u].add(v);adj[v].add(u)
        require(multipartite_components(adj)==(not forbidden(adj)), 'graph classification')
        count+=1
print(json.dumps({'status':'PASS','labeled_graphs_checked':count,
 'maximum_vertices':6,'exact_partial_hinge_witnesses':4,
 'scope':'finite diagnostics for analytically proved general classification'},indent=2))
