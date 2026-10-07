"""Heuristic QMC/grid falsification of frozen-coordinate deletion majorant r; no certificate claims."""
import importlib.util
from pathlib import Path
from fractions import Fraction as Q
import json
import numpy as np
from scipy.stats import qmc

helper=Path('/tmp/coopgt_one_sided_scan.py')
if not helper.exists():helper=Path(__file__).with_name('one_sided_scan.py')
spec=importlib.util.spec_from_file_location('s',helper)
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)

def evaluate(row,power=12):
    n=row['n'];es=[tuple(e) for e in row['edges']];c=list(map(Q,row['capacities']))
    m=len(es);cs=s.fibonacci_cuts(n,es) if row['label'].startswith('fibonacci') else s.v.cutsets(n,es)
    D=s.effective(n,es,c);T=s.v.maxflow(n,es,c)
    d=np.array(D,float)/float(T)
    mat=np.array([[bool(C>>e&1) for e in range(m)] for C in cs],float)
    U=qmc.Sobol(m,scramble=True,seed=71029).random_base2(power)
    def coordinate(e,dd):
        scores=(U*dd)@mat.T;inc=mat[:,e]>0
        A=scores[:,inc].min(axis=1)-dd[e]*U[:,e]
        B=scores[:,~inc].min(axis=1) if np.any(~inc) else np.full(len(U),np.inf)
        a=np.clip(B-A,0,dd[e])
        return float(np.mean(2*a-a*a/dd[e])) if dd[e]>0 else 0.0
    z=[coordinate(e,d) for e in range(m)];yy=z.copy();at=[float(x) for x in d]
    trials=0
    for e in range(m):
        if not d[e]:continue
        co=np.any(mat[mat[:,e]>0]>0,axis=0);co[e]=False
        ce=c.copy();ce[e]=Q(0)
        d0=np.array(s.effective(n,es,ce),float)/float(T)
        # If every co-cut partner is fixed, conditional formula is monotone.
        if np.all(np.abs(d0[co]-d[co])<1e-14):continue
        grid=sorted(set(np.linspace(0,d[e],17).tolist()+np.maximum(0,d-d0).tolist()))
        for t in grid:
            if not 0<t<d[e]:continue
            dt=np.minimum(d,d0+t)
            val=coordinate(e,dt);trials+=1
            if val>yy[e]:yy[e]=val;at[e]=t
    return dict(label=row['label'],n=n,m=m,K=len(cs),T=str(T),edges=es,
                capacities=list(map(str,c)),sum_r=sum(z),sum_grid_own_envelope_r=sum(yy),
                estimated_excess=sum(yy)-sum(z),max_coordinate_gain=max(np.array(yy)-np.array(z)),
                r=z,grid_own_envelope_r=yy,normalized_best_reports=at,grid_trials=trials,
                sobol_power=power,seed=71029)

def main():
    data=json.loads(Path('/tmp/coopgt_one_sided_scan.json').read_text())['results']
    # Independent structural classes plus small profiles with largest hybrid gains.
    chosen=data[:40]+[r for r in data[40:] if r['label']!='random']
    rows=[]
    for j,row in enumerate(chosen):
        ans=evaluate(row);rows.append(ans)
        print(json.dumps({'done':j+1,'cases':len(chosen),'label':row['label'],
                          'excess':ans['estimated_excess'],'max_total':max(x['sum_grid_own_envelope_r'] for x in rows)}),flush=True)
        Path('/tmp/coopgt_frozen_marginal_scan.json').write_text(json.dumps(
            {'status':'HEURISTIC QMC AND FINITE REPORT GRID ONLY','complete':j+1==len(chosen),
             'rows':rows},indent=2)+'\n')

if __name__=='__main__':main()
