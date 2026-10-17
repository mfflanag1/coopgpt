"""Exact special-case certificate for the local-compression obstruction."""
from fractions import Fraction as F


def det3(A):
    return (A[0][0]*(A[1][1]*A[2][2]-A[1][2]*A[2][1])
            -A[0][1]*(A[1][0]*A[2][2]-A[1][2]*A[2][0])
            +A[0][2]*(A[1][0]*A[2][1]-A[1][1]*A[2][0]))


def main():
    e=(F(3,5),F(0),F(4,5))
    X=tuple(tuple(F(i==j)-e[i]*e[j] for j in range(3)) for i in range(3))
    assert sum(x*x for x in e)==1
    assert det3(X)==0
    assert X[0][0]==F(16,25) and X[1][1]==1 and X[2][2]==F(9,25)
    assert X[0][2]==-F(12,25)
    assert F(16,25)>F(9,25)
    assert F(1,5)*(2-F(1,5))==F(9,25)  # g1 solves lambda(2-lambda)=eta.
    checks=0
    for n in range(2,1001):
        k=n-1
        C=tuple(tuple(X[i][j]+F(k if i==j and i<2 else 0) for j in range(3)) for i in range(3))
        assert det3(C)==F(9*k*(k+1),25)>0
        # Leading principal minors prove C positive definite.
        assert C[0][0]>0 and C[0][0]*C[1][1]>0
        # Rayleigh at e3 gives G<=9/25, below every local standalone.
        assert C[2][2]==F(9,25)<F(16,25)
        # Max-marginal ratio lower is 1+(n-1)g1/G.
        assert 1+F(k,5)/F(9,25)==1+F(5*k,9)
        # The exact limiting ratio in the arbitrary-law proof.
        assert 1+k*F(1,2)/F(k,k+1)==1+F(n,2)
        checks+=1
    # Local netting loses the two-owner global gain.
    owners=[(F(1),F(1),F(0)),(F(0),F(1),F(1))]
    globalT=min(map(sum,zip(*owners)))
    globalS=sum(min(x) for x in owners)
    local=[x[:2] for x in owners]
    localT=min(map(sum,zip(*local)))
    localS=sum(min(x) for x in local)
    assert globalT-globalS==1 and localT-localS==0
    attenuation=0
    for m in range(2,16):
        # Rational Householder gives a non-coordinate orthogonal frame.
        v=[F(j+1) for j in range(m)]
        vnorm=sum(t*t for t in v)
        H=[[F(i==j)-2*v[i]*v[j]/vnorm for j in range(m)] for i in range(m)]
        for r in range(1,m+1):
            Q=H[:r]
            assert all(sum(Q[i][j]*Q[k][j] for j in range(m))==F(i==k)
                       for i in range(r) for k in range(r))
            squared=[sum(Q[j][i]**2 for j in range(r)) for i in range(m)]
            assert all(0<=t<=1 for t in squared)
            localS=sum(1-t for t in squared)
            assert localS==m-r and (m-1)-localS==r-1
            attenuation+=1
    print(f'PASS: {checks} exact growing-owner compression certificates; global caps forced; '
          f'V-cap linear lower and exact limit; local-netting coverage failure; {attenuation} adaptive-gain identities.')


if __name__=='__main__':main()
