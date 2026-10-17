"""Finite necessary price-field LP with exact separation formulas, floating solves.

This is discovery only. It is justified by the separately audited aggregate-
price existence theorem, but numerical optima are not proof certificates.
Unlike the earlier full enumeration, coalition holdings are separated at the
worst box corner for each high/low pair. No report inequality is weakened when
the finite separation loop converges. No canonical files are edited.
"""
import argparse,itertools,math,json,time
from pathlib import Path
import numpy as np
from fractions import Fraction as Q
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

def run(levels, seconds=600, batch=20000):
    start=time.monotonic()
    levels=tuple(sorted(set(levels)))
    assert levels[0]==0 and len(levels)>1
    states=np.array(list(itertools.product(levels,repeat=4)),dtype=np.int64)
    look={tuple(c):i for i,c in enumerate(states)}
    def value(a):
        a=np.asarray(a)
        return np.minimum(np.minimum(a[...,0]+a[...,2],a[...,1]+a[...,2]),a[...,1]+a[...,3])
    def canonical(c):
        g=math.gcd(*map(int,c));c=tuple(int(x)//g for x in c) if g else tuple(c)
        rev=c[::-1]
        return (rev,True) if rev<c else (c,False)
    cols={};ids=np.full(states.shape,-1,dtype=np.int64);nextcol=1
    for i,c in enumerate(states):
        canon,rev=canonical(c)
        for v in range(4):
            if not c[v]:continue
            vertex=3-v if rev else v
            if canon==canon[::-1]:vertex=min(vertex,3-vertex)
            key=(canon,vertex)
            if key not in cols:cols[key]=nextcol;nextcol+=1
            ids[i,v]=cols[key]
    rr=[];cc=[];vv=[];rhs=[];seen=set()
    def add(terms,b,key=None):
        if key is not None:
            if key in seen:return False
            seen.add(key)
        r=len(rhs)
        for j,x in terms.items():
            if x:rr.append(r);cc.append(j);vv.append(x)
        rhs.append(b);return True
    for i,c in enumerate(states):
        if not np.any(c):continue
        terms={0:-float(value(c))}
        for v in range(4):
            if c[v]:terms[ids[i,v]]=terms.get(ids[i,v],0)+int(c[v])
        add(terms,0)
        for u,v in ((0,1),(1,2),(2,3)):
            if c[u] and c[v]:
                terms={}
                for vertex in (u,v):
                    j=ids[i,vertex];terms[j]=terms.get(j,0)-1
                add(terms,-1)
    highs=[];lows=[]
    for i,c in enumerate(states):
        for low in itertools.product(*[levels[:levels.index(int(x))+1] for x in c]):
            j=look[low]
            if i!=j:highs.append(i);lows.append(j)
    highs=np.array(highs,dtype=np.int32);lows=np.array(lows,dtype=np.int32)
    delta=states[highs]-states[lows];outside=value(delta)
    print(json.dumps({'stage':'built','states':len(states),'variables':nextcol,'pairs':len(highs),'seconds':time.monotonic()-start}),flush=True)
    history=[];objective=np.zeros(nextcol);objective[0]=1
    result=None;converged=False
    for iteration in range(100):
        remaining=seconds-(time.monotonic()-start)
        if remaining<=0:break
        mat=coo_matrix((vv,(rr,cc)),shape=(len(rhs),nextcol)).tocsr()
        result=linprog(objective,A_ub=mat,b_ub=rhs,bounds=[(1,2)]+[(0,None)]*(nextcol-1),method='highs',options={'time_limit':min(remaining,180)})
        if not result.success:
            history.append({'iteration':iteration,'status':int(result.status),'message':result.message});break
        prices=np.zeros(states.shape,dtype=float);mask=ids>=0;prices[mask]=result.x[ids[mask]]
        pdiff=prices[highs]-prices[lows]
        lhs=np.sum(delta*prices[highs]+states[lows]*np.minimum(0,pdiff),axis=1)
        violation=outside-lhs
        bad=np.flatnonzero(violation>1e-8)
        record={'iteration':iteration,'factor':float(result.fun),'rows':len(rhs),'violations':len(bad),'max_violation':float(max(0,violation.max())),'seconds':time.monotonic()-start}
        history.append(record);print(json.dumps(record),flush=True)
        if not len(bad):converged=True;break
        if len(bad)>batch:bad=bad[np.argpartition(violation[bad],-batch)[-batch:]]
        added=0
        for z in bad:
            h=int(highs[z]);l=int(lows[z]);bits=tuple(bool(x<0) for x in pdiff[z]);key=(h,l,bits)
            terms={}
            for v in range(4):
                retained=int(states[l,v]) if bits[v] else 0
                holding=int(delta[z,v])+retained
                if holding:
                    j=ids[h,v];terms[j]=terms.get(j,0)-holding
                if retained:
                    j=ids[l,v];terms[j]=terms.get(j,0)+retained
            added+=add(terms,-int(outside[z]),key)
        if added==0:raise RuntimeError('Numerical separation repeats already imposed cuts')
    report={'graph':'path4','levels':levels,'homogeneous_reflection_symmetric':True,'states':len(states),'variables':nextcol,'pairs':len(highs),'converged':converged,'history':history,'factor':float(result.fun) if result is not None and result.fun is not None else None,'seconds':time.monotonic()-start,'scope':'floating necessary price-field LP only; exact dual reconstruction required for theorem'}
    if result is not None and result.success:
        report['prices']={','.join(map(str,c)):prices[i].tolist() for i,c in enumerate(states)}
        report['dual_support']=[{'terms':[(int(j),float(x)) for j,x in zip(mat.indices[mat.indptr[r]:mat.indptr[r+1]],mat.data[mat.indptr[r]:mat.indptr[r+1]])],'rhs':float(rhs[r]),'multiplier':float(m)} for r,m in enumerate(result.ineqlin.marginals) if abs(m)>1e-10]
        # Rounded NONNEGATIVE integer combinations remain exact inequalities.
        # Repair negative price coefficients using p_j <= B_j*kappa from
        # funding and nonnegativity at any state containing that price slot.
        upper={}
        for i,c in enumerate(states):
            f=int(value(c))
            for v in range(4):
                if c[v]:
                    j=int(ids[i,v]);b=Q(f,int(c[v]))
                    upper[j]=min(upper.get(j,b),b)
        weights=[max(0,int(round(-float(m)*10**9))) for m in result.ineqlin.marginals]
        coefficients=[0]*nextcol;target=0
        for r,weight in enumerate(weights):
            if not weight:continue
            target+=weight*int(rhs[r])
            for j,x in zip(mat.indices[mat.indptr[r]:mat.indptr[r+1]],mat.data[mat.indptr[r]:mat.indptr[r+1]]):
                assert float(x).is_integer()
                coefficients[int(j)]+=weight*int(x)
        denominator=-Q(coefficients[0])
        repairs=[]
        for j,a in enumerate(coefficients[1:],1):
            if a<0:
                denominator+=(-a)*upper[j];repairs.append((j,-a,str(upper[j])))
        if denominator>0:
            certified=-Q(target)/denominator
            report['exact_lower_certificate']={'bound':str(certified),'decimal':float(certified),'integer_weight_scale':10**9,'nonzero_weights':sum(w>0 for w in weights),'repairs':repairs,'derivation':'Nonnegative integer combination of displayed necessary inequalities; eliminate negative price coefficients with exact p_j<=B_j*kappa funding bounds. Remaining price coefficients nonnegative, so kappa>=-combined_rhs/denominator.','combined_kappa_coefficient':coefficients[0],'combined_rhs':target}
    path=Path(__file__).with_name('graph_outside_cuts_'+('_'.join(map(str,levels)))+'.json');path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('prices','dual_support','history')}),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--levels',type=int,nargs='+',default=[0,1,2,4,8]);ap.add_argument('--seconds',type=int,default=600);a=ap.parse_args();run(a.levels,a.seconds)
