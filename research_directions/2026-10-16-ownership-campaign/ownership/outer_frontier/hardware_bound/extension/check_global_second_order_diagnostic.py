"""Floating falsification/replay, not a proof or actual envelope optimizer."""
import json, math, random
from pathlib import Path
random.seed(161023)
K=math.e-1

def phi(a,b):
    A,B=sum(a),sum(b)
    if min(A,B)<=0:return [0.0]*len(a)
    if A>B:return phi(b,a)
    d=[min(t,A) for t in b]
    q=0.5*math.exp(1-sum(d)/A)
    return [(1-q)*x+q*y for x,y in zip(a,d)]

def state(h,l,p):
    n=len(p); z=[0.0]*n
    for hh,ll in zip(h,l):
        for i,t in enumerate(phi(hh,ll)):z[i]+=t
    a=[sum(hh[i] for hh in h) for i in range(n)]
    return phi(a,[p[i]+z[i] for i in range(n)]),z,a

local_checks=0; max_in=0.; max_pos=0.
for k in range(30000):
    n=random.randrange(2,24)
    a=[10**random.uniform(-3,1) if random.random()>.1 else 0. for _ in range(n)]
    b=[10**random.uniform(-3,1) if random.random()>.1 else 0. for _ in range(n)]
    i=random.randrange(n); side=random.randrange(2)
    x=a if side==0 else b
    dt=1e-7*max(1,sum(a),sum(b)); old=phi(a,b)
    x[i]+=dt; new=phi(a,b); x[i]-=dt
    slope=[(y-z)/dt for y,z in zip(new,old)]
    inc=sum(max(0.,-slope[j]) for j in range(n) if j!=i)
    pos=sum(max(0.,t) for t in slope)
    if inc>.50001 or pos>1+2/math.e+.00001:
        raise RuntimeError(('local derivative',inc,pos,a,b,i,side))
    max_in=max(max_in,inc);max_pos=max(max_pos,pos);local_checks+=1

restores=0; min_gain=0.; incoming_checks=0; max_ratio=0.
for k in range(2000):
    n=random.randrange(8,45); branches=random.randrange(1,8)
    h=[[random.expovariate(1) if random.random()>.3 else 0. for _ in range(n)] for _ in range(branches)]
    sc=sum(map(sum,h));h=[[x/sc for x in row]for row in h]
    l=[[random.expovariate(1)*random.uniform(.02,2)/n/branches if random.random()>.3 else 0. for _ in range(n)]for _ in range(branches)]
    p=[random.expovariate(1)*random.uniform(.2,6)/n for _ in range(n)]
    full,z,a=state(h,l,p); S=sum(min(1,p[i]+z[i])for i in range(n))
    X=sum(min(sum(hh),sum(ll))for hh,ll in zip(h,l)if sum(hh)<=sum(ll))
    for i in random.sample(range(n),min(n,8)):
        if S<1.5+math.e*z[i]:continue
        hd=[row[:]for row in h];ld=[row[:]for row in l]
        for j in range(branches):
            hd[j][i]*=random.random();ld[j][i]*=random.random()
        before,_,_=state(hd,ld,p)
        restored,zr,_=state(h,ld,p)
        gain=restored[i]-before[i]
        if gain< -1e-11:raise RuntimeError(('hardware restoration',gain,S,z[i],h,l,p,i,hd,ld))
        min_gain=min(min_gain,gain);restores+=1
        incoming=sum(max(0,zr[t]-z[t])for t in range(n)if t!=i)
        vi=0.
        for hh,ll in zip(h,l):
            H,L=sum(hh),sum(ll)
            if H>0 and H<=L:
                q=.5*math.exp(1-sum(min(x,H)for x in ll)/H)
                vi+=q*min(ll[i],H)
        rhs=z[i]-vi+(K*vi*(1+math.log(X/(2*vi)))if vi>0 else 0)
        if incoming>rhs+1e-11:raise RuntimeError(('local entropy',incoming,rhs,X,vi,z[i]))
        if rhs>0:max_ratio=max(max_ratio,incoming/rhs)
        incoming_checks+=1

result=dict(status='PASS',kind='floating diagnostic only',local_derivative_checks=local_checks,
 maximum_incoming_slope=max_in,maximum_all_positive_slope=max_pos,
 actual_hardware_restorations=restores,min_restoration_gain=min_gain,
 local_only_entropy_checks=incoming_checks,max_incoming_to_bound_ratio=max_ratio)
Path(__file__).with_name('global_second_order_diagnostic.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
