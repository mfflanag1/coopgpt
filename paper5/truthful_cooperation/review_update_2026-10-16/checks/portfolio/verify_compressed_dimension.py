"""Exact verification of compressed finite support/endpoint obstructions."""
from fractions import Fraction as Q
from math import isqrt,comb
from pathlib import Path
import random,json
C={};rng=random.Random(20261015)
def chk(x,k):
    if not x:raise AssertionError(k)
    C[k]=C.get(k,0)+1
def scalar_supports(dim):
    out=[]
    for pos in (0,dim//2,dim-1):
        w=[Q(0)]*dim;w[pos]=Q(1);out.append(w)
    out.append([Q(1,dim)]*dim)
    x=[rng.randrange(10) for _ in range(dim)];s=sum(x)
    out.append([Q(z,s) for z in x]);out.append([Q(z,3) for z in x])
    return out
def cyclic_sums(w,k):
    d=len(w);cur=sum(w[:k]);ans=[]
    for j in range(d):ans.append(cur);cur+=w[(j+k)%d]-w[j]
    return ans
def construction(n,mode):
    if mode=='T':
        m=1
        def S(k):return sum(Q(k-l,n-l) for l in range(k))
        while S(m+1)<=1:m+=1
        norm=S(m);delta=[Q(m-l,n-l)/norm if l<m else Q(0) for l in range(n)]
        threshold=Q(m)-Q(1,n*n);a=None
    else:
        m=isqrt(2*n);a=1/(1+sum(Q(m-l,n-l) for l in range(1,m)))
        delta=[a]+[a*Q(m-l,n-l) if l<m else Q(0) for l in range(1,n)]
        threshold=a*m-Q(2,n*n)
    chk(sum(delta)==1,'delta_sum')
    chk(all(delta[i]>=delta[i+1] for i in range(n-1)),'delta_decreasing')
    chk(delta[0]>=Q(1,n)+Q(1,n*n),'baseline_gap_parameter')
    v=[sum(delta[l:]) for l in range(n)]+[Q(0)]
    ac=[None]+[v[l]/(n-l) for l in range(1,n)]
    eps=Q(1,100*n**6);t=1+(n-1)*eps;eta=Q(1,n**3)
    actual=[];rawclosed=[]
    for l in range(n):
        r=n-l;x0=r*eps;x1=1+(r-1)*eps
        scores=[('baseline',(l*x0+r*x1)/n,1)]
        for s in range(1,n):
            for h in range(max(0,s-r),min(l,s)+1):
                score=Q(n*n,s*s)*(h*x0+(s-h)*x1)+ac[s]*((l-h)*x0+(r-s+h)*x1)
                scores.append(((s,h),score,comb(l,h)*comb(r,s-h)))
        C['subset_score_classes']=C.get('subset_score_classes',0)+len(scores)
        best=min(x[1] for x in scores);winners=[x for x in scores if x[1]==best]
        chk(sum(x[2] for x in winners)==1,'unique_gradient')
        chk(winners[0][0]==('baseline' if not l else (l,l)),'forced_gradient_identity')
        expected=t if not l else v[l]+eps*(Q(n*n*r,l)+(r-1)*v[l])
        chk(best==expected,'exact_mask_value')
        actual.append(best)
        if l:
            raw=Q(n*n,l*l)*(1+(l-1)*eps)+ac[l]*r*eps
            chk(raw>t,'closed_raw_exceeds_T');rawclosed.append(raw)
    actual.append(Q(0));end=[actual[l]-actual[l+1] for l in range(n)]
    V=max(end);budgets=[]
    for l in range(n):
        chk(end[l]>=0,'endpoint_nonnegative')
        chk(end[l]/t>=delta[l]-eta,'endpoint_error_bound')
        cap=t if mode=='T' else V
        budget=(l*cap+(n-l)*end[l])/t;budgets.append(budget)
        chk(budget>=threshold,'every_nonempty_mask_lower')
    if mode=='T':
        A=n-2*m;dim=n;anchors=n
        tau=Q(m,4*n**3)
        chk(n*Q(n*n,m)*tau==Q(1,4),'T_anchor_technology_upper')
        for w in scalar_supports(n):
            mass=sum(w);scarce=cyclic_sums(w,m)
            chk(sum(scarce)/n==Q(m,n)*mass,'T_anchor_cyclic_mean')
            good=[z for z in scarce if z<=mass/2]
            chk(len(good)>=n-2*m,'T_anchor_good_windows')
            chk(all(mass-z+tau*z>=Q(1,4) for z in good),'T_anchor_full_prices')
    else:
        R=1
        while R**4<n**3:R+=1
        D=n+R;A=Q(n*R,D);dim=n+D;anchors=D
        for w in scalar_supports(D):
            mass=sum(w);jmax=max(range(D),key=lambda j:w[j]);good=[]
            for j in range(D):
                is_scarce=(jmax-j)%D<n
                if not is_scarce:good.append(j)
            chk(len(good)==R,'V_anchor_max_coordinate_windows')
            chk(D*w[jmax]>=1,'V_anchor_all_owner_prices')
            chk(Q(n*len(good),D)==A,'V_anchor_budget')
        chk(V/t>=a-eta,'V_regular_cap_lower')
    chk(A>0 and threshold>0,'positive_combination')
    L=threshold*A/(threshold+A)
    return {'mode':mode,'n':n,'m':m,'dimension':dim,'anchor_profiles':anchors,
            'regular_lower':str(threshold),'anchor_lower':str(A),'combined_lower':str(L),
            'lower_decimal':float(L),'actual_minimum_regular_budget':str(min(budgets))}

examples=[construction(n,mode) for n in (9,12,16,25,40,64) for mode in ('T','V')]
out={'status':'pass','arithmetic':'exact rational; all subset-cardinality/intersection classes',
     'counts':C,'examples':examples,'scope':'architecture lower only, not unrestricted lower'}
Path(__file__).with_name('COMPRESSED_DIMENSION_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
