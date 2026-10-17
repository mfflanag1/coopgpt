from fractions import Fraction as Q
from itertools import combinations, product
if not __debug__:
    raise RuntimeError('Assertions must remain enabled')

def inverse(A):
    n=len(A); a=[[Q(v) for v in row]+[Q(int(i==j)) for j in range(n)] for i,row in enumerate(A)]
    for j in range(n):
        k=next((k for k in range(j,n) if a[k][j]),None)
        if k is None:return None
        a[j],a[k]=a[k],a[j]; v=a[j][j]; a[j]=[t/v for t in a[j]]
        for k in range(n):
            if k!=j:
                v=a[k][j]; a[k]=[t-v*s for t,s in zip(a[k],a[j])]
    return [r[n:] for r in a]

def solver(rows,n):
    bases=[]
    for k in range(1,min(n,len(rows))+1):
        for ix in combinations(range(len(rows)),k):
            B=[rows[j] for j in ix]
            H=inverse([[sum(x*y for x,y in zip(a,b)) for b in B] for a in B])
            if H is not None:bases.append((ix,B,H))
    def solve(b):
        if not any(b):return [Q(0)]*n,[Q(0)]*len(rows)
        for ix,B,H in bases:
            lam=[sum(h*b[j] for h,j in zip(row,ix)) for row in H]
            if min(lam)<0:continue
            q=[sum(l*a[j] for l,a in zip(lam,B)) for j in range(n)]
            if all(sum(a*x for a,x in zip(row,q))>=v for row,v in zip(rows,b)):
                dual=[Q(0)]*len(rows)
                for j,l in zip(ix,lam):dual[j]=l
                return q,dual
        raise AssertionError(('no KKT point',rows,b))
    return solve

checks=0; witnesses=0; examples=[]
for n in range(1,6):
    families=[('singletons',[(i,) for i in range(n)])]
    if n>=2:families += [('path',[(i,i+1) for i in range(n-1)]),('star',[(0,i) for i in range(1,n)])]
    if n>=3:families += [('cycle',[(i,(i+1)%n) for i in range(n)])]
    if n<=4 and n>=2:families += [('complete',list(combinations(range(n),2)))]
    for name,sets in families:
        A=[tuple(Q(int(j in s)) for j in range(n)) for s in sets]
        solve=solver(A,n); z,lam=solve([Q(1)]*len(A)); rho=sum(t*t for t in z)
        assert rho==sum(lam)
        assert all(0<=t<=min(1,rho) for t in z)
        V=[(Q(1),)+row for row in A]; vs=solver(V,n+1)
        vf,_=vs([Q(1)]*len(A)); t=rho/(1+rho)
        assert vf==[t]+[a/(1+rho) for a in z]
        assert sum(a*a for a in vf)==t
        caps=[t]
        for i in range(n):
            off=[Q(0) if row[i] else Q(1) for row in A]
            zm,_=solve(off); rho_off=sum(a*a for a in zm)
            w=[sum(l*row[j] for l,row in zip(lam,A) if row[i]) for j in range(n)]
            assert sum(a*b for a,b in zip(z,w))==z[i]
            assert sum(a*a for a in w)<=z[i]
            assert rho_off>=rho-z[i]
            cap=min(t,z[i]/(1+rho-z[i])); caps.append(cap)
            inc=[j for j,row in enumerate(A) if row[i]]
            patterns=[tuple(Q(1,2) for _ in inc),tuple(Q(0) for _ in inc)]
            for j in range(len(inc)):
                patterns += [tuple(Q(0) if k==j else Q(1) for k in range(len(inc))),tuple(Q(1,2) if k==j else Q(1) for k in range(len(inc)))]
            for vals in patterns:
                b=[Q(1)]*len(A)
                for j,v in zip(inc,vals):b[j]=v
                qb,_=solve(b); qv,lv=vs(b)
                assert qb[i]<=z[i]  # finite checks only; general theorem in rank-two note
                assert qv[0]<=t
                assert qv[i+1]<=qv[0]
                assert qv[i+1]<=cap
                assert qv[0]>=rho_off/(1+rho_off)
                assert sum(x*x for x in qv)<=qv[0]
                witnesses+=1
        assert sum(a*a for a in caps)<=1
        for b in ([Q(0)]*len(A),[Q(1,2)]*len(A)):
            qv,_=vs(b); assert qv[0]<=t
        checks+=1; examples.append((n,name,str(rho)))
# Check the aggregation algebra at a dense rational set, branch without irrational arithmetic.
scalar_checks=0
for den in range(1,51):
    for num in range(1,10*den+1):
        r=Q(num,den); t=r/(1+r)
        if r*r-r-1<=0:
            bound=t*t+r*(1+2*r)**2/(1+r)**4
            assert 1-bound==-(2*r+1)*(r*r-r-1)/(1+r)**4
        else:
            bound=t*t+1/r
            assert 1-bound==(r*r-r-1)/(r*(1+r)**2)
        assert bound<=1
        scalar_checks+=1
print({'status':'PASS','base_systems':checks,'own_relaxation_KKT_witnesses':witnesses,'rational_aggregation_checks':scalar_checks,'examples':examples})
