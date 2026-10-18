from fractions import Fraction as R
from pathlib import Path
from itertools import product
import json
from check_scalar_importance_qp_family import LOW,HIGH,verify_kkt,potential_certificates

comparisons=0
chain_kkt=[]
for M in range(1,9):
    n=M+2
    for m in range(1,M+1):
        # Actual row reports: P, then X1,Y1,...,XM,YM.
        b=[[0]*(2*M+1) for _ in range(n)]
        b[0][0]=1
        for j in range(1,M+1):
            b[1][2*j-1]=int(j<=m)
            b[j+1][2*j]=1
        def production(c):
            return min(c[0],sum(min(c[2*j-1],c[2*j]) for j in range(1,M+1)))
        # The unique unpenalized equal-weight QP candidate, independently
        # checked by all coverage constraints and nonnegative KKT multipliers.
        q=R(1,2*m+1); t=m*q
        y=[t,t]+[q]*m+[R(0)]*(M-m)
        branch_masks=[3|(1<<(j+1)) for j in range(1,m+1)]
        dual={mask:2*q for mask in branch_masks}
        for mask in range(1<<n):
            c=[sum(b[i][r] for i in range(n) if mask>>i&1) for r in range(2*M+1)]
            v=production(c)
            assert v==int(bool(mask&1) and bool(mask&2) and any(mask&(1<<(j+1)) for j in range(1,m+1)))
            slack=sum(y[i] for i in range(n) if mask>>i&1)-v
            assert slack>=0 and dual.get(mask,0)*slack==0
            comparisons+=1
        assert [2*z for z in y]==[sum(lam for mask,lam in dual.items() if mask>>i&1) for i in range(n)]
        assert all(lam>=0 for lam in dual.values())
        chain_kkt.append({'M':M,'m':m,'common_payment':str(t),'leaf_payment':str(q),'branch_multiplier':str(2*q),'unique_QP_optimum':True})

# Same weighted formulas as the proof, now verified against the FULL actual
# low/high coverage polyhedra by exact KKT, rather than algebra alone.
weighted=0
minimum_loss=None
for wp,wa,wb,wd in product(range(1,6),repeat=4):
    e=R(wp*wa,wp+wa); alpha=R(wp,wp+wa)
    ql=e/(e+wb); qh=e/(e+wb+wd)
    yl=[(1-alpha)*(1-ql),alpha*(1-ql),ql,R(0)]
    yh=[(1-alpha)*(1-qh),alpha*(1-qh),qh,qh]
    verify_kkt(LOW,yl,[wp,wa,wb,wd],{7:2*wb*ql})
    verify_kkt(HIGH,yh,[wp,wa,wb,wd],{7:2*wb*qh,11:2*wd*qh})
    loss=yl[1]+yl[2]-yh[1]-yh[2]
    assert loss==(1-alpha)*(ql-qh)>0
    minimum_loss=loss if minimum_loss is None else min(minimum_loss,loss)
    weighted+=1
pl=potential_certificates(LOW); ph=potential_certificates(HIGH)
result={'status':'PASS','maximum_branches':8,'actual_packing_subset_profile_comparisons':comparisons,'chain_QP_KKT_certificates':chain_kkt,'owner_specific_weight_quadruples_with_full_low_high_KKT':weighted,'weighted_minimum_pair_loss_on_grid':str(minimum_loss),'low_global_surplus_potentials':[p['g'] for p in pl],'high_global_surplus_potentials':[p['g'] for p in ph],'chain_pair_TCWM_funding_bound':'(M+2)/3 (analytic strict-convexity argument, not inferred from these quadratic optima)','scope':'Exact actual-packing coverage, complementary slackness, gradient stationarity, and positive Hessians certify the quadratic optima. The broad nonsmooth theorem remains a written conventional proof.'}
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='chain_QP_KKT_certificates'},indent=2))
