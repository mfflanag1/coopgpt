"""Independent reconstruction of paper4's three realizing families.
Uses only exact LPs (z3) -- no vertex enumeration."""
from fractions import Fraction as F
import itertools, audit, z3
from lmax import lmax
import famcheck

def envelope(rows):
    n=len(rows[0]); full=(1<<n)-1
    v=[F(0)]*(1<<n)
    for S in range(1,full): v[S]=min(sum(g[i] for i in range(n) if S>>i&1) for g in rows)
    v[full]=F(sum(rows[0]))
    return v

def decomposable(n,v):
    full=(1<<n)-1
    for A in range(1,full):
        B=full^A
        if all(v[S]==v[S&A]+v[S&B] for S in range(1,full+1)): return True
    return False

def family1(m):
    n=m+1; r=n-1
    def vec(d): 
        x=[F(0)]*n
        for k,val in d.items(): x[k]+=F(val)
        return x
    g1=vec({3:m-1, r:m-1})
    g2=vec({2:m-1, 3:m-1})
    d3={0:1,1:1,2:1,r:m-1}
    if m>=5: d3[4]=m-4
    g3=vec(d3)
    g4=vec({**{i:1 for i in range(m)}, r:m-2})
    return [g1,g2,g3,g4], m, [F(1)]*m+[F(m-2)]

def family2(m,h):
    r=h-2; D=F((h-2)*(h-3)); n=m+h
    p1,p2=0,1; Q=list(range(2,m)); a,b=m,m+1; K=list(range(m+2,m+h))
    def z0(): return [F(0)]*n
    u=z0(); u[p2]+=D
    for j in Q: u[j]+=D
    u[a]+=3*D; u[b]+=3*D
    for k in K: u[k]+=F((2*r-1)*(r-1))
    zz=z0(); zz[p1]+=4*D
    for j in Q: zz[j]+=D
    for k in K: zz[k]+=F(2*(r*r-1))
    rows=[u,zz]
    for kk in K:
        w=z0(); w[p1]+=D
        for j in Q: w[j]+=D
        w[a]+=3*D; w[b]+=3*D
        for k in K:
            if k!=kk: w[k]+=F(r*(2*r-1))
        rows.append(w)
    phi=[D]*m+[2*D]*h
    rows.append(list(phi))
    for j in Q:
        q=list(phi); q[p1]+=D; q[j]-=D; rows.append(q)
    return rows, m, [F(x) for x in phi]

def family3(m,h):
    n=m+h; p1,p2,p3=0,1,2; Q=list(range(3,m)); H=list(range(m,m+h))
    r1,rh=H[0],H[-1]
    def z0(): return [F(0)]*n
    A=z0(); A[p1]+=2; A[p3]+=3
    for j in Q: A[j]+=1
    A[r1]+=5
    for x in H:
        if x not in (r1,rh): A[x]+=3
    B=z0(); B[p2]+=2; B[p3]+=1
    for j in Q: B[j]+=1
    B[r1]+=4
    for x in H:
        if x!=r1: B[x]+=3
    C=z0()
    for j in Q: C[j]+=1
    C[rh]+=F(3*h+4)
    phi=z0(); phi[p1]+=1; phi[p2]+=1; phi[p3]+=2
    for j in Q: phi[j]+=1
    for x in H: phi[x]+=3
    rows=[A,B,C,list(phi)]
    for j in Q:
        q=list(phi); q[p1]+=1; q[j]-=1; rows.append(q)
    return rows, m, [F(x) for x in phi]

def check(name,rows,m,phi_claim,hclaimed=None):
    n=len(rows[0]); full=(1<<n)-1
    tot=set(sum(g) for g in rows)
    v=envelope(rows)
    sing=[str(v[1<<i]) for i in range(n)]
    ex=famcheck.exact_lp(n,v)
    mn=audit.lmin(n,v)
    H=sum(1<<i for i in range(m,n)); h=n-m
    phiH=sum(mn[i] for i in range(m,n))
    bl=audit.strata(mn)
    ok_bound = all(mn[i]<mn[j] for i in range(m) for j in range(m,n))
    print(f"{name:22s} n={n} m={m} h={h} totals={'OK' if len(tot)==1 else 'MISMATCH'+str(tot)} "
          f"sing0={all(s=='0' for s in sing)} exact={ex}")
    print(f"    Lmin={[str(q) for q in mn]}  matches_claim={mn==phi_claim}")
    print(f"    strata={[len(b) for b in bl]}  L|H strict boundary={ok_bound}  "
          f"phi(H)={phiH} v(H)={v[H]} slack={phiH-v[H]}  decomposable={decomposable(n,v)}")

print("=== family1 (unique richest) ===")
for m in (4,5,6):
    rows,mm,pc=family1(m); check(f"family1 m={m},h=1",rows,mm,pc)
print("=== family2 (two-poorer), needs m>=2,h>=4 ===")
for (m,h) in ((2,4),(2,5),(3,4)):
    rows,mm,pc=family2(m,h); check(f"family2 m={m},h={h}",rows,mm,pc)
print("=== family3 (three-poorer), needs m>=3,h>=2 ===")
for (m,h) in ((3,2),(3,3),(4,2)):
    rows,mm,pc=family3(m,h); check(f"family3 m={m},h={h}",rows,mm,pc)
