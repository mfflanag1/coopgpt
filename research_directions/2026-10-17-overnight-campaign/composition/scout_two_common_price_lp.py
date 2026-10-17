"""Numerical necessary-condition scout. No finite-grid feasible point is a mechanism."""
from fractions import Fraction as Q
from itertools import product, combinations
from pathlib import Path
import argparse, json, time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix, save_npz

def vertices(a,b,v):
    lines=[(Q(1),Q(0),Q(0)),(Q(0),Q(1),Q(0))]+list(zip(a,b,v))
    pts={(Q(0),Q(0))}
    for (x,y,z),(xx,yy,zz) in combinations(lines,2):
        det=x*yy-y*xx
        if det:
            p=(z*yy-y*zz)/det;q=(x*zz-z*xx)/det
            if p>=0 and q>=0:pts.add((p,q))
    return [(p,q,tuple(max(Q(0),vv-aa*p-bb*q) for aa,bb,vv in zip(a,b,v))) for p,q in pts]

def run(levels, a, b, v, tag):
    start=time.time();d=len(a)+2;dual=vertices(a,b,v)
    raw=list(product(levels,repeat=d)); canonical={};rawid={}
    for c in raw:
        norm=next((x for x in c if x),Q(1));key=tuple(x/norm for x in c)
        if key not in canonical:canonical[key]=len(canonical)
        rawid[c]=canonical[key]
    caps=list(canonical);N=len(caps);kappa=N*d
    values=[min(c[0]*p+c[1]*q+sum(cc*pp for cc,pp in zip(c[2:],priv)) for p,q,priv in dual) for c in caps]
    rr=[];cc=[];dd=[];rhs=[];labels=[];var=kappa+1
    def constraint(terms,bound,label):
        row=len(rhs)
        for col,val in terms:
            if val:rr.append(row);cc.append(col);dd.append(float(val))
        rhs.append(float(bound));labels.append(label)
    for n,c in enumerate(caps):
        constraint([(n*d+j,c[j]) for j in range(d)]+[(kappa,-values[n])],0,('budget',n))
        if c[0] and c[1]:
            for j in range(d-2):
                if c[j+2]:constraint([(n*d,-a[j]),(n*d+1,-b[j]),(n*d+j+2,-1)],-v[j],('cover',n,j))
    transitions=[]
    for c in raw:
        old=rawid[c]
        for j in range(d):
            pos=levels.index(c[j])
            if pos==len(levels)-1:continue
            newc=list(c);newc[j]=levels[pos+1];newc=tuple(newc);new=rawid[newc];delta=newc[j]-c[j]
            z=[]
            for h in range(d):
                if c[h]:
                    aux=var;var+=1;z.append(aux)
                    constraint([(old*d+h,c[h]),(new*d+h,-c[h]),(aux,-1)],0,('loss',len(transitions),h))
            constraint([(aux,1) for aux in z]+[(new*d+j,-delta)],0,('transition',len(transitions)))
            transitions.append((tuple(map(str,c)),tuple(map(str,newc)),j))
    A=coo_matrix((dd,(rr,cc)),shape=(len(rhs),var)).tocsr()
    obj=np.zeros(var);obj[kappa]=1
    bounds=[(0,None)]*var
    for n,c in enumerate(caps):
        for j in range(d):
            if not c[j]:bounds[n*d+j]=(0,0)
    sol=linprog(obj,A_ub=A,b_ub=np.array(rhs),bounds=bounds,method='highs',options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
    result={'status':str(sol.message),'success':bool(sol.success),'numerical_lower':float(sol.fun) if sol.success else None,
            'a':list(map(str,a)),'b':list(map(str,b)),'v':list(map(str,v)),'levels':list(map(str,levels)),
            'homogeneous_profiles':N,'raw_profiles':len(raw),'transitions':len(transitions),'variables':var,'constraints':len(rhs),'seconds':time.time()-start,
            'scope':'Numerical necessary-price relaxation only; no exact lower or full-domain upper established.'}
    path=Path(__file__).parent/tag
    path.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    if sol.success:
        np.savez_compressed(str(path)+'.npz',x=sol.x,dual=sol.ineqlin.marginals,rhs=np.array(rhs),objective=obj)
        save_npz(str(path)+'_matrix.npz',A)
        path.with_name(path.name+'_metadata.json').write_text(json.dumps({'caps':[list(map(str,c)) for c in caps],'labels':labels,'transitions':transitions,'kappa_column':kappa},indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--epsilon',default='1/4');p.add_argument('--levels',default='0,1/4,1');p.add_argument('--tag',default='TWO_COMMON_PRICE_LP_SCOUT');p.add_argument('--base-profit',default='3/2');p.add_argument('--a');p.add_argument('--b');p.add_argument('--v');args=p.parse_args()
    e=Q(args.epsilon)
    aa=list(map(Q,args.a.split(','))) if args.a else [Q(1),Q(1),e]
    bb=list(map(Q,args.b.split(','))) if args.b else [Q(1),e,Q(1)]
    vv=list(map(Q,args.v.split(','))) if args.v else [Q(args.base_profit),Q(1),Q(1)]
    run(list(map(Q,args.levels.split(','))),aa,bb,vv,args.tag)
