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
rng=random.Random(7834)
for it in range(3000):
    c=tuple(Q(rng.randrange(1,20),rng.randrange(1,8)) for _ in range(3))
    p=radial(c)
    for j in range(3):
        delta=Q(rng.randrange(1,5),rng.randrange(1,12));cc=list(c);cc[j]+=delta;pp=radial(cc)
        for mask in range(1,8):
            if not mask>>j&1:continue
            old=sum((c[i]*p[i] for i in range(3) if mask>>i&1),Q(0))
            new=sum((cc[i]*pp[i] for i in range(3) if mask>>i&1),Q(0))
            if new<old:
                out={'capacities':list(map(str,c)),'restored_coordinate':j,'delta':str(delta),'coalition_mask':mask,'old_price':list(map(str,p)),'new_price':list(map(str,pp)),'old_payment':str(old),'new_payment':str(new),'loss':str(old-new),'old_segments':radial(c,True)[1],'new_segments':radial(cc,True)[1]}
                out=json.loads(json.dumps(out,default=str));Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));raise SystemExit
print('no failure in bounded exact scout')
