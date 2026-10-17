from fractions import Fraction as Q
from itertools import combinations
if not __debug__:
    raise RuntimeError('Run without -O; assertions are the verifier.')

def inverse(A):
    n=len(A)
    m=[[Q(x) for x in row]+[Q(int(i==j)) for j in range(n)] for i,row in enumerate(A)]
    for k in range(n):
        p=next((i for i in range(k,n) if m[i][k]),None)
        if p is None:return None
        m[k],m[p]=m[p],m[k]
        v=m[k][k];m[k]=[x/v for x in m[k]]
        for i in range(n):
            if i!=k:
                v=m[i][k]
                m[i]=[x-v*y for x,y in zip(m[i],m[k])]
    return [r[n:] for r in m]

def forest_data(n,edges):
    adj=[[] for _ in range(n)]
    for a,b in edges:adj[a].append(b);adj[b].append(a)
    comp=[None]*n;par=[None]*n
    for root in range(n):
        if comp[root] is not None:continue
        comp[root]=root;par[root]=0;stack=[(root,-1)]
        while stack:
            u,parent=stack.pop()
            for v in adj[u]:
                if v==parent:continue
                if comp[v] is not None:return None
                comp[v]=root;par[v]=1-par[u];stack.append((v,u))
    return adj,comp,par

def path(adj,a,b):
    queue=[a];prev={a:None}
    for u in queue:
        if u==b:break
        for v in adj[u]:
            if v not in prev:prev[v]=u;queue.append(v)
    out=[]
    while b is not None:out.append(b);b=prev[b]
    return out[::-1]

def exceptional(n,edges,H):
    adj,comp,par=forest_data(n,edges)
    if len({comp[v] for v in H})>1 or len({par[v] for v in H})==1:return {}
    h=next(v for v in H if sum(par[w]==par[v] for w in H)==1)
    common=set(path(adj,H[0],H[1])) & set(path(adj,H[0],H[2])) & set(path(adj,H[1],H[2]))
    assert len(common)==1
    p=path(adj,next(iter(common)),h)
    ans={p[j]:frozenset((p[j],p[j+1])) for j in range(len(p)-1)}
    ans[h]=frozenset(H)
    return ans

bases=derivatives=negative=0
for n in range(3,6):
    all_edges=list(combinations(range(n),2))
    for ecount in range(n):
        for edges in combinations(all_edges,ecount):
            if forest_data(n,edges) is None:continue
            for acount in range(n-ecount):
                for anchors in combinations(range(n),acount):
                    for H in combinations(range(n),3):
                        sets=[frozenset(e) for e in edges]+[frozenset((a,)) for a in anchors]+[frozenset(H)]
                        B=[[int(j in S) for j in range(n)] for S in sets]
                        G=[[sum(x*y for x,y in zip(r,s)) for s in B] for r in B]
                        inv=inverse(G)
                        if inv is None:continue
                        bases+=1
                        bad=exceptional(n,edges,H)
                        for r,S in enumerate(sets):
                            for i in S:
                                d=sum(Q(B[l][i])*inv[l][r] for l in range(len(B)))
                                if d<0:
                                    assert d==-1 and bad.get(i)==S,(n,edges,anchors,H,r,i,d,bad)
                                    negative+=1
                                derivatives+=1
print('Small bases PASS',bases,'bases',derivatives,'own derivatives',negative,'negative derivatives',flush=True)

arm_checks=0
for L in range(1,16,2):
    # hub0, majority endpoints2 and4, minority endpoint4+L.
    n=5+L
    edges=[(0,1),(1,2),(0,3),(3,4)]
    p=[0]+list(range(5,5+L))
    edges += list(zip(p,p[1:]))
    H=(2,4,p[-1])
    sets=[frozenset(e) for e in edges]+[frozenset(H)]
    B=[[int(j in S) for j in range(n)] for S in sets]
    assert len(B)==n
    G=[[sum(x*y for x,y in zip(r,s)) for s in B] for r in B]
    inv=inverse(G);assert inv is not None
    q=[sum(B[r][i] for r in range(n)) for i in range(n)]
    b=[sum(B[r][i]*q[i] for i in range(n)) for r in range(n)]
    for j in range(L):
        r=4+j;i=p[j]
        response=[sum(Q(B[l][v])*inv[l][r] for l in range(n)) for v in range(n)]
        assert response[i]==-1
        eps=Q(1,2)/(1+max(abs(inv[l][r]) for l in range(n)))
        lam=[1-eps*inv[l][r] for l in range(n)]
        assert all(x>0 for x in lam)
        qnew=[sum(B[l][v]*lam[l] for l in range(n)) for v in range(n)]
        assert all(x>0 for x in qnew)
        assert qnew[i]==q[i]+eps
        for rr in range(n):
            assert sum(B[rr][v]*qnew[v] for v in range(n))==b[rr]-(eps if rr==r else 0)
        arm_checks+=1
print('Growing arms PASS',arm_checks,'exact strictly feasible KKT perturbations')
