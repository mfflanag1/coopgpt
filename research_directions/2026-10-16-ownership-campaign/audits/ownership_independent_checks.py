#!/usr/bin/env python3
"""Fresh exact rational audit implementation; no imports of candidate/certificate code."""
from fractions import Fraction as F
from itertools import product
import json,random,hashlib
from pathlib import Path

def require(ok,msg):
    if not ok:raise ValueError(msg)

def labels(raw):
    seen={}
    return tuple(seen.setdefault(v,len(seen)) for v in raw)

def worth(profile,hw,loc,mask):
    P,hs,ls=profile;na=max(loc)+1;nb=max(hw)+1
    grid=P if mask&(1<<(na+nb)) else F()
    h=[x if mask&(1<<(na+hw[j])) else F() for j,x in enumerate(hs)]
    l=[x if mask&(1<<loc[j]) else F() for j,x in enumerate(ls)]
    local=sum(min(x,y) for x,y in zip(h,l))
    return local+min(grid,sum(h)-local)

def rule(profile,hw,loc,theta):
    P,h,l=profile;na=max(loc)+1;nb=max(hw)+1
    ell=[min(x,y) for x,y in zip(h,l)];r=[x-y for x,y in zip(h,ell)]
    L=sum(ell);Q=sum(r);H=sum(h);R=min(P,Q);G=min(P,H);T=L+R
    E=[sum(ell[j] for j,b in enumerate(hw) if b==k) for k in range(nb)]
    RR=[sum(r[j] for j,b in enumerate(hw) if b==k) for k in range(nb)]
    LL=[sum(ell[j] for j,a in enumerate(loc) if a==k) for k in range(na)]
    if L:
        x=[e*min(F(1),max(F(),(P-Q+rr)/L)) for e,rr in zip(E,RR)]
        a=[e*(T-G)/L for e in LL];c=G-max(F(),sum(x)-L/4)
    else:a=[F()]*na;x=[F()]*nb;c=G
    full=a+x+[c];baseline=[F()]*na+E+[R]
    return [theta*y+(1-theta)*z for y,z in zip(full,baseline)]

def inspect(profile,hw,loc,theta,rng,counts):
    y=rule(profile,hw,loc,theta);na=max(loc)+1;nb=max(hw)+1;n=na+nb+1;allm=(1<<n)-1
    T=worth(profile,hw,loc,allm)
    require(all(x>=0 for x in y),'nonnegative')
    require(sum(y)<=(1+theta/4)*T,'funding')
    for mask in range(1<<n):
        require(sum(y[k] for k in range(n) if mask&(1<<k))>=worth(profile,hw,loc,mask),'crossed-block coalition')
        counts['coalitions']+=1
    for a in range(na):
        require(y[a]>=theta*(T-worth(profile,hw,loc,allm^(1<<a))),'actual local marginal floor')
        counts['floors']+=1
    P,h,l=profile
    for owner in range(n):
        hp=h.copy();lp=l.copy();pp=P
        if owner<na:
            for j,a in enumerate(loc):
                if a==owner:lp[j]*=rng.choice([F(),F(1,3),F(2,3),F(1)])
        elif owner<na+nb:
            for j,b in enumerate(hw):
                if b==owner-na:hp[j]*=rng.choice([F(),F(1,3),F(2,3),F(1)])
        else:pp*=rng.choice([F(),F(1,3),F(2,3),F(1)])
        low=rule((pp,hp,lp),hw,loc,theta)
        require(low[owner]<=y[owner],'whole actual owner underreport')
        counts['bundle_underreports']+=1
    counts['profiles']+=1

def pair_reduction(rng,counts):
    for trial in range(180):
        n=rng.randrange(1,5);h=[F(rng.randrange(8),2) for _ in range(n)];l=[F(rng.randrange(8),2) for _ in range(n)];P=F(rng.randrange(8),2)
        ell=[min(x,y) for x,y in zip(h,l)];r=[x-y for x,y in zip(h,ell)];x=[F(rng.randrange(8),2) for _ in range(n)]
        a=[max(F(),ell[j]-x[j])+F(rng.randrange(5),3) for j in range(n)];c=F(rng.randrange(15),2)
        y=a+x+[c];e=[a[j]+x[j]-ell[j] for j in range(n)];part=tuple(range(n));profile=(P,h,l)
        actual=True
        for mask in range(1<<(2*n+1)):
            actual &=sum(y[k] for k in range(2*n+1) if mask&(1<<k))>=worth(profile,part,part,mask)
            counts['reduction_full_coalitions']+=1
        reduced=all(v>=0 for v in e)
        for assignment in product(range(3),repeat=n):
            J=[j for j,z in enumerate(assignment) if z==1];K=[j for j,z in enumerate(assignment) if z==2]
            reduced &= c+sum(x[j] for j in J)+sum(e[j] for j in K)>=min(P,sum(h[j] for j in J)+sum(r[j] for j in K))
            counts['reduction_disjoint_pairs']+=1
        require(actual==reduced,'coalition reduction equivalence')
    counts['reduction_profiles']=180

def dual(theta):
    # Variables B and (a,b,c,x,y) at O,U,V. All rows in <= convention.
    co={'B':F()};rhs=F()
    def add(weight,terms,bound):
        nonlocal rhs
        for name,value in terms.items():co[name]=co.get(name,F())+weight*value
        rhs+=weight*bound
    add(F(1,5),dict(Oa=1,Ob=1,Oc=1,Ox=1,Oy=1,B=-2),0)
    for left in ['Oa Ob Ox Oy','Oa Oc Ox Oy','Ob Oc Ox Oy']:
        add(F(1,10),{s:-1 for s in left.split()},-2)
    add(F(1,10),dict(Ox=1,Ux=-1),0);add(F(1,10),dict(Oy=1,Vy=-1),0)
    for tag,other in [('U','y'),('V','x')]:
        row={tag+s:1 for s in 'abcxy'};row['B']=-3;add(F(1,10),row,0)
        add(F(1,10),{tag+'c':-1,tag+other:-1},-1)
        for a in 'ab':add(F(1,10),{tag+a:-1},-theta)
    require(co['B']==-1 and all(v==0 for k,v in co.items() if k!='B'),'14-row exact coefficient cancellation')
    require(rhs==-(4+2*theta)/5,'14-row exact RHS')
    return {'theta':str(theta),'factor_coefficient':str(co['B']),'rhs':str(rhs),'payment_coefficients_zero':True}

def main():
    rng=random.Random(161101);counts=dict(profiles=0,coalitions=0,floors=0,bundle_underreports=0,reduction_full_coalitions=0,reduction_disjoint_pairs=0)
    for hw in [(0,0),(0,1)]:
        for loc in [(0,0),(0,1)]:
            for vals in product(map(F,[0,1,2]),repeat=5):
                for theta in [F(),F(1,2),F(1)]:inspect((vals[0],list(vals[1:3]),list(vals[3:])),hw,loc,theta,rng,counts)
    for trial in range(500):
        m=rng.randrange(3,8);hw=labels([rng.randrange(3) for _ in range(m)]);loc=labels([rng.randrange(3) for _ in range(m)])
        h=[F(rng.randrange(12),rng.randrange(1,5)) for _ in range(m)];l=[F(rng.randrange(12),rng.randrange(1,5)) for _ in range(m)]
        P=F(rng.randrange(20),rng.randrange(1,5));theta=rng.choice([F(),F(1,3),F(1,2),F(1)])
        inspect((P,h,l),hw,loc,theta,rng,counts)
    pair_reduction(rng,counts)
    report=dict(status='EXACT RATIONAL PASS',counts=counts,dual=[dual(t) for t in [F(),F(1,3),F(1)]],scope='Independent finite rational corroboration and exact14-row identity, not universal proof',script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
