"""Direct finite-mask checks for actual fixed direct-sum technology."""
from itertools import product
from fractions import Fraction as Q
from math import comb
import json
from pathlib import Path
counts={'profiles':0,'conditional_masks':0,'relative_caps':0,'endpoint_differences':0,'budget_equalities':0}
def require(v):
    if not v:raise AssertionError('direct selector check failed')
for n in range(2,9):
    m=1
    while m*(m-1)<2*(n-1):m+=1
    d=n*m
    def f(x):return sum(sum(sorted(x[t*n:(t+1)*n])[:t+1]) for t in range(m))
    for k in range(1,m+1):
        b=[]
        for i in range(n):
            bi=[Q(0)]*d;bi[(k-1)*n+i]=Q(1);b.append(tuple(bi))
        counts['profiles']+=1
        grand=tuple(sum(bi[e] for bi in b) for e in range(d));T=f(grand);require(T==k)
        for q in (Q(0),Q(1,7),Q(1,2),Q(1)):
            R=Q(0)
            for i in range(n):
                others=[j for j in range(n) if j!=i];P=Q(0);M=Q(0)
                for bits in product((0,1),repeat=n-1):
                    x=tuple(sum(bit*b[j][e] for bit,j in zip(bits,others)) for e in range(d))
                    outside=any(b[i][e]>0 and x[e]==0 for e in range(d));require(outside)
                    # By the definition of extended relative support, the own
                    # bundle lies outside the selected aggregate's support face.
                    capped=T
                    y=tuple(x[e]+b[i][e] for e in range(d));delta=f(y)-f(x)
                    closed=n-1-sum(bits);prob=q**closed*(1-q)**sum(bits)
                    P+=prob*capped;M+=prob*delta
                    require(delta==(1 if closed<=k-1 else 0))
                    counts['conditional_masks']+=1;counts['relative_caps']+=1;counts['endpoint_differences']+=1
                require(P==T)
                R+=q*P+(1-q)*M
            tail=sum(Q(comb(n-1,c))*q**c*(1-q)**(n-1-c) for c in range(k))
            require(R/T==n*q+Q(n,k)*(1-q)*tail);counts['budget_equalities']+=1
out={'status':'pass','arithmetic':'exact rational','counts':counts,'scope':'direct fixed-technology mask enumeration; no asymptotic or novelty inference'}
Path(__file__).with_name('RELATIVE_SELECTOR_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
