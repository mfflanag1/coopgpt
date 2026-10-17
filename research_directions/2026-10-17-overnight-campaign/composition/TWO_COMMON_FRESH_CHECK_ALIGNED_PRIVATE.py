"""Exact finite checks of the aligned-private structural theorem, not its proof."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import random,json
R=random.Random(701042)
root=Path(__file__).resolve().parent

def dot(x,y):return sum((a*b for a,b in zip(x,y)),Q(0))
def knapsack(cap,coeff,w,c):
    vals=[(cap*p+sum((cj*max(Q(0),wj-aj*p) for cj,wj,aj in zip(c,w,coeff)),Q(0)),p)
          for p in {Q(0),*(wj/aj for wj,aj in zip(w,coeff))}]
    val=min(v for v,p in vals)
    return val,min(p for v,p in vals if v==val)
def selected(P,Qq,a,b,c):
    w=tuple(aa+bb for aa,bb in zip(a,b));wp=dot(w,c)
    kp,p=knapsack(P,a,w,c);kq,q=knapsack(Qq,b,w,c)
    f=min(P+Qq,kp,kq)
    if f==P+Qq:return f,(Q(0),)*len(a)
    if f==wp:return f,w
    assert kp!=kq
    if kp<kq:return f,tuple(max(Q(0),ww-aa*p) for ww,aa in zip(w,a))
    return f,tuple(max(Q(0),ww-bb*q) for ww,bb in zip(w,b))
def forms(P,Qq,a,b):
    w=tuple(aa+bb for aa,bb in zip(a,b))
    lines=[(Q(1),Q(0),Q(0)),(Q(0),Q(1),Q(0)),*zip(a,b,w)]
    vs={(Q(1),Q(1))}
    for (a0,b0,w0),(a1,b1,w1) in combinations(lines,2):
        d=a0*b1-a1*b0
        if d:
            p=(w0*b1-w1*b0)/d;q=(a0*w1-a1*w0)/d
            if min(p,q)>=0:vs.add((p,q))
    return [(P*p+Qq*q,tuple(max(Q(0),ww-aa*p-bb*q) for ww,aa,bb in zip(w,a,b))) for p,q in vs]
def radial(P,Qq,a,b,c):
    fs=forms(P,Qq,a,b)
    af=[(z,dot(c,g)) for z,g in fs]
    cuts={Q(0),Q(1)}
    for (z,s),(zz,ss) in combinations(af,2):
        if s!=ss:
            t=(zz-z)/(s-ss)
            if 0<t<1:cuts.add(t)
    cuts=sorted(cuts);p=[Q(0)]*len(a)
    for lo,hi in zip(cuts,cuts[1:]):
        t=(lo+hi)/2
        f,g=selected(P,Qq,a,b,tuple(t*x for x in c))
        assert f==min(z+t*s for z,s in af)
        for j in range(len(a)):p[j]+=(hi-lo)*g[j]
    f,_=selected(P,Qq,a,b,c)
    assert dot(c,p)==f
    return f,p
count_dr=count_dual=count_tcwm=0
for case in range(90):
    m=1+case%6
    a=tuple(Q(R.randint(1,7),R.randint(1,5)) for _ in range(m))
    b=tuple(Q(R.randint(1,7),R.randint(1,5)) for _ in range(m))
    P=Q(R.randint(1,8),R.randint(1,3));Qq=Q(R.randint(1,8),R.randint(1,3))
    fs=forms(P,Qq,a,b)
    for trial in range(10):
        c=tuple(Q(R.randint(0,8),R.randint(1,4)) for _ in range(m))
        d=tuple(x+Q(R.randint(0,6),R.randint(1,5)) for x in c)
        fc,gc=selected(P,Qq,a,b,c);fd,gd=selected(P,Qq,a,b,d)
        assert all(x>=y for x,y in zip(gc,gd)),(a,b,P,Qq,c,d,gc,gd)
        count_dr+=1
        for cap,f in ((c,fc),(d,fd)):
            assert f==min(z+dot(cap,g) for z,g in fs)
            count_dual+=1
        if trial<2:
            fc,pc=radial(P,Qq,a,b,c);fd,pd=radial(P,Qq,a,b,d)
            assert all(x>=y for x,y in zip(pc,pd))
            # Outsider bundle is fixed, inside the old aggregate; the entire
            # capacity increment is assigned to the same fixed coalition.
            out=tuple(x*Q(R.randint(0,4),4) for x in c)
            before=dot(tuple(x-o for x,o in zip(c,out)),pc)
            after=dot(tuple(x-o for x,o in zip(d,out)),pd)
            assert after>=before
            count_tcwm+=1
# Displayed common-report caveat.
a=(Q(1),Q(1),Q(1,4));b=(Q(1),Q(1,4),Q(1));c=(Q(1,4),Q(4),Q(1))
_,p0=radial(Q(1),Q(1),a,b,c);_,p1=radial(Q(2),Q(1),a,b,c)
assert p0==[Q(7,9),Q(5,18),Q(25,36)]
assert p1==[Q(8,9),Q(5,9),Q(5,9)]
assert p0[2]-p1[2]==Q(5,36)
result={'status':'PASS','exact_antitone_checks':count_dr,'independent_dual_arrangement_values':count_dual,'actual_coalition_private_restorations':count_tcwm,'common_restoration_private_loss':'5/36','scope':'Finite falsification checks supplement the all-capacity proof; common-report TCWM is not established.'}
(root/'TWO_COMMON_FRESH_ALIGNED_PRIVATE_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
