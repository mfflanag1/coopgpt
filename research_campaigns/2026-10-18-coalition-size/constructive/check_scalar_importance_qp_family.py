from fractions import Fraction as R
from itertools import combinations, product
from pathlib import Path
import json

LOW=[(1,0,0,0,0),(0,1,0,0,0),(0,0,1,0,0),(0,0,0,0,1)]
HIGH=[(1,0,0,0,0),(0,1,0,1,0),(0,0,1,0,0),(0,0,0,0,1)]
def F(x):
    return min(x[0], min(x[1],x[2])+min(x[3],x[4]))
def values(b):
    return {mask:F([sum(b[i][j] for i in range(len(b)) if mask>>i&1) for j in range(5)]) for mask in range(1<<len(b))}
def verify_kkt(b,y,weights,multipliers):
    """Full exact KKT against actual packing coalition values and y>=0.
    Multiplier convention: minimize sum_i weights_i*y_i^2, constraints
    sum_C y_i>=v(C). All omitted cover/lower-bound multipliers are zero.
    Positive weights make the objective strictly convex, so KKT certifies the
    unique global minimizer of the full coverage QP, not just feasibility.
    """
    v=values(b)
    assert len(y)==len(weights)==len(b) and all(w>0 for w in weights)
    assert all(t>=0 for t in y)
    for mask, val in v.items():
        slack=sum(y[i] for i in range(len(b)) if mask>>i&1)-val
        lam=multipliers.get(mask,R(0))
        assert slack>=0 and lam>=0 and lam*slack==0
    grad=[2*w*t for w,t in zip(weights,y)]
    dual=[sum(lam for mask,lam in multipliers.items() if mask>>i&1) for i in range(len(b))]
    assert grad==dual,(grad,dual)
    return {'gradient':list(map(str,grad)),'cover_multipliers':{str(k):str(v) for k,v in multipliers.items()},'all_coverage_constraints':len(v),'strict_convexity':'all quadratic weights positive'}

def potential_certificates(b):
    B=[sum(x[j] for x in b) for j in range(5)]
    V=F(B); assert V==1
    certificates=[]
    for i,bi in enumerate(b):
        floor=F(bi); assert floor==0
        cap=[B[j]-bi[j] for j in range(5)]
        corners=list(product(*[sorted({0,c}) for c in cap]))
        scored=[(F([a[j]+bi[j] for j in range(5)])-F(a),a) for a in corners]
        maximum,witness=max(scored)
        # For EVERY real a in the box, monotonicity gives
        # F(a+bi)-F(a)<=F(B)=V. Thus a unit corner witness certifies
        # the global continuous maximum, not merely a corner maximum.
        if maximum==V:
            upper='Global upper V=1 attained: F(a+bi)<=F(B), F(a)>=0.'
        else:
            # The only zero case is D at low. Its sole positive coordinate
            # is Y2, while X2 is identically zero throughout the feasible box.
            # Hence min(X2,Y2)=0 before and after for ALL real a in the box.
            assert maximum==0 and bi==(0,0,0,0,1) and cap[3]==0
            upper='Global zero identity: only Y2 changes and X2 is identically0.'
        certificates.append({'owner':i,'floor':floor,'g':maximum-floor,'corner_count':len(corners),'maximizing_corner':list(witness),'global_upper_certificate':upper})
    return certificates

def run():
    vl=values(LOW); vh=values(HIGH)
    assert all(v==int(mask&7==7) for mask,v in vl.items())
    assert all(v==int(mask&3==3 and bool(mask&12)) for mask,v in vh.items())
    pl=potential_certificates(LOW); ph=potential_certificates(HIGH)
    assert [[x['g'] for x in p] for p in [pl,ph]]==[[1,1,1,0],[1,1,1,1]]
    yl=[R(1,3)]*3+[R(0)]; yh=[R(2,5),R(2,5),R(1,5),R(1,5)]
    kl=verify_kkt(LOW,yl,[R(1)]*4,{7:R(2,3)})
    kh=verify_kkt(HIGH,yh,[R(1)]*4,{7:R(2,5),11:R(2,5)})
    assert yl[1]+yl[2]-yh[1]-yh[2]==R(1,15)
    return {'status':'PASS','low_potential_certificates':pl,'high_potential_certificates':ph,'low_payments':list(map(str,yl)),'high_payments':list(map(str,yh)),'low_KKT':kl,'high_KKT':kh,'protected_pair_loss':'1/15','scope':'Exact global potential witnesses plus analytic global upper bounds; full exact QP KKT certifies unique optima. Arbitrary penalties and convex costs still use the written proof.'}
if __name__=='__main__':
    result=run()
    Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
