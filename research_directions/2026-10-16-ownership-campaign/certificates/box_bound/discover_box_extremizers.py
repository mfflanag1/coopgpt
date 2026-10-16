#!/usr/bin/env python3
"""Bounded numerical discovery, not a theorem or exhaustive search."""
import sys, json, time
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution
MIX=Path('/private/tmp/coopgpt-ownership-20261016/mixed')
sys.path.insert(0,str(MIX))
from owner_box_reference import box_range_rule

OUT=Path(__file__).parent

def rows_from(x,n,m):
    h=np.array(x[:n*m]).reshape(n,m)
    if h.sum()<1e-10: return None
    h=h/h.sum()
    l=np.array(x[n*m:2*n*m]).reshape(n,m)
    p=np.array(x[2*n*m:])
    return [[float(p[i])]+list(map(float,h[i]))+list(map(float,l[i])) for i in range(n)]

def run(n,m,seed,maxiter=100):
    best=[0,None]
    def obj(x):
        rows=rows_from(x,n,m)
        if rows is None:return 0.
        ans,_,_,_,_,v=box_range_rule(rows)
        if v['F']<1e-7:return 0.
        ratio=sum(ans)/v['F']
        if ratio>best[0]:best[:]=[ratio,rows]
        return -ratio
    bounds=[(0.,1.)]*(n*m)+[(0.,1.5)]*(n*m)+[(0.,1.5)]*n
    start=time.time()
    res=differential_evolution(obj,bounds,seed=seed,popsize=7,maxiter=maxiter,tol=1e-8,polish=True,workers=1)
    rows=best[1];ans,ws,los,ups,K,v=box_range_rule(rows)
    record={'kind':'FLOAT DIAGNOSTIC ONLY','n':n,'m':m,'seed':seed,'nfev':res.nfev,'elapsed':time.time()-start,'ratio':sum(ans)/v['F'],'rows':rows,'payments':ans,'witnesses':ws,'lower':los,'upper':ups,'K':K,'v':v}
    dest=OUT/f'discovery-n{n}-m{m}-s{seed}.json'
    dest.write_text(json.dumps(record,indent=2))
    print(json.dumps({'file':str(dest),'ratio':record['ratio'],'elapsed':record['elapsed'],'rows':rows}),flush=True)

if __name__=='__main__':
    n,m,seed=map(int,sys.argv[1:4]);run(n,m,seed)
