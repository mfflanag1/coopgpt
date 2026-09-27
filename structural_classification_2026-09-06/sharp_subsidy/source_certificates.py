"""Rational witnesses; the all-q justification is in SIMULTANEOUS_PROTECTION.md."""
from fractions import Fraction as F
from itertools import product
from math import lcm


def require(ok,msg):
    if not ok: raise ValueError(msg)


def labels(q):
    return [0]+list(range(1,3*q+1))


def payoff(q,alpha=F(0),l0=F(0),d=None,r=None,e=None,f=None):
    d=list(d or [F(0)]*q);r=list(r or [F(0)]*q)
    e=list(e or [F(0)]*q);f=list(f or [F(0)]*q)
    require(q>=1 and all(len(v)==q for v in (d,r,e,f)),'parameter dimensions')
    pars=[alpha,l0]+d+r+e+f
    require(all(v>=0 for v in pars),'negative parameter')
    require((q+1)*alpha+l0+sum(d+r+e+f)<=1,'simplex budget')
    m=3*q+1;a=[alpha]*m;b=[F(0)]*m;c=[F(0)]*m
    b[0]=1-alpha-l0;c[0]=l0;last=l0
    for s in range(1,q+1):
        O,L,R=3*s-2,3*s-1,3*s
        oo=last+e[s-1];ll=last+alpha+d[s-1]+r[s-1]+e[s-1]+f[s-1]
        a[O]=4-d[s-1]-oo;b[O]=d[s-1];c[O]=oo
        b[L]=1-alpha-ll;c[L]=ll;b[R]=1-alpha-r[s-1];c[R]=r[s-1]
        last=ll
    return a+b+c


def vertices(q):
    out=[payoff(q),payoff(q,alpha=F(1,q+1)),payoff(q,l0=F(1))]
    for key in ('d','r','e','f'):
        for s in range(q):
            v=[F(0)]*q;v[s]=F(1);out.append(payoff(q,**{key:v}))
    return out


def ideals(q):
    m=3*q+1
    return [F(4)if j%3==1 else F(1,q+1)for j in range(m)]+[F(1)]*(2*m)


def optimal(q):
    t=F(1,2*q+3)
    return payoff(q,alpha=t/(q+1),l0=t,d=[t]*q,r=[t]*q)


def independent_triangle(q):
    m=3*q+1;A=[[0]*m for _ in range(m)];B=[[0]*m for _ in range(m)];C=[[0]*m for _ in range(m)]
    for s in range(q+1): C[0 if s==0 else 3*s-1][0 if s==0 else 3*s-1]=1
    partial=[]
    for s in range(1,q+1):
        O,L,R,P=3*s-2,3*s-1,3*s,(0 if s==1 else 3*s-4)
        A[O][O]=A[O][R]=B[O][O]=B[O][L]=2
        C[R][R]=C[R][L]=C[P][O]=1
        partial += [[O,R,L],[P,P,O]]
    return {'q':q,'K':3,'m':m,'T':6*q+1,'edges':[(0,1),(0,2),(1,2)],'matrices':[A,B,C],'partial_matching':partial}


def check_cover(market,p):
    K,m=market['K'],market['m'];require(len(p)==K*m,'cover dimension')
    require(all(v>=0 for v in p),'negative payoff');require(sum(p)==market['T'],'efficiency')
    den=lcm(*(F(v).denominator for v in p));ints=[int(v*den)for v in p]
    count=0
    for t in product(range(m),repeat=K):
        val=sum(A[t[a]][t[b]]for (a,b),A in zip(market['edges'],market['matrices']))
        require(sum(ints[s*m+t[s]]for s in range(K))>=den*val,'uncovered full team')
        count+=1
    return count


def unmatched(market):
    K,m=market['K'],market['m'];used=set();worth=0
    for t in market['partial_matching']:
        require(len(t)==K and all(0<=j<m for j in t),'matching dimension')
        players={s*m+t[s]for s in range(K)}
        require(not used&players,'overlapping partial matching');used|=players
        worth+=sum(A[t[a]][t[b]]for (a,b),A in zip(market['edges'],market['matrices']))
    return sorted(set(range(K*m))-used),market['T']-worth


def verify_triangle(q,H=None,x=None,market=None):
    market=market or independent_triangle(q);vs=vertices(q);H=H or ideals(q);x=x or optimal(q)
    diagonal=sum(sum(A[j][j] for A in market['matrices']) for j in range(market['m']))
    require(diagonal==market['T'],'integral diagonal lower certificate')
    count=sum(check_cover(market,v)for v in vs)+check_cover(market,x)
    require([max(v[i]for v in vs)for i in range(3*market['m'])]==H,'wrong ideal maxima')
    U,delta=unmatched(market);require(delta==1,'wrong residual budget')
    upper=F(delta)/sum(H[i]for i in U)
    lower=min(v/h for v,h in zip(x,H)if h)
    require(lower==upper==F(1,2*q+3),'primal-dual mismatch')
    return {'q':q,'K':3,'m':market['m'],'T':market['T'],'rho':str(upper),'H':list(map(str,H)),'x':list(map(str,x)),'U':U,'sum_ideals_U':str(sum(H[i]for i in U)),'vertices':len(vs),'cover_checks':count,'status':'PASS'}
