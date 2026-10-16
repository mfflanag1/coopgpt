#!/usr/bin/env python3
"""Exact polynomial identities supporting the all-shape architecture theorem."""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json
COUNT=0

def require(x,msg):
    if not x:raise RuntimeError(msg)

def trim(a):
    a=list(map(Q,a))
    while len(a)>1 and a[-1]==0:a.pop()
    return tuple(a)

def add(a,b):return trim([(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0) for i in range(max(len(a),len(b)))])
def scale(a,c):return trim([x*c for x in a])
def neg(a):return scale(a,-1)
def sub(a,b):return add(a,neg(b))
def mul(a,b):
    z=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):z[i+j]+=x*y
    return trim(z)
def powp(a,n):
    z=(Q(1),)
    for _ in range(n):z=mul(z,a)
    return z
def deriv(a):return trim([Q(i)*a[i] for i in range(1,len(a))] or [0])
def ev(a,x):return sum(z*x**i for i,z in enumerate(a))
def shift(a,x):return trim([sum(a[j]*comb(j,i)*x**(j-i) for j in range(i,len(a))) for i in range(len(a))])
def rat(a,b=(1,)):return trim(a),trim(b)
def ra(a,b):return rat(add(mul(a[0],b[1]),mul(b[0],a[1])),mul(a[1],b[1]))
def rn(a):return rat(neg(a[0]),a[1])
def rs(a,b):return ra(a,rn(b))
def rm(a,b):return rat(mul(a[0],b[0]),mul(a[1],b[1]))
def rd(a,b):return rat(mul(a[0],b[1]),mul(a[1],b[0]))
def diff(a):return rat(sub(mul(deriv(a[0]),a[1]),mul(a[0],deriv(a[1]))),mul(a[1],a[1]))
def identity(a,b,name):
    global COUNT
    require(mul(a[0],b[1])==mul(b[0],a[1]),name);COUNT+=1

x=(0,1);one=(1,);omx=(1,-1);twoxmone=(-1,2);v=(-2,3)
d=mul(omx,twoxmone)
C=rat(powp(v,2),scale(d,8))
identity(C,rs(rat(powp(x,2),scale(d,8)),rat([Q(1,2)])),'ceiling numerator identity')
dC=rat(mul(x,v),scale(powp(d,2),8))
identity(diff(C),dC,'ceiling derivative')
chi=rat(v,mul(x,d))
identity(dC,rm(ra(C,rat([Q(1,2)])),chi),'critical ODE equality')
T=(-12,55,-91,53)
identity(rs(ra(rm(rat(omx),dC),C),rat([Q(1,10)])),
         rat(T,scale(mul(omx,powp(twoxmone,2)),20)),'tangent cubic')
Qbal=rs(rd(rm(rat((1,1)),rs(rat([Q(1,10)]),C)),rat(omx)),rm(rat(x),dC))
N=(-4,-24,173,-316,186)
identity(rs(rat([Q(1,2)]),Qbal),rat(N,scale(powp(d,2),40)),'balance numerator')
require(shift(N,Q(2,3))==trim([0,Q(52,9),37,180,186]),'balance shifted coefficients');COUNT+=1
F=rat(powp((1,1),3),scale(x,54))
g=rm(rs(rat(one),rm(rat((2,)),C)),F)
Gnum=mul((-8,24,-17),powp((1,1),3))
identity(g,rat(Gnum,scale(mul(x,d),216)),'funding rational expression')
J=(-8,64,-199,308,-235,68)
identity(diff(g),rat(mul(powp((1,1),2),J),scale(mul(powp(x,2),powp(d,2)),216)),'funding derivative quintic')
require(shift(J,Q(2,3))==trim([Q(4,243),-Q(164,81),-Q(221,27),-Q(148,9),-Q(25,3),68]),'funding shifted coefficients');COUNT+=1
require(ev(J,Q(2,3))==Q(4,243)>0 and ev(J,Q(27,40))==-Q(25331,25600000)<0,'rho bracket');COUNT+=1
require(ev(T,Q(17,25))==-Q(211,15625)<0 and ev(T,Q(683,1000))==Q(936311,10**9)>0,'tau bracket');COUNT+=1
require(182**2-4*159*55==-1856<0,'tangent monotone derivative');COUNT+=1
require(1-Q(9,10)-Q(1,27)-Q(13,225)==Q(7,1350)>0,'small-s nonmax margin');COUNT+=1
require(1-Q(15,17)-Q(1,27)-Q(5,72)==Q(41,3672)>0,'large-s nonmax margin');COUNT+=1
require(Q(2,15)>Q(5,72) and Q(1,5)>Q(5,72),'long endpoint margins');COUNT+=1
out={'status':'PASS: exact polynomial and rational identities','checks':COUNT,
     'scope':'Polynomial identities and displayed rational sign margins; not a standalone complete mechanism proof.'}
(Path(__file__).parent/'scalar-identities.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
