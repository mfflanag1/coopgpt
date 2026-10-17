"""Exact finite/log-symbolic obstruction checks. Run python3 -I, never -O."""
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
import json
P=Q(1);private=[Q(3,5),Q(3,5),Q(5,4)];eps=Q(1,50)
lo=(P,*private);hi=(P+eps,private[0]+eps,private[1]+eps,private[2])
A=(Q(0),private[0],private[1],Q(0));outside=(P,Q(0),Q(0),private[2])
D=(eps,eps,eps,Q(0));AA=tuple(a+d for a,d in zip(A,D))
assert tuple(a+b for a,b in zip(A,outside))==lo
assert tuple(a+b for a,b in zip(AA,outside))==hi
for C in (lo,hi):
 p,x,y,h=C;b=x+y
 assert h>b>p
ratios=(hi[0]/(hi[1]+hi[2]),hi[0]/hi[3])
assert ratios==(Q(51,62),Q(102,125))
assert min(ratios)>Q(4,5)
def value(C):
 p,x,y,z=C
 return min(2*p,x+y+z,p+x+y,p+x+z,p+y+z)
assert value(D)==2*eps
assert value(lo)==min(lo[0],sum(lo[1:3]))+min(lo[0],lo[3])
assert value(hi)==min(hi[0],sum(hi[1:3]))+min(hi[0],hi[3])
# exp(9/5)>5 proves gamma<5/9, hence tau>4/5.
partial95=sum((Q(9,5)**k/factorial(k) for k in range(4)),Q(0))
assert partial95==Q(674,125)>5
# exp(5/3)>5 proves log5<5/3. Gamma>1/2 then gives a gap>eps/12.
partial53=sum((Q(5,3)**k/factorial(k) for k in range(5)),Q(0))
assert partial53>5
margin=eps*Q(1,2)*(1-Q(1,2)*Q(5,3))
assert margin==Q(1,600)
out={'status':'PASS','arithmetic':'exact rational; no floating gamma/log values',
     'low':list(map(str,lo)),'high':list(map(str,hi)),
     'same_fixed_owners':True,'restored_bundle':list(map(str,D)),
     'outside_production':str(value(D)),'strict_shortfall_lower_bound':str(margin),
     'ratio_arguments':list(map(str,ratios)),
     'exp_9_5_positive_Taylor_lower_bound':str(partial95),
     'exp_5_3_positive_Taylor_lower_bound':str(partial53),
     'analytic_dependency':'Q(t)=E min(1,U/t), monotone; Q(4/5)=1-gamma+(gamma/4)log5; see note.',
     'scope':'Exact obstruction to logarithmic two-block extension only; no all-mechanism lower.'}
Path(__file__).with_name('TWO_COMMON_FRESH_LOG_OUT_BLOCK_EXACT_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
