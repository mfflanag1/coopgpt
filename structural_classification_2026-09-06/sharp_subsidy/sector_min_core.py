"""Sparse core constraints using three shared sector-minimum variables."""
from itertools import product


def core_rows(m,P):
    if type(m)is not int or m<1:raise ValueError('size')
    if any(len(t)!=3 or any(type(j)is not int or not 0<=j<m for j in t)for t in P):raise ValueError('indices')
    if any(len({t[s]for t in P})!=len(P)for s in range(3)):raise ValueError('P overlap')
    support=set();special={(j,j,j)for j in range(m)}|{tuple(t)for t in P}
    for a,b,c in special:
        support.update(((0,a,b),(1,a,c),(2,b,c)))
    edges=sorted(support);idx={e:k for k,e in enumerate(edges)};rows=[]
    sector_pairs=[(0,1),(0,2),(1,2)]
    # Each row is (pair coefficient ids, payoff/minimum coefficient mapping),
    # interpreted as sum(weights[ids]) + sum(coeff * local_variable) <= 0.
    for s in range(3):
        for j in range(m):rows.append(([],{3*m+s:1,s*m+j:-1}))
    for e in edges:
        p,a,b=e;s,t=sector_pairs[p];u=3-s-t
        rows.append(([idx[e]],{s*m+a:-1,t*m+b:-1,3*m+u:-1}))
        if a!=b:
            for third in (a,b):
                team=[None]*3;team[s]=a;team[t]=b;team[u]=third;special.add(tuple(team))
    for a,b,c in sorted(special):
        es=[idx[e]for e in ((0,a,b),(1,a,c),(2,b,c))if e in idx]
        rows.append((es,{a:-1,m+b:-1,2*m+c:-1}))
    return edges,rows,sorted(special)
