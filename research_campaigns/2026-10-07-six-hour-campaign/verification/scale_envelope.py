"""Exact finite checks of the parameter identities in the scale obstruction."""
from fractions import Fraction as Q
import json


def run():
    counts=0;rows=[]
    for K in range(1,41):
        M=64*K**4;N=256*K**6;b=[Q(3,4)+Q(j*j,4*K*K) for j in range(1,K+1)]
        n=[M*(K-j) for j in range(1,K+1)];eta=Q(1,16*K*K)
        assert b[-1]==1 and n[-1]==0
        assert all(b[j]+n[j]>1 for j in range(K-1))
        for i in range(1,K+1):
            r=Q(i,2*K*K*M);g=[bj+nj*r for bj,nj in zip(b,n)]
            assert 0<r<=1 and all(bj/N<=r for bj in b)
            assert Q(1,N)==Q(1,4*K*K*M)
            assert all(bj/N<=Q(1,4*K*K*M) for bj in b)
            assert g[i-1]==1-Q((K-i)**2,4*K*K)>=Q(3,4)
            for j in range(1,K+1):
                assert g[j-1]-g[i-1]==Q((j-i)**2,4*K*K)
                variance=(b[j-1]**2/N+n[j-1]*r*r)/12
                assert variance<=Q(1,12*N)+Q(1,48*K*M)
                if i<K:
                    original_heavy=Q(K+j,4*K*K*M) if j<K else Q(0)
                    balanced=b[j-1]+n[j-1]*min(r,original_heavy)
                    assert balanced==min(Q(1),g[j-1])
                    if j!=i:assert balanced-g[i-1]>=Q(1,4*K*K)
                counts+=1
        err=K*(Q(1,12*N)+Q(1,48*K*M))/eta**2
        assert err==Q(1,12*K)+Q(1,12)<=Q(1,6)
        rows.append(dict(K=K,owners=K*N+M*K*(K-1)//2,score_failure_bound=str(err),
                         envelope_lower_bound=str(Q(5*K,8))))
    return dict(status='PASS',exact_parameter_cases=40,score_comparisons=counts,rows=rows,
                scope='Checks parameter algebra and concentration inequalities; analytic all-K proof is separate.')


if __name__=='__main__':print(json.dumps(run(),indent=2))
