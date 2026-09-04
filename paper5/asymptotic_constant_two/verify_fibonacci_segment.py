from fractions import Fraction as F
import json
from pathlib import Path
import z3
from verify_closure import Q,optimum


def fib(j):
    x,y=0,1
    for _ in range(j):
        x,y=y,x+y
    return x


def generators(m,r,perturb=False):
    scale=fib(m+1)
    aa=[F(fib(m-i),scale) for i in range(m)]
    if perturb:
        aa[0]-=F(1,10)
    bb=[1-v for v in aa]
    U=[F(r-m)]+aa+bb+[F(0)]*r
    V=[F(0)]*(2*m+1)+[F(1)]*r
    return U,V


def all_rows(U,V,y):
    n=len(U)
    sums_u=[F(0)]*(2**n)
    sums_v=[F(0)]*(2**n)
    sums_y=[z3.RealVal(0)]*(2**n)
    rows=[u>=0 for u in y]+[sum(y)==sum(U)]
    for mask in range(1,2**n-1):
        bit=mask & -mask
        i=bit.bit_length()-1
        prev=mask^bit
        sums_u[mask]=sums_u[prev]+U[i]
        sums_v[mask]=sums_v[prev]+V[i]
        sums_y[mask]=sums_y[prev]+y[i]
        rows.append(sums_y[mask]>=Q(min(sums_u[mask],sums_v[mask])))
    return rows


def check(m,r,perturb=False):
    U,V=generators(m,r,perturb)
    n=len(U)
    if sum(U)!=r or sum(V)!=r or any(min(u,v)!=0 for u,v in zip(U,V)):
        raise RuntimeError('normalization or efficiency failed')
    y=z3.Reals(' '.join('p%d'%i for i in range(n)))
    rows=all_rows(U,V,y)
    # Receiver-coordinate reconstruction of the proposed segment parameter.
    t=1-y[-1]
    segment=[y[i]==Q(V[i])+t*Q(U[i]-V[i]) for i in range(n)]
    solver=z3.Solver()
    solver.set(timeout=120000)
    solver.add(*rows,z3.Not(z3.And(*segment)))
    answer=solver.check()
    if perturb:
        if answer!=z3.sat:
            raise RuntimeError('perturbed unit-sum negative control did not produce off-segment core allocation')
        point=[str(solver.model().eval(u,model_completion=True)) for u in y]
        return {'m':m,'r':r,'status':'off-segment witness found','point':point}
    if answer!=z3.unsat:
        raise RuntimeError(('core not verified segment',m,r,answer))
    floor=z3.Real('floor')
    ceiling=z3.Real('ceiling')
    floorval=optimum(rows+[u>=floor for u in y],floor,True)
    ceilval=optimum(rows+[u<=ceiling for u in y],ceiling,False)
    scale=fib(m+1)
    tmin=F(scale,scale+1)
    tmax=F(1,r-m+1)
    xx=[tmin*u+(1-tmin)*v for u,v in zip(U,V)]
    zz=[tmax*u+(1-tmax)*v for u,v in zip(U,V)]
    if floorval!=min(xx) or ceilval!=max(zz):
        raise RuntimeError('selector objective mismatch')
    for lev,point,minimize in ((floorval,xx,True),(ceilval,zz,False)):
        s=z3.Solver()
        s.set(timeout=120000)
        s.add(*rows,*[(u>=Q(lev) if minimize else u<=Q(lev)) for u in y],z3.Or(*[u!=Q(v) for u,v in zip(y,point)]))
        if s.check()!=z3.unsat:
            raise RuntimeError('first-stage uniqueness failed')
    overlap=sum(min(u,v) for u,v in zip(xx,zz))
    deficit=2*overlap/r
    expected=2*F(1,scale+1)+2*F(1,r-m+1)
    if deficit!=expected or overlap<F(r,n-1):
        raise RuntimeError('deficit formula or generic bound mismatch')
    return {'m':m,'r':r,'n':n,'F':scale,'Lmin':[str(v) for v in xx],'Lmax':[str(v) for v in zz],'deficit':str(deficit),'rho':str(2-deficit),'n_times_deficit':str(n*deficit),'full_coalitions':2**n-2,'unique_first_stage_selectors':True,'core_exactly_segment':True}


if __name__=='__main__':
    records=[]
    for m,r in ((2,3),(2,4),(3,4),(3,5),(4,5)):
        result=check(m,r)
        records.append(result)
        print('PASS',m,r,result['rho'],flush=True)
    negative=check(2,3,True)
    print('PASS perturbed unit-sum negative control',flush=True)
    symbolic=[]
    for m in range(2,65):
        denom=fib(m+1)
        a=[F(fib(m-i),denom) for i in range(m)]
        b=[1-v for v in a]
        if min(a+b)!=F(1,denom) or sum(a+b)!=m:
            raise RuntimeError('Fibonacci coefficient identity failed')
        if any(a[i+1]+a[i+2]+b[i]!=1 for i in range(m-2)):
            raise RuntimeError('recurrence row failed')
        if a[m-2]+b[m-1]!=1 or a[0]+a[1]!=1:
            raise RuntimeError('boundary row failed')
        symbolic.append({'m':m,'F':denom})
    sequence=[]
    for n in (128,256,512,1024,4096,65536):
        # Elementary explicit all-n choice: F_(4 ceil(log2 n)+1)>=n^2.
        ell=(n-1).bit_length()
        m=4*ell
        r=n-2*m-1
        if r<=m or fib(m+1)<n*n:
            raise RuntimeError('all-n parameter domain failed')
        deficit=2*F(1,fib(m+1)+1)+2*F(1,n-3*m)
        sequence.append({'n':n,'m':m,'r':r,'deficit':str(deficit),'n_times_deficit':str(n*deficit)})
    payload={'evidence':'Full coalition exact finite replay plus arithmetic calibrations; conventional all-parameter proof separate','cases':records,'negative_control':negative,'fibonacci_rows':symbolic,'all_n_sequence':sequence}
    with open(Path(__file__).with_name('fibonacci_segment_calibration.json'),'w') as f:
        json.dump(payload,f,indent=2,sort_keys=True)
        f.write('\n')
