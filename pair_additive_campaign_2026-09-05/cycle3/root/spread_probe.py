"""Bounded diagnostic of a candidate within-sector spread lemma.

Floating-point discovery only. Reads existing records; does not generate games.
"""
import json
from pathlib import Path
from itertools import product
import numpy as np
from scipy.optimize import linprog

ROOT=Path(__file__).resolve().parent
_adjacent_campaign=Path(__file__).resolve().parents[2]
CAM=(_adjacent_campaign if (_adjacent_campaign/'experiment'/'screen_records.json').is_file()
     else Path('/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/pair_additive_campaign_2026-09-05'))

def probe(rec):
    m=rec['m']; n=3*m
    A,B,C=(np.array(rec[k],dtype=float) for k in ('A','B','C'))
    rows=[]; rhs=[]
    for i,j,k in product(range(m),repeat=3):
        r=np.zeros(n); r[[i,m+j,2*m+k]]=-1
        rows.append(r); rhs.append(-A[i,j]-B[i,k]-C[j,k])
    best=(0,None,None,None)
    for i in range(n):
        for j in range(i//m*m,(i//m+1)*m):
            if i==j: continue
            obj=np.zeros(n); obj[i]=-1; obj[j]=1
            opt=linprog(obj,A_ub=rows,b_ub=rhs,A_eq=[np.ones(n)],b_eq=[rec['T']],bounds=(0,None),method='highs')
            if not opt.success: raise RuntimeError(opt.message)
            spread=-opt.fun
            val=spread/rec['x'][i] if rec['x'][i]>1e-8 else (float('inf') if spread>1e-7 else 0)
            if val>best[0]: best=(val,i,j,opt.x.tolist())
    return dict(label=rec['label'],spread_over_x=best[0],target=best[1],comparison=best[2],witness=best[3])

if __name__=='__main__':
    records=json.loads((CAM/'experiment/screen_records.json').read_text())
    eligible=[r for r in records if r['status']=='nonempty_core_float']
    # Explicit cap: first64 eligible archived records in their saved order.
    selected=eligible[:64]
    out=[]
    for r in selected:
        row=probe(r); out.append(row)
        if row['spread_over_x']>3+1e-7:
            (ROOT/'spread_candidate.json').write_text(json.dumps(dict(record=r,probe=row),indent=2)+'\n')
            break
    report=dict(evidence='floating-point diagnostic; exactification required',candidate_lemma='max_y(y_i-min_same_sector(y)) <= 3*x_i',eligible_archive_count=len(eligible),cap=64,completed=len(out),results=out)
    (ROOT/'spread_probe.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(completed=len(out),max_spread_over_x=max(v['spread_over_x'] for v in out),violation=any(v['spread_over_x']>3+1e-7 for v in out))))
    # Recorded protocol amendment: the first gate happened to contain only
    # m2 records, so inspect all already-generated eligible m3 records.
    selected_m3=[r for r in eligible if r['m']==3]
    out_m3=[]
    for rec in selected_m3:
        row=probe(rec);out_m3.append(row)
        if row['spread_over_x']>3+1e-7:
            (ROOT/'spread_candidate.json').write_text(json.dumps(dict(record=rec,probe=row),indent=2)+'\n')
            break
    (ROOT/'spread_probe_m3.json').write_text(json.dumps(dict(protocol_amendment='First64 archived eligible records were all m2; inspect all78 previously generated m3 records as a separate diagnostic, with no new games.',cap=len(selected_m3),completed=len(out_m3),results=out_m3),indent=2)+'\n')
    # The tested stronger conjecture has subsequently been exactly refuted by
    # the finite example. These earlier clean cells are diagnostic history.
    print(json.dumps(dict(m3_completed=len(out_m3),max_spread_over_x=max(v['spread_over_x'] for v in out_m3),subsequent_status='conjecture exactly refuted; see FINITE_ATTAINMENT.md')))
