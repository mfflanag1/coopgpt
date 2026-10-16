#!/usr/bin/env python3
"""Exact adaptive rational covering certificate; no floating acceptance decisions."""
from fractions import Fraction as F
from math import factorial
from functools import lru_cache
from pathlib import Path
import hashlib,json

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

@lru_cache(None)
def eup(x):
    require(0<=x<=1,'exp upper domain')
    return sum(x**k/factorial(k) for k in range(13))+(x**13/factorial(13))/(1-x/14)

@lru_cache(None)
def elo(v):
    require(F(1,4)<=v<=F(1),'reciprocal lower domain')
    x=(1-v)/v
    return sum((-x)**k/factorial(k) for k in range(18))

def cover(lo,hi,threshold,kind):
    work=[(lo,hi,0)];accepted=[]
    while work:
        a,b,depth=work.pop()
        low=elo(a)
        require(low>=0,'negative exp lower')
        if kind==1:
            bracket=2-a-low;require(bracket>=0,'multiply sign')
            upper=eup(b)*bracket-1+b
        else:upper=(1-low)/(1-b)
        if upper<threshold:accepted.append((a,b,upper,depth));continue
        require(depth<20,'certificate subdivision limit')
        mid=(a+b)/2
        work.extend(((a,mid,depth+1),(mid,b,depth+1)))
    accepted.sort()
    require(accepted[0][0]==lo and accepted[-1][1]==hi,'cover endpoints')
    require(all(x[1]==y[0] for x,y in zip(accepted,accepted[1:])),'cover gap or overlap')
    require(sum(b-a for a,b,_,_ in accepted)==hi-lo,'cover length')
    maximum=max(x[2] for x in accepted)
    return {'leaves':len(accepted),'max_depth':max(x[3] for x in accepted),
      'max_upper_fraction':str(maximum),'max_upper_approx':float(maximum),
      'threshold':str(threshold),'partition_sha256':hashlib.sha256('\n'.join(f'{a}:{b}:{u}' for a,b,u,_ in accepted).encode()).hexdigest()}

def run():
    require(eup(F(1))<F(87,32),'e upper comparison')
    require(F(1471,1000)<F(128,87),'switch scalar versus 4/e')
    require(F(7,5)<F(128,87),'first scalar versus 4/e')
    # Small-v second endpoint: use v<=1/5, requiring a wider certificate domain.
    # We instead retain v<=1/4 with the actual subtracted exponential bounded
    # from below only on [1/5,1/4]; [0,1/5] is elementary.
    require(eup(F(1,5))*F(9,5)-F(4,5)<F(1471,1000),'v<=1/5 endpoint')
    # Handle [1/5,1/4] directly with a higher odd Taylor degree, x<=4.
    def low_general(v):
        x=(1-v)/v
        return sum((-x)**k/factorial(k) for k in range(26))
    small=[]
    for i in range(128):
        a=F(1,5)+F(i,2560);b=F(1,5)+F(i+1,2560)
        lower=low_general(a);require(lower>=0,'small interval lower')
        upper=eup(b)*(2-a-lower)-1+b
        require(upper<F(1471,1000),'small scalar interval failure')
        small.append(upper)
    endpoint0=cover(F(1,4),F(1,2),F(7,5),0)
    endpoint1=cover(F(1,4),F(1),F(1471,1000),1)
    source=Path(__file__).with_name('SIGNED_OTHER_LOCAL_LOSS_FOUR_OVER_E.txt')
    return {'status':'PASS','arithmetic':'exact Fraction adaptive interval/Taylor certificate',
      'first_endpoint_middle':endpoint0,'second_endpoint_main':endpoint1,
      'second_endpoint_small_cells':len(small),'second_endpoint_small_max_fraction':str(max(small)),
      'e_upper_fraction':str(eup(F(1))),'signed_constant_approx':4/2.718281828459045,
      'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest() if source.exists() else 'proof-pending'}
if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))
