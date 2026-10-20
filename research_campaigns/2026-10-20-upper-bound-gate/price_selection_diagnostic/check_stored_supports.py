"""Price-selection phase I on the 56 previously stored dual supports only."""
from fractions import Fraction as Q
from pathlib import Path
import json
import numpy as np
from scipy.optimize import linprog

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'finite_diagnostics'


def check(seed):
    data=json.loads((SOURCE/f'case_{seed}_certificate.json').read_text());case=data['case'];d=case['d'];A=case['A'];pi=list(map(Q,case['pi']))
    states=data['owner_states'];profiles=data['profiles']
    b=[[states[i][p[i]] for i in range(4)] for p in profiles]
    def total(k):return tuple(sum(b[k][i][a] for i in range(4)) for a in range(d))
    values={tuple(v['cap']):Q(v['value']) for v in data['oracles']}
    edges=[v for v in data['certificate'] if v['tag'][0]=='out']
    if not edges:return dict(seed=seed,edges=0,status='NO COMPARISON SUPPORT')
    nodes=sorted({k for e in edges for k in e['tag'][1:3]});index={k:j for j,k in enumerate(nodes)}
    P=len(nodes)*d;nv=P+len(edges);rows=[];rhs=[];tags=[];eq=[];eqrhs=[]
    for k in nodes:
        for e in range(len(pi)):
            row={index[k]*d+a:-Q(A[a][e]) for a in range(d) if A[a][e]}
            rows.append(row);rhs.append(-pi[e]);tags.append(['activity',k,e])
        eq.append({index[k]*d+a:Q(v) for a,v in enumerate(total(k)) if v});eqrhs.append(values[total(k)])
    obj=[Q(0)]*nv
    for j,item in enumerate(edges):
        _,lo,hi,C=item['tag'];delta=tuple(sum(b[hi][i][a]-b[lo][i][a] for i in C) for a in range(d));de=values[delta]
        row={P+j:Q(-1)}
        for i in C:
            for a in range(d):
                jj=index[hi]*d+a;row[jj]=row.get(jj,Q(0))+b[hi][i][a]
                jj=index[lo]*d+a;row[jj]=row.get(jj,Q(0))-b[lo][i][a]
        rows.append({j:v for j,v in row.items() if v});rhs.append(de);tags.append(['edge',j]);obj[P+j]=Q(item['weight'])
    def dense(rs):
        out=np.zeros((len(rs),nv))
        for i,row in enumerate(rs):
            for j,v in row.items():out[i,j]=float(v)
        return out
    sol=linprog(list(map(float,obj)),A_ub=dense(rows),b_ub=list(map(float,rhs)),A_eq=dense(eq),b_eq=list(map(float,eqrhs)),bounds=(0,None),method='highs')
    if not sol.success:raise RuntimeError(sol.message)
    primal=[Q(float(v)).limit_denominator(10**8) for v in sol.x]
    primal_ok=min(primal)>=0 and all(sum(row[j]*primal[j] for j in row)<=rb for row,rb in zip(rows,rhs)) and all(sum(row[j]*primal[j] for j in row)==rb for row,rb in zip(eq,eqrhs))
    upper=sum(c*x for c,x in zip(obj,primal))
    weights=[Q(float(-v)).limit_denominator(10**8) for v in sol.ineqlin.marginals]
    tau=[Q(float(-v)).limit_denominator(10**8) for v in sol.eqlin.marginals]
    residual=list(obj)
    for row,w in zip(rows,weights):
        for j,v in row.items():residual[j]+=w*v
    for row,w in zip(eq,tau):
        for j,v in row.items():residual[j]+=w*v
    lower=-sum(w*rb for w,rb in zip(weights,rhs))-sum(w*rb for w,rb in zip(tau,eqrhs))
    dual_ok=min(weights)>=0 and min(residual)>=0
    status='EXACT ZERO WITNESS' if primal_ok and upper==0 else ('EXACT POSITIVE OPTIMUM' if primal_ok and dual_ok and upper==lower and lower>0 else 'UNVERIFIED FLOAT')
    result=dict(seed=seed,edges=len(edges),profiles=len(nodes),status=status,float_minimum=sol.fun,exact_upper=str(upper) if primal_ok else None,exact_lower=str(lower) if dual_ok else None,
        prices={str(k):list(map(str,primal[index[k]*d:(index[k]+1)*d])) for k in nodes},
        obstruction=[dict(tag=t,weight=str(w)) for t,w in zip(tags,weights) if w],efficiency_multipliers={str(k):str(w) for k,w in zip(nodes,tau) if w},
        scope='Exact phase-I upper and dual lower for the fixed stored comparison support; optimality of the original payment dual is separate.')
    (ROOT/f'case_{seed}.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('seed','status','float_minimum','exact_lower','exact_upper')}),flush=True)
    return result


if __name__=='__main__':
    results=[check(seed) for seed in range(10,66)]
    (ROOT/'results.json').write_text(json.dumps(results,indent=2)+'\n')
