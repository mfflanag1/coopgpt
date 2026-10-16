#!/usr/bin/env python3
"""Diagnostic: pure-hardware recipients plus one local-power owner, P=0."""
import sys,json,time
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution
sys.path.insert(0,'/private/tmp/coopgpt-ownership-20261016/mixed')
from owner_box_reference import box_range_rule
OUT=Path(__file__).parent

def run(k,m,seed):
 def rows_from(x):
  h=np.array(x[:k*m]).reshape(k,m);h=h/max(h.sum(),1e-99)
  l=np.array(x[k*m:]);rows=[[0.]+list(map(float,r))+[0.]*m for r in h]
  return rows+[[0.]+[0.]*m+list(map(float,l))]
 def obj(x):
  ans,_,_,_,_,v=box_range_rule(rows_from(x))
  return -sum(ans)/v['F'] if v['F']>1e-7 else 0.
 start=time.time();res=differential_evolution(obj,[(0.,1.)]*(k*m)+[(0.,.8)]*m,seed=seed,popsize=10,maxiter=650,tol=1e-10,polish=True)
 rows=rows_from(res.x);ans,ws,los,ups,K,v=box_range_rule(rows)
 r={'kind':'FLOAT DIAGNOSTIC ONLY','k':k,'m':m,'seed':seed,'nfev':res.nfev,'elapsed':time.time()-start,'ratio':sum(ans)/v['F'],'rows':rows,'payments':ans,'witnesses':ws,'lower':los,'upper':ups,'K':K,'v':v}
 dest=OUT/f'star-k{k}-m{m}-s{seed}.json';dest.write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
if __name__=='__main__':run(*map(int,sys.argv[1:4]))
