#!/usr/bin/env python3
"""Exact scalar corroboration plus independently written finite stress checks.

Finite report checks do NOT prove continuum or unrestricted-count assertions.
The conventional proofs in the adjacent .txt files carry those quantifiers.
"""
from fractions import Fraction as Q
import argparse, itertools, json, math, random

def require(ok, message):
    if not ok: raise RuntimeError(message)

C=1+1/(2*math.e)

def primitive(first, second):
    # Independently allocate to resource accounts, retaining actual owner labels.
    totals=(sum(first),sum(second)); short=0 if totals[0]<=totals[1] else 1
    pools=(first,second); T=totals[short]
    if T<=0: return [0.0]*len(first),[0.0]*len(first),[0.0]*len(first)
    capped=[min(x,T) for x in pools[1-short]]
    rate=.5*math.exp(1-sum(capped)/T)
    parts=[[0.0]*len(first) for _ in range(2)]
    for i in range(len(first)):
        parts[short][i]=(1-rate)*pools[short][i]
        parts[1-short][i]=rate*capped[i]
    return [x+y for x,y in zip(*parts)],parts[0],parts[1]

def evaluate(rows):
    n=len(rows); d=(len(rows[0])-1)//2
    power=[r[0] for r in rows]; hardware=[sum(r[1:1+d]) for r in rows]
    local=[0.0]*n; role_h=[0.0]*n; role_l=[0.0]*n; M=0.0
    for j in range(d):
        h=[r[1+j] for r in rows];l=[r[1+d+j] for r in rows]
        M+=min(sum(h),sum(l))
        y,hh,ll=primitive(h,l)
        for i in range(n):local[i]+=y[i];role_h[i]+=hh[i];role_l[i]+=ll[i]
    outer=[power[i]+local[i] for i in range(n)]
    pay,_,_=primitive(hardware,outer)
    H=sum(hardware);P=sum(power);F=min(H,P+M)
    return dict(n=n,d=d,p=power,a=hardware,z=local,zh=role_h,zl=role_l,B=outer,H=H,P=P,M=M,F=F,N=pay)

def robust_bound(v):
    H,P,M=v['H'],v['P'],v['M'];K=P+C*M;a=v['a'];B=v['B']
    if H<=0 or K<=0:return [0.0]*v['n'],'zero'
    if K<=H:
        cap=[min(x,K) for x in a];r=.5*math.exp(1-sum(cap)/K)
        return [b+r*d for b,d in zip(B,cap)],'K<=H'
    if P>=H:
        u=[min(p,H)/H for p in v['p']];U=sum(u)
        ans=[]
        for i in range(v['n']):
            vi=min(B[i],H)/H;ai=a[i]/H
            ans.append(a[i]+.5*H*math.exp(1-U-(vi-u[i]))*max(0,vi-ai))
        return ans,'P>=H'
    q0=.5*math.exp(1-K/H);q1=0 if P==0 else .5*math.exp(1-H/P)
    return [((1-q0)*x+q0*b if x>=b else q1*x+(1-q1)*b) for x,b in zip(a,B)],'middle'

def exact_constants():
    count=0
    e_lower=Q(8,3);e_upper=Q(65,24)+Q(1,100)
    require(e_upper==Q(1631,600) and e_upper<Q(11,4),'e upper bound');count+=1
    require(1+1/(2*e_lower)<Q(6,5),'C<6/5');count+=1
    require(Q(3)*Q(5,4)<4,'exp(6/5)<4 product bound');count+=1
    require(Q(96,55)<Q(9,5),'power-limited middle constant');count+=1
    require(Q(69,50)+Q(23,20)*Q(1,4)==Q(667,400)<Q(9,5),'p<=1/4 bound');count+=1
    f=lambda p:Q(809,550)+Q(213,220)*p-Q(8,11)*p*p
    require(f(Q(1,2))==Q(3901,2200)<Q(9,5),'middle tangent endpoint');count+=1
    require(Q(213,220)-Q(16,11)*Q(1,2)>0,'tangent quadratic increasing');count+=1
    require(Q(1347,880)+Q(81,308)==Q(11049,6160)<Q(9,5),'chord quadratic maximum');count+=1
    require(Q(9,5)-Q(11049,6160)==Q(39,6160),'strict rational margin');count+=1
    # Corroborate exact polynomial identities at enough rational points for
    # degree<=2; coefficients are rational and formulas are shown in proof.
    for p in [Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)]:
        require(Q(41,25)-(Q(163,100)+Q(13,25)*p-p*p)==(p-Q(1,2))*(p-Q(1,50)),'old quadratic identity');count+=1
        require(Q(29,20)-10*p-p*p==(Q(13,25)-2*p)*(5+p)-(Q(23,20)+Q(13,25)*p-p*p),'ratio derivative identity');count+=1
    return count

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--profiles',type=int,default=3000);ap.add_argument('--seed',type=int,default=20261016);args=ap.parse_args()
    rng=random.Random(args.seed); checks=0; regions={};max_ratio=0;envelope_max=0
    for case in range(args.profiles):
        n=rng.randint(2,8);d=rng.randint(1,5)
        values=[0,0,0,.125,.25,.5,1,2,5,20]
        rows=[[rng.choice(values) for _ in range(1+2*d)] for _ in range(n)]
        if case%4==0:
            for r in rows:r[0]=0
        if case%4==1:
            for r in rows:
                for j in range(1,len(r)):
                    if rng.random()<.6:r[j]=0
        v=evaluate(rows);bounds,region=robust_bound(v);regions[region]=regions.get(region,0)+1
        scale=max(1,v['H'],sum(v['B']));tol=1e-10*scale
        require(sum(v['zl'])<=v['H']/2+tol,'local power role bound')
        require(all(v['zh'][i]<=v['a'][i]+tol for i in range(n)),'hardware own cap')
        require(sum(bounds)<=1.8*v['F']+tol,'sum of robust bounds exceeds proven factor')
        checks+=3
        env=v['N'].copy()
        for i in range(n):
            for trial in range(20):
                altered=[r.copy() for r in rows]
                if trial<len(rows[i]):altered[i][trial]=0
                else:altered[i]=[x*rng.choice([0,.25,.5,.75,1]) for x in rows[i]]
                w=evaluate(altered);env[i]=max(env[i],w['N'][i])
                require(w['N'][i]<=bounds[i]+tol,'actual underreport exceeds range-robust owner bound')
                checks+=1
        if v['F']>0:
            max_ratio=max(max_ratio,sum(bounds)/v['F']);envelope_max=max(envelope_max,sum(env)/v['F'])
        if n<=5 and case%20==0:
            for mask in range(1,1<<n):
                sub=[[x if mask>>i&1 else 0 for x in r] for i,r in enumerate(rows)]
                worth=evaluate(sub)['F']
                require(sum(v['N'][i] for i in range(n) if mask>>i&1)>=worth-tol,'base coalition coverage');checks+=1
    # Calibrate known actual nested nonmonotonicity; must not accidentally
    # test a corrected or different primitive.
    profile=[[3,.875,5,0,0],[0,1,0,0,0],[0,1,0,0,0],[0,0,0,1,0]]
    full=evaluate(profile)['N'][0];profile[0][1]=.75;under=evaluate(profile)['N'][0]
    require(under>full+.0015,'known nested incentive failure not reproduced');checks+=1
    print(json.dumps(dict(status='PASS',exact_scalar_checks=exact_constants(),finite_stress_checks=checks,profiles=args.profiles,seed=args.seed,regions=regions,max_robust_bound_ratio=max_ratio,max_sampled_envelope_ratio=envelope_max,nested_calibration_gain=under-full,scope='finite stress checks and exact scalar algebra; universal theorem rests on written proof')))

if __name__=='__main__':main()
