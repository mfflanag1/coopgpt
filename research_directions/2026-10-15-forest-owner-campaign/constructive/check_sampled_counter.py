from fractions import Fraction as Q
from itertools import product
c=[Q(99,100),Q(1),Q(99,100),Q(1),Q(99,100)]
covers=[(1,3),(0,2,3),(1,2,4),(0,2,4)]
q=Q(1,100);p=1-q;T=Q(2)
Z=Q(0);g=Q(0);mm=[Q(0)]*5
for bits in product([0,1],repeat=5):
 vals=[sum((c[i]*bits[i] for i in C),Q(0)) for C in covers]
 k=min(range(4),key=lambda j:vals[j])
 prob=p**sum(bits)*q**(5-sum(bits))
 Z+=prob*sum((c[i] for i in covers[k]),Q(0));g+=prob*vals[k]
 for i in range(5):
  if not bits[i]:
   on=min(sum((c[j]*(bits[j] or j==i) for j in C),Q(0)) for C in covers)
   mm[i]+=prob/q*(on-vals[k])
R=Z-g+p*sum(mm)
print('T',T,'q',q,'Z',Z,'Z/T',Z/T,float(Z/T),'1/p',1/p,'difference',Z/T-1/p)
print('g',g,'R/T',R/T,float(R/T))
if not Z/T>1/p:
 raise ValueError("proposed sampled-cover bound was not refuted")

print('exact sampled-cover counterexample PASS')
