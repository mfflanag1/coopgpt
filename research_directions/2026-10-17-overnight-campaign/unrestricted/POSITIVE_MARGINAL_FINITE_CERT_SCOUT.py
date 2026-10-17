"""Bounded LP discovery; emitted dual is independently checked with Fraction."""
from pathlib import Path
from fractions import Fraction as Q
from math import comb
import json
import numpy as np
from scipy.optimize import linprog

B=Path(__file__).resolve().parent

def choose(n,k):
    return comb(n,k) if 0<=k<=n else 0

def row(N,q,k,t):
    z=N-q-k
    return [Q(sum(choose(k,j)*(choose(z,l-j)-(q-1)*choose(z,l-1-j))
                  for j in range(t+1,k+1)),choose(N-1,l)) for l in range(N)]

summaries=[]
for N,s in [(16,4),(24,4),(32,5)]:
    coverage=[Q(3*l*(l-1),(N-1)*(N-2)) for l in range(N)]
    rows=[coverage];ids=[None]
    for q in range(2,s+1):
        for k in range(1,N-q+1):
            for t in range(k):
                rows.append(row(N,q,k,t));ids.append((q,k,t))
    result=linprog(np.ones(N),A_ub=-np.asarray(rows,dtype=float),
                   b_ub=np.asarray([-1.]+[0.]*(len(rows)-1)),
                   bounds=(0,None),method='highs',options={'time_limit':45})
    summary={'N':N,'s':s,'rows':len(rows),'status':int(result.status),
             'numeric_objective':None if result.fun is None else float(result.fun)}
    if result.success:
        weights=[max(Q(0),Q(str(-float(x))).limit_denominator(10**8))
                 for x in result.ineqlin.marginals]
        coefficients=[sum((w*r[l] for w,r in zip(weights,rows) if w),Q(0))
                      for l in range(N)]
        scale=max(Q(1),max(coefficients))
        bound=weights[0]/scale
        support=[{'q':ids[i][0],'k':ids[i][1],'t':ids[i][2],
                  'weight':str(weights[i]/scale)}
                 for i in range(1,len(rows)) if weights[i]]
        summary.update({'exact_bound':str(bound),'exact_bound_decimal':float(bound),
                        'support_rows':len(support),'rescaling':str(scale)})
        certificate={'N':N,'s':s,'coverage_weight':str(bound),
                     'transition_weights':support,
                     'scope':'Fixed nonnegative whole-owner marginal weights only; finite rational dual. Not an unrestricted-mechanism lower.'}
        (B/f'POSITIVE_MARGINAL_FINITE_CERT_N{N}_S{s}.json').write_text(json.dumps(certificate,indent=2)+'\n')
        summaries.append(summary)
        print(json.dumps(summary),flush=True)
        if bound>2:
            break
    else:
        summaries.append(summary);print(json.dumps(summary),flush=True)
(B/'POSITIVE_MARGINAL_FINITE_CERT_DISCOVERY.json').write_text(json.dumps(summaries,indent=2)+'\n')
