from fractions import Fraction as Q
from itertools import product
import json
from verify_double_star import direct

def formula(U,V,Qcap,G,a,b,c):
    plus=lambda x:max(Q(0),x)
    delta=plus(a-b-c)
    alpha=min(b,plus(a-c))
    beta=min(c,plus(a-b))
    gamma=max(Q(0),min(a,b,c,b+c-a))
    return (delta*min(U,V)+alpha*min(U,V+Qcap)+beta*min(V,U+G)
      +gamma*min(U+G,V+Qcap,U+V)
      +plus(b-a)*min(U,Qcap)+plus(c-a)*min(V,G))
checks=0
for a,b,c in product(map(Q,[1,2,3,4,5]),repeat=3):
    for U,V,Qcap,G in product(map(Q,[0,1,2,3]),repeat=4):
        oracle=direct(U,V,(Qcap,),(G,),(b,),(c,),a)
        candidate=formula(U,V,Qcap,G,a,b,c)
        if oracle!=candidate:raise RuntimeError((a,b,c,U,V,Qcap,G,oracle,candidate))
        checks+=1
print(json.dumps({'status':'PASS','exact_rational_checks':checks,
 'scope':'all weighted three-edge path positive decomposition; finite corroboration'},indent=2))
