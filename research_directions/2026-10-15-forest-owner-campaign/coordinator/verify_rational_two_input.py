"""Independent finite checks of rational mixed-owner payments; no tolerances.
These finite checks supplement, and do not replace, the all-profile proof.
"""
from fractions import Fraction as Q
from itertools import product
from math import factorial
import json
from pathlib import Path

def require(x, message):
    if not x:
        raise RuntimeError(message)

def ek(u,k):
    return sum((u**j/Q(factorial(j)) for j in range(k+1)),Q(0))

def payments(rows,k):
    totals=tuple(sum(r[j] for r in rows) for j in (0,1))
    t=min(totals)
    if not t:
        return (Q(0),)*len(rows)
    s=0 if totals[0]<=totals[1] else 1
    d=[min(r[1-s],t) for r in rows]
    u=sum(d)/t-1
    p=1/(2*ek(u,k))
    return tuple((1-p)*r[s]+p*di for r,di in zip(rows,d))

def run(n,levels,k):
    profiles=list(product(levels,repeat=2*n))
    y={}
    count=dict(profiles=0,coalitions=0,increases=0,budgets=0)
    delta=Q(3,2)**(k+1)/factorial(k+1)
    if k==1:
        bound=Q(3,2)
    elif k==2:
        # b=21/100: min_u b(1+u+u^2/2)-u/2>0 by completing the square.
        b=Q(21,100)
        require(b-(b-Q(1,2))**2/(2*b)>0,'invalid quadratic certificate')
        bound=1+b
    else:
        require(delta<1,'invalid Taylor denominator')
        e_lower=sum((Q(1,factorial(j)) for j in range(13)),Q(0))
        bound=1+1/(2*e_lower*(1-delta))
    for profile in profiles:
        rows=tuple(tuple(Q(v) for v in profile[2*i:2*i+2]) for i in range(n))
        ys=payments(rows,k); y[profile]=ys
        require(all(v>=0 for v in ys),'negative payment')
        total=min(sum(r[0] for r in rows),sum(r[1] for r in rows))
        require(sum(ys)<=bound*total,'budget failure')
        count['budgets']+=1;count['profiles']+=1
        for mask in range(1<<n):
            worth=min(sum(rows[i][j] for i in range(n) if mask>>i&1) for j in (0,1))
            require(sum(ys[i] for i in range(n) if mask>>i&1)>=worth,'coalition failure')
            count['coalitions']+=1
    for profile in profiles:
        for j,v in enumerate(profile):
            pos=levels.index(v)
            if pos+1==len(levels):continue
            nxt=list(profile);nxt[j]=levels[pos+1]
            require(y[tuple(nxt)][j//2]>=y[profile][j//2],'whole-owner monotonicity failure')
            count['increases']+=1
    return dict(k=k,n=n,levels=list(map(str,levels)),factor_certificate=str(bound),**count)

def main():
    results=[run(n,levels,k) for k in (1,2,4,6,10) for n,levels in ((3,(Q(0),Q(1),Q(2))),(4,(Q(0),Q(1))))]
    output=dict(status='PASS',arithmetic='exact rational; no assertions or tolerances',checks=results,limitation='Finite checks supplement the analytic all-profile proof.')
    print(json.dumps(output,indent=2))
if __name__=='__main__':main()
