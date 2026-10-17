"""Exact cardinality-class enumeration of all subset-form scores, not sampling."""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json
C={}
def chk(x,key):
    if not x:raise AssertionError(key)
    C[key]=C.get(key,0)+1

def offcoef(n,s,k):return Q(n-s,n*n) if s<k else Q(0)
def candidate_scores(n,k,l,eps):
    r=n-l;x0=r*eps;x1=1+(r-1)*eps
    out=[('baseline',(l*x0+r*x1)/n,1)]
    for s in range(1,n):
        a=offcoef(n,s,k)
        for h in range(max(0,s-r),min(l,s)+1):
            score=Q(n*n,s*s)*(h*x0+(s-h)*x1)+a*((l-h)*x0+(r-s+h)*x1)
            multiplicity=comb(l,h)*comb(r,s-h)
            out.append(((s,h),score,multiplicity))
    return out

examples=[]
for n in (5,6,8,9,12,16,25,40,64):
    m=1
    while Q((m+1)*(m+8),2)<=n-1:m+=1
    eps=Q(1,100*n**6);t=1+(n-1)*eps;S=Q(m*(m+1),2);D=n-3*m-1
    chk(S<=D,'triangular_parameter')
    pi=[Q(m-k+1)/S for k in range(1,m+1)];chk(sum(pi)==1,'profile_weights')
    B=[[] for l in range(n)]
    for k in range(1,m+1):
        vals=[];grads=[]
        for l in range(n):
            scores=candidate_scores(n,k,l,eps);v=min(z[1] for z in scores)
            winners=[z for z in scores if z[1]==v]
            chk(sum(z[2] for z in winners)==1,'unique_gradient_all_subset_types')
            expected='baseline' if l==0 else (l,l)
            chk(winners[0][0]==expected,'forced_gradient_identity')
            if l:
                C['subset_score_classes']=C.get('subset_score_classes',0)+len(scores)
                raw=Q(n*n,l*l)*(1+(l-1)*eps)+offcoef(n,l,k)*(n-l)*eps
                chk(raw>=t,'closed_owner_full_cap')
            vals.append(v);grads.append(winners[0][0])
        vals.append(Q(0));chk(vals[0]==t,'grand_value')
        for l in range(n):
            r=n-l;delta=vals[l]-vals[l+1];chk(delta>=0,'endpoint_nonnegative')
            R=l*t+r*delta
            if l==k-1:chk(Q(r)*delta/t>=D,'threshold_endpoint_D')
            B[l].append(R/t)
    weighted=[]
    for l in range(n):
        avg=sum(p*b for p,b in zip(pi,B[l]));weighted.append(avg)
        chk(avg>=m,'all_proper_mask_weighted_bound')
    L=Q(m*(n-1),n-1+m);wr=Q(n-1,n-1+m);wa=Q(m,n-1+m)
    chk(wr*m==wa*(n-1)==L,'anchor_combination_balance')
    # Independently check finite anchor supports via all subset cardinalities,
    # positions of the low coordinate, plus baseline.
    delta=Q(1,4*n**3);Tanchor=Q(1,4)
    W=[tuple(Q(1,n) for _ in range(n))]
    for s in range(1,n):W.append(tuple(Q(n*n,s*s) if j<s else Q(0) for j in range(n)))
    for w in W:
        chk(sum(w)>=1,'empty_support_sum')
        ratios=[]
        for j in range(n):
            wz=sum(w[e]*(delta if e==j else 1) for e in range(n))
            ratios.append(n*min(wz,Tanchor)/Tanchor)
        chk(sum(ratios)/n>=n-1,'empty_anchor_average')
    examples.append({'n':n,'m':m,'D':D,'proved_lower_exact':str(L),'lower_decimal':float(L),
                     'minimum_weighted_proper_mask_budget':str(min(weighted)),
                     'all_masks_covered_by_exact_symmetry_classes':2**n-1})
out={'status':'pass','arithmetic':'exact fractions; every subset-cardinality/intersection score checked',
     'counts':C,'examples':examples,
     'scope':'finite verification of proof construction; no novelty assertion'}
Path(__file__).with_name('FINITE_MASK_V2_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
