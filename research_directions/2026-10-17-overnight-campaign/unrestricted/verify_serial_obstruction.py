if not __debug__:
    raise RuntimeError('Run this exact checker without Python -O; assertions are required.')
from fractions import Fraction as Q
from itertools import combinations
import json

def require(ok,msg):
    if not ok:raise RuntimeError(msg)
out=[]
for m in range(2,101):
    k=2*m;n=k+m;alpha=Q(1,k*k);M=k**3
    T=min(alpha*(k+m*M),Q(k))
    first=min(alpha*n,Q(k));small=first/n;large=small+(T-first)/m
    worth=min(alpha*(k+M),Q(k-m+1));paid=k*small+large
    require(T==k,'grand value');require(small==alpha,'small payment')
    require(large==Q(k,m)*(1-alpha),'large payment')
    require(k*small+m*large==T,'efficiency');require(worth==m+1,'worth')
    ratio=worth/paid
    target=Q(m+1)/(2+Q(1,2*m)*(1-Q(1,m)))
    require(ratio==target,'ratio');require(ratio>Q(n,6),'linear bound')
    out.append({'m':m,'n':n,'ratio':str(ratio)})
require(out[0]['ratio']=='24/17','small witness')
print(json.dumps({'status':'PASS_EXACT_IDENTITIES','cases':len(out),'first':out[0],'last':out[-1],
 'scope':'Exact finite checks of an analytic unbounded family, not unrestricted-mechanism impossibility.'},indent=2))
