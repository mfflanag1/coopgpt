if not __debug__:
    raise RuntimeError('Run this exact checker without Python -O; assertions are required.')
from fractions import Fraction as Q
import json
def require(ok,msg):
    if not ok:raise RuntimeError(msg)
rows=[]
for m in range(2,22,2):
    edges=[(0,1,2),(0,1,3),(0,2,3)];z=[-2,1,1,1];cur=1;defining=(0,1,2)
    for j in range(m):
        uv=[v for v in defining if v!=cur];require(len(uv)==2,'defining edge')
        dup=len(z);z.append(z[cur]);edges.append(tuple(uv+[dup]))
        nxt=len(z);z.append(-2*z[cur]);edges.append((cur,dup,nxt));cur=nxt;defining=edges[-1]
    a=2**m;require(z[cur]==a,'positive final amplitude')
    require(len(edges)==len(z)-1 and len(set(map(frozenset,edges)))==len(edges),'simple n-1 edges')
    require(all(sum(z[v] for v in e)==0 for e in edges),'incidence kernel')
    omega=[a*a]+[1]*(len(edges)-1);c=[sum(omega[j] for j,e in enumerate(edges) if v in e) for v in range(len(z))]
    require(min(c)>0,'positive capacity');require(sum(x*y for x,y in zip(c,z))==0,'weighted orthogonality')
    norm=sum(c[v]*z[v]**2 for v in range(len(z)));positive=sum(c[v]*z[v] for v in range(len(z)) if z[v]>0)
    require(norm==Q(17,2)*a*a+14,'exact geometric norm')
    require(positive>=2*a*a,'positive mass')
    R=Q(a*positive,norm);require(R>=Q(16,75)*a and R>Q(a,5),'unbounded projection mass')
    # For the quadratic regularizer h=t^2, h'/h''=1/3 at t0.
    derivative=(1-R)/3
    rows.append({'m':m,'resources':len(z),'activities':len(edges),'amplitude':a,'positive_projection_mass':str(R),'quadratic_payment_derivative':str(derivative)})
print(json.dumps({'status':'PASS_EXACT_FAMILY_IDENTITIES','instances':len(rows),'first':rows[0],'last':rows[-1]},indent=2))
