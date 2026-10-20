"""Exact payment witnesses for seed15 and its five-profile price-sign regions."""
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT.parent/'finite_diagnostics/case_15_certificate.json').read_text())
PROFILES=DATA['profiles'];STATES=DATA['owner_states'];D=4
B=[[tuple(STATES[i][p[i]]) for i in range(4)] for p in PROFILES]
VALUES={tuple(o['cap']):Q(o['value']) for o in DATA['oracles']}
COALS=[tuple(c) for n in range(1,5) for c in combinations(range(4),n)]


def cap(k,C):return tuple(sum(B[k][i][a] for i in C) for a in range(4))


def rows_for(ids,prices=None):
    index={k:j for j,k in enumerate(ids)};K=4*len(ids);rows=[];rhs=[];tags=[]
    for k in ids:
        rows.append({**{4*index[k]+i:Q(1) for i in range(4)},K:-VALUES[cap(k,range(4))]});rhs.append(Q(0));tags.append(['budget',k])
        for C in COALS:
            rows.append({4*index[k]+i:Q(-1) for i in C});rhs.append(-VALUES[cap(k,C)]);tags.append(['cover',k,list(C)])
    for lo in ids:
        for hi in ids:
            if hi==lo:continue
            changed={i for i in range(4) if B[lo][i]!=B[hi][i]}
            if len(changed)>2 or any(B[lo][i][a]>B[hi][i][a] for i in changed for a in range(4)):continue
            for C in COALS:
                if len(C)>2 or not changed.issubset(C):continue
                delta=tuple(sum(B[hi][i][a]-B[lo][i][a] for i in C) for a in range(4));de=VALUES[delta]
                if prices is not None:
                    defect=sum(prices[lo][a]*B[lo][i][a]-prices[hi][a]*B[hi][i][a] for i in C for a in range(4))+de
                    if defect<0:continue
                row={4*index[lo]+i:Q(1) for i in C};row.update({4*index[hi]+i:Q(-1) for i in C})
                rows.append(row);rhs.append(-de);tags.append(['out',lo,hi,list(C)])
    return K,rows,rhs,tags


def find(ids,prices=None):
    import numpy as np
    from scipy.sparse import coo_matrix
    from scipy.optimize import linprog
    K,rows,rhs,tags=rows_for(ids,prices);rr=[];cc=[];dd=[]
    for i,row in enumerate(rows):
        for j,v in row.items():rr.append(i);cc.append(j);dd.append(float(v))
    mat=coo_matrix((dd,(rr,cc)),shape=(len(rows),K+1)).tocsr();obj=np.zeros(K+1);obj[K]=1
    sol=linprog(obj,A_ub=mat,b_ub=list(map(float,rhs)),bounds=(0,None),method='highs')
    if not sol.success:raise RuntimeError(sol.message)
    candidate=[Q(float(v)).limit_denominator(10**8) for v in sol.x]
    if min(candidate)<0 or any(sum(v*candidate[j] for j,v in row.items())>rb for row,rb in zip(rows,rhs)):raise ValueError('rational primal failed')
    return dict(profiles=ids,exact_upper=str(candidate[K]),payments=list(map(str,candidate[:-1])),rows=len(rows),comparison_rows=sum(t[0]=='out' for t in tags),prices=None if prices is None else {str(k):list(map(str,p)) for k,p in prices.items()})


def price_regions():
    def low(t):return (t,Q(5,2)-t,Q(0),max(t,1-2*t,Q(0)))
    for t,s in product((Q(0),Q(5,2)),(Q(0),Q(2,3))):
        yield dict(t=str(t),s=str(s),prices={37:low(t),133:low(s),101:(Q(5,2),Q(0),Q(0),Q(5,2)),149:(Q(1,3),Q(13,6),Q(0),Q(1,3)),165:(Q(0),Q(5,2),Q(0),Q(1))})


if __name__=='__main__':
    full=find(list(range(256)));five=find([37,101,133,149,165]);regions=[]
    for region in price_regions():
        result=find([37,101,133,149,165],region['prices']);result.update(t=region['t'],s=region['s']);regions.append(result)
    output=dict(full_lattice=full,five_profiles=five,nonnegative_price_regions=regions)
    (ROOT/'payment_primal.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(dict(full_upper=full['exact_upper'],five_upper=five['exact_upper'],region_uppers=[r['exact_upper'] for r in regions]),indent=2))
