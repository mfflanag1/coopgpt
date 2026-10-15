"""Exact V-cap witness checks; mathematical universal claims use the proof."""
from fractions import Fraction as Q
from pathlib import Path
import json
import random

C={}
def chk(ok,key):
    if not ok: raise AssertionError(key)
    C[key]=C.get(key,0)+1

rng=random.Random(20261015)
examples=[]
for n in (5,6,8,9,12,16,25,40,64):
    m=1
    while Q((m+1)*(m+8),2)<=n-1:m+=1
    eps=Q(1,100*n**6);t=1+(n-1)*eps
    a=1-Q(2*m+1,n);S0=Q(m*(m+1),2);D=n-3*m-1
    chk(0<a<=1 and S0<=D,'parameters')
    pi=[Q(m-k+1)/S0 for k in range(1,m+1)]
    budgets=[[] for _ in range(n)]
    for k in range(1,m+1):
        values=[t]
        for l in range(1,n):
            r=n-l;off=Q(n-l,n*n) if l<k else Q(0)
            values.append(Q(n*n*r,l)*eps+off*r*(1+(r-1)*eps))
        values.append(Q(0))
        deltas=[values[l]-values[l+1] for l in range(n)]
        V=max(deltas)
        chk(0<=V<=t,'max_coalition_marginal_range')
        chk(V/t>=a,'all_owner_V_lower')
        chk(Q(n-k+1)*deltas[k-1]/t>=D,'threshold_endpoint')
        for l in range(n):
            chk(deltas[l]>=0,'endpoint_nonnegative')
            if l:
                off=Q(n-l,n*n) if l<k else Q(0)
                raw=Q(n*n,l*l)*(1+(l-1)*eps)+off*(n-l)*eps
                chk(raw>=t>=V,'closed_price_exceeds_V')
            budgets[l].append((l*V+(n-l)*deltas[l])/t)
    minimum=min(sum(p*b for p,b in zip(pi,bs)) for bs in budgets)
    for bs in budgets:chk(sum(p*b for p,b in zip(pi,bs))>=a*m,'proper_mask_weighted_bound')
    # The cyclic anchor first-moment identity is exact for every weight vector;
    # direct checks below additionally test diverse rational support vectors.
    dim=n*n
    supports=[]
    for pos in (0,dim//2,dim-1):
        w=[Q(0)]*dim;w[pos]=Q(1);supports.append(w)
    supports.append([Q(1,dim)]*dim)
    raw=[rng.randrange(10) for _ in range(dim)];total=sum(raw)
    supports.append([Q(x,total) for x in raw])
    supports.append([Q(x,3) for x in raw])
    for w in supports:
        mass=sum(w);chk(mass>=1,'support_mass')
        current=sum(w[:n]);window=[]
        for j in range(dim):
            window.append(current)
            current+=w[(j+n)%dim]-w[j]
        chk(sum(window)/dim==mass/n,'cyclic_scarce_expectation')
        good=[j for j,z in enumerate(window) if z<=mass/2]
        chk(Q(len(good),dim)>=1-Q(2,n),'cyclic_markov_bound')
        for j in good:
            chk(2*(mass-window[j])>=1,'every_owner_full_V_cap_on_good_anchor')
        chk(Q(n*len(good),dim)>=n-2,'empty_anchor_budget')
    A0=n-2;L=(a*m)*A0/(a*m+A0)
    wr=Q(A0)/(A0+a*m);wa=(a*m)/(A0+a*m)
    chk(wr*a*m==wa*A0==L,'combined_lower')
    examples.append({'n':n,'m':m,'a':str(a),'proved_lower':str(L),
                     'lower_decimal':float(L),'minimum_actual_regular_budget':str(minimum),
                     'resource_dimension':n*m+n*n,'anchor_profiles':n*n})

out={'status':'pass','arithmetic':'exact rational','counts':C,'examples':examples,
     'scope':'finite checks of explicit proof; not novelty or unrestricted lower'}
Path(__file__).with_name('VCAP_MASK_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
