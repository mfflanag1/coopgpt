from fractions import Fraction as Q
from common_cap_arity_mechanism import Radical

def parameter(t,k,M):
    target=k**(2*k)*M**(k-1);scale=t**k*(k+1)**(k+1)
    lo=hi=1
    while scale*hi**(2*k)<target:hi*=2
    while lo<hi:
        m=(lo+hi)//2
        if scale*m**(2*k)>=target:hi=m
        else:lo=m+1
    return Q(lo)

def production(c,a,k):
    c=list(map(Q,c));a=list(map(Q,a));t=len(a)
    return min(min(c[v]/a[v] for v in range(t)),sum(min(c[j:j+k]) for j in range(t,len(c),k)))

def coalition_payment(c,s,a,k,C=None):
    c=list(map(Q,c));s=list(map(Q,s));a=list(map(Q,a));t=len(a)
    if not t or k<1 or (len(c)-t)%k or len(c)==t or len(s)!=len(c):raise ValueError('dimension')
    if any(x<=0 for x in a) or any(y<0 or x<y for x,y in zip(c,s)):raise ValueError('coefficients/holdings')
    M=(len(c)-t)//k;C=parameter(t,k,M) if C is None else Q(C)
    if C<1:raise ValueError('C>=1')
    if any(c[v]==0 for v in range(t)):return Radical(k=k)
    H=1/sum(a[v]/c[v] for v in range(t))
    gs=[min(H/C,*c[j:j+k]) for j in range(t,len(c),k)];G=sum(gs)
    if not G:return Radical(k=k)
    h=min(Q(1),C*G/H);zp=H*sum(s[v]/c[v] for v in range(t));z=Q(0)
    for j,g in enumerate(gs):
        for v in range(t+j*k,t+(j+1)*k):
            if c[v]:z+=g*s[v]/c[v]
    rad=Q(k**k)*H/((k+1)**(k+1)*C*G)
    if rad>=1:return Radical(h*zp+z,k=k)
    return Radical(h*zp,z,rad,k)
