"""Bounded arbitrary-payment lower discovery on fixed-owner pure-unit profiles.

All n owners remain fixed, fully eligible, and owner-label averaging is valid.
No resource automorphism or marginal-payment representation is assumed.  q0 is
a free nonnegative payment to each zero-report owner. Numerical results alone
are not certificates or all-profile upper bounds.

Read PURE_UNIT_REDUCTION.txt for the exact scope and coverage reduction.
"""
from __future__ import annotations
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import argparse, json, time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def production(a, edges):
    """Numerical discovery oracle; retain exact feasible primal/dual witnesses."""
    A = np.zeros((len(a),len(edges)))
    for k,e in enumerate(edges):
        A[list(e),k] = 1
    z=linprog(-np.ones(len(edges)), A_ub=A, b_ub=a, bounds=(0,None),method='highs')
    need(z.success, 'production LP failed')
    x=[Q(float(v)).limit_denominator(100000) for v in z.x]
    p=[Q(float(-v)).limit_denominator(100000) for v in z.ineqlin.marginals]
    need(all(v>=0 for v in x+p), 'negative oracle witness')
    need(all(sum(x[k] for k,e in enumerate(edges) if j in e)<=a[j]
             for j in range(len(a))), 'invalid primal oracle witness')
    need(all(sum(p[j] for j in e)>=1 for e in edges), 'invalid dual oracle witness')
    v=sum(x)
    need(v==sum(a[j]*p[j] for j in range(len(a))), 'oracle gap')
    return v,x,p


def solve(name, edges, levels, s, n=None, iterations=50, seconds=120):
    begin=time.monotonic(); d=1+max(max(e) for e in edges)
    n=d*levels+1 if n is None else n
    need(n>d*levels, 'reserve at least one actual zero owner in every profile')
    states=list(product(range(levels+1),repeat=d)); ids={a:k for k,a in enumerate(states)}
    stride=d+1; K=len(states)*stride; nvars=K+1
    records=[]; coefficients=[]; rhs=[]; seen=set(); values=[]; oracles=[]
    def add(c,b,tag):
        key=json.dumps(tag)
        if key in seen: return False
        seen.add(key); records.append(tag); coefficients.append(c); rhs.append(b)
        return True
    def ix(k,j): return k*stride+j
    for k,a in enumerate(states):
        v,x,p=production(a,edges); values.append(v)
        oracles.append({'value':str(v),'primal':list(map(str,x)),'dual':list(map(str,p))})
        c={ix(k,j):Q(a[j]) for j in range(d) if a[j]}
        c[ix(k,d)]=Q(n-sum(a)); c[K]=-v
        add(c,Q(0),['budget',k])
        for e in edges:
            if all(a[j] for j in e):
                add({ix(k,j):Q(-1) for j in e},Q(-1),['coverage',k,list(e)])
    transitions=[]
    for k,a in enumerate(states):
        for i in range(d):
            if a[i]<levels:
                b=list(a); b[i]+=1; h=ids[tuple(b)]
                transitions.append((k,h,i))
                add({ix(k,d):Q(1),ix(h,i):Q(-1)},Q(0),['tcwm',k,h,i,[0]*stride])
    history=[]; solution=None
    for it in range(iterations):
        remain=seconds-(time.monotonic()-begin)
        if remain<=0: break
        rr=[];cc=[];dd=[]
        for r,c in enumerate(coefficients):
            for j,v in c.items():
                if v:rr.append(r);cc.append(j);dd.append(float(v))
        mat=coo_matrix((dd,(rr,cc)),shape=(len(rhs),nvars)).tocsr()
        obj=np.zeros(nvars);obj[K]=1
        z=linprog(obj,A_ub=mat,b_ub=np.array(list(map(float,rhs))),bounds=(0,None),method='highs',options={'time_limit':remain})
        if not z.success:
            history.append({'iteration':it,'success':False,'message':z.message});break
        solution=(z,mat)
        q=z.x[:K].reshape((-1,stride)); added=0;maxviolation=0.
        for k,h,i in transitions:
            a=states[k]; remaining=s-1; count=[0]*stride
            loss=q[k]-q[h]
            mult=list(a)+[n-sum(a)-1]
            for j in sorted(range(stride),key=lambda j:loss[j],reverse=True):
                if loss[j]<=0 or remaining<=0:break
                count[j]=min(remaining,mult[j]);remaining-=count[j]
            violation=q[k,d]-q[h,i]+sum(count[j]*loss[j] for j in range(stride))
            maxviolation=max(maxviolation,violation)
            if violation>1e-8:
                c={ix(k,d):Q(1),ix(h,i):Q(-1)}
                for j,t in enumerate(count):
                    if t:
                        c[ix(k,j)]=c.get(ix(k,j),Q(0))+t
                        c[ix(h,j)]=c.get(ix(h,j),Q(0))-t
                added+=add(c,Q(0),['tcwm',k,h,i,count])
        hist={'iteration':it,'factor':float(z.fun),'cuts_added':added,'max_violation':maxviolation,'constraints':len(rhs),'elapsed':time.monotonic()-begin}
        history.append(hist);print(json.dumps({'name':name,**hist}),flush=True)
        if not added:break
    info={'name':name,'edges':edges,'d':d,'n':n,'s':s,'levels':levels,'profiles':len(states),'history':history,'elapsed':time.monotonic()-begin,'scope':'finite necessary relaxation for arbitrary mechanisms; no continuous upper claim'}
    if solution is None:return info
    z,mat=solution
    multipliers=[Q(float(-v)).limit_denominator(10**7) if v < -1e-9 else Q(0) for v in z.ineqlin.marginals]
    combo={};right=Q(0);cert=[]
    for j,m in enumerate(multipliers):
        if not m:continue
        for t,v in coefficients[j].items():combo[t]=combo.get(t,Q(0))+m*v
        right+=m*rhs[j];cert.append({'multiplier':str(m),'row':records[j]})
    # Rational reconstruction need not preserve exact zero coefficients. Repair
    # any negative payment coefficient with its own profile's budget row. This
    # loses a tiny amount in the bound but produces a fully rational certificate.
    repairs=0
    for k,a in enumerate(states):
        counts=list(a)+[n-sum(a)]
        t=max([Q(0)]+[-combo.get(ix(k,j),Q(0))/count
                         for j,count in enumerate(counts) if count])
        if t>0:
            for j,count in enumerate(counts):
                if count:combo[ix(k,j)]=combo.get(ix(k,j),Q(0))+t*count
            combo[K]=combo.get(K,Q(0))-t*values[k]
            cert.append({'multiplier':str(t),'row':['budget',k]});repairs+=1
    good=combo.get(K,Q(0))<0 and all(v>=0 for t,v in combo.items() if t!=K)
    info.update(float_optimum=float(z.fun),exact_dual_valid=good,dual_support=len(cert),rounding_repairs=repairs,exact_lower=str(right/combo[K]) if good else None)
    payload={**info,'states':states,'oracles':oracles,'certificate':cert,'combo_nonzero':{str(t):str(v) for t,v in combo.items() if v},'rhs':str(right),'factor_index':K}
    Path(__file__).with_name(name+'.json').write_text(json.dumps(payload,indent=2)+'\n')
    return info


def case(name):
    if name=='min3':return [(0,1,2)]
    if name=='cap2':return [(0,1,2),(0,3,4)]
    if name=='cap3':return [(0,1,2),(0,3,4),(0,5,6)]
    if name=='double_star':return [(0,1,2),(0,3,4),(1,5,6)]
    if name=='cycle6':return [tuple(sorted((i,(i+1)%6,(i+2)%6))) for i in range(6)]
    if name=='fano':return [(0,1,2),(0,3,4),(0,5,6),(1,3,5),(1,4,6),(2,3,6),(2,4,5)]
    if name=='pasch':return [(0,1,2),(0,3,4),(5,1,4),(5,3,2)]
    raise ValueError(name)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('case');ap.add_argument('--levels',type=int,default=2);ap.add_argument('--s',type=int,default=8);ap.add_argument('--seconds',type=int,default=120);ap.add_argument('--iterations',type=int,default=50)
    args=ap.parse_args();name=f'{args.case}_L{args.levels}_S{args.s}'
    info=solve(name,case(args.case),args.levels,args.s,seconds=args.seconds,iterations=args.iterations)
    print(json.dumps(info),flush=True)
