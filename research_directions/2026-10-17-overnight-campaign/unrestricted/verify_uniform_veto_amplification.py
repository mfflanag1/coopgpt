from fractions import Fraction as Q
if not __debug__:raise RuntimeError('Assertions must remain enabled')
n=5
A=[tuple(Q(int(j in ((r+t)%n for t in range(3)))) for j in range(n)) for r in range(n)]
z=[Q(1,3)]*n; lam=[Q(1,9)]*n; rho=sum(x*x for x in z)
b=[Q(11,12),Q(1),Q(1),Q(1),Q(1)]
q=[Q(5,18),Q(13,36),Q(5,18),Q(13,36),Q(13,36)]
l=[Q(t,108) for t in (1,19,10,10,19)]
assert [sum(x*y for x,y in zip(row,q)) for row in A]==b
assert [sum(l[r]*A[r][j] for r in range(n)) for j in range(n)]==q
L=sum(l); assert sum(x*x for x in q)<=L<=rho
p=q[1]; E=n*p*p
checks=0
for K in range(1,41):
    H=(K-1)*rho+L; alpha=1/(1+H); u=1-alpha
    for block in range(K):
        xx=[u]+[alpha*x for k in range(K) for x in (q if k==block else z)]
        multipliers=[alpha*x for k in range(K) for x in (l if k==block else lam)]
        assert xx[0]==sum(multipliers)
        norm=sum(x*x for x in xx); dual=Q(0)
        for k in range(K):
            for r,row in enumerate(A):
                rhs=u+alpha*b[r] if k==block else Q(1)
                # Only row0 changes, and it contains focal owner1.
                if rhs!=1:assert k==block and row[1]
                lhs=u+sum(row[j]*xx[1+k*n+j] for j in range(n))
                assert lhs>=rhs
                assert multipliers[k*n+r]*(lhs-rhs)==0
                dual+=multipliers[k*n+r]*rhs
            for j in range(n):
                assert xx[1+k*n+j]==sum(multipliers[k*n+r]*A[r][j] for r in range(n))
        assert norm==dual
        checks+=1
    exact_lower=(K*rho/(1+K*rho))**2+K*E/(1+(K-1)*rho+L)**2
    common_lower=(K*K*rho*rho+K*E)/(1+K*rho)**2
    assert exact_lower>=common_lower
    assert common_lower-1==(K*(E-2*rho)-1)/(1+K*rho)**2
print({'status':'PASS','explicit_copied_KKT_witnesses':checks,'maximum_copies':40,'base_rho':str(rho),'base_witness_squared_sum':str(E),'base_violates_factor_two':E>2*rho})
