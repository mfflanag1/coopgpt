from fractions import Fraction as Q
from math import comb
if not __debug__:
    raise RuntimeError('Assertions required: run without Python -O')

def C(n,k): return comb(n,k) if 0<=k<=n else 0
checks=0
for n in range(2,9):
    M=n*(n+1)+1
    for k in range(1,n):
        target=(1<<k)-1
        forms=[]
        for U in range(1,1<<n):
            u=U.bit_count()
            forms.append((U,[Q(u+1,2) if U>>j&1 else Q(M) for j in range(n)],int(U==target)))
        for T in range(1,1<<n):
            old=[sum(a[j] for j in range(n) if T>>j&1) for U,a,z in forms]
            q=Q(T.bit_count()*(T.bit_count()+1),2)
            assert min(old)==q
            assert [U for (U,a,z),v in zip(forms,old) if v==q]==[T]
            assert min(v-q for (U,a,z),v in zip(forms,old) if U!=T)>=Q(1,2)
            new=[v+Q(z,4)*int(T&1!=0) for (U,a,z),v in zip(forms,old)]
            assert min(new)-q==(Q(1,4) if T==target else 0)
            checks+=1
for n in range(2,201):
    for k in range(1,n+1):
        ca=C(n-1,k-1)
        assert Q(C(n-2,k-2),ca)==Q(k-1,n-1)
        if k<n:
            cb=C(n-1,k)
            assert Q(n-k,cb)==Q(k,ca)
            assert Q((n-k)*ca,cb)==k
        checks+=1
    # Arithmetic constant only; full coefficient elimination is analytic
    # in LINEAR_TCWM_OWNER_OBSTRUCTION.txt, not checked by this line.
    assert Q(n-1,2)+Q(1,n)==Q(n*n-n+2,2*n)
print(f'PASS {checks} exact gadget and coefficient checks; all-n proof in text')
