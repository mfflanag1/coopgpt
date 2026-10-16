#!/usr/bin/env python3
"""Independent explicit range-rule implementation and finite stress tests.
No finite test is presented as a substitute for the universal analytic proof.
"""
import argparse,json,math,random
from verify_envelope_bounds import evaluate,primitive,require,C

def range_rule(rows,attainers=False):
    v=evaluate(rows);n=v['n'];H=v['H'];P=v['P'];K=P+C*v['M'];a=v['a'];beta=v['B'];p=v['p']
    if H<=0 or K<=0:return [0.0]*n,[[0.0]*n for _ in range(n)],v
    if n==1:return [v['F']],[beta.copy()],v
    answers=[];witnesses=[]
    for i in range(n):
        pm=P-p[i];b=beta[i];hi=a[i];cases=[]
        others=[j for j in range(n) if j!=i]
        if P<=H:
            U=min(K,H);T=U if b<=hi else min(U,b+pm)
            own=min(b,max(0.0,T-pm))
            q=0.0 if T==0 else .5*math.exp(1-sum(min(x,T) for x in a)/T)
            val=0.0 if T==0 else own+q*(min(hi,T)-own)
            w=p.copy();w[i]=own;w[others[0]]+=max(0.0,T-sum(w));cases.append((val,w,'short'))
        if K>=H:
            d=min(b,H);s=sum(min(p[j],H) for j in others);waste=sum(max(p[j]-H,0) for j in others)
            w=p.copy();w[i]=b
            if d>=hi:
                rho=max(1.0,(d+s)/H)
                w[others[0]]+=max(0.0,H-sum(w))
            else:
                rho=min((d+(n-1)*H)/H,(K-waste)/H)
                remaining=max(0.0,K-sum(w))
                for j in others:
                    move=min(remaining,max(0.0,H-w[j]));w[j]+=move;remaining-=move
            val=hi+.5*math.exp(1-rho)*(d-hi);cases.append((val,w,'long'))
        require(bool(cases),'no feasible regime')
        val,w,mode=max(cases,key=lambda x:x[0]);answers.append(val);witnesses.append(w)
    return answers,witnesses,v

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--profiles',type=int,default=4000);ap.add_argument('--seed',type=int,default=483903);args=ap.parse_args()
    rng=random.Random(args.seed);checks=0;maxratio=0;maxprofile=None
    for case in range(args.profiles):
        n=rng.randint(1,9);d=rng.randint(1,5)
        choices=[0,0,0,.125,.25,.5,1,2,4,16]
        rows=[[rng.choice(choices) for _ in range(1+2*d)] for _ in range(n)]
        if case%5==0:
            for row in rows:row[0]=0
        if case%5==1:
            for row in rows:
                for j in range(1,len(row)):
                    if rng.random()<.8:row[j]=0
        R,att,v=range_rule(rows,True);K=v['P']+C*v['M'];tol=2e-10*max(1,v['H'],K)
        require(sum(R)<=1.75*v['F']+tol,'7/4 budget violation')
        require(all(R[i]>=v['N'][i]-tol for i in range(n)),'range rule below base')
        checks+=2
        for i in range(n):
            w=att[i]
            # Zero-valued special cases return a dummy zero vector; all
            # nonzero cases must actually attain the claimed supremum.
            if v['H']>0 and K>0:
                require(all(w[j]>=v['p'][j]-tol for j in range(n)),'attainer below power floor')
                require(w[i]<=v['B'][i]+tol and sum(w)<=K+tol,'infeasible attainer')
                val=primitive(v['a'],w)[0][i]
                require(abs(val-R[i])<=tol,'closed-form value not attained');checks+=3
            for trial in range(12):
                if n>=2:
                    x=rng.random()*v['z'][i];remaining=max(0,C*v['M']-x)
                    weights=[rng.random() if j!=i else 0 for j in range(n)];s=sum(weights)
                    use=rng.random()*remaining
                    w=[v['p'][j]+(x if j==i else use*weights[j]/s) for j in range(n)]
                    val=primitive(v['a'],w)[0][i]
                    require(val<=R[i]+tol,'random feasible vector beats closed form');checks+=1
                reduced=[row.copy() for row in rows]
                if trial<len(rows[i]):reduced[i][trial]=0
                else:reduced[i]=[x*rng.choice([0,.25,.5,.75,1]) for x in rows[i]]
                RR,_,_=range_rule(reduced)
                require(RR[i]<=R[i]+tol,'actual own underreport improves range payment');checks+=1
        if v['F']>0 and sum(R)/v['F']>maxratio:
            maxratio=sum(R)/v['F'];maxprofile=dict(rows=rows,payments=R,F=v['F'],ratio=maxratio)
    print(json.dumps(dict(status='PASS',profiles=args.profiles,finite_checks=checks,seed=args.seed,max_sampled_ratio=maxratio,max_profile=maxprofile,scope='finite diagnostic checks, exact attainer formulas numerically cross-checked; unrestricted continuum theorem is analytic')))

if __name__=='__main__':main()
