if not __debug__:
    raise RuntimeError('Run this exact checker without Python -O; assertions are required.')
from fractions import Fraction as Q
import json
def require(ok,msg):
    if not ok:raise RuntimeError(msg)
table=[]
for D in range(1,31):
    c=[Q(1)]+[Q(2)]*(D-1)+[Q(1)]
    z=[Q(-1,2)**l for l in range(D+1)]
    require(all(z[l]+2*z[l+1]==0 for l in range(D)),'edge tangent')
    require(sum((-1)**l*c[l] for l in range(D+1))==0,'base stationarity')
    norm=sum(c[l]/2**l for l in range(D+1));require(norm==3*(1-Q(1,2**D)),'geometric norm')
    W=sum(c[l] for l in range(0,D+1,2));require(W==D,'even capacity coefficient')
    derivative=Q(1,3)-Q(1,3)*W/norm
    if D>=3:require(derivative<0,'Huber strict local loss')
    table.append({'depth':D,'resources':2**(D+1)-1,'positive_projection_mass':str(W/norm),'huber_derivative':str(derivative)})
D=3;cp=[Q(2),Q(2),Q(2),Q(1)]
p=[Q(x,29) for x in (7,11,9,10)];lam=[Q(x,29) for x in (28,16,20)]
require(all(0<x<Q(1,2) for x in p),'strict quadratic prices')
require(all(p[l]+2*p[l+1]==1 for l in range(D)),'tight activities')
for l in range(D+1):
    incident=(lam[l-1] if l>0 else 0)+(lam[l] if l<D else 0)
    require(incident==2*cp[l]*p[l],'full KKT at level')
old=Q(3);new=cp[0]*p[0]+4*cp[2]*p[2]
require(new==Q(86,29) and old-new==Q(1,29),'exact mixed-owner loss')
print(json.dumps({'status':'PASS_EXACT_TREE_AND_KKT_IDENTITIES','depths':len(table),
 'first_huber_failure':table[2],'last':table[-1],
 'depth3_old_payment':str(old),'depth3_new_payment':str(new),'underreport_gain':'1/29'},indent=2))
