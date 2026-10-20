"""Only budget-positive nodes require efficiency; fixed stored duals only."""
from collections import defaultdict
from fractions import Fraction as Q
from pathlib import Path
import json
import numpy as np
from scipy.optimize import linprog

ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent/'finite_diagnostics'


def check(seed):
    data=json.loads((SOURCE/f'case_{seed}_certificate.json').read_text());case=data['case'];d=case['d'];A=case['A'];pi=list(map(Q,case['pi']))
    b=[[data['owner_states'][i][p[i]] for i in range(4)] for p in data['profiles']]
    def total(k):return tuple(sum(b[k][i][a] for i in range(4)) for a in range(d))
    values={tuple(o['cap']):Q(o['value']) for o in data['oracles']}
    edges=[v for v in data['certificate'] if v['tag'][0]=='out'];nu=defaultdict(Q);nodes=set()
    for v in data['certificate']:
        tag=v['tag'];nodes.add(tag[1])
        if tag[0]=='out':nodes.add(tag[2])
        elif tag[0]=='budget':nu[tag[1]]+=Q(v['weight'])
    nodes=sorted(nodes);index={k:j for j,k in enumerate(nodes)};budget_nodes=sorted(k for k,v in nu.items() if v>0)
    P=len(nodes)*d;nv=P+len(edges);rows=[];rhs=[];tags=[];eq=[];eqrhs=[]
    for k in nodes:
        for e in range(len(pi)):
            rows.append({index[k]*d+a:-Q(A[a][e]) for a in range(d) if A[a][e]});rhs.append(-pi[e]);tags.append(['activity',k,e])
    for k in budget_nodes:
        eq.append({index[k]*d+a:Q(v) for a,v in enumerate(total(k)) if v});eqrhs.append(values[total(k)])
    obj=[Q(0)]*nv
    for j,item in enumerate(edges):
        _,lo,hi,C=item['tag'];delta=tuple(sum(b[hi][i][a]-b[lo][i][a] for i in C) for a in range(d));row={P+j:Q(-1)}
        for i in C:
            for a in range(d):
                v=index[hi]*d+a;row[v]=row.get(v,Q(0))+b[hi][i][a]
                v=index[lo]*d+a;row[v]=row.get(v,Q(0))-b[lo][i][a]
        rows.append({j:v for j,v in row.items() if v});rhs.append(values[delta]);tags.append(['edge',j]);obj[P+j]=Q(item['weight'])
    def matrix(rs):
        out=np.zeros((len(rs),nv))
        for i,row in enumerate(rs):
            for j,v in row.items():out[i,j]=float(v)
        return out
    sol=linprog(list(map(float,obj)),A_ub=matrix(rows),b_ub=list(map(float,rhs)),A_eq=matrix(eq),b_eq=list(map(float,eqrhs)),bounds=(0,None),method='highs')
    if not sol.success:raise RuntimeError(sol.message)
    x=[Q(float(v)).limit_denominator(10**8) for v in sol.x]
    primal_ok=min(x)>=0 and all(sum(v*x[j] for j,v in row.items())<=rb for row,rb in zip(rows,rhs)) and all(sum(v*x[j] for j,v in row.items())==rb for row,rb in zip(eq,eqrhs))
    upper=sum(a*v for a,v in zip(obj,x));weights=[Q(float(-v)).limit_denominator(10**8) for v in sol.ineqlin.marginals];tau=[Q(float(-v)).limit_denominator(10**8) for v in sol.eqlin.marginals]
    residual=list(obj)
    for row,w in zip(rows,weights):
        for j,v in row.items():residual[j]+=w*v
    for row,w in zip(eq,tau):
        for j,v in row.items():residual[j]+=w*v
    lower=-sum(w*rb for w,rb in zip(weights,rhs))-sum(w*rb for w,rb in zip(tau,eqrhs))
    dual_ok=min(weights)>=0 and min(residual)>=0
    status='EXACT ZERO WITNESS' if primal_ok and upper==0 else ('EXACT POSITIVE OPTIMUM' if primal_ok and dual_ok and upper==lower and lower>0 else 'UNVERIFIED FLOAT')
    result=dict(seed=seed,status=status,profiles=len(nodes),budget_profiles=budget_nodes,comparison_rows=len(edges),float_minimum=sol.fun,exact_upper=str(upper) if primal_ok else None,exact_lower=str(lower) if dual_ok else None,
        prices={str(k):list(map(str,x[index[k]*d:(index[k]+1)*d])) for k in nodes},obstruction=[dict(tag=t,weight=str(w)) for t,w in zip(tags,weights) if w],efficiency_multipliers={str(k):str(w) for k,w in zip(budget_nodes,tau) if w})
    (ROOT/f'case_{seed}.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('seed','status','exact_upper','exact_lower')}),flush=True)
    return result


if __name__=='__main__':
    records=[check(15)]+[check(s) for s in range(10,66) if s!=15]
    (ROOT/'results.json').write_text(json.dumps(records,indent=2)+'\n')
