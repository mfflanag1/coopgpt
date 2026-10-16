"""Exact independent max-profit flow oracle for bipartite resource graphs."""
from fractions import Fraction as Q

def value(cap,edges):
    d=len(cap);neighbors=[[] for _ in range(d)]
    for u,v,p in edges:
        u,v=int(u),int(v);neighbors[u].append(v);neighbors[v].append(u)
    color={}
    for root in range(d):
        if root in color:continue
        color[root]=0;stack=[root]
        while stack:
            u=stack.pop()
            for v in neighbors[u]:
                if v not in color:color[v]=1-color[u];stack.append(v)
                elif color[v]==color[u]:raise RuntimeError('non-bipartite graph')
    N=d+2;s=d;t=d+1;graph=[[] for _ in range(N)]
    def add(u,v,c,k):
        graph[u].append([v,Q(c),Q(k),len(graph[v])]);graph[v].append([u,Q(0),-Q(k),len(graph[u])-1])
    for u,c in enumerate(cap):
        if color[u]==0:add(s,u,c,0)
        else:add(u,t,c,0)
    total=sum(cap)
    for u,v,p in edges:
        u,v=int(u),int(v)
        if color[u]==1:u,v=v,u
        add(u,v,total,-Q(p))
    objective=Q(0)
    while True:
        dist=[None]*N;dist[s]=Q(0);prev=[None]*N
        for _ in range(N-1):
            change=False
            for u in range(N):
                if dist[u] is None:continue
                for k,(v,c,cost,rev) in enumerate(graph[u]):
                    if c>0 and (dist[v] is None or dist[u]+cost<dist[v]):dist[v]=dist[u]+cost;prev[v]=(u,k);change=True
            if not change:break
        if dist[t] is None or dist[t]>=0:break
        node=t;path=[]
        while node!=s:
            u,k=prev[node];path.append((u,k));node=u
            if len(path)>N:raise RuntimeError('negative cycle in shortest path')
        amount=min(graph[u][k][1] for u,k in path);objective-=amount*dist[t]
        for u,k in path:
            v,c,cost,rev=graph[u][k];graph[u][k][1]-=amount;graph[v][rev][1]+=amount
    return objective
