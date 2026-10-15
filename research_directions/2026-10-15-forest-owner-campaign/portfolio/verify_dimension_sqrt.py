"""Exact checks of the coordinate and Bernoulli identities in the dimension proof."""
from fractions import Fraction as Q
from itertools import product
from math import comb
from pathlib import Path
import random
import json

C={};rng=random.Random(20261015)
def chk(ok,key):
    if not ok: raise AssertionError(key)
    C[key]=C.get(key,0)+1
def mask_weight(B,q):
    s=sum(B);return (1-q)**s*q**(len(B)-s)
def cap_ratio(u,s):
    return Q(0) if not u else Q(1) if not s else min(u/s,Q(1))
def dot(w,b):return sum(x*y for x,y in zip(w,b))
def integrate_mask(B,a,extra_closed=False):
    # Integral q^(n-|B|)(1-q)^|B| on [0,a], exact polynomial expansion.
    n=len(B);s=sum(B);z=n-s
    return sum(Q((-1)**j*comb(s,j))*a**(z+j+1)/Q(z+j+1) for j in range(s+1))

for n in range(1,10):
    for case in range(16):
        u=[Q(rng.randrange(8),rng.randrange(1,6)) for _ in range(n)]
        if case==0:u=[Q(0)]*n
        if case==1:u=[Q(1)]*n
        for q in (Q(1,2),Q(1,3),Q(1,5),Q(2,5)):
            lhs=Q(0);recip=Q(0);positive=Q(0)
            for B in product((0,1),repeat=n):
                s=sum(x for bit,x in zip(B,u) if bit);prob=mask_weight(B,q)
                lhs+=prob*sum(cap_ratio(x,s) for bit,x in zip(B,u) if not bit)
                recip+=prob*sum(x/(x+s) if x else Q(0) for bit,x in zip(B,u) if not bit)
                positive+=prob*bool(s)
            chk(recip==q/(1-q)*positive,'scalar_size_bias_identity')
            chk(lhs<=2*q/(1-q)*positive,'scalar_reciprocal_bound')

examples=[]
for n in range(1,7):
    for d in range(1,5):
        for case in range(12):
            W=[tuple(Q(rng.randrange(6),rng.randrange(1,4)) for _ in range(d)) for _ in range(5)]
            b=[tuple(Q(rng.randrange(5),rng.randrange(1,4)) for _ in range(d)) for _ in range(n)]
            if case==0:b=[tuple(Q(0) for _ in range(d)) for _ in range(n)]
            f=lambda x:min(dot(w,x) for w in W)
            c=tuple(sum(bi[e] for bi in b) for e in range(d));T=f(c)
            masks=[]
            for B in product((0,1),repeat=n):
                x=tuple(sum(bi[e] for bi,bit in zip(b,B) if bit) for e in range(d))
                fx=f(x);w=min(W,key=lambda z:dot(z,x))
                for relative in (False,True):
                    closed=Q(0);endpoint=Q(0)
                    for i,bi in enumerate(b):
                        price=dot(w,bi)
                        off_face=any(not x[e] and bi[e] for e in range(d))
                        cap=T if relative and off_face else min(price,T)
                        ratio=sum(cap_ratio(bi[e],x[e]) for e in range(d))
                        chk(cap<=T*ratio,'pointwise_coordinate_domination')
                        if B[i]:
                            delta=fx-f(tuple(x[e]-bi[e] for e in range(d)))
                            endpoint+=delta
                            chk(0<=delta<=T,'endpoint_range')
                        else:closed+=cap
                    masks.append((B,relative,closed,endpoint,fx))
            for q in (Q(1,2),Q(1,3),Q(1,5)):
                for relative in (False,True):
                    closed=sum(mask_weight(B,q)*cl for B,rel,cl,en,fx in masks if rel==relative)
                    chk(closed<=2*d*q/(1-q)*T,'expected_closed_resource_bound')
            for a in (Q(1,2),Q(1,3),Q(1,5)):
                for relative in (False,True):
                    integral=sum(integrate_mask(B,a)*(cl+en) for B,rel,cl,en,fx in masks if rel==relative)
                    endint=sum(integrate_mask(B,a)*en for B,rel,cl,en,fx in masks if rel==relative)
                    ga=sum(mask_weight(B,a)*fx for B,rel,cl,en,fx in masks if rel==relative)
                    gint=sum(integrate_mask(B,a)*fx for B,rel,cl,en,fx in masks if rel==relative)
                    chk(endint==T-(1-a)*ga-gint,'integration_by_parts_identity')
                    chk(integral/a<=(1/a+d*a/(1-a))*T,'integrated_dimension_upper')
            C['profiles']=C.get('profiles',0)+1

out={'status':'pass','arithmetic':'exact rational, explicit masks, normal and relative supports',
     'counts':C,'scope':'finite validation of universal proof, not an exhaustive theorem proof'}
Path(__file__).with_name('DIMENSION_SQRT_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
