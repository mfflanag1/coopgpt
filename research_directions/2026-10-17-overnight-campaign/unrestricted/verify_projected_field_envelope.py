"""Exact projected-field certificates and growing scalar-slack obstruction."""
from fractions import Fraction as F
from itertools import combinations


def dot(a,b):return sum((x*y for x,y in zip(a,b)),F(0))


def solve(a,b):
    n=len(b);mat=[list(map(F,row))+[F(v)] for row,v in zip(a,b)]
    for j in range(n):
        k=next((k for k in range(j,n) if mat[k][j]),None)
        if k is None:return None
        mat[j],mat[k]=mat[k],mat[j]
        c=mat[j][j];mat[j]=[v/c for v in mat[j]]
        for k in range(n):
            if k!=j:
                c=mat[k][j];mat[k]=[x-c*y for x,y in zip(mat[k],mat[j])]
    return [row[-1] for row in mat]


def projection(rows,rhs,n):
    for size in range(min(n,len(rows))+1):
        for ids in combinations(range(len(rows)),size):
            rr=[rows[t] for t in ids]
            lam=solve([[dot(x,y) for y in rr] for x in rr],[rhs[t] for t in ids])
            if lam is None or any(v<0 for v in lam):continue
            q=[sum((v*row[j] for v,row in zip(lam,rr)),F(0)) for j in range(n)]
            if all(dot(row,q)>=b for row,b in zip(rows,rhs)):return q
    raise AssertionError('No exact projection')


def witness(rows,b,low,q,lam,i):
    n=len(q);rest=[j for j in range(n) if j!=i];d=q[i]
    assert d>0 and all(v>=0 for v in lam)
    assert all(q[j]==sum(v*row[j] for row,v in zip(rows,lam)) for j in range(n))
    assert all(dot(row,q)>=v and l*(dot(row,q)-v)==0 for row,v,l in zip(rows,low,lam))
    incident=[t for t,row in enumerate(rows) if row[i]]
    off=[t for t,row in enumerate(rows) if not row[i]]
    assert all(low[t]==b[t] for t in off) and all(0<=low[t]<=b[t] for t in incident)
    assert sum(lam[t] for t in incident)==d
    p=[sum(lam[t]*rows[t][j] for t in incident)/d for j in rest]
    u=[q[j] for j in rest]
    rr=[[rows[t][j] for j in rest] for t in off];bb=[b[t] for t in off]
    r=projection(rr,bb,len(rest))
    # Exact shifted KKT representation: u-dp is the off-row normal.
    assert all(u[a]-d*p[a]==sum(lam[t]*rows[t][j] for t in off) for a,j in enumerate(rest))
    B=sum(lam[t]*b[t] for t in incident)/d
    assert d+dot(p,u)<=B
    shift=[x-y for x,y in zip(u,r)]
    assert d*dot(p,shift)>=dot(shift,shift)
    slack=sum(lam[t]*(b[t]-sum(rows[t][j]*r[a] for a,j in enumerate(rest))) for t in incident)/d
    assert d*d+dot(shift,shift)<=d*slack


def main():
    rows=[(0,1,0,1),(1,0,1,1),(1,1,0,0),(1,1,0,1)]
    witness(rows,list(map(F,[3,3,2,5])),[F(3),F(3),F(2),F(15,4)],
            [F(3,4),F(5,4),F(1,2),F(7,4)],[F(1),F(1,2),F(0),F(1,4)],3)
    rows=[tuple(F((j-r)%5<3) for j in range(5)) for r in range(5)]
    witness(rows,[F(3)]*5,[F(11,4)]+[F(3)]*4,
            [F(5,6),F(13,12),F(5,6),F(13,12),F(13,12)],
            [F(1,36),F(19,36),F(5,18),F(5,18),F(19,36)],1)
    checks=0
    for m in range(1,51):
        for k in range(1,51):
            u=F(m,m+k);leaf=F(1,m+k)
            assert u+k*leaf==1 and m*leaf==u
            assert u*u+m*k*leaf*leaf==F(m,m+k)
            r=F(m-1,m+k-1);slack=1-r
            assert slack==F(k,m+k-1)
            if m==k:
                assert u*u+m*k*leaf*leaf==F(1,2)
                assert 1+m*k*slack==1+F(k**3,2*k-1)
                assert 1+m*k*slack*slack==1+F(k**4,(2*k-1)**2)
            checks+=1
    print(f'PASS: two exact nonmonotone projected-field/curvature witnesses; {checks} growing-group KKT and scalar-slack formulas.')


if __name__=='__main__':main()
