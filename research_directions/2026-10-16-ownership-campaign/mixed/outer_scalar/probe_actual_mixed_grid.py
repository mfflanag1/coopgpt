"""Falsification-only search, not a proof. Pure fragmented hardware; two power owners."""
import numpy as np
from scipy.optimize import differential_evolution
import json
from pathlib import Path

def local(b,c):
    L=b+c
    if L>=1:
        db=min(b,1.);dc=min(c,1.);q=.5*np.exp(1-db-dc)
        return 1-q,q*db,q*dc
    if L<=0:return 0.,0.,0.
    q=.5*np.exp(max(-745,1-1/L))
    return q,(1-q)*b,(1-q)*c

def outer(b,c,p):
    zh,zb,zc=local(b,c);total=zh+zb+zc+p
    if total>=1:
        db=min(p+zb,1.);S=zh+db+zc;q=.5*np.exp(1-S)
        return 1-q*(1-zh),q*db,q*zc
    if total<=0:return 0.,0.,0.
    q=.5*np.exp(max(-745,1-1/total))
    return q,(1-q)*(p+zb),(1-q)*zc

def objective(x):
    p,b,c,ub,uc=x
    if p+min(1,b+c)<1:return 1-p-min(1,b+c)
    raw=outer(b,c,p)
    return -(raw[0]+max(raw[1],outer(b*ub,c,p)[1])+max(raw[2],outer(b,c*uc,p)[2]))
results=[]
for seed in [123,677,9001]:
    r=differential_evolution(objective,[(0,2),(0,3),(0,3),(0,1),(0,1)],seed=seed,popsize=20,maxiter=400,tol=1e-9,polish=True)
    results.append({'value':-float(r.fun),'x':r.x.tolist(),'raw':list(outer(*r.x[[1,2,0]]))})
print(json.dumps(results,indent=2))
Path(__file__).with_suffix('.json').write_text(json.dumps(results,indent=2)+'\n')
