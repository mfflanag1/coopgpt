"""Minimize negative defects for the fixed exact seed35 certificate."""
from fractions import Fraction as Q
from pathlib import Path
import json
import numpy as np
from scipy.optimize import linprog


ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/'case_35_certificate.json').read_text());case=data['case'];d=case['d'];A=case['A'];pi=list(map(Q,case['pi']))
states=data['owner_states'];profiles=data['profiles']
b=[[states[i][p[i]] for i in range(4)] for p in profiles]
def total(k):return tuple(sum(b[k][i][a] for i in range(4)) for a in range(d))
values={tuple(v['cap']):Q(v['value']) for v in data['oracles']}
edges=[v for v in data['certificate'] if v['tag'][0]=='out']
nodes=sorted({k for e in edges for k in e['tag'][1:3]});index={k:j for j,k in enumerate(nodes)}
P=len(nodes)*d;nv=P+len(edges);rows=[];rhs=[];eq=[];eqrhs=[]
for k in nodes:
    for e in range(len(pi)):
        row=np.zeros(nv)
        for a in range(d):row[index[k]*d+a]=-A[a][e]
        rows.append(row);rhs.append(-float(pi[e]))
    row=np.zeros(nv)
    for a,cap in enumerate(total(k)):row[index[k]*d+a]=cap
    eq.append(row);eqrhs.append(float(values[total(k)]))
obj=np.zeros(nv)
for j,item in enumerate(edges):
    _,lo,hi,C=item['tag'];delta=tuple(sum(b[hi][i][a]-b[lo][i][a] for i in C) for a in range(d));de=values[delta]
    row=np.zeros(nv)
    for i in C:
        for a in range(d):row[index[hi]*d+a]+=b[hi][i][a];row[index[lo]*d+a]-=b[lo][i][a]
    row[P+j]=-1;rows.append(row);rhs.append(float(de));obj[P+j]=float(Q(item['weight']))
sol=linprog(obj,A_ub=rows,b_ub=rhs,A_eq=eq,b_eq=eqrhs,bounds=(0,None),method='highs')
if not sol.success:raise RuntimeError(sol.message)
p={k:[Q(float(v)).limit_denominator(10**6) for v in sol.x[index[k]*d:(index[k]+1)*d]] for k in nodes}
for k in nodes:
    assert min(p[k])>=0
    assert sum(p[k][a]*total(k)[a] for a in range(d))==values[total(k)]
    assert all(sum(A[a][e]*p[k][a] for a in range(d))>=pi[e] for e in range(len(pi)))
pos=neg=Q(0);defects=[]
for item in edges:
    _,lo,hi,C=item['tag'];delta=tuple(sum(b[hi][i][a]-b[lo][i][a] for i in C) for a in range(d))
    defect=sum(p[lo][a]*b[lo][i][a]-p[hi][a]*b[hi][i][a] for i in C for a in range(d))+values[delta]
    w=Q(item['weight']);pos+=w*max(defect,0);neg+=w*max(-defect,0)
    defects.append(dict(tag=item['tag'],weight=str(w),defect=str(defect)))
result=dict(seed=35,solver_minimum_negative_float=sol.fun,exact_negative_of_selected_prices=str(neg),exact_positive_of_selected_prices=str(pos),exact_all_defects_nonnegative=all(Q(v['defect'])>=0 for v in defects),prices={str(k):list(map(str,v)) for k,v in p.items()},defects=defects,
    scope='Exact feasible price witnesses are checked. A positive float optimum alone would not prove unavoidable cancellation; exact zero does prove removable negative terms.')
(ROOT/'price_reselection.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('prices','defects')},indent=2))
