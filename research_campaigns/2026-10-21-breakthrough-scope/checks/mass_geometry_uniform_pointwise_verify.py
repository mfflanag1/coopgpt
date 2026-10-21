#!/usr/bin/env python3
"""Exact complete-row certificate for uniform-full normalized inflation."""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import json

focal=0
A=tuple(range(1,6))
B=tuple(range(6,13))
G=(focal,)+A
rows=[G]+list(combinations(B,6))+[(focal,a)+D for a in A for D in combinations(B,4)]
assert len(rows)==183 and len(set(rows))==183 and all(len(r)==6 for r in rows)
full=[F(1,6)]*13
changed=[F(5,18)]+[F(1,18)]*5+[F(1,6)]*7
lam_full=[F(1,6)]+[F(1,36)]*7+[F(0)]*175
lam_changed=[F(0)]+[F(1,756)]*7+[F(1,630)]*175

for q,lam,rhs in [(full,lam_full,[F(1)]*183),
                  (changed,lam_changed,[F(0)]+[F(1)]*182)]:
    for r,row in enumerate(rows):
        payment=sum(q[j] for j in row)
        assert payment>=rhs[r]
        assert lam[r]>=0
        assert lam[r]*(payment-rhs[r])==0
    for j in range(13):
        assert q[j]==sum(lam[r] for r,row in enumerate(rows) if j in row)
    assert sum(x*x for x in q)==sum(lam[r]*rhs[r] for r in range(len(rows)))

rho=sum(x*x for x in full)
L=sum(lam_changed)
p=full[focal]/rho
theta=changed[focal]/L
assert rho==F(13,36) and L==F(31,108) and p==F(6,13)
assert theta==F(30,31) and theta-2*p==F(18,403)>0
w=[x/L for x in changed]
t=1/L
assert all(sum(w[j] for j in row)==t for row in rows[1:])
assert sum(x*x for x in w)==t

sample=[]
for s in range(2,101):
    k,n=s*s,s**3
    na,nb=k-1,(s-1)*k
    qi,qa,qb=F(s+1,2*k),F(1,2*k),F(1,k)
    lm,lb=qi,F((s-1)**2,2*s**3)
    assert lm*F(s-1,na)==qa
    assert lm*F(k-s,nb)+lb*F(k,nb)==qb
    assert qi+(s-1)*qa+(k-s)*qb==k*qb==1
    assert qi+na*qa==F(s+1,2*s)
    mass=lm+lb
    assert mass==qi*qi+na*qa*qa+nb*qb*qb
    theta_s=qi/mass
    assert theta_s==F(s*(s+1),2*s*s-s+1)
    if s>=3:
        assert theta_s>F(2,s)
    H=F(1,s)*(theta_s**2+F(n-1,s*s))
    assert H==1-F(1,s**3)+theta_s**2/s
    if s in [2,3,5,10,20,50,100]:
        sample.append(dict(s=s,n=n,theta=str(theta_s),p=str(F(1,s)),
                           inflation=str(theta_s*s),chosen_H=str(H)))
result=dict(status='PASS',rows=183,owners=13,
            rho=str(rho),L=str(L),p=str(p),theta=str(theta),
            theta_minus_2p=str(theta-2*p),inflation=str(theta/p),
            full_q=[str(x) for x in full],changed_q=[str(x) for x in changed],
            all_rows=[list(row) for row in rows],
            full_lambda=[str(x) for x in lam_full],
            changed_lambda=[str(x) for x in lam_changed],
            family_samples=sample,
            scope='Pointwise bound false; aggregate H<=4 is not refuted.')
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in
                 ['all_rows','full_lambda','changed_lambda']},indent=2))
