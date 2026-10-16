#!/usr/bin/env python3
"""Bounded numerical discovery with explicit aggregate scarcity parameters."""
import sys, json, time
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution
sys.path.insert(0,'/private/tmp/coopgpt-ownership-20261016/mixed')
from owner_box_reference import box_range_rule
OUT=Path(__file__).parent

def rows_from(x,n,m):
    h=np.array(x[:n*m]).reshape(n,m);l=np.array(x[n*m:2*n*m]).reshape(n,m);p=np.array(x[2*n*m:2*n*m+n])
    h=h/max(h.sum(),1e-99);l=l/max(l.sum(),1e-99)*x[-2];p=p/max(p.sum(),1e-99)*x[-1]
    return [[float(p[i])]+list(map(float,h[i]))+list(map(float,l[i])) for i in range(n)]

def run(n,m,seed,maxiter=200):
    best=[0,None];calls=[0]
    def obj(x):
        calls[0]+=1;rows=rows_from(x,n,m)
        ans,_,_,_,_,v=box_range_rule(rows)
        if v['F']<1e-7:return 0.
        ratio=sum(ans)/v['F']
        if ratio>best[0]:best[:]=[ratio,rows]
        return -ratio
    bounds=[(0.,1.)]*(2*n*m+n)+[(0.,2.),(0.,1.5)]
    start=time.time();res=differential_evolution(obj,bounds,seed=seed,popsize=8,maxiter=maxiter,tol=1e-9,polish=True,workers=1)
    rows=best[1];ans,ws,los,ups,K,v=box_range_rule(rows)
    record={'kind':'FLOAT DIAGNOSTIC ONLY','n':n,'m':m,'seed':seed,'nfev':calls[0],'elapsed':time.time()-start,'ratio':sum(ans)/v['F'],'rows':rows,'payments':ans,'witnesses':ws,'lower':los,'upper':ups,'K':K,'v':v}
    dest=OUT/f'normalized-n{n}-m{m}-s{seed}.json';dest.write_text(json.dumps(record,indent=2));print(json.dumps(record),flush=True)
if __name__=='__main__':run(*map(int,sys.argv[1:4]))
