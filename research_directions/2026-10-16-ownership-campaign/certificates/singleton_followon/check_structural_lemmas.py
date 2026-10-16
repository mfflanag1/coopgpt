#!/usr/bin/env python3
"""Exact star-lemma replay and numerical high-P coupling checks; no LP search."""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import json
import math
import random
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'range_algorithm'))
from verify_range_mechanism import C0, primitive, payments


def require(condition,message):
    if not condition:
        raise ValueError(message)


def worth(h,local,p,mask):
    n=len(h)
    hardware=[h[j] if mask & (1 << (n+1+j)) else F() for j in range(n)]
    power=[local[j] if mask & (1 << j) else F() for j in range(n)]
    own=sum(min(x,y) for x,y in zip(hardware,power))
    shared=p if mask & (1 << n) else F()
    return own+min(shared,sum(hardware)-own)


def exact_stars():
    seeds=[(0,),(1,),(1,1),(1,2),(1,3),(0,1,1),(1,2,2),(1,1,1),
           (1,2,3,4),(0,0,1,3),(1,1,1,1),(1,1,2,3,5,8,13,21)]
    rng=random.Random(16102028)
    seeds += [tuple(F(rng.randrange(8),rng.randrange(1,5)) for _ in range(8))
              for _ in range(12)]
    counts={'star_domains':0,'subset_inequalities':0,'full_coalitions':0,
            'floors':0,'own_report_edges':0,'zero_profiles':0}
    max_factor=F()
    for raw in seeds:
        ell=tuple(map(F,raw)); n=len(ell); L=sum(ell)
        p_values=set((F(),L/5,L/4,L/2,2*L/3,L,2*L,*ell))
        for p in sorted(p_values):
            q=tuple(min(p,L-e) for e in ell)
            u=tuple((L+6*p)/5-z for z in q)
            x=tuple(min(e,p,z) for e,z in zip(ell,u))
            c=min(p,L/5)
            for mask in range(1 << n):
                w=sum(ell[j] for j in range(n) if mask & (1 << j))
                xx=sum(x[j] for j in range(n) if mask & (1 << j))
                require(min(p,w)-xx<=c,'Subset hardware inequality failed')
                counts['subset_inequalities']+=1
            base=tuple(e-z for e,z in zip(ell,x))+(c,)+x
            profiles=[(ell,base)]
            for i in range(n):
                h=list(ell);h[i]+=p
                ci=max(q[i],p-x[i])
                hardware=tuple(x[i] if j==i else F() for j in range(n))
                y=ell+(ci,)+hardware
                profiles.append((tuple(h),y))
                require(y[n+1+i]>=base[n+1+i],'Star own-report edge failed')
                counts['own_report_edges']+=1
                if p==0:
                    require(y==base,'Coincident profiles assigned different payments')
            full=(1 << (2*n+1))-1
            for h,y in profiles:
                T=worth(h,ell,p,full)
                require(all(v>=0 for v in y),'Negative payment')
                require(sum(y)<=F(6,5)*T,'Star budget failed')
                if T:
                    max_factor=max(max_factor,sum(y)/T)
                else:
                    require(sum(y)==0,'Nonzero payment at zero production')
                    counts['zero_profiles']+=1
                for a in range(n):
                    floor=T-worth(h,ell,p,full ^ (1 << a))
                    require(y[a]>=floor,'Star singleton floor failed')
                    counts['floors']+=1
                if n<=4:
                    for mask in range(full+1):
                        lhs=sum(y[i] for i in range(2*n+1) if mask & (1 << i))
                        require(lhs>=worth(h,ell,p,mask),'Star coalition failed')
                        counts['full_coalitions']+=1
            counts['star_domains']+=1
    return {'status':'EXACT RATIONAL PASS','counts':counts,
            'max_funding_factor':str(max_factor),
            'scope':'Replay of a proved restricted star-domain lemma, not a continuous upper.'}


def high_p(trials=1800):
    rng=random.Random(16102029)
    worst=0.; smallest_slack=0.; class_counts={'positive_gap':0,'negative_gap':0,'ties':0}
    for trial in range(trials):
        n,m=rng.randrange(1,21),rng.randrange(1,6)
        h=[[0. if rng.random()<.25 else 10**rng.uniform(-3,3) for _ in range(m)] for _ in range(n)]
        ell=[[0. if rng.random()<.25 else 10**rng.uniform(-3,3) for _ in range(m)] for _ in range(n)]
        H=math.fsum(v for row in h for v in row)
        if H==0:
            continue
        target=H if trial%3==0 else H*(1.01+10**rng.uniform(-3,2))
        if trial%2==0:
            p=[target]+[0.]*(n-1)
        else:
            weights=[rng.random() for _ in range(n)]
            denom=math.fsum(weights)
            p=[target*w/denom for w in weights]
        z=[0.]*n
        M=0.
        for j in range(m):
            hh=[h[i][j] for i in range(n)]
            ll=[ell[i][j] for i in range(n)]
            zz=primitive(hh,ll)
            for i in range(n):z[i]+=zz[i]
            M+=min(math.fsum(hh),math.fsum(ll))
        a=[math.fsum(row)/H for row in h]
        uu=[min(v/H,1.) for v in p]
        vv=[min((p[i]+z[i])/H,1.) for i in range(n)]
        U,Z,t=math.fsum(uu),math.fsum(z)/H,C0*M/H
        dp=math.fsum(max(0.,v-aa) for v,aa in zip(vv,a))
        dm=math.fsum(max(0.,aa-v) for v,aa in zip(vv,a))
        for v,aa in zip(vv,a):
            class_counts['positive_gap' if v>aa else 'negative_gap' if v<aa else 'ties']+=1
        profile=tuple(v for i in range(n) for v in (*h[i],*ell[i],p[i]))
        actual=math.fsum(payments(profile,n,m)[0])/H
        bound_a=1+math.exp(1-U)*(dp-math.exp(-t)*dm)/2
        bound_b=1+math.exp(1-U)*(U+.5-math.exp(-t)*(1.5-Z))/2
        bound_d=1.75-math.exp(-C0)*(1.5-C0)/2
        for slack in (bound_a-actual,bound_b-bound_a,bound_d-bound_b,
                      U+.5-dp,dm-max(0.,dp-U-Z+1)):
            require(slack>=-2e-10,'High-P coupling inequality failed')
            smallest_slack=min(smallest_slack,slack)
        worst=max(worst,actual)
    return {'status':'NUMERICAL PASS','trials':trials,'class_counts':class_counts,
            'largest_observed_factor':worst,'minimum_numeric_inequality_slack':smallest_slack,
            'proved_high_p_bound_numeric_display':1.75-math.exp(-C0)*(1.5-C0)/2,
            'scope':'Binary floats/math.exp; supplementary stress test, not a proof.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    report={'stars':exact_stars(),'high_p':high_p(),
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    encoded=json.dumps(report,indent=2)+'\n'
    args.output.write_text(encoded)
    print(encoded,end='')
