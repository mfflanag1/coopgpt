"""Exact checks for finite-support arbitrary-mask architecture obstruction."""
from fractions import Fraction as Q
from itertools import combinations
from math import isqrt
from pathlib import Path
import json
counts={}
def chk(ok,key):
    if not ok:raise AssertionError(key)
    counts[key]=counts.get(key,0)+1

def forms(n,k):
    V=[tuple(Q(1,n) for _ in range(n))]
    for s in range(k,n):
        for S in combinations(range(n),s):
            SS=set(S);V.append(tuple(Q(n*n,s*s) if i in SS else Q(0) for i in range(n)))
    return V

def evaluate(V,x):
    dots=[sum(a*b for a,b in zip(v,x)) for v in V];value=min(dots)
    return value,[V[i] for i,z in enumerate(dots) if z==value]

results=[]
for n in range(4,9):
    m=isqrt(n);eps=Q(1,8*n**4);t=1+(n-1)*eps
    allV=[forms(n,k) for k in range(1,m+1)]
    b=tuple(tuple(Q(1) if e==i else eps for e in range(n)) for i in range(n))
    budgets={mask:[] for mask in range(1,1<<n)}
    for k,V in enumerate(allV,1):
        totals={mask:tuple(sum(b[i][e] for i in range(n) if mask>>i&1) for e in range(n)) for mask in range(1<<n)}
        vals={mask:evaluate(V,x) for mask,x in totals.items()}
        chk(vals[(1<<n)-1][0]==t,'grand_value')
        for mask in range(1,1<<n):
            l=n-mask.bit_count();r=n-l;x=totals[mask];v,active=vals[mask]
            chk(len(active)==1,'unique_global_active_gradient')
            w=active[0]
            if l<k:
                chk(w==V[0],'baseline_selected')
            else:
                expected=tuple(Q(n*n,l*l) if not(mask>>i&1) else Q(0) for i in range(n))
                chk(w==expected,'closed_subset_selected')
            R=Q(0)
            for i in range(n):
                if mask>>i&1:
                    pay=v-vals[mask^(1<<i)][0]
                    if l==k-1:chk(pay>=Q(n-m,n),'threshold_endpoint_lower')
                else:
                    pay=min(sum(w[e]*b[i][e] for e in range(n)),t)
                    if l>=k:chk(pay==t,'full_closed_cap')
                chk(pay>=0,'nonnegative_payment');R+=pay
            if l==k-1:chk(R/t>=Q(n,8),'normalized_threshold_budget')
            if l>=k:chk(R/t>=l,'normalized_closed_budget')
            budgets[mask].append(R/t)
    worst=None
    for mask,R in budgets.items():
        l=n-mask.bit_count();avg=sum(R)/m
        if l<m:chk(avg>=Q(n,8*m),'uniform_profile_low_closed')
        else:chk(avg>=m,'uniform_profile_high_closed')
        chk(avg/2>=Q(m,16),'combined_proper_mask_bound')
        worst=avg/2 if worst is None else min(worst,avg/2)
    # At empty mask inspect every block1 extreme form plus convex combinations
    # and positive multiples. These are genuine global-support restrictions.
    delta=Q(1,4*n**3)
    anchors=[tuple(delta if e==j else Q(1) for e in range(n)) for j in range(n)]
    Ts=[n*evaluate(allV[0],z)[0] for z in anchors]
    chk(all(0<T<=Q(1,4) for T in Ts),'anchor_value_bounds')
    W=allV[0]+[tuple((x+y)/2 for x,y in zip(allV[0][0],w)) for w in allV[0][1:]]
    for w in W:
        chk(sum(w)>=1,'anchor_support_sum')
        R=[]
        for z,T in zip(anchors,Ts):
            R.append(n*min(sum(x*y for x,y in zip(w,z)),T)/T)
        chk(sum(R)/n>=n-1,'empty_anchor_average')
        chk(sum(R)/(2*n)>=Q(m,16),'combined_empty_mask_bound')
    results.append({'n':n,'m':m,'proved_lower':str(Q(m,16)),
                    'minimum_half_regular_budget_over_proper_masks':str(worst),
                    'proper_masks':(1<<n)-1,'anchor_supports_checked':len(W)})
out={'status':'pass','arithmetic':'exact rational; explicitly enumerated finite form minima',
     'counts':counts,'cases':results,'scope':'bounded checks; proof in FINITE_SUPPORT_MASK_OBSTRUCTION.txt'}
Path(__file__).with_name('FINITE_MASK_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
