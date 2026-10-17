import numpy as np
c=.5430633898250876
t0=1/c-1

def q(r):
    if r>t0:return c/r
    return 1-c-c*(1-r)*np.log1p(-r)/r

def prices(x):
    a,b,cc,d=x; l=a+cc; r=b+d
    return np.array([q(max(a/b,l/r)),q(min(r/l,b/a)),q(min(l/r,cc/d)),q(max(d/cc,r/l))])

def check(x):
    p=prices(x)
    J=np.empty((4,4))
    for j in range(4):
        h=1e-6*x[j]; delta=np.zeros(4);delta[j]=h
        J[:,j]=(prices(x+delta)-prices(x-delta))/(2*h)
    vals=[]
    for js in [(0,), (1,), (2,), (3,), (0,1),(1,2),(2,3)]:
        v=p[list(js)].sum()+sum(x*np.minimum(0,J[:,list(js)].sum(axis=1)))
        vals.append(v-(len(js)==2))
    return min(vals),vals,p,J
rng=np.random.default_rng(563)
worst=(1,None)
for k in range(5000):
    x=np.exp(rng.uniform(-4,4,4)); value,vals,p,J=check(x)
    if value<worst[0]:worst=(value,x)
    if value<-.00001:
        print('FAIL',x, 'margin',value,'all',vals,'prices',p);break
else:print('PASS numeric',worst)
