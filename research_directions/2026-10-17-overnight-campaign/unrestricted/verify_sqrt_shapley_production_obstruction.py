from fractions import Fraction as Q
from math import comb,prod
if not __debug__:raise RuntimeError('Run without -O; assertions are required.')
k,m,ell=2,40,5
D=prod(Q(ell+j,m+1+j) for j in range(k+1))
a=1-Q(ell,m+1)+D/(k+1);b=D/(k+1);d=1-a-4*b
assert D==Q(5,1763) and a==Q(4649,5289) and b==Q(5,5289)
assert d==Q(620,5289)>0 and d*d-16*a*b==Q(4160,9324507)>0
print({'n':43,'veto_phi':str(a),'each_A_phi':str(b),'coverage_ratio':float(a)**.5+2*float(b)**.5})
for r in range(5,11):
 k=2**r;m=k*k;ell=m-4*r*k
 assert 0<ell<=m
 D=prod(Q(ell+j,m+1+j) for j in range(k+1))
 assert D<=Q(ell+k,m+1+k)**(k+1)
 assert Q((4*r*k+1)*(k+1),k*k+k+1)>=3*r
 assert D<Q(1,k**3)
 assert 1-Q(ell,m+1)<=Q(4*r+1,k)
 a=1-Q(ell,m+1)+D/(k+1);b=D/(k+1)
 print({'r':r,'n':1+k+m,'coverage_ratio':float(a)**.5+k*float(b)**.5})
t=16
center=1-sum(Q((-1)**j*comb(t,j),t*j+1) for j in range(t+1))
assert 0<center<Q(1,4)
print({'pointwise_counter_t':t,'center_phi':float(center),'projection_coordinate_square':.25,'status':'PASS'})
