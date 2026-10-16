"""Exact scalar certificate for mixed-envelope intermediate F=H bound.
Uses Fraction arithmetic, a proved Taylor lower bound, and interval quadratics.
No grid sampling is used to establish the universal inequality.
"""
from fractions import Fraction as F
from math import factorial
import json

def exp_neg_lower(x):
    bound=sum(((-x)**k/F(factorial(k)) for k in range(12)),F(0))
    return F((bound*10**6).__floor__(),10**6)

def quad_max(a,b,c,l,u):
    candidates=[(l,a*l*l+b*l+c),(u,a*u*u+b*u+c)]
    if a<0:
        t=-b/(2*a)
        if l<=t<=u:candidates.append((t,a*t*t+b*t+c))
    return max(candidates,key=lambda p:p[1])

def run():
    # e > 125/46 implies C=1+1/(2e)<148/125.
    e_lower=sum((F(1,factorial(k)) for k in range(8)),F(0))
    if not e_lower>F(125,46):raise RuntimeError('C bound failed')
    records=[]
    intervals=[(F(1,4),F(1,2)),(F(1,2),F(5,8)),(F(5,8),F(3,4)),(F(3,4),F(7,8)),(F(7,8),F(1))]
    for l,u in intervals:
        if u<=F(1,2):
            # Convexity on [1/4,1/2]: tangent at1/2 is (4p-1)/e.
            e1=exp_neg_lower(F(1)); A=4*e1; B=-e1
            label='tangent at1/2'
        else:
            # Concavity on [1/2,1]: chord between exact endpoint values.
            fl=exp_neg_lower(1/l-1); fu=exp_neg_lower(1/u-1)
            A=(fu-fl)/(u-l); B=fl-A*l
            label='endpoint chord'
        mid=(l+u)/2
        # e^(-p-23/125) >= e^(-mid-23/125)*(1+mid-p).
        em=exp_neg_lower(mid+F(23,125))
        # W <=3/2+p - (p+1/2)(A*p+B)/2 -79/500*em*(1+mid-p).
        a=-A/2
        b=1-B/2-A/4+F(79,500)*em
        c=F(3,2)-B/4-F(79,500)*em*(1+mid)
        where,value=quad_max(a,b,c,l,u)
        if not value<F(7,4):raise RuntimeError(f'interval failed {l,u}: {value}')
        records.append({'interval':[str(l),str(u)],'lower_bound':label,'f_lower_slope':str(A),'f_lower_intercept':str(B),'exponential_at_midpoint_lower':str(em),'maximizer':str(where),'quadratic_max':str(value),'decimal_diagnostic':float(value),'exact_gap':str(F(7,4)-value)})
    return {'status':'pass','scope':'universal scalar inequality, assuming the accompanying analytic reductions and elementary exp/convexity lemmas','C_upper':'148/125','e_lower':str(e_lower),'domain':'p in[0,1]; p<=1/4 follows from W<=3/2+p; remaining intervals covered below','records':records}

if __name__=='__main__':print(json.dumps(run(),indent=2))
