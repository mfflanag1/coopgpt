#!/usr/bin/env python3
"""Independent finite numerical checks; theorem and rational certificate separate."""
import itertools,random,json,math
from pathlib import Path
from coupled_reference import coupled_rule,optimize_coupled,eta,kappa
from check_cyclic_obstruction import primitive,rows as cyclic_rows
from owner_box_reference import box_range_rule
from verify_envelope_bounds import evaluate

OUT=Path(__file__).parent

def require(ok,message):
    if not ok:raise ArithmeticError(message)

def run():
    counts={'response_inequalities':0,'sharp_attainers':0,'physical_profiles':0,'coalitions':0,'own_underreports':0,'generic_domains':0,'auxiliary_competitors':0}
    vals=[0.,.25,.75,1.5]
    # Exhaustive small local profiles, no inherited test code.
    for data in itertools.product(vals,repeat=6):
        h=list(data[:3]);l=list(data[3:]);z=primitive(h,l)
        for i in range(3):
            k=sum(h[t]>0 for t in range(3) if t!=i)
            require(sum(z[t] for t in range(3) if t!=i)+1e-11>=eta(k)*(z[i]-h[i]),'mixed response inequality')
            counts['response_inequalities']+=1
            if h[i]==0:
                require(sum(z[t] for t in range(3) if t!=i)+1e-11>=kappa(k)*z[i],'zero-hardware response')
                counts['response_inequalities']+=1
    for k in range(1,10):
        target=.5*math.exp(1-k);l=0.;u=1.
        for _ in range(80):
            m=(l+u)/2
            if m*math.exp(m)<target:l=m
            else:u=m
        own=(l+u)/2
        h=[own]+[1.]*k;local=[1.]+[0.]*k;z=primitive(h,local)
        require(abs(sum(z[1:])/(z[0]-own)-eta(k))<2e-12,'sharp local attainer')
        counts['sharp_attainers']+=1
    rng=random.Random(161083)
    max_ratio=0.;max_profile=None
    for case in range(220):
        n=rng.randrange(1,6);m=rng.randrange(1,4)
        rr=[[rng.choice([0.,0.,.25,.75,1.5]) for _ in range(1+2*m)] for _ in range(n)]
        if case%3==0:
            for r in rr:r[0]=0.
        if case%4==0:rr[-1][1:1+m]=[0.]*m
        ans,w,g,v=coupled_rule(rr);box,*_=box_range_rule(rr)
        tol=1e-8*max(1.,v['H'],v['P']+sum(v['z']))
        require(all(v['N'][i]-tol<=ans[i]<=box[i]+tol for i in range(n)),'coupled sandwich')
        if v['F']>0 and sum(ans)/v['F']>max_ratio:
            max_ratio=sum(ans)/v['F'];max_profile={'rows':rr,'payments':ans,'v':v}
        for mask in range(1<<n):
            coal=[i for i in range(n) if mask>>i&1]
            if not coal:value=0.
            else:value=evaluate([rr[i] for i in coal])['F']
            require(sum(ans[i] for i in coal)+tol>=value,'coalition coverage')
            counts['coalitions']+=1
        for i in range(n):
            for choice in range(3):
                reduced=[r.copy() for r in rr]
                if choice==0:reduced[i][1:1+m]=[0.]*m # specifically crosses hardware boundary
                elif choice==1:reduced[i]=[x/2 for x in reduced[i]]
                else:reduced[i][rng.randrange(1+2*m)]=0.
                small,_,_,sv=coupled_rule(reduced)
                require(small[i]<=ans[i]+tol,'whole-owner monotonicity')
                require(sv['N'][i]<=ans[i]+tol,'envelope witness')
                counts['own_underreports']+=1
        counts['physical_profiles']+=1
    # Generic boxes: independent valid feasible points, not local-production data.
    for case in range(1400):
        n=rng.randrange(2,7);i=rng.randrange(n)
        a=[rng.randrange(1,13)/4 for _ in range(n)];H=sum(a)
        if case%3==0:a[i]=0.;H=sum(a)
        p=[rng.randrange(0,7)/4 for _ in range(n)]
        gamma=rng.choice([eta(1),eta(2),eta(3),kappa(2),1.])
        z=rng.randrange(0,13)/4;beta=p[i]+z
        full=[p[t]+rng.randrange(0,13)/4 for t in range(n)];full[i]=beta
        need=max(0.,gamma*(z-a[i])-sum(full[t]-p[t] for t in range(n) if t!=i))
        full[(i+1)%n]+=need
        lo=[p[t]+(full[t]-p[t])*rng.random() for t in range(n)];lo[i]=p[i]
        up=[full[t]+rng.randrange(0,13)/4 for t in range(n)];up[i]=beta
        K=sum(full)+rng.randrange(0,9)/4
        answer,w,mode=optimize_coupled(a,lo,up,beta,K,p,i,gamma)
        tol=1e-8*max(1,H,K)
        require(answer+tol>=primitive(a,full)[i],'generic full vector beats optimizer')
        counts['auxiliary_competitors']+=1
        for trial in range(40):
            aux=[lo[t]+rng.random()*(up[t]-lo[t]) for t in range(n)]
            if sum(aux)>K:continue
            if sum(aux[t]-p[t] for t in range(n) if t!=i)<gamma*(aux[i]-p[i]-a[i]):continue
            require(primitive(a,aux)[i]<=answer+tol,'generic auxiliary beats optimizer')
            counts['auxiliary_competitors']+=1
        counts['generic_domains']+=1
    cyclic=[]
    for n in [3,4,5,7,11]:
        rr=[[float(t) for t in r] for r in cyclic_rows(n)]
        ans,*_=coupled_rule(rr)
        require(sum(ans)/n<1.401,'cyclic improvement')
        cyclic.append({'hardware_owners':n,'branches':n,'ratio':sum(ans)/n})
    result={'status':'FINITE FLOAT PASS','counts':counts,'max_sampled_ratio_not_a_bound':max_ratio,'max_profile':max_profile,'cyclic_replays':cyclic,'scope':'Numerical corroboration only. Sharp response and mechanism proofs are in COUPLED_BOX_THEOREM.txt; strict cyclic ratios use separate exact rational certificates.'}
    (OUT/'coupled-rule-checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':run()
