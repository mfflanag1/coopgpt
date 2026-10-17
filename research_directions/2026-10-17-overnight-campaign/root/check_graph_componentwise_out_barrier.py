from fractions import Fraction as Q
from itertools import product
import json
edges=[(0,1),(0,3),(2,3)]
profiles=[tuple(map(Q,[20,19,10,9])),(Q(199,10),Q(19),Q(10),Q(89,10))]
def F(c):
 return min(sum(c[i]*z[i]/2 for i in range(4)) for z in product(range(3),repeat=4) if all(z[i]+z[j]>=2 for i,j in edges))
for C in profiles:
 t1=C[1]/C[0];t2=C[3]/C[2]
 assert Q(89,100)<=t2<t1<1
 p=(t1/2,1-t1/2,t2/2,1-t2/2)
 assert all(p[i]+p[j]>=1 for i,j in edges)
 assert p[0]+p[3]>1
 assert F(C)==C[1]+C[3]
 # Sharp binary logarithmic law on this entire region: ell=c*t, s=c/t.
 # Track coefficient of the fixed positive constant c exactly.
 payment_coefficient=C[0]*t1+C[3]/t2
 assert payment_coefficient==29
withdraw=tuple(a-b for a,b in zip(profiles[0],profiles[1]))
assert F(withdraw)==Q(1,10)
print(json.dumps({'status':'PASS','arithmetic':'Fraction, symbolic common factor c','payment_coefficient_both_profiles':'29','withheld_production':'1/10','scope':'exact finite failure of componentwise sharp two-pool OUT transform'}))
