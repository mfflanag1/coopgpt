"""Exact local polynomial checks for the adaptive-mixture rigidity proof.
Analytic compactness/variation proof remains in the text, not inferred from tests.
"""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json

def add(a,b):
 n=max(len(a),len(b));return [(a[k] if k<len(a) else 0)+(b[k] if k<len(b) else 0) for k in range(n)]
def mul(a,b):
 c=[Q(0)]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):c[i+j]+=x*y
 return c
def scale(a,c):return [c*x for x in a]
def bernstein(n,k):return [Q(0)]*k+[Q((-1)**j*comb(n-k,j)) for j in range(n-k+1)]
def pad(a,n):return a+[Q(0)]*(n-len(a))
def marginal_polynomial(b,i,worth):
 n=len(b);out=[Q(0)]*n;others=[j for j in range(n) if j!=i]
 for mask in range(1<<(n-1)):
  subset=[others[j] for j in range(n-1) if mask>>j&1]
  gain=worth([b[j] for j in subset+[i]])-worth([b[j] for j in subset])
  out=add(out,scale(bernstein(n-1,mask.bit_count()),gain))
 return out

def basis(k):return [Q(0)]+[Q((-1)**j*comb(k,j)) for j in range(k+1)]
def basis_coordinates(poly,D):
 rem=pad(poly[:],D+1);co=[Q(0)]*(D+1)
 for degree in range(D,0,-1):
  f=pad(basis(degree-1),D+1);co[degree]=rem[degree]/f[degree]
  rem=add(rem,scale(f,-co[degree]))
 co[0]=rem[0];assert all(x==0 for x in rem[1:])
 reconstructed=[co[0]]+[Q(0)]*D
 for degree in range(1,D+1):reconstructed=add(reconstructed,scale(pad(basis(degree-1),D+1),co[degree]))
 assert reconstructed==pad(poly,D+1)
 return co

def min2(rows):return min((sum((row[j] for row in rows),Q(0)) for j in [0,1]),default=Q(0))

def threshold_checks():
 count=0;max_degree=0
 for q in range(2,6):
  for k in range(1,5):
   for t in range(k):
    low=[[Q(1,k),Q(0)] for _ in range(k)]+[[Q(0),Q(t,k)]]+[[Q(0),Q(1)] for _ in range(q-1)]
    high=[r[:] for r in low];high[k][1]+=Q(1,k)
    lo=[Q(0)]*(k+q);hi=lo[:]
    for i in range(k,k+q):
     lo=add(lo,marginal_polynomial(low,i,min2));hi=add(hi,marginal_polynomial(high,i,min2))
    delta=add(hi,scale(lo,-1))
    h=mul([Q((-1)**j*comb(q-2,j)) for j in range(q-1)],[Q(1),Q(-q)])
    tail=[Q(0)]*(k+1)
    for j in range(t+1,k+1):tail=add(tail,scale(bernstein(k,j),comb(k,j)))
    expected=scale(mul(h,tail),Q(1,k))
    assert pad(delta,k+q)==pad(expected,k+q)
    D=k+q-1
    basis_coordinates(lo,D);basis_coordinates(hi,D)
    count+=1;max_degree=max(max_degree,D)
 return dict(exact_threshold_tests=count,max_degree=max_degree,all_basis_reconstructions_passed=True)

def star_worth(rows):
 if not rows:return Q(0)
 return min(sum((r[0] for r in rows),Q(0)),sum((r[1] for r in rows),Q(0)))
def sentinels():
 for k in range(8):
  rows=[[Q(1),Q(0)]]+[[Q(0),Q(1)] for _ in range(k+1)]
  actual=marginal_polynomial(rows,1,star_worth)
  assert actual==pad(basis(k),k+2)
 return dict(exact_sentinels=8)

def scales():
 rows=[]
 for N in [1,2,3,10,100]:
  D=7;T=12;L=N*N*T;A=N*(D*L+N*T+1)
  assert Q(A+D*L+N*T+1,A)==1+Q(1,N)
  e=Q(D+1)*(Q(1,N)+Q(2*T,L))
  assert e==Q(D+1)*(Q(1,N)+Q(2,N*N))
  rows.append(dict(N=N,L=L,A=A,variation_over_B=str(e)))
 return rows

if __name__=='__main__':
 result=dict(status='PASS',threshold=threshold_checks(),sentinels=sentinels(),scales=scales(),scope='Exact polynomial/scaling ingredients only; analytic proof separately audited.')
 Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
