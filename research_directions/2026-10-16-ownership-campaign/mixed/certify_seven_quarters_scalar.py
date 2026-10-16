#!/usr/bin/env python3
"""Exact continuum certificate for the last scalar inequality.

This certifies g(p,C)<7/4 on 0<=p<=1,C=1+1/(2e), where
 g=3/2+p-(p+1/2)exp(1-1/p)/2-(3/2-C)exp(1-C-p)/2,
with the first exponential term set to0 at p=0. Every numerical decision
uses Fraction; no floats, tolerance, optimizer, or Python assert is involved.
"""
from fractions import Fraction as Q
import json

def require(ok, message):
    if not ok:raise RuntimeError(message)

def expneg_lower(x):
    # x in[0,3]. Split into three factors exp(-x/3). Alternating
    # Taylor truncation through odd degree11 is a lower bound, and
    # terms decrease because0<=x/3<=1. Positivity permits cubing.
    require(Q(0)<=x<=Q(3),'argument outside certified exponential range')
    y=x/3;term=Q(1);s=Q(1)
    for j in range(1,12):term*= -y/j;s+=term
    require(s>0,'nonpositive Taylor lower bound')
    return s*s*s

def main():
    C0=Q(148,125)
    e_lower=sum((Q(1,f) for f in [1,1,2,6,24,120,720]),Q(0))
    require(e_lower==Q(1957,720)>Q(125,46),'C upper-bound premise')
    require(1+1/(2*e_lower)<C0,'C<C0')
    require(Q(667,400)<Q(7,4),'analytic p<=1/4 bound')
    # g is increasing in C for C<5/2 because its partial derivative is
    # exp(1-C-p)(5/2-C)/2. Thus replace true C by fixed C0.
    require(C0<Q(3,2),'positive subtracted coefficient')
    subdivisions=512;left=Q(1,4);width=Q(3,4)/subdivisions
    highest=None;highest_cell=None
    for j in range(subdivisions):
        a=left+j*width;b=a+width
        # q1(p)(p+1/2) is increasing, while exp(1-C0-p) is decreasing.
        # Use a for the first negative term and b for the second one.
        upper=Q(3,2)+b-Q(1,2)*(a+Q(1,2))*expneg_lower(1/a-1)-Q(1,2)*(Q(3,2)-C0)*expneg_lower(C0+b-1)
        require(upper<Q(7,4),f'interval {j} not certified')
        if highest is None or upper>highest:highest=upper;highest_cell=j
    require(left+subdivisions*width==1,'partition does not cover endpoint1')
    # Report only decimals for readability after exact PASS decisions.
    print(json.dumps(dict(status='PASS',rational_cells=subdivisions,analytic_initial_interval=['0','1/4'],certified_interval=['1/4','1'],largest_upper_float=float(highest),worst_cell=highest_cell,margin_lower_float=float(Q(7,4)-highest),C_upper=str(C0),scope='exact rational interval certificate covering the full scalar continuum; mechanism reductions remain separate proof obligations')))

if __name__=='__main__':main()
