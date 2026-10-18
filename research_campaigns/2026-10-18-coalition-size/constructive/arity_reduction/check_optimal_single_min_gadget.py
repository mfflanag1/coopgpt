from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json

counts={'single_min_primal_dual_profiles':0,'naive_shared_lift_certificates':0}
for r in range(3,9):
    beta=Q(1,r*(r-2))
    for c in product(range(3),repeat=r):
        k=min(range(r),key=lambda i:c[i]);m=c[k]
        x=[Q(a-m) for a in c];z=[Q(m)]*r
        price={(i,j):(r-1)*beta if i==k else beta if j==k else Q(0)
               for i in range(r) for j in range(r) if i!=j}
        assert all(x[i]+z[j]<=c[i] for i,j in price)
        assert all(sum(price[i,j] for j in range(r) if j!=i)>=beta for i in range(r))
        assert all(sum(price[i,j] for i in range(r) if i!=j)>=(r-1)*beta for j in range(r))
        B=beta*sum(c);primal=beta*sum(x)+(r-1)*beta*sum(z)
        dual=sum(c[i]*price[i,j] for i,j in price)
        assert primal==dual==B+m
        counts['single_min_primal_dual_profiles']+=1
    assert Q(1,r-2)==Q(r-(r-1),(r-1)-1)

witness=None
for r in range(3,13):
    beta=Q(1,r*(r-2))
    # Original rows (color, available_flag), with r original activities e_j.
    originals=[(i,available) for i in range(r) for available in [False,True]]
    orig_cap={a:Q(int(a[1])) for a in originals}
    orig_edges={j:[(i,i!=j) for i in range(r)] for j in range(r)}
    assert all(min(orig_cap[a] for a in rows)==0 for rows in orig_edges.values())
    rows=[(a,j) for a in originals for j in range(r) if j!=a[0]]
    caps={row:orig_cap[row[0]] for row in rows}
    columns={}
    for a in originals:
        columns['baseline_'+str(a)]=([(a,j) for j in range(r) if j!=a[0]],beta,Q(0))
    for e,original_rows in orig_edges.items():
        for omitted in range(r):
            used=[(a,omitted) for a in original_rows if a[0]!=omitted]
            columns[f'joint_{e}_{omitted}']=(used,(r-1)*beta,Q(int(e==omitted)))
    assert all(len(used)==r-1 for used,profit,amount in columns.values())
    use={row:sum(amount for used,profit,amount in columns.values() if row in used) for row in rows}
    assert all(use[row]<=caps[row] for row in rows)
    price={row:beta for row in rows}
    assert all(sum(price[row] for row in used)>=profit for used,profit,amount in columns.values())
    primal=sum(profit*amount for used,profit,amount in columns.values())
    dual=sum(caps[row]*price[row] for row in rows)
    baseline=beta*sum(orig_cap.values())
    assert primal==dual==Q(r-1,r-2)
    assert baseline==Q(1,r-2) and primal-baseline==1
    counts['naive_shared_lift_certificates']+=1
    if r==4:
        witness={
          'r':r,'original_value':'0','gadget_value':str(primal),'baseline':str(baseline),
          'row_capacities':{str(row):str(caps[row]) for row in rows},
          'dual_price_every_row':str(beta),
          'columns':{name:{'rows':list(map(str,used)),'profit':str(profit),'primal_amount':str(amount)}
                     for name,(used,profit,amount) in columns.items()}}
result={'status':'PASS','counts':counts,
 'scope':'All-real single-minimum proof is supplemented by exact certificates; shared-resource extension is explicitly rejected.'}
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
Path(__file__).with_name('shared_lift_r4_counterexample.json').write_text(json.dumps(witness,indent=2)+'\n')
print(json.dumps(result,indent=2))
