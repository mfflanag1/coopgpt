from fractions import Fraction as Q
from itertools import combinations
import json

def add(a,b):
    r=[Q(0)]*max(len(a),len(b))
    for i,x in enumerate(a): r[i]+=x
    for i,x in enumerate(b): r[i]+=x
    while len(r)>1 and not r[-1]: r.pop()
    return r

def mul(a,b):
    r=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): r[i+j]+=x*y
    while len(r)>1 and not r[-1]: r.pop()
    return r

def scale(a,c): return [x*c for x in a]

def power(a,k):
    r=[Q(1)]
    for _ in range(k): r=mul(r,a)
    return r

def worth(z,S):
    return min(sum((max(z[i],0) for i in S),Q(0)),
               sum((max(-z[i],0) for i in S),Q(0)))

def kernels(z):
    out=[]
    for i in range(len(z)):
        others=[j for j in range(len(z)) if j!=i]
        poly=[Q(0)]
        for k in range(len(others)+1):
            prob=mul(power([Q(0),Q(1)],k),power([Q(1),Q(-1)],len(others)-k))
            for S in combinations(others,k):
                marginal=worth(z,S+(i,))-worth(z,S)
                poly=add(poly,scale(prob,marginal))
        assert poly[0]==0
        out.append(poly[1:] if len(poly)>1 else [Q(0)])
    return out

t=Q(1,2)
low=(Q(2),t,Q(-1),Q(0))
high=(Q(2),t,Q(-1),-t)
kl=kernels(low)
kh=kernels(high)
assert kl==[[Q(1),-t],[t,-t],[1+t,-t],[Q(0)]]
assert kh==[[1+t,-2*t,t],[2*t,-3*t,t],
            [1+t,-2*t,t],[2*t,-2*t,t]]
assert kh[0]==kh[2]
core=add(scale(kh[0],2),kh[3])
pair=add(kh[0],kh[3])
identity=add(scale(pair,2+t),scale(core,-(1+t)))
assert identity==scale([Q(1),Q(-2),Q(1)],t*(1-t))
assert worth(high,(0,2,3))==1+t
assert worth(high,(1,3))==t
mass=(1+t)/(2+t)
at_one=lambda p:sum(p,Q(0))
small_total=mass*(at_one(kh[1])+at_one(kh[3]))
assert small_total==Q(3,10)<t
assert t-small_total==Q(1,5)

# Padding by any number of null owners does not affect these kernels.
for extra in range(1,5):
    assert kernels(low+(Q(0),)*extra)[:4]==kl
    assert kernels(high+(Q(0),)*extra)[:4]==kh

# Symbolic low moment identity checked in its affine h coefficient.
# (2+t)*(U+t)-(1+t)^2 = -t^2*h, with U=(1-t^2*h)/(2+t).
lhs=add(scale([Q(1)/(2+t)+t,-t*t/(2+t)],2+t),[-(1+t)**2])
assert lhs==[Q(0),-t*t]

result={"status":"PASS","arithmetic":"exact rational polynomials",
        "low":[str(x) for x in low],"high":[str(x) for x in high],
        "low_kernels":[[str(x) for x in p] for p in kl],
        "high_kernels":[[str(x) for x in p] for p in kh],
        "forced_small_pair_payment":str(small_total),
        "small_pair_worth":str(t),"coverage_shortfall":str(t-small_total),
        "null_padding_checks":8,
        "scope":"common report-dependent positive scaled-semivalue cone; not unrestricted mechanisms"}
print(json.dumps(result,indent=2))
