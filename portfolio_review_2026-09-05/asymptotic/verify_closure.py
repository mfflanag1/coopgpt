from fractions import Fraction as F
import json
from pathlib import Path
import z3


def Q(v):
    v=F(v)
    return z3.Q(v.numerator,v.denominator)


def frac(v):
    v=z3.simplify(v)
    return F(v.as_long()) if z3.is_int_value(v) else F(v.numerator_as_long(),v.denominator_as_long())


def optimum(cons,expr,maximize):
    s=z3.Optimize()
    s.set(timeout=60000)
    s.add(*cons)
    h=s.maximize(expr) if maximize else s.minimize(expr)
    if s.check()!=z3.sat:
        raise RuntimeError('optimization failed or unknown')
    return frac(h.value())


def selector(cons,y,mode):
    fixed={}
    stages=[]
    while len(fixed)<len(y):
        free=[i for i in range(len(y)) if i not in fixed]
        prefix=cons+[y[i]==Q(v) for i,v in fixed.items()]
        t=z3.FreshReal('t')
        upward=mode=='min'
        lev=optimum(prefix+[(y[i]>=t if upward else y[i]<=t) for i in free],t,upward)
        face=prefix+[(y[i]>=Q(lev) if upward else y[i]<=Q(lev)) for i in free]
        pinned=[i for i in free if optimum(face,y[i],upward)==lev]
        if not pinned:
            raise RuntimeError('empty fixed stratum')
        fixed.update({i:lev for i in pinned})
        stages.append({'level':str(lev),'players':pinned})
    return [fixed[i] for i in range(len(y))],stages


def family(n,a):
    q=F(1,n-1)
    x=[1-(n-1)*a]+[a]*(n-1)
    z=[q,F(0)]+[q]*(n-2)
    e1=[F(i==0) for i in range(n)]
    e3=[F(i==2) for i in range(n)]
    return [x,z,e1,e3]


def check(n,a):
    q=F(1,n-1)
    points=family(n,a)
    y=z3.Reals(' '.join('y%d'%i for i in range(n)))
    nonneg=[u>=0 for u in y]
    base=nonneg+[sum(y)==1]
    rows=[]
    for mask in range(1,2**n-1):
        ids=[i for i in range(n) if mask>>i&1]
        val=min(sum(p[i] for i in ids) for p in points)
        rows.append(sum(y[i] for i in ids)>=Q(val))
    cap=[y[1]<=Q(a)]+[y[1]+y[i]<=Q(q) for i in range(3,n)]
    for left,right in ((rows,cap),(cap,rows)):
        s=z3.Solver()
        s.set(timeout=60000)
        s.add(*(base+left),z3.Not(z3.And(*right)))
        if s.check()!=z3.unsat:
            raise RuntimeError(('core equivalence failed',n,str(a),s.check()))
    x,bx=selector(base+rows,y,'min')
    z,bz=selector(base+rows,y,'max')
    b=q+F(n-4,2)*a
    expected_x=[b,a,b]+[q-a]*(n-3)
    expected_z=expected_x if n==4 else points[1]
    if x!=expected_x or z!=expected_z:
        raise RuntimeError(('selector mismatch',n,a,x,z,expected_x,expected_z))
    overlap=sum(min(u,v) for u,v in zip(x,z))
    expected_rho=F(0) if n==4 else 2*(n-3)*a
    if 2-2*overlap!=expected_rho or overlap<F(1,n-1):
        raise RuntimeError('overlap mismatch')
    if any(sum(p)!=1 or min(p)<0 for p in points):
        raise RuntimeError('invalid generators')
    if any(min(p[i] for p in points)!=0 for i in range(n)):
        raise RuntimeError('not normalized')
    return {'n':n,'a':str(a),'Lmin':[str(v) for v in x],'Lmax':[str(v) for v in z],'rho':str(expected_rho),'Lmin_stages':bx,'Lmax_stages':bz,'coalitions':len(rows)}


if __name__=='__main__':
    out=[]
    for n in range(4,10):
        for a in sorted({F(0),F(1,n**3),F(1,8*(n-1)),F(1,2*(n-1))}):
            row=check(n,a)
            out.append(row)
            print(n,a,row['rho'],flush=True)
    # Deliberately extrapolate the small-a formula outside its stated chamber.
    n=5
    a=F(1,5)
    pts=family(n,a)
    y=z3.Reals('nc0 nc1 nc2 nc3 nc4')
    cons=[u>=0 for u in y]+[sum(y)==1]
    for mask in range(1,2**n-1):
        ids=[i for i in range(n) if mask>>i&1]
        cons.append(sum(y[i] for i in ids)>=Q(min(sum(p[i] for i in ids) for p in pts)))
    got,_=selector(cons,y,'min')
    q=F(1,n-1)
    invalid=[q+F(n-4,2)*a,a,q+F(n-4,2)*a]+[q-a]*(n-3)
    if got==invalid:
        raise RuntimeError('out-of-chamber negative control did not fail')
    payload={'evidence':'Exact finite calibration; all-parameter proof separate','cases':out,'negative_control':{'n':n,'a':str(a),'actual_Lmin':[str(v) for v in got],'invalid_extrapolation':[str(v) for v in invalid]}}
    with open(Path(__file__).with_name('closure_calibration.json'),'w') as f:
        json.dump(payload,f,indent=2,sort_keys=True)
        f.write('\n')
