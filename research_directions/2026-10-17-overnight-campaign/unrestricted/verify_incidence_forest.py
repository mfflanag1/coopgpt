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

def forest(rows,n):
    p=list(range(n+len(rows)))
    def find(i):
        while p[i]!=i:
            p[i]=p[p[i]];i=p[i]
        return i
    for r,S in enumerate(rows):
        for i in S:
            a,b=find(i),find(n+r)
            if a==b:return False
            p[a]=b
    return True

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
            assert d[i]>=0
            derivatives+=1;zeros+=d[i]==0

bases=derivatives=zeros=systems=0
for n in range(1,6):
    available=[frozenset(i for i in range(n) if mask>>i&1) for mask in range(1,1<<n)]
    for m in range(1,min(n,4)+1):
        for rows in combinations(available,m):
            if forest(rows,n):
                systems+=1;check(rows,n)

# Both sides can have degree greater than two in the same connected tree.
growing=0
for k in range(3,31):
    rows=[frozenset([0]+list(range(1+j*k,1+(j+1)*k))) for j in range(k)]
    assert forest(rows,1+k*k)
    check(rows,1+k*k);growing+=1

print({'status':'PASS','forest_systems':systems,'independent_bases':bases,
       'own_derivatives':derivatives,'pinned_zero_derivatives':zeros,
       'growing_high_degree_examples':growing})
