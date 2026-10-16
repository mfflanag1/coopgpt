#!/usr/bin/env python3
"""Exact rational interval certificate for the compact scalar endpoint."""
from fractions import Fraction as F
from math import factorial
from pathlib import Path
import hashlib,json

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def exp_upper(x,n=12):
    require(F(0)<=x<=1,'positive Taylor domain')
    s=sum((x**k)/factorial(k) for k in range(n+1))
    tail=(x**(n+1))/factorial(n+1)/(1-x/F(n+2))
    return s+tail

def exp_negative_lower(x,n=17):
    require(x>=0 and n%2==1,'negative Taylor domain/parity')
    return sum(((-x)**k)/factorial(k) for k in range(n+1))

def run():
    require(exp_upper(F(1,4))<F(9,7),'small-v endpoint exp bound')
    cells=256; maximum=F(0);where=None
    for i in range(cells):
        lo=F(1,4)+F(3*i,4*cells);hi=F(1,4)+F(3*(i+1),4*cells)
        x=(1-lo)/lo
        lower=exp_negative_lower(x)
        require(lower>=0,'negative exponential lower not nonnegative')
        bracket=2-lo-lower
        require(bracket>=0,'interval multiplication sign')
        # exp(v), +v use hi; -v and monotone exp(1-1/v) use lo.
        upper=exp_upper(hi)*bracket-1+hi
        require(upper<F(3,2),'scalar endpoint exceeds three halves')
        if upper>maximum:maximum=upper;where=(lo,hi)
    source=Path(__file__).with_name('SIGNED_OTHER_LOCAL_LOSS_THREE_HALVES.txt')
    return {'status':'PASS','arithmetic':'exact rational interval/Taylor certificate',
      'compact_interval':['1/4','1'],'cells':cells,'upper_exp_degree':12,'lower_exp_degree':17,
      'maximum_interval_upper_approx':float(maximum),'maximum_interval_upper_fraction':str(maximum),
      'maximizing_cell':[str(x) for x in where],
      'strict_margin_fraction':str(F(3,2)-maximum),
      'small_v_exp_upper_fraction':str(exp_upper(F(1,4))),
      'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest() if source.exists() else 'proof-not-yet-written'}
if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))
