"""Bounded discovery LP: fixed pure binary owners and coalitional outside output.

Within each of two fixed groups, symmetry reduces reports to active counts.
Every inequality is still an actual-owner coalition deviation. Exact rational
dual replay is required before treating a floating result as a lower bound.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse,json,time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

def solve(m):
    start=time.monotonic();states=[(a,b) for a in range(m+1) for b in range(m+1)]
    index={s:j for j,s in enumerate(states)};cost=4*len(states)
    rows=[];cols=[];vals=[];rhs=[];tags=[]
    def add(coeff,b,tag):
        r=len(rhs)
        for j,v in coeff.items():
            if v:rows.append(r);cols.append(j);vals.append(v)
        rhs.append(b);tags.append(tag)
    for a,b in states:
        j=4*index[a,b]
        add({j:a,j+1:m-a,j+2:b,j+3:m-b,cost:-min(a,b)},0,['budget',a,b])
        for x in range(1,a+1):
            for y in range(1,b+1):
                add({j:-x,j+2:-y},-min(x,y),['cover',a,b,x,y])
        for ka in range(a+1):
            for kb in range(b+1):
                if ka+kb==0:continue
                h=4*index[a-ka,b-kb]
                # Each expression is affine in optional unchanged members.
                for ra in set([0,a-ka]):
                    for rb in set([0,b-kb]):
                        for za in set([0,m-a]):
                            for zb in set([0,m-b]):
                                coeff={j:-(ka+ra),j+1:-za,j+2:-(kb+rb),j+3:-zb,
                                       h:ra,h+1:ka+za,h+2:rb,h+3:kb+zb}
                                add(coeff,-min(ka,kb),['outside',a,b,ka,kb,ra,rb,za,zb])
    mat=coo_matrix((vals,(rows,cols)),shape=(len(rhs),cost+1)).tocsr()
    objective=np.zeros(cost+1);objective[cost]=1
    result=linprog(objective,A_ub=mat,b_ub=rhs,bounds=(0,None),options={'time_limit':120})
    out={'m_per_type':m,'owners':2*m,'profiles':len(states),'rows':len(rhs),
         'status':int(result.status),'message':result.message,'seconds':time.monotonic()-start}
    if result.success:
        out['floating_optimum']=float(result.fun);coeff={};right=Q(0);cert=[]
        for r,v in enumerate(result.ineqlin.marginals):
            if v>=-1e-8:continue
            weight=Q(float(-v)).limit_denominator(10**7)
            for t in range(mat.indptr[r],mat.indptr[r+1]):
                k=int(mat.indices[t]);coeff[k]=coeff.get(k,Q(0))+weight*int(mat.data[t])
            right+=weight*rhs[r];cert.append({'weight':str(weight),'tag':tags[r]})
        valid=coeff.get(cost,0)<0 and all(v>=0 for k,v in coeff.items() if k!=cost)
        out.update(exact_dual_valid=valid,exact_bound=str(right/coeff[cost]) if valid else None,dual_rows=len(cert))
        payload={**out,'certificate':cert,'floating_payments':{str(state):result.x[4*index[state]:4*index[state]+4].tolist() for state in states}}
        Path(__file__).with_name(f'outside_anonymous_{m}.json').write_text(json.dumps(payload,indent=2)+'\n')
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--m',type=int,default=3);a=ap.parse_args()
    print(json.dumps(solve(a.m),indent=2),flush=True)
