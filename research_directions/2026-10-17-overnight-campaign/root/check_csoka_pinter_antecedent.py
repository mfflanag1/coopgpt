from fractions import Fraction as F
import json
from pathlib import Path
X=[[0,100,0,100,100],[100,100,F(3,2),100,F(3,2)],[1,1,1,100,100],[0,0,100,0,100],[0,0,100,100,0],[3,100,3,3,100],[0,100,F(3,2),100,F(3,2)],[0,100,100,0,0],[100,0,0,0,100],[100,0,F(3,2),100,F(3,2)],[100,3,100,3,3],[100,100,F(3,2),0,F(3,2)],[3,0,3,3,100],[0,0,3,100,0],[2,5,100,3,2],[3,100,3,3,0],[100,3,0,3,3],[3,0,0,6,3],[0,4,2,7,1]]
Y=[r[:] for r in X];Y[-1][1]-=3
profiles=[('X',X,[3,0,0,6,3]),('Y',Y,[0,1,2,7,1])]
def values(rows): return {m:min(sum(F(row[i]) for i in range(5) if m>>i&1) for row in rows) for m in range(1,32)}
if __name__=='__main__':
 from scipy.optimize import linprog
 evidence={}
 for name,rows,candidate in profiles:
  v=values(rows);a=[[-int(m>>i&1) for i in range(5)] for m in range(1,31)];b=[-float(v[m]) for m in range(1,31)]
  assert sum(candidate)==v[31]
  assert all(sum(candidate[i] for i in range(5) if m>>i&1)>=w for m,w in v.items())
  # Discover then verify exact dual witnesses for min and max of owner's payment.
  bounds=[]
  for sign in [-1,1]:
   c=[0,sign,0,0,0]
   r=linprog(c,A_ub=a,b_ub=b,A_eq=[[1]*5],b_eq=[float(v[31])],bounds=[(None,None)]*5,method='highs')
   assert r.success
   du=[F(float(t)).limit_denominator(100000) for t in r.ineqlin.marginals]
   de=F(float(r.eqlin.marginals[0])).limit_denominator(100000)
   assert all(t<=0 for t in du)
   assert all(sum(du[j]*a[j][i] for j in range(30))+de==c[i] for i in range(5))
   val=sum(du[j]*(-v[j+1]) for j in range(30))+de*v[31]
   assert val==sign*candidate[1]
   bounds.append({'sign':sign,'grand_multiplier':str(de),'coalition_multipliers':{str(j+1):str(t) for j,t in enumerate(du) if t},'bound':str(val)})
  evidence[name]={'grand_value':str(v[31]),'candidate':candidate,'owner2_payment':candidate[1],'exact_dual_certificates':bounds}
 out=Path(__file__).with_suffix('.json');out.write_text(json.dumps(evidence,indent=2)+'\n')
 print(json.dumps(evidence,indent=2))
