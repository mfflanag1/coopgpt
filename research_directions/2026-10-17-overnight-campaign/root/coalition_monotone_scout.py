"""Finite-grid discovery only; exact dual proves only the recorded lower bound."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import argparse, json, time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def solve(n, levels, joint=True):
    start=time.monotonic()
    states=list(product(levels, repeat=2*n)); look={s:k for k,s in enumerate(states)}
    ci=n*len(states); rr=[]; cc=[]; vv=[]; rhs=[]; tags=[]
    def add(coeff,b,tag):
        k=len(rhs)
        for j,v in coeff.items():
            if v: rr.append(k); cc.append(j); vv.append(v)
        rhs.append(b); tags.append(tag)
    def worth(p,mask):
        return min(sum(p[2*i] for i in range(n) if mask>>i&1),sum(p[2*i+1] for i in range(n) if mask>>i&1))
    for k,p in enumerate(states):
        add({**{k*n+i:1 for i in range(n)},ci:-worth(p,(1<<n)-1)},0,['budget',k])
        for mask in range(1,1<<n):
            v=worth(p,mask)
            if v: add({k*n+i:-1 for i in range(n) if mask>>i&1},-v,['coverage',k,mask])
        for j in range(2*n):
            ix=levels.index(p[j])
            if ix+1==len(levels): continue
            high=p[:j]+(levels[ix+1],)+p[j+1:]; h=look[high]; owner=j//2
            masks=[s for s in range(1,1<<n) if s>>owner&1] if joint else [1<<owner]
            for mask in masks:
                add({**{k*n+i:1 for i in range(n) if mask>>i&1},**{h*n+i:-1 for i in range(n) if mask>>i&1}},0,['monotone',k,h,mask,owner])
    mat=coo_matrix((vv,(rr,cc)),shape=(len(rhs),ci+1)).tocsr()
    obj=np.zeros(ci+1);obj[-1]=1
    ans=linprog(obj,A_ub=mat,b_ub=np.array(rhs),bounds=(0,None),options={'time_limit':240})
    info={'owners':n,'levels':levels,'coalition_total_monotone':joint,'profiles':len(states),'rows':len(rhs),'status':int(ans.status),'message':ans.message,'seconds':time.monotonic()-start}
    if ans.success:
        info['float_optimum']=float(ans.fun); combo={};right=Q(0);cert=[]
        for r,v in enumerate(ans.ineqlin.marginals):
            if v>=-1e-8:continue
            w=Q(float(-v)).limit_denominator(10**7)
            for ix in range(mat.indptr[r],mat.indptr[r+1]):
                j=int(mat.indices[ix]); combo[j]=combo.get(j,Q(0))+w*int(mat.data[ix])
            right+=w*int(rhs[r]);cert.append({'weight':str(w),'tag':tags[r]})
        valid=combo.get(ci,0)<0 and all(v>=0 for j,v in combo.items() if j!=ci)
        info['exact_dual_valid']=valid;info['exact_bound']=str(right/combo[ci]) if valid else None
        info['dual_rows']=len(cert)
        if valid:
            used=set()
            for item in cert:
                tag=item['tag'];used.add(tag[1])
                if tag[0]=='monotone':used.add(tag[2])
            payload={**info,'profiles_by_id':{str(k):states[k] for k in sorted(used)},'certificate':cert}
            name='coalition_monotone_'+str(n)+'_'+'_'.join(map(str,levels))+('_joint' if joint else '_individual')+'.json'
            Path(__file__).with_name(name).write_text(json.dumps(payload,indent=2)+'\n')
    return info

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--owners',type=int,default=3);ap.add_argument('--levels',type=int,nargs='+',default=[0,1,2]);ap.add_argument('--individual',action='store_true');args=ap.parse_args()
    print(json.dumps(solve(args.owners,tuple(args.levels),not args.individual),indent=2),flush=True)
