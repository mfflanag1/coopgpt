"""Exact dual replay after floating discovery, restricted 13-owner report grid."""
from projective_plane_discovery import setup
from fractions import Fraction as Q
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
import json

q=3;high=3
n,inc,reps,variables,bits,transitions,nvar=setup(q)
rows=[];cols=[];vals=[];rhs=[];coefficients=[];metadata=[]
def row(coefs,b,meta):
    r=len(rhs)
    for j,a in coefs.items():
        if a:rows.append(r);cols.append(j);vals.append(a)
    rhs.append(int(b));coefficients.append({int(j):int(a) for j,a in coefs.items() if a});metadata.append(meta)
for H in reps:
    reports=1+(high-1)*bits[H]
    values=((bits*reports)@inc).min(axis=1)
    labels=variables[H];local=sorted(set(int(x) for x in labels))
    counts=np.stack([bits[:,labels==v].sum(axis=1) for v in local],axis=1)
    strongest={}
    for C in range(1,len(bits)):
        key=tuple(int(x) for x in counts[C]);worth=int(values[C])
        if worth>strongest.get(key,(-1,None))[0]:strongest[key]=(worth,C)
    for key,(worth,C) in strongest.items():
        row({v:-a for v,a in zip(local,key)},-worth,{'kind':'coverage','profile':H,'coalition':C,'worth':worth})
    budget={v:int((labels==v).sum()) for v in local};budget[nvar]=-int(values[-1])
    row(budget,0,{'kind':'budget','profile':H,'T':int(values[-1])})
for left,right in transitions:
    if left!=right:row({left:1,right:-1},0,{'kind':'monotonicity','left':left,'right':right})
A=coo_matrix((vals,(rows,cols)),shape=(len(rhs),nvar+1)).tocsr()
c=np.zeros(nvar+1);c[-1]=1
res=linprog(c,A_ub=A,b_ub=np.array(rhs),bounds=[(0,None)]*nvar+[(0,None)],method='highs')
if not res.success:raise RuntimeError(res.message)
weights={r:Q(float(-x)).limit_denominator(1000000000) for r,x in enumerate(res.ineqlin.marginals) if x<-1e-9}
sumcoef=[Q(0)]*(nvar+1);bound=Q(0)
for r,w in weights.items():
    if w<0:raise RuntimeError('negative certificate weight')
    bound-=w*rhs[r]
    for j,a in coefficients[r].items():sumcoef[j]+=w*a
if not all(x>=0 for x in sumcoef[:-1]):raise RuntimeError('exact payment sign failure')
if sumcoef[-1]>=0:raise RuntimeError('missing negative budget coefficient')
factor=bound/(-sumcoef[-1])
if factor!=Q(75,68):raise RuntimeError(f'unexpected exact bound{factor}')
profiles=sorted({metadata[r]['profile'] for r in weights if 'profile' in metadata[r]})
out={'status':'exact_dual_replayed','q':q,'owners':n,'resources':n,'reports':[1,high],
     'factor':str(factor),'profile_orbits_used':len(profiles),
     'high_counts_used':sorted({H.bit_count() for H in profiles}),
     'payment_variables':nvar,'weighted_constraints':len(weights),
     'sum_coefficients':[str(x) for x in sumcoef], 'negative_rhs':str(bound),
     'terms':[{'row':r,'weight':str(w),'rhs':rhs[r],
               'coefficients':coefficients[r],'source':metadata[r]} for r,w in weights.items()],
     'scope':'restricted-domain symmetrized exact dual; no asymptotic or novelty claim'}
Path(__file__).with_name('PROJECTIVE_PLANE_CERTIFICATE.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in('sum_coefficients','terms')},indent=2))
