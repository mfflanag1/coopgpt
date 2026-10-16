#!/usr/bin/env python3
"""Exact-certified finite Model A LP; SciPy is discovery only.

The domain is a Cartesian grid in P,h_1..h_m,L_1..L_m. All owners are fixed:
local blocks first, grid owner next, then separate hardware owners. Coalition
constraints enumerate every positive-worth coalition; zero-worth constraints
follow from explicit nonnegativity. Adjacent own-coordinate edges generate all
componentwise unilateral comparisons inside this Cartesian grid. Feasible finite
LPs NEVER prove continuous upper bounds. Exact duals are universal obstructions
only to the extent that these finite profiles/constraints are valid restrictions.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse,gzip,hashlib,json
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from verify_split_rule import worth, values, require


def rational(x): return F(float(x)).limit_denominator(10**7)
def solve_static(b,blocks,theta):
    m=len(blocks);k=max(blocks)+1;n=m+k+1;full=(1<<n)-1;T=worth(b,full,blocks)
    rows=[];rhs=[];tags=[]
    for mask in range(1,1<<n):
        v=worth(b,mask,blocks)
        if v:
            rows.append([-int(bool(mask&(1<<i))) for i in range(n)]);rhs.append(-v);tags.append(['coalition',mask])
    for a in range(k):
        floor=theta*(T-worth(b,full^(1<<a),blocks))
        if floor:rows.append([-int(i==a) for i in range(n)]);rhs.append(-floor);tags.append(['floor',a])
    if not rows:return F(),{'primal':['0']*n,'dual':[]}
    ans=linprog(np.ones(n),A_ub=np.array(rows,dtype=float),b_ub=np.array(rhs,dtype=float),bounds=(0,None),method='highs')
    require(ans.success,'Static LP failure: '+ans.message)
    x=list(map(rational,ans.x));w=list(map(lambda z:rational(-z),ans.ineqlin.marginals))
    require(all(v>=0 for v in x),'Static negative primal')
    require(all(sum(F(a)*v for a,v in zip(row,x))<=r for row,r in zip(rows,rhs)),'Static exact primal failure')
    require(all(v>=0 for v in w),'Static negative dual')
    require(all(sum(w[t]*rows[t][i] for t in range(len(rows)))>=-1 for i in range(n)),'Static exact dual failure')
    require(sum(x)==-sum(v*r for v,r in zip(w,rhs)),'Static exact duality gap')
    return sum(x),{'primal':list(map(str,x)),'dual':[{'weight':str(v),'tag':tag} for v,tag in zip(w,tags) if v]}


def solve(blocks,levels,theta,normalizer='production'):
    require(set(blocks)==set(range(max(blocks)+1)),'Nonempty contiguous block labels required')
    require(0<=theta<=1,'Theta in [0,1]')
    require(levels==tuple(sorted(set(levels))) and min(levels)>=0,'Sorted nonnegative levels')
    m=len(blocks);k=max(blocks)+1;n=m+k+1;d=2*m+1;full=(1<<n)-1
    profiles=list(product(levels,repeat=d));lookup={b:q for q,b in enumerate(profiles)}
    owner=(k,)+tuple(range(k+1,n))+blocks
    statics=[];static_certs=[]
    for b in profiles:
        val,cert=solve_static(b,blocks,theta);statics.append(val);static_certs.append(cert)
    C=n*len(profiles);rows=[];rhs=[];tags=[];counts={'budget':0,'coalition':0,'floor':0,'monotone':0}
    def add(row,right,tag):
        rows.append({i:F(v) for i,v in row.items() if v});rhs.append(F(right));tags.append(tag);counts[tag[0]]+=1
    for q,b in enumerate(profiles):
        T=worth(b,full,blocks);denominator=T if normalizer=='production' else statics[q]
        add({**{q*n+i:1 for i in range(n)},C:-denominator},0,['budget',q])
        for mask in range(1,1<<n):
            v=worth(b,mask,blocks)
            if v:add({q*n+i:-1 for i in range(n) if mask&(1<<i)},-v,['coalition',q,mask])
        for a in range(k):
            floor=theta*(T-worth(b,full^(1<<a),blocks))
            if floor:add({q*n+a:-1},-floor,['floor',q,a])
        for coordinate in range(d):
            pos=levels.index(b[coordinate])
            if pos+1<len(levels):
                high=list(b);high[coordinate]=levels[pos+1];qhigh=lookup[tuple(high)];i=owner[coordinate]
                add({q*n+i:1,qhigh*n+i:-1},0,['monotone',q,qhigh,i])
    ri=[];ci=[];data=[]
    for r,row in enumerate(rows):
        for col,v in row.items():ri.append(r);ci.append(col);data.append(float(v))
    mat=coo_matrix((data,(ri,ci)),shape=(len(rows),C+1)).tocsr();objective=np.zeros(C+1);objective[C]=1
    ans=linprog(objective,A_ub=mat,b_ub=np.array(rhs,dtype=float),bounds=(0,None),method='highs')
    require(ans.success,'Transition LP failure: '+ans.message)
    x=list(map(rational,ans.x));weights=[rational(-v) if v<-1e-9 else F() for v in ans.ineqlin.marginals]
    primal_valid=all(v>=0 for v in x) and all(sum(v*x[i] for i,v in row.items())<=right for row,right in zip(rows,rhs))
    combo={};right=F();support=[]
    for w,row,b,tag in zip(weights,rows,rhs,tags):
        if not w:continue
        require(w>0,'Negative dual coefficient')
        for i,v in row.items():combo[i]=combo.get(i,F())+w*v
        right+=w*b;support.append({'weight':str(w),'tag':tag})
    dual_valid=combo.get(C,F())<0 and all(v>=0 for i,v in combo.items() if i!=C)
    lower=right/combo[C] if dual_valid else None
    require(primal_valid,'Exact transition primal reconstruction failed')
    require(dual_valid,'Exact transition dual reconstruction failed')
    require(lower==x[C],'Exact transition duality gap')
    ratios=[(val/worth(b,full,blocks),q) for q,(b,val) in enumerate(zip(profiles,statics)) if worth(b,full,blocks)]
    maximum,index=max(ratios) if ratios else (F(),0)
    return {'status':'PASS','blocks':list(blocks),'levels':list(map(str,levels)),'theta':str(theta),'normalizer':normalizer,'profiles':len(profiles),'owners':n,'dimension':d,'row_counts':counts,'exact_optimum':str(x[C]),'exact_dual_lower':str(lower),'float_discovery_optimum':ans.fun,'static_max_factor':str(maximum),'static_max_profile':list(map(str,profiles[index])),'dual_support':len(support),'dual_certificate':support,'dual_budget_coefficient':str(combo[C]),'dual_rhs':str(right),'all_profiles':[list(map(str,b)) for b in profiles],'static_funding':list(map(str,statics)),'static_certificates':static_certs,'primal':list(map(str,x)),'scope':'Exact finite-domain optimum only; dual is a valid restricted-profile lower, primal is not a universal upper.','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--blocks',default='0,1');ap.add_argument('--levels',default='0,1,2');ap.add_argument('--theta',default='1');ap.add_argument('--normalizer',choices=['production','static'],default='production');ap.add_argument('--output',required=True,type=Path)
    a=ap.parse_args();result=solve(tuple(map(int,a.blocks.split(','))),tuple(map(F,a.levels.split(','))),F(a.theta),a.normalizer)
    encoded=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if a.output.suffix=='.gz':
        with gzip.open(a.output,'wt') as handle:handle.write(encoded)
    else:a.output.write_text(encoded)
    print(json.dumps({key:value for key,value in result.items() if key not in ['all_profiles','static_funding','static_certificates','primal','dual_certificate']},indent=2))
