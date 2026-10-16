"""Propose a rational feasible point of a finite LP relaxation; not a game."""
from pathlib import Path
from fractions import Fraction as F
import importlib.util,json
import numpy as np
from scipy.optimize import linprog
BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('replay',BASE/'verify_high_S_certificate.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
S=F(47,25);delta=F(1,125);vv=F(1,30)
rows=v.reconstruct(S,S,delta,delta,True)
q=v.negative_exp_polynomial(S-1,24)/2
beta=(1/v.negative_exp_polynomial(v.K_HIGH,25)-2)/(1-v.c_high)
for ss in v.CAP_TANGENTS:
 t=v.negative_exp_polynomial(1-ss,24)/2
 con=1-v.c_low+delta/ss;coef=(t-v.c_low)/ss-1
 rows.append(([-q*beta*v.C_BAR*coef,-F(3,4)*q,-2*q,F(3,4)*q,F(1)],2*q*(S-1)+q*beta*v.C_BAR*con))
b=v.negative_exp_polynomial(S-1+delta,25)/2
objective=[F(0),F(0),-b,b*F(4,15)*v.K_HIGH**2*vv**2,F(1)]
aa=np.array([list(map(float,a))for a,r in rows]);bb=np.array([float(r)-1e-9 for a,r in rows])
lp=linprog(-np.array(objective,dtype=float),A_ub=aa,b_ub=bb,bounds=[(0,None),(0,None),(float(vv),float(vv)),(0,None),(0,None)],method='highs',options={'primal_feasibility_tolerance':1e-10,'dual_feasibility_tolerance':1e-10})
v.require(lp.success,'Strict feasible LP proposal')
x=[F(str(round(float(t),12)))for t in lp.x];x[2]=vv
slacks=[r-sum(ai*xi for ai,xi in zip(a,x))for a,r in rows]
v.require(min(slacks)>0,'Exact strict feasibility after rationalization')
value=1+sum(a*z for a,z in zip(objective,x))
v.require(value>F(8,5),'Exact objective exceeds 8/5')
out={'scope':'Finite rational supporting-row relaxation only; NOT an actual profile or a theorem lower bound','S':str(S),'delta':str(delta),'v':str(vv),'point':list(map(str,x)),'rows':len(rows),'inverse_tangents':list(map(str,v.CAP_TANGENTS)),'objective':list(map(str,objective)),'objective_value':str(value),'objective_display':float(value),'minimum_slack':str(min(slacks))}
(BASE/'finite_support_obstruction.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
