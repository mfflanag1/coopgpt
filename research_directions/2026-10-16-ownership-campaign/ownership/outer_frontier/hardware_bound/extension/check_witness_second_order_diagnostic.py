"""Floating corroboration of the second-order class theorem, not a proof."""
import math,random,itertools,json
r=random.Random(1601026);c=1/(2*math.e);K=math.e-1

def require(v,s):
    if not v:raise RuntimeError(s)
def gain(d,a,us,ws,rho,eps):
    V=sum(w*math.exp(u) for w,u in zip(ws,us));U=sum(w*u*math.exp(u) for w,u in zip(ws,us))
    D=eps*((rho-1)*(V-1)-U)
    return c*(a*(-math.expm1(-D))+eps*(math.exp(-D)*(d*V-U)-d))
local_checks=0;hardware_checks=0;local_derivatives=0;hardware_derivatives=0
for trial in range(300):
    ds=[r.uniform(.2,1.) for _ in range(14)];rho=sum(ds)
    require(rho>=3,'ratio construction')
    T=r.uniform(.01,.4);q=.5*math.exp(1-rho);eps=q*T;A=1-T
    weights=[r.random()+.1 for _ in range(1+trial%4)];weights=[w/sum(weights) for w in weights]
    if eps*math.e*(rho-1)<=1:
        for _ in range(15):
            d=r.choice(ds);a=A*r.random();us=[d*r.random() for _ in weights]
            gd=gain(d,a,us,weights,rho,eps);gfull=gain(1,a,us,weights,rho,eps)
            require(gd<=gfull+1e-12,'full-cap domination')
            require(gfull<=(a/A)*gain(1,A,us,weights,rho,eps)+1e-12,'hardware convex concentration')
            if rho>=6 and T<=.5 and eps<1/6:
                require(gd<=(a/A)*gain(1,A,[1.]*len(weights),weights,rho,eps)+1e-12,'all-delete optimum')
            jj=trial%len(weights);step=min(1e-5,us[jj]/10,(d-us[jj])/10)
            if step>1e-10:
                up=us.copy();um=us.copy();up[jj]+=step;um[jj]-=step
                numerical=(gain(d,a,up,weights,rho,eps)-gain(d,a,um,weights,rho,eps))/(2*step)
                V=sum(w*math.exp(u) for w,u in zip(weights,us));U=sum(w*u*math.exp(u) for w,u in zip(weights,us))
                D=eps*((rho-1)*(V-1)-U);zp=eps*(d*V-U)
                # For general d the own local derivative is epsilon*e^u*(d-u-1).
                u=us[jj]
                analytic=c*eps*weights[jj]*math.exp(u-D)*((rho-2-u)*(a-zp)+(d-u-1))
                require(abs(numerical-analytic)<=1e-6*eps+1e-11,'local derivative identity')
                local_derivatives+=1
            local_checks+=1
    # One actual hardware-only owner's arbitrary report, using exact aggregate
    # local accounts for this changed branch and fixed outer full total2.
    w=r.choice(weights);Tj=w*T;h0=Tj*r.uniform(.05,.5)
    def hw_pay(h):
        delta=h0-h;t=Tj-delta
        cap=[min(d*Tj,t) for d in ds];R=sum(cap)/t;qq=.5*math.exp(1-R)
        Zold=Tj*(1+q*(rho-1));Znew=t*(1+qq*(R-1))
        H=1-delta;B=2+Znew-Zold;Q=.5*math.exp(1-B/H)
        require(B>=H and R>=rho-1e-10,'hardware orientation')
        return h*(1-Q*qq)
    vals=[hw_pay(h0*j/20) for j in range(21)]
    require(all(x<=y+1e-12 for x,y in zip(vals,vals[1:])),'hardware monotonicity')
    h=.37*h0;delta=h0-h;t=Tj-delta;H=1-delta
    caps=[min(d*Tj,t) for d in ds];R=sum(caps)/t;qq=.5*math.exp(1-R);mc=sum(d*Tj>t for d in ds)
    Zold=Tj*(1+q*(rho-1));Znew=t*(1+qq*(R-1));B=2+Znew-Zold;Ro=B/H;Q=.5*math.exp(1-Ro)
    Zder=1+qq*(R*R-R-1+mc*(2-R))
    qder=qq*(R-mc)/t;Qder=Q*(Ro-Zder)/H
    Nder=1-Q*qq-h*(Qder*qq+Q*qder)
    require(1-1e-12<=Zder<1.5 and Nder>=.375-1e-12,'hardware derivative bounds')
    step=h0*1e-5
    # Avoid comparing across a cap boundary with a formula from just one cell.
    if min(abs(d*Tj-t) for d in ds)>10*step:
        numerical=(hw_pay(h+step)-hw_pay(h-step))/(2*step)
        require(abs(numerical-Nder)<1e-6,'hardware derivative identity')
        hardware_derivatives+=1
    hardware_checks+=20
# Scalar optimizer: bisection on the strictly decreasing derivative, no scipy.
seq=[]
for L in [20.,50.,100.,200.]:
    eps=math.exp(-L);lo=2*math.e**2*eps;hi=1.
    def deriv(T):
        D=eps*(K*math.log(T/(2*eps))-math.e)
        # divide derivative by eps to avoid cancellation at tiny eps.
        return (math.expm1(-D)+math.exp(-D)*K*eps*(1/T-1))/eps
    require(deriv(lo)>0 and deriv(hi)<0,'optimizer endpoint signs')
    for _ in range(150):
        mid=(lo+hi)/2
        if deriv(mid)>0:lo=mid
        else:hi=mid
    T=(lo+hi)/2
    require(0<T<.5 and abs(deriv(T))<1e-8*L,'optimizer stationarity')
    x=1/T;D=eps*(K*math.log(T/(2*eps))-math.e)
    F=c*((1-T)*(-math.expm1(-D))-eps)
    leading=c*K*eps*(L-math.log(L))
    seq.append({'L':L,'T_star':T,'inverse_T_offset':x-L+math.log(L),'second_order_constant':(F-leading)/eps})
print(json.dumps({'status':'PASS','scope':'Floating attempted falsification only; analytic proof load-bearing.','local_report_comparisons':local_checks,'hardware_report_comparisons':hardware_checks,'local_derivative_comparisons':local_derivatives,'hardware_derivative_comparisons':hardware_derivatives,'optimizer_diagnostics':seq,'inverse_T_offset_limit':1-math.log(2)-math.e/K,'second_order_constant_limit':-c*(2*math.e+K*math.log(2))},indent=2))
