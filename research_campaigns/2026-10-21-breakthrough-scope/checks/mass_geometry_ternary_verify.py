#!/usr/bin/env python3
"""Independent exact scalar replay of the ternary-cube proof; stdlib only.
This verifies the parameter inequalities, not an enumeration of the enormous
row family. Coverage of all rows and all transport cuts is proved in the audit.
"""
from fractions import Fraction as F
from math import isqrt
import json
from pathlib import Path

D=10000
h=D//5
n=3**D
q=n//3
m=n-2*D-1
K=(601*m)//1000
beta=F(K,m); b=1-beta
s=D+h+K;k=n-s
r=F(49,100);a=F(2,5)
x=F(h,D);y=F(h*(h-1),D*(D-1))
e=2*D*(D-1)
f=(q-1-D*(D-1),q-D-D*(D-1)//2,q-D-D*(D-1)//2)
checks={}
def check(name,condition):
    checks[name]=bool(condition)
    assert condition,name
check('d divisible by five',D%5==0)
check('far counts sum',sum(f)==m-e)
check('far counts positive',min(f)>0)
Pmix=F(2,3)*(1-x*r)
Psame=F(2,3)-(2*x*(1-r)-y*(1-r)**2)/3
check('mixed probability exact',Pmix==F(451,750))
check('mixed margin',Pmix>F(601,1000)>=beta)
check('same-sign margin',Psame>F(601,1000)>=beta)
check('beta range',F(3,5)<beta<=F(601,1000)<F(2,3))
check('Q lower cut (i)',K-e>=max(f))
check('Q upper cut (ii)',K<=min(f[i]+f[j] for i in range(3) for j in range(i+1,3)))
check('two-color cuts (iii)',all(K-e>=(3*beta-1)*(f[i]+f[j]) for i in range(3) for j in range(i+1,3)))
check('singleton cuts (iv)',beta<=F(2,3))
check('expected far size',K-e*beta==beta*sum(f))
check('row cardinality',k==1+D-h+m-K)
t=1+(D-h)*a+(m-K)*b
check('support norm identity',t==1+2*D*a*a+m*b*b)
gap=h*(beta-F(3,5))-beta
check('off-row gap identity',D*a+(k-D)*b-t==gap)
check('strict all-off gap',gap>0)
rho=F(n,k*k);ell=1/t
check('minnorm hull Cauchy',t>=F(k*k,n))
check('mass upper bound',ell<=rho)
check('row below half',2*k<n)
H=F(n*n,k*k);J=F(n,k)
check('H greater than four',H>4)
check('J greater than two',J>2)
# Common-veto amplification. Each of M*n private owners has selected witness
# ell/[1+(M-1)rho+ell]. Its row RHS is lifted as u+(1-u)*base_rhs.
M=(n-3)//6
check('M integral',6*M==n-3)
N=M*n+1
private=M*n*ell/(1+(M-1)*rho+ell)
veto=M*rho/(1+M*rho)
check('rho convenient upper',rho<=F(1000000,159201*n))
check('ell convenient lower',ell>=F(25,4*n+21))
check('funding elementary integer margin',139226*n>64939476)
check('private funding above n/2',private>F(n,2))
check('N below n2/6',6*N<n*n)
check('squared funding ratio above 3/2',private*private>F(3,2)*N)
check('total above sqrt N',(private+veto)**2>N)

def interval(value,scale=10**9):
    a=(value.numerator*scale)//value.denominator
    return [str(F(a,scale)),str(F(a+1,scale))]
ratio_squared=(private+veto)**2/N
scale=10**9
rlo=isqrt((ratio_squared.numerator*scale*scale)//ratio_squared.denominator)
result={
 'status':'PASS', 'd':D, 'h':h, 'n_definition':'3^10000',
 'block_count':'(n-3)/6','owner_count':'n*(n-3)/6+1',
 'checks':checks, 'beta_interval':interval(beta),
 'exceptional_mixed_probability':str(Pmix),'exceptional_same_probability':str(Psame),
 'off_row_gap_interval':interval(gap),
 'H_interval':interval(H),'J_interval':interval(J),
 'squared_selected_funding_ratio_interval':interval(ratio_squared),
 'selected_funding_ratio_interval':[str(F(rlo,scale)),str(F(rlo+1,scale))],
 'proof_scope':'Exact scalar replay; combinatorial all-row and all-cut coverage proved separately.'}
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
