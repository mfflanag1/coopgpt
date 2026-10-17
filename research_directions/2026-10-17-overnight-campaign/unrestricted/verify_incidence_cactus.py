from fractions import Fraction as Q
from itertools import combinations

if not __debug__:
    raise RuntimeError('Assertions must remain enabled')

def inverse(A):
    n=len(A)
    M=[[Q(x) for x in row]+[Q(i==j) for j in range(n)] for i,row in enumerate(A)]
    for k in range(n):
        p=next((i for i in range(k,n) if M[i][k]),None)
        if p is None:return None
        M[k],M[p]=M[p],M[k]
        v=M[k][k];M[k]=[x/v for x in M[k]]
        for i in range(n):
            if i!=k:
                v=M[i][k];M[i]=[x-v*y for x,y in zip(M[i],M[k])]
    return [row[n:] for row in M]

def cactus(rows,n):
    # Independent combinatorial test: every biconnected edge block is an
    # isolated edge or a simple cycle. Tarjan's edge-stack decomposition.
    adj=[[] for _ in range(n+len(rows))]
    for r,S in enumerate(rows):
        for i in S:
            adj[i].append(n+r);adj[n+r].append(i)
    disc=[-1]*len(adj);low=[-1]*len(adj);stack=[];counter=0;valid=True
    def block_ok(edges):
        if len(edges)==1:return True
        degree={}
        for a,b in edges:
            degree[a]=degree.get(a,0)+1;degree[b]=degree.get(b,0)+1
        return all(v==2 for v in degree.values())
    def dfs(u,parent):
        nonlocal counter,valid
        disc[u]=low[u]=counter;counter+=1
        for v in adj[u]:
            if v==parent:continue
            if disc[v]<0:
                stack.append((u,v));dfs(v,u);low[u]=min(low[u],low[v])
                if low[v]>=disc[u]:
                    edges=[]
                    while True:
                        edge=stack.pop();edges.append(edge)
                        if edge==(u,v):break
                    valid=valid and block_ok(edges)
            elif disc[v]<disc[u]:
                stack.append((u,v));low[u]=min(low[u],disc[v])
    for u in range(len(adj)):
        if disc[u]<0:dfs(u,-1)
    assert not stack
    return valid

def check(rows,n):
    global bases,derivatives,zeros
    G=[[len(a&b) for b in rows] for a in rows]
    H=inverse(G)
    if H is None:return
    bases+=1
    for r,S in enumerate(rows):
        d=[sum(H[s][r] for s,U in enumerate(rows) if i in U) for i in range(n)]
        assert all(sum(d[i] for i in U)==Q(s==r) for s,U in enumerate(rows))
        for i in S:
            assert d[i]>=0,(rows,r,i,d)
            derivatives+=1;zeros+=d[i]==0

bases=derivatives=zeros=systems=0
for n in range(1,6):
    available=[frozenset(i for i in range(n) if mask>>i&1) for mask in range(1,1<<n)]
    for m in range(1,min(n,4)+1):
        for rows in combinations(available,m):
            if cactus(rows,n):
                systems+=1;check(rows,n)

# Many four-cycles sharing a high-degree row. Every even endpoint also has
# an attached leaf row, so row and column degrees both exceed two.
growing=0
for k in range(2,16):
    rows=[frozenset(range(2*k))]
    for j in range(k):
        rows.append(frozenset([2*j,2*j+1,2*k+j]))
        rows.append(frozenset([2*j,3*k+j]))
    assert cactus(rows,4*k)
    check(rows,4*k);growing+=1

# Alternating cycles with one or several singleton anchors exercise hard
# zero pins and source components whose endpoint sum is forced to zero.
pinned=0
for k in range(3,13):
    cycle=[frozenset([j,(j+1)%k]) for j in range(k)]
    for anchor in range(k):
        rows=cycle+[frozenset([anchor])]
        assert cactus(rows,k)
        check(rows,k);pinned+=1

bad=[frozenset([0,1]),frozenset([0,2]),frozenset([0,1,2])]
assert not cactus(bad,3)
H=inverse([[len(a&b) for b in bad] for a in bad])
d=[sum(H[s][2] for s,S in enumerate(bad) if i in S) for i in range(3)]
assert d==[Q(-1),Q(1),Q(1)]
lo=[Q(1),Q(0),Q(0)];hi=[Q(1,2)]*3
assert all(sum(lo[i] for i in S)>=1 for S in bad)
assert all(sum(hi[i] for i in S)>=v for S,v in zip(bad,[Q(1),Q(1),Q(3,2)]))
assert sum(lo)==1 and sum(hi)==Q(3,2) and hi[0]<lo[0]

print({'status':'PASS','cactus_systems':systems,'independent_bases':bases,
       'own_derivatives':derivatives,'pinned_zero_derivatives':zeros,
       'growing_high_degree_cacti':growing,'anchored_cycle_systems':pinned,
       'overlapping_cycle_counterexample':'exact (-1,1,1)'})
