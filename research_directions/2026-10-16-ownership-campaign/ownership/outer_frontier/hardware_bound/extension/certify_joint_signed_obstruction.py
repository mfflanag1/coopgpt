#!/usr/bin/env python3
from fractions import Fraction as F
from math import factorial
from pathlib import Path
import json,hashlib

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def lower(x,n):return sum((x**k/F(factorial(k)) for k in range(n+1)),F(0))
def upper(x,n):
    require(0<=x<n+2,'Taylor-tail domain')
    return lower(x,n)+x**(n+1)/F(factorial(n+1))/(1-x/F(n+2))

# Exact polynomial identities in symbolic q: tuple(constant, q coefficient).
# These replay the ACTUAL primitive on all three rational profiles.
def add(x,y):return(x[0]+y[0],x[1]+y[1])
def sub(x,y):return(x[0]-y[0],x[1]-y[1])
def scale(c,x):return(c*x[0],c*x[1])
def alloc(short,long_cap):return(short,long_cap-short)
zero=(F(0),F(0));one=(F(1),F(0))
full_h=[F(1),F(0),F(0)] # B,G,A
full_l=[F(0),F(1),F(2,5)]
require(sum(full_h)==1 and sum(full_l)==F(7,5),'full primitive totals')
full=[alloc(h,min(l,F(1))) for h,l in zip(full_h,full_l)]
require(full==[(F(1),F(-1)),(F(0),F(1)),(F(0),F(2,5))],'full symbolic payments')
# Both deleted profiles have capped-long ratio exactly1, hence q_new=1/2.
def deleted_exact(local):
    H=sum(full_h);L=sum(local);T=min(H,L)
    short,long=(full_h,local) if H<=L else(local,full_h)
    caps=[min(x,T) for x in long]
    require(sum(caps)==T,'deleted profile ratio one')
    return[(x+y)/2 for x,y in zip(short,caps)]
afterG=deleted_exact([F(0),F(0),F(2,5)])
afterA=deleted_exact([F(0),F(1),F(0)])
require(afterG==[F(1,5),F(0),F(1,5)],'G deletion payments')
require(afterA==[F(1,2),F(1,2),F(0)],'A deletion payments')
LG=sub(add(full[0],full[2]),(afterG[0]+afterG[2],F(0)))
LA=sub(full[0],(afterA[0],F(0)))
den=add(full[1],full[2]);total=add(LG,LA)
require(LG==(F(3,5),F(-3,5)),'exact G signed loss')
require(LA==(F(1,2),F(-1)),'exact A excluded-cap loss')
require(den==(F(0),F(7,5)),'full local denominator')
require(total==(F(11,10),F(-8,5)),'joint numerator')
# total/[(7/5)q]=(11/(2q)-8)/7; 1/(2q)=exp(2/5).
require(total==(F(11,10),F(-8,5)) and scale(F(5,7),total)==(F(11,14),F(-8,7)),
        'symbolic ratio reduction')
symbolic={'full_payments':[[str(x) for x in row] for row in full],
 'after_G':[str(x) for x in afterG],'after_A':[str(x) for x in afterA],
 'G_loss':[str(x) for x in LG],'A_loss':[str(x) for x in LA],
 'sum_loss':[str(x) for x in total],'denominator':[str(x) for x in den]}

v=F(2,5);w=F(45,128)
elo=lower(v,4);whi=upper(w,12);ehi=upper(v,12)
checks={
 'exp_two_fifths_lower':elo>F(82,55),
 'joint_ratio_above_six_fifths':(11*elo-8)/7>F(6,5),
 'critical_root_above_45_over_128':w*whi<F(1,2),
 'Lambda_below_six_fifths':(1-w)**2/w==F(6889,5760)<F(6,5),
 'each_fragment_diffuse':ehi<F(3,2),
}
for key,ok in checks.items():require(ok,key)
p=Path(__file__).with_name('JOINT_SIGNED_RESPONSE_OBSTRUCTION.txt')
print(json.dumps({'status':'PASS','arithmetic':'exact Fraction Taylor inequalities',
 'checks':checks,'exact_symbolic_primitive':symbolic,'exp_lower':str(elo),'exp_upper_at_w':str(whi),
 'joint_ratio_exact_lower':str((11*elo-8)/7),
 'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest()},indent=2,sort_keys=True))
