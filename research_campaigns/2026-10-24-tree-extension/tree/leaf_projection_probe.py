import math,itertools,json,random
from pathlib import Path

def forms(n,edges,order,c,alpha=1/math.sqrt(2),beta=.5):
    zero=(0.,)*n
    def plus(x,y):return tuple(a+b for a,b in zip(x,y))
    def minus(x,y):return tuple(a-b for a,b in zip(x,y))
    def value(x):return sum(a*b for a,b in zip(x,c))
    def pick(fs,kind):return kind(fs,key=value)
    def subs(S):
        for mask in range(1<<len(S)):yield tuple(S[k] for k in range(len(S)) if mask>>k&1)
    adj=[set() for _ in range(n)]
    for i,j in edges:adj[i].add(j);adj[j].add(i)
    col={0:0};queue=[0]
    for v in queue:
        for u in adj[v]:
            if u not in col:col[u]=1-col[v];queue.append(u)
    W=[None]*n
    for parity in [0,1]:
        L=tuple(i for i in order if col[i]==parity);Ls=frozenset(L);rank={}
        for S in subs(L):
            candidates=[]
            for T in subs(S):
                N=set().union(*(adj[t] for t in T)) if T else set()
                candidates.append(tuple(float(i in S and i not in T)+alpha*(i in N) for i in range(n)))
            rank[frozenset(S)]=pick(candidates,min)
        prefix=[]
        for v in L:
            lows=[];highs=[]
            for S in subs(prefix):
                old=zero
                for i in S:old=plus(old,W[i])
                Sv=frozenset((*S,v))
                lows.append(minus(minus(rank[Ls],rank[Ls-Sv]),old))
                highs.append(minus(rank[Sv],old))
            low=pick(lows,max);high=pick(highs,min)
            target=tuple(beta*float(i==v) for i in range(n))
            W[v]=pick([pick([target,low],max),high],min)
            prefix.append(v)
    return W

def certificate(n,edges,W,c):
    p=[sum(x*y for x,y in zip(row,c))/c[j] for j,row in enumerate(W)]
    D=[[W[j][v]/c[j]-(p[j]/c[j] if j==v else 0) for v in range(n)] for j in range(n)]
    singles=[p[v]+sum(c[j]*min(D[j][v],0) for j in range(n)) for v in range(n)]
    ec=[p[u]+p[v]+sum(c[j]*min(D[j][u]+D[j][v],0) for j in range(n)) for u,v in edges]
    return p,singles,ec,D

if __name__=='__main__':
    rng=random.Random(814);records=[]
    for n in [5,6,7,8]:
        edges=[(i,i+1) for i in range(n-1)]
        order=[]
        for k in range((n+1)//2):
            order.append(k)
            if n-1-k!=k:order.append(n-1-k)
        for run in range(5000):
            c=[rng.choice([.125,.25,.5,1,2,4,8]) for _ in range(n)]
            W=forms(n,edges,order,c);p,s,e,D=certificate(n,edges,W,c)
            if min(s)<-1e-8 or min(e)<1-1e-8:
                j=min(range(len(e)),key=e.__getitem__);u,v=edges[j]
                theta=[int(D[k][u]+D[k][v]<0) for k in range(n)]
                records.append(dict(n=n,order=order,c=c,p=p,coordinate_min=min(s),edge_min=min(e),edge=edges[j],theta=theta,W=W,run=run));break
        else:records.append(dict(n=n,status='no counterexample in finite diagnostic'))
    out=Path(__file__).with_suffix('.json');out.write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(records,indent=2))
