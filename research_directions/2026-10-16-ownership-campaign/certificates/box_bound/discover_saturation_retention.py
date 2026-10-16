#!/usr/bin/env python3
"""Bounded diagnostic for one-owner response from local capped ratio exactly2."""
import math,json
from pathlib import Path
from scipy.optimize import differential_evolution
c=.5/math.e;C=1+c

def value(v,detail=False):
 x,u,f,g=v
 owncap=f*min(x,u)
 othermin=u+min(1-x,u);othermax=2-x
 others=othermin+g*(othermax-othermin)
 rho=(owncap+others)/u;q=.5*math.exp(1-rho)
 short=1. if q<c else 1-u
 full=(1-c)*short+c*x
 reduced=(1-q)*(short-(1-u))+q*owncap
 total=u+q*(owncap+others-u)
 loss=C-total
 ratio=(full-reduced)/loss if loss>1e-10 else 100.
 if detail:return dict(ratio=ratio,x=x,u=u,owncap=owncap,othercap=others,rho=rho,q=q,own_short=short,full=full,reduced=reduced,total=total)
 return ratio
res=differential_evolution(value,[(0,1),(.0001,.99999),(0,1),(0,1)],seed=161099,popsize=15,maxiter=300,tol=1e-10,polish=True)
out=value(res.x,True);out['lambda_derivative']=(1-3*c)/C;out['scope']='FLOAT DISCOVERY ONLY; no retained-response theorem is inferred';Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
