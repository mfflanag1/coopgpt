#!/usr/bin/env python3
from fractions import Fraction as Q
if not __debug__:raise RuntimeError('Run without -O')
n=5
A=[[int((j-r)%n in (0,1,2)) for j in range(n)] for r in range(n)]
q=[Q(5,6),Q(13,12),Q(5,6),Q(13,12),Q(13,12)]
lam=[Q(1,36),Q(19,36),Q(5,18),Q(5,18),Q(19,36)]
assert min(lam)>0
assert [sum(A[r][j]*q[j] for j in range(n)) for r in range(n)]==[Q(11,4),3,3,3,3]
assert [sum(A[r][j]*lam[r] for r in range(n)) for j in range(n)]==q
assert 5*Q(13,12)**2>5*Q(13,12)
for s in range(n):
 qr=[q[(j-s)%n] for j in range(n)]
 lr=[lam[(r-s)%n] for r in range(n)]
 assert qr[(s+1)%n]==Q(13,12)
 assert [sum(A[r][j]*lr[r] for r in range(n)) for j in range(n)]==qr
 assert [sum(A[r][j]*qr[j] for j in range(n)) for r in range(n)]==[Q(11,4) if r==s else Q(3) for r in range(n)]
print('PASS: all five rotated exact KKT witnesses and aggregate inequality')
