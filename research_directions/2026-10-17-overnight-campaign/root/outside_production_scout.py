"""Discovery LP for withholding plus independent use of the withheld bundle.

Fixed owner identities, binding resource-vector underreports, nonnegative
payments. Duals are reconstructed in rational arithmetic; a successful finite
primal is not an all-real upper theorem.
"""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import argparse,json,time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def solve(n,levels,individual=False,pure=False):
    start=time.monotonic()
    dims=n if pure else 2*n
    states=list(product(levels,repeat=dims));look={s:k for k,s in enumerate(states)}
    profiles=[tuple((p[i] if i%2==0 else 0,p[i] if i%2 else 0) for i in range(n)) if pure else tuple(zip(p[::2],p[1::2])) for p in states]
    ci=n*len(states);rr=[];cc=[];vv=[];rhs=[];tags=[]
    def add(coeff,b,tag):
        row=len(rhs)
        for col,val in coeff.items():
            if val:rr.append(row);cc.append(col);vv.append(val)
        rhs.append(b);tags.append(tag)
    for k,p in enumerate(profiles):
        f=min(sum(t[0] for t in p),sum(t[1] for t in p))
        add({**{k*n+i:1 for i in range(n)},ci:-f},0,['budget',k])
        for mask in range(1,1<<n):
            members=[i for i in range(n) if mask>>i&1]
            val=min(sum(p[i][0] for i in members),sum(p[i][1] for i in members))
            if val:add({k*n+i:-1 for i in members},-val,['coverage',k,mask])
            if individual and len(members)>1:continue
            coords=members if pure else [j for i in members for j in (2*i,2*i+1)]
            raw=states[k]
            for lower in product(*[tuple(v for v in levels if v<=raw[j]) for j in coords]):
                lo=list(raw)
                for j,v in zip(coords,lower):lo[j]=v
                lo=tuple(lo)
                if lo==raw:continue
                h=look[lo];lp=profiles[h]
                outside=min(sum(p[i][0]-lp[i][0] for i in members),sum(p[i][1]-lp[i][1] for i in members))
                add({**{h*n+i:1 for i in members},**{k*n+i:-1 for i in members}},-outside,['outside',k,h,mask])
    mat=coo_matrix((vv,(rr,cc)),shape=(len(rhs),ci+1)).tocsr()
    obj=np.zeros(ci+1);obj[ci]=1
    ans=linprog(obj,A_ub=mat,b_ub=np.asarray(rhs),bounds=(0,None),options={'time_limit':240})
    out={'owners':n,'levels':levels,'pure':pure,'individual_only':individual,'states':len(states),'rows':len(rhs),'status':int(ans.status),'message':ans.message,'seconds':time.monotonic()-start}
    if ans.success:
        out['floating_optimum']=float(ans.fun);combo={};right=Q(0);cert=[]
        for row,v in enumerate(ans.ineqlin.marginals):
            if v>=-1e-8:continue
            w=Q(float(-v)).limit_denominator(10**8)
            for ix in range(mat.indptr[row],mat.indptr[row+1]):
                j=int(mat.indices[ix]);combo[j]=combo.get(j,Q(0))+w*int(mat.data[ix])
            right+=w*int(rhs[row]);cert.append({'weight':str(w),'tag':tags[row]})
        valid=combo.get(ci,0)<0 and all(v>=0 for j,v in combo.items() if j!=ci)
        out.update(exact_dual_valid=valid,exact_bound=str(right/combo[ci]) if valid else None,dual_rows=len(cert))
        used=set()
        for item in cert:
            t=item['tag'];used.add(t[1])
            if t[0]=='outside':used.add(t[2])
        payload={**out,'profiles_by_id':{str(k):profiles[k] for k in sorted(used)},'certificate':cert}
        name=f'outside_{n}_{"_".join(map(str,levels))}_{"pure" if pure else "mixed"}_{"individual" if individual else "coalition"}.json'
        Path(__file__).with_name(name).write_text(json.dumps(payload,indent=2)+'\n')
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--owners',type=int,default=3);ap.add_argument('--levels',type=int,nargs='+',default=[0,1,2]);ap.add_argument('--individual',action='store_true');ap.add_argument('--pure',action='store_true');a=ap.parse_args()
    print(json.dumps(solve(a.owners,tuple(a.levels),a.individual,a.pure),indent=2),flush=True)
