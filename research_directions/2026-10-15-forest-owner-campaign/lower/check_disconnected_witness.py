from fractions import Fraction as Q
from flow_oracle import value
from itertools import product
import json
p=[(0,1,1,1,1,1,1,0),(0,1,1,2,1,1,1,2),(2,1,1,1,2,1,1,0)]
y=[tuple(map(Q,['1/2','1','1','1/2'])),tuple(map(Q,['3/4','1/4','7/4','1/2'])),tuple(map(Q,['1/2','7/4','1/4','3/4']))]
e=[(j,j+1,1) for j in range(7)]
def require(t,m):
    if not t:raise RuntimeError(m)
def val(k,mask):return value(tuple(p[k][r] if mask>>(r%4)&1 else 0 for r in range(8)),e)
for k in range(3):
    require(val(k,15)==3,'grand value')
    for mask in range(1,16):require(sum(y[k][i] for i in range(4) if mask>>i&1)>=val(k,mask),'coverage')
    require(sum(y[k])<=Q(13,12)*3,'budget')
require(y[0][3]<=y[1][3] and y[0][0]<=y[2][0],'incentives')
require(val(0,9)==1,'baseline AD')
for k,expected in [(1,{3:1,6:2,13:3}),(2,{6:2,11:3,12:1})]:
    for mask,target in expected.items():require(val(k,mask)==target,'coalition worth')
# Exact weighted sum: budget U,V weight2; six U,V coalitions weight1;
# baseline AD weight1; two direct own transitions weight1.
rows=[]
def add(coef,rhs):rows.append((coef,Q(rhs)))
for k in (1,2):add({**{4*k+i:2 for i in range(4)},12:-6},0)
for k,masks in [(1,[3,6,13]),(2,[6,11,12]),(0,[9])]:
    for mask in masks:add({4*k+i:-1 for i in range(4) if mask>>i&1},-val(k,mask))
add({3:1,7:-1},0);add({0:1,8:-1},0)
combo={};rhs=Q(0)
for row,b in rows:
    rhs+=b
    for i,a in row.items():combo[i]=combo.get(i,Q(0))+a
require(all(a==0 for i,a in combo.items() if i!=12),'payment cancellation')
require(combo[12]==-12 and rhs==-13,'dual inequality')
print(json.dumps(dict(status='PASS',exact_finite_optimum='13/12',profiles=3,coalition_checks=45,dual_constraints=len(rows),oracle='exact max-profit flow',identity='-12 C <= -13')))
