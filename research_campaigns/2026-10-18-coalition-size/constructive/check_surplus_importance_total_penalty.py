from fractions import Fraction as R
from itertools import combinations
import json
from pathlib import Path
base=Path(__file__).resolve().parent
low=[(2,4,3),(3,3,0),(4,1,4)]
high=[(2,6,3),(3,3,0),(4,1,4)]
def worth(b,S): return min(sum(b[i][j] for i in S) for j in range(3))
def data(b):
    V=worth(b,range(3)); f=list(map(min,b)); g=[min(V,max(x))-a for x,a in zip(b,f)]
    return V,f,g,[min(R(V,a*a),R(2,a)) for a in g]
def feasible(b,y):
    return all(sum(y[i] for i in S)>=worth(b,S) for k in range(1,4) for S in combinations(range(3),k))
Vl,fl,gl,wl=data(low); Vh,fh,gh,wh=data(high)
assert (Vl,fl,gl,wl)==(7,[2,0,1],[2,3,3],[R(1),R(2,3),R(2,3)])
assert (Vh,fh,gh,wh)==(7,[2,0,1],[4,3,3],[R(7,16),R(2,3),R(2,3)])
zl=[R(1),R(3,2),R(3,2)]; yl=[z+f for z,f in zip(zl,fl)]
assert [2*w*z for w,z in zip(wl,zl)]==[2,2,2]
assert feasible(low,yl)
records=[]
for wh,qbar,mults in [([R(7,16),R(2,3),R(2,3)],R(96,85),[R(7,8),R(11,24),R(4,3)]),([R(1,4),R(1,3),R(1,3)],R(12,11),[R(1,2),R(1,6),R(2,3)])]:
    zh=[qbar,qbar,3-qbar]; yh=[z+f for z,f in zip(zh,fh)]
    assert feasible(high,yh)
    assert (wh[0]+wh[1]+wh[2])*qbar==3*wh[2]
    boundary=[R(1),R(1),R(2)]
    grad=[2*w*z for w,z in zip(wh,boundary)]
    a,b,c=mults
    assert grad==[a,a+b,a+b+c] and min(mults)>=0
    assert feasible(high,[z+f for z,f in zip(boundary,fh)])
    loss=yl[0]+yl[1]-yh[0]-yh[1]
    assert loss>0
    records.append({'weights':list(map(str,wh)),'q_max':str(qbar),'high_payment':list(map(str,yh)),'minimum_pair_loss':str(loss),'boundary_KKT_multipliers':list(map(str,mults))})
result={'status':'PASS','low_payment':list(map(str,yl)),'certificates':records,'scope':'Exact algebra and all subset coverage; arbitrary nondecreasing penalty conclusion uses the written region proof.'}
(base/'check_surplus_importance_total_penalty.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
