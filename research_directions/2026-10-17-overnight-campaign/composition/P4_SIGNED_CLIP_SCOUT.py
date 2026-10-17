import numpy as np
c=.5430633898250876;t0=1/c-1

def q(r):
    if r>t0:return c/r
    return 1-c-c*(1-r)*np.log1p(-r)/r

def pair(a,b):
    if a>=b:return np.array([c*b/a,q(b/a)])
    p=pair(b,a);return p[::-1]

def rawprices(x):
    a,b,cc,d=x;p=np.zeros(4)
    u,v=pair(b,a+cc);p[1]+=u;p[[0,2]]+=v
    u,v=pair(cc,b+d);p[2]+=u;p[[1,3]]+=v
    p[[0,1]]+=pair(a,b);p[[2,3]]+=pair(cc,d)
    return p/2

def prices(x):
    f=min(x[0]+x[2],x[1]+x[3],x[1]+x[2])
    return np.minimum(f/x,rawprices(x))

def check(x):
    p=prices(x);J=np.empty((4,4))
    for j in range(4):
        h=1e-5*x[j];delta=np.zeros(4);delta[j]=h
        J[:,j]=(prices(x+delta)-prices(x-delta))/(2*h)
    vals=[]
    for js in [(0,), (1,), (2,), (3,), (0,1),(1,2),(2,3)]:
        v=p[list(js)].sum()+sum(x*np.minimum(0,J[:,list(js)].sum(axis=1)))
        vals.append(v-(len(js)==2))
    f=min(x[0]+x[2],x[1]+x[3],x[1]+x[2])
    return min(vals),vals,p,J,x@p/f
rng=np.random.default_rng(7436);worst=(1,None);fund=(0,None);mono=(1,None)
for k in range(10000):
    x=np.exp(rng.uniform(-7,7,4));value,vals,p,J,kappa=check(x)
    if min(vals[:4])<mono[0]:mono=(min(vals[:4]),x)
    if min(vals[4:])<worst[0]:worst=(min(vals[4:]),x)
    if kappa>fund[0]:fund=(kappa,x)
print('worst edge',worst,'worst mono',mono,'maxfund',fund,'scaledbound',fund[0]/(1+worst[0]))
