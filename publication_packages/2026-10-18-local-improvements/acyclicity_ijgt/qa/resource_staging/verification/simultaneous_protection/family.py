from fractions import Fraction as F
from itertools import combinations

def construct(q,K,cycle=None,allowed=None):
    if not isinstance(q,int)or q<1 or K<3:raise ValueError('invalid dimensions')
    cycle=list(range(K))if cycle is None else list(cycle);ell=len(cycle)
    if ell<3 or len(set(cycle))!=ell or any(v not in range(K)for v in cycle):raise ValueError('invalid cycle')
    cycle_edges={tuple(sorted((cycle[j],cycle[(j+1)%ell])))for j in range(ell)}
    if allowed is None:allowed=cycle_edges|{tuple(sorted((cycle[0],v)))for v in range(K)if v not in cycle}
    edges=sorted(set(tuple(sorted(e))for e in allowed))
    if not cycle_edges<=set(edges)or any(len(e)!=2 or e[0]==e[1]or e[0]not in range(K)or e[1]not in range(K)for e in edges):raise ValueError('invalid allowed graph')
    m=3*q+1;L=lambda s:0 if s==0 else 3*s-1;O=lambda s:3*s-2;R=lambda s:3*s
    matrices={e:[[0]*m for _ in range(m)]for e in edges}
    def setval(u,v,i,j,value):
        e=tuple(sorted((u,v)))
        if u>v:i,j=j,i
        matrices[e][i][j]=value
    a,b,c=cycle[:3];last=cycle[-1]
    for s in range(q+1):setval(b,c,L(s),L(s),1)
    for s in range(1,q+1):
        o,l,r,pr=O(s),L(s),R(s),L(s-1)
        setval(a,b,o,o,2);setval(a,b,o,r,2)
        setval(a,last,o,o,2);setval(a,last,o,l,2)
        for i,j in ((r,r),(r,l),(pr,o)):setval(b,c,i,j,1)
        for h in range(2,ell-1):
            setval(cycle[h],cycle[h+1],o,o,2);setval(cycle[h],cycle[h+1],l,l,2)
    t=F(1,K*(q+1));tau=F(1,3*(q+1));shift=F(K-3,3)*t
    p=[[F(0)]*m for _ in range(K)];y=[[F(0)]*m for _ in range(K)]
    for s in range(q+1):
        j=L(s);p[a][j]=tau-shift;p[b][j]=1-(3*s+2)*tau-shift;p[c][j]=(3*s+1)*tau-shift;y[c][j]=1
    for s in range(1,q+1):
        j=R(s);p[a][j]=tau-shift;p[b][j]=1-2*tau-shift;p[c][j]=tau-shift;y[b][j]=1
        j=O(s);p[a][j]=4-(3*s-1)*tau-shift;p[b][j]=tau-shift;p[c][j]=(3*s-2)*tau-shift;y[a][j]=3;y[c][j]=1
    high={O(s)for s in range(1,q+1)}|{L(s)for s in range(1,q+1)}
    for v in range(K):
        if v in (a,b,c):continue
        for j in range(m):
            bonus=2*int(v in cycle and j in high);p[v][j]=bonus+t;y[v][j]=bonus
    partial=[]
    for s in range(1,q+1):
        for av,bv,cv in ((O(s),R(s),L(s)),(L(s-1),L(s-1),O(s))):
            team=[cv]*K;team[a]=av;team[b]=bv;team[c]=cv;partial.append(team)
    return {'q':q,'m':m,'K':K,'cycle':cycle,'edges':edges,'matrices':[matrices[e]for e in edges],'T':6*q+1+4*q*(ell-3),'target':c*m,'floor':str(t),'target_ideal':'1','ratio':str(t),'x_floor':[str(v)for row in p for v in row],'y_ideal':[str(v)for row in y for v in row],'matching':[[j]*K for j in range(m)],'partial_matching':partial}
