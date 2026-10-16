"""Independent full-owner replay; high precision is diagnostic, not proof."""
from decimal import Decimal as D, localcontext, ROUND_FLOOR, ROUND_CEILING
import json
from pathlib import Path


def require(test, message):
    if not test:
        raise RuntimeError(message)


def primitive(a, b):
    sa, sb = sum(a), sum(b)
    if min(sa, sb) == 0:
        return [D(0)] * len(a)
    short, long = (a, b) if sa <= sb else (b, a)
    total = min(sa, sb)
    caps = [min(x, total) for x in long]
    q = (1 - sum(caps) / total).exp() / 2
    return [(1-q)*x+q*y for x,y in zip(short,caps)]


def evaluate(branches, grid, n):
    hardware, local = [D(0)]*n, [D(0)]*n
    production = D(0)
    for h, l in branches:
        production += min(sum(h),sum(l))
        payments = primitive(h,l)
        hardware = [x+y for x,y in zip(hardware,h)]
        local = [x+y for x,y in zip(local,payments)]
    accounts = [p+z for p,z in zip(grid,local)]
    return primitive(hardware,accounts), local, hardware, accounts, production


def run(value):
    eps=D(value); e=D(1).exp(); c=1/(2*e); K=e-1
    L=(1/eps).ln(); T=1/L; q=eps/T; rho=1+(T/(2*eps)).ln()
    k=int(L.to_integral_value(rounding=ROUND_FLOOR))
    count=int(rho.to_integral_value(rounding=ROUND_FLOOR))
    caps=[D(1)]*count
    if rho>D(count): caps.append(rho-count)
    fragments=max(2,int((T/k/eps).to_integral_value(rounding=ROUND_CEILING)))
    core_h_start=len(caps)
    G=core_h_start+k*fragments; A=G+1; tiny_h=G+2; n=tiny_h+6
    branches=[]
    for j in range(k):
        h,l=[D(0)]*n,[D(0)]*n
        for f in range(fragments): h[core_h_start+j*fragments+f]=T/k/fragments
        for i,d in enumerate(caps): l[i]=d*T/k
        branches.append((h,l))
    t=2*e*eps
    h,l=[D(0)]*n,[D(0)]*n
    for i in range(tiny_h,n): h[i]=t/6
    l[G]=l[A]=t
    branches.append((h,l))
    h,l=[D(0)]*n,[D(0)]*n
    h[0]=1-T-t
    branches.append((h,l))
    zcore=T+eps*(rho-1)
    grid=[D(0)]*n; grid[G]=D(1); grid[A]=1-zcore-t
    full,z,hardware,accounts,M=evaluate(branches,grid,n)
    tol=D('1e-60')
    require(abs(sum(hardware)-1)<tol,'hardware normalization')
    require(max(z)<=eps+tol,'local-payment diffuseness')
    require(abs(sum(min(x,D(1)) for x in accounts)-2)<tol,'full S=2')
    require(abs(sum(full)-(1+c))<tol,'raw total C')
    require(grid[A]>0 and accounts[A]<1 and accounts[G]>1,'grid cap configuration')
    require(sum(grid)+M>1,'physical hardware bottleneck')
    changed=[]
    for j,(h,l) in enumerate(branches):
        l2=l.copy()
        if j<k:l2[0]=D(0)
        changed.append((h,l2))
    pay1,_,_,acc1,_=evaluate(changed,grid,n)
    delta=eps*(K*rho-(2*e-1))
    predicted1=c*((1-T-t)*(1-(-delta).exp())-eps)
    require(abs((pay1[0]-full[0])-predicted1)<tol,'core exact actual gain')
    require(abs(sum(min(x,D(1)) for x in acc1)-2-delta)<tol,'core changed S')
    changed=[]
    for j,(h,l) in enumerate(branches):
        l2=l.copy()
        if j==k:l2[A]=D(0)
        changed.append((h,l2))
    payA,_,_,accA,_=evaluate(changed,grid,n)
    predictedA=c*((e*eps).exp()*(accounts[A]-eps)-accounts[A])
    require(abs((payA[A]-full[A])-predictedA)<tol,'grid-owner exact actual gain')
    require(abs(sum(min(x,D(1)) for x in accA)-(2-e*eps))<tol,'grid-owner changed S')
    require(predicted1>0 and predictedA>0,'both reports improve')
    achieved=sum(full)+predicted1+predictedA
    residual=(achieved-(1+c)-c*K*eps*(L-L.ln()))/eps
    return {'epsilon':value,'owners':n,'productive_branches':k+1,
            'actual_envelope_lower':str(achieved),
            'residual_coefficient':str(residual),
            'limiting_coefficient':str(-c*(e+1+K*D(2).ln())),
            'checks':11}


with localcontext() as ctx:
    ctx.prec=90
    result={'status':'PASS','scope':'Full-owner 90-digit diagnostic replay; not an exact arithmetic proof.',
            'cases':[run(x) for x in ['0.001','0.0001','0.00001']]}
text=json.dumps(result,indent=2)
Path(__file__).with_suffix('.json').write_text(text+'\n')
print(text)
