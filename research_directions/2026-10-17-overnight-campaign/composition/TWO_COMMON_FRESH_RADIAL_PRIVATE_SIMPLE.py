from fractions import Fraction as Q
from itertools import combinations,product
import random,json
from pathlib import Path

A=[Q(1),Q(1),Q(1,4)];B=[Q(1),Q(1,4),Q(1)];W=[Q(3,2),Q(1),Q(1)]
lines=[(Q(1),Q(0),Q(0)),(Q(0),Q(1),Q(0))]+list(zip(A,B,W))
verts=set()
for (a,b,w),(aa,bb,ww) in combinations(lines,2):
    det=a*bb-aa*b
    if not det:continue
    p=(w*bb-ww*b)/det;q=(a*ww-aa*w)/det
    if p>=0 and q>=0:verts.add((p,q))
forms=[]
for p,q in sorted(verts):forms.append((p+q,tuple(max(Q(0),w-a*p-b*q) for a,b,w in zip(A,B,W))))

def radial(c,details=False):
    affine=[(base,sum((a*b for a,b in zip(c,grad)),Q(0)),grad) for base,grad in forms]
    cuts={Q(0),Q(1)}
    for (a,b,_),(aa,bb,__) in combinations(affine,2):
        if b!=bb:
            t=(aa-a)/(b-bb)
            if 0<t<1:cuts.add(t)
    cuts=sorted(cuts);p=[Q(0)]*3;segments=[]
    for lo,hi in zip(cuts,cuts[1:]):
        mid=(lo+hi)/2; vals=[base+mid*slope for base,slope,g in affine];k=min(range(len(vals)),key=vals.__getitem__)
        g=affine[k][2]
        for j in range(3):p[j]+=(hi-lo)*g[j]
        if not segments or segments[-1][2]!=g:segments.append([lo,hi,g])
        else:segments[-1][1]=hi
    f=min(base+sum((a*b for a,b in zip(c,g)),Q(0)) for base,g in forms)
    assert sum((a*b for a,b in zip(c,p)),Q(0))==f
    return (p,segments,f) if details else p
for c in product((Q(1),Q(2),Q(3),Q(4)),repeat=3):
    p=radial(c)
    for j in range(3):
        for delta in (Q(1,2),Q(1),Q(2)):
            cc=list(c);cc[j]+=delta;pp=radial(cc)
            for mask in range(1,8):
                if not mask>>j&1:continue
                old=sum((c[i]*p[i] for i in range(3) if mask>>i&1),Q(0))
                new=sum((cc[i]*pp[i] for i in range(3) if mask>>i&1),Q(0))
                if new<old and radial(c,True)[1][-1][2]==(Q(0),Q(0),Q(0)) and radial(cc,True)[1][-1][2]==(Q(0),Q(0),Q(0)):
                    print(c,j,delta,mask,old,new,'loss',old-new)
                    print('old',radial(c,True));print('new',radial(cc,True));raise SystemExit
