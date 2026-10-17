#!/usr/bin/env python3
"""Exact bounded diagnostic, NOT the continuous proof. Independent integer DP."""
from fractions import Fraction as Q
from itertools import product
import json, random, pathlib, hashlib
ROOT=pathlib.Path(__file__).resolve().parent

def optimal(h,l,p,a,b):
    # Direct DP over feasible per-pod local/grid outputs, integral unit matrix.
    dp={0:Q(0)}
    for hi,li,ai,bi in zip(h,l,a,b):
        nd={}
        for used,val in dp.items():
            for g in range(min(hi,p-used)+1):
                for q in range(min(li,hi-g)+1):
                    z=val+ai*q+bi*g
                    nd[used+g]=max(nd.get(used+g,Q(-1)),z)
        dp=nd
    return max(dp.values(),default=Q(0))

def base(h,l,p,theta):
    ell=[min(x,y) for x,y in zip(h,l)];r=[x-y for x,y in zip(h,ell)]
    L=sum(ell);H=sum(h);Qsum=sum(r);G=min(p,H);R=min(p,Qsum);M=L+R-G
    baseline=[Q(0),Q(R)]+list(map(Q,ell))
    if not L: end=[Q(0),Q(G)]+[Q(0)]*len(h)
    else:
        x=[Q(e)*min(Q(1),max(Q(0),Q(p-Qsum+ri,L))) for e,ri in zip(ell,r)]
        X=sum(x);end=[Q(M),Q(G)-max(Q(0),X-Q(L,4))]+x
    return [(1-theta)*u+theta*v for u,v in zip(baseline,end)]

def comp(h,l,p,a,b,theta):
    n=len(h);y=[Q(0)]*(n+2);F=Q(0)
    for i in range(n):
        val=max(Q(0),a[i]-b[i])*min(h[i],l[i]);F+=val
        y[0]+=theta*val;y[i+2]+=(1-theta)*val
    breaks=sorted(set([Q(0)]+b+[max(Q(0),bi-ai) for ai,bi in zip(a,b)]))
    for lo,hi in zip(breaks,breaks[1:]):
        hh=[h[i] if b[i]>=hi else 0 for i in range(n)]
        ll=[l[i] if b[i]>=hi and b[i]-a[i]<hi else 0 for i in range(n)]
        ell=[min(x,z) for x,z in zip(hh,ll)]
        T=sum(ell)+min(p,sum(hh)-sum(ell));F+=(hi-lo)*T
        yy=base(hh,ll,p,theta)
        y=[u+(hi-lo)*v for u,v in zip(y,yy)]
    return F,y

def run():
    rng=random.Random(172026);profiles=[]
    # One-pod all-small cases, then deterministic heterogeneous multi-pod cases.
    for h,l,p,a,b in product(range(3),repeat=5):
        profiles.append(([h],[l],p,[Q(a)],[Q(b)]))
    for n in [2,3,4]:
        for _ in range(240):
            profiles.append(([rng.randrange(4) for _ in range(n)],
                             [rng.randrange(4) for _ in range(n)],rng.randrange(6),
                             [Q(rng.randrange(7),rng.choice([1,2,3])) for _ in range(n)],
                             [Q(rng.randrange(7),rng.choice([1,2,3])) for _ in range(n)]))
    counts={'profiles':0,'coalition_checks':0,'own_deviation_checks':0,'theta_cases':0}
    for h,l,p,a,b in profiles:
        n=len(h);F=optimal(h,l,p,a,b)
        for theta in [Q(0),Q(1,3),Q(1)]:
            fc,y=comp(h,l,p,a,b,theta)
            if fc!=F: raise AssertionError(('decomposition',h,l,p,a,b,fc,F))
            if any(v<0 for v in y) or sum(y)>(1+theta/4)*F: raise AssertionError(('funding',h,l,p,a,b,theta,y,F))
            G=optimal(h,[0]*n,p,a,b)
            if y[0]!=theta*(F-G):raise AssertionError(('floor',h,l,p,a,b,theta,y,F,G))
            for mask in range(1<<(n+2)):
                hh=[v if mask&(1<<(i+2)) else 0 for i,v in enumerate(h)]
                ll=l if mask&1 else [0]*n;pp=p if mask&2 else 0
                fs=optimal(hh,ll,pp,a,b);fc_s,_=comp(hh,ll,pp,a,b,theta)
                if fc_s!=fs:raise AssertionError(('coalition identity',mask,h,l,p,a,b,fs,fc_s))
                if sum(v for i,v in enumerate(y) if mask&(1<<i))<fs:raise AssertionError(('coverage',mask,h,l,p,a,b,theta,y,fs))
                counts['coalition_checks']+=1
            for pp in range(p+1):
                _,yd=comp(h,l,pp,a,b,theta)
                if yd[1]>y[1]:raise AssertionError(('C incentive',h,l,p,pp,a,b,theta,y,yd))
                counts['own_deviation_checks']+=1
            for i in range(n):
                for hh_i in range(h[i]+1):
                    hh=list(h);hh[i]=hh_i;_,yd=comp(hh,l,p,a,b,theta)
                    if yd[i+2]>y[i+2]:raise AssertionError(('H incentive',i,h,hh,l,p,a,b,theta,y,yd))
                    counts['own_deviation_checks']+=1
            for ll in product(*(range(v+1) for v in l)):
                _,yd=comp(h,list(ll),p,a,b,theta)
                if yd[0]>y[0]:raise AssertionError(('A bundle incentive',h,l,ll,p,a,b,theta,y,yd))
                counts['own_deviation_checks']+=1
            counts['theta_cases']+=1
        counts['profiles']+=1
    # Pure threshold-edge inclusion is false, unlike the shifted threshold identity.
    # h=(1,1),L=(1,0),P=1,a=(2,0),b=(3,2), true optimum4, naive layer5.
    witness={'h':[1,1],'l':[1,0],'p':1,'a':[2,0],'b':[3,2],
             'actual':4,'naive_edge_threshold_integral':5}
    out={'status':'PASS','evidence':'exact finite diagnostic; continuous proof separate',
         'counts':counts,'naive_layer_failure':witness,
         'sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
    (ROOT/'route_value_checks.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':run()
