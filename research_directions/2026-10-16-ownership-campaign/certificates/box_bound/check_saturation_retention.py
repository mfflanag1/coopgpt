#!/usr/bin/env python3
"""Independent finite floating checks; proofs are in SATURATION_RETENTION_THEOREM.txt."""
from math import exp
from random import Random
from pathlib import Path
import json

BASE=Path(__file__).parent
RNG=Random(16102026)
C0=1/(2*exp(1)); C=1+C0; LAMBDA=(1-3*C0)/C

def require(condition, message='validation failed'):
    if not condition:
        raise AssertionError(message)

def phi(a,b):
    aa=sum(a);bb=sum(b);t=min(aa,bb)
    if t<=0:return [0.0]*len(a)
    s,l=(a,b) if aa<=bb else (b,a)
    capped=[min(x,t) for x in l]
    q=.5*exp(1-sum(capped)/t)
    return [(1-q)*x+q*y for x,y in zip(s,capped)]

def tokens(total,n):
    out=[0]*n
    for _ in range(total):
        eligible=[i for i in range(n) if out[i]<4]
        out[RNG.choice(eligible)]+=1
    return out

def branch(n):
    t=RNG.choice([.25,.5,1.,2.])
    s=[t*x/4 for x in tokens(4,n)]
    l=[t*x/4 for x in tokens(8,n)]
    l=[x+(RNG.choice([0.,.5,2.])*t if x==t else 0.) for x in l]
    return (s,l) if RNG.randrange(2) else (l,s)

def nested(h,l):
    n=len(h);m=len(h[0]);z=[0.]*n
    prod=0.
    for j in range(m):
        a=[h[i][j] for i in range(n)];b=[l[i][j] for i in range(n)]
        prod+=min(sum(a),sum(b))
        v=phi(a,b)
        z=[x+y for x,y in zip(z,v)]
    hw=[sum(row) for row in h]
    return phi(hw,z),z,min(sum(hw),prod)

def run():
    count=0;worst=0.;totalworst=0.
    for _ in range(1400):
        n=RNG.randrange(3,8);a,b=branch(n);full=phi(a,b)
        for i in range(n):
            for _ in range(7):
                ar=a[:];br=b[:]
                ar[i]*=RNG.choice([0.,.25,.5,.75,1.])
                br[i]*=RNG.choice([0.,.25,.5,.75,1.])
                reduced=phi(ar,br)
                ownloss=full[i]-reduced[i]
                totalloss=sum(full)-sum(reduced)
                residual=ownloss-LAMBDA*totalloss
                worst=min(worst,residual);totalworst=min(totalworst,totalloss)
                require(residual>=-2e-12 and totalloss>=-2e-12, (a,b,i,ar,br,residual))
                count+=1
    facecount=0;deviations=0;worstgain=0.;skips=0
    for _ in range(900):
        if facecount>=240:break
        n=RNG.randrange(3,8);m=RNG.randrange(1,6)
        h=[[] for _ in range(n)];l=[[] for _ in range(n)]
        for j in range(m):
            a,b=branch(n)
            for i in range(n):h[i].append(a[i]);l[i].append(b[i])
        for i in range(n):h[i].append(0.);l[i].append(0.)
        _,z,f=nested(h,l);zt=sum(z)
        cap=sum(min(sum(row),zt) for row in h)
        if cap>2*zt+1e-12:skips+=1;continue
        deficit=2*zt-cap
        for i in range(n):
            add=min(deficit,max(0.,zt-sum(h[i])))
            h[i][-1]+=add;deficit-=add
        require(abs(deficit)<=2e-12, 'validation failed')
        full,z,f=nested(h,l)
        require(abs(sum(full)-C*C*f)<=2e-11, 'validation failed')
        for i in range(n):
            for k in range(35):
                hr=[row[:] for row in h];lr=[row[:] for row in l]
                if k<2*(m+1):
                    target=hr if k<m+1 else lr
                    target[i][k%(m+1)]*=.999
                else:
                    hr[i]=[x*RNG.choice([0.,.25,.5,.75,1.]) for x in hr[i]]
                    lr[i]=[x*RNG.choice([0.,.25,.5,.75,1.]) for x in lr[i]]
                changed,_,_=nested(hr,lr)
                gain=changed[i]-full[i];worstgain=max(worstgain,gain)
                require(gain<=3e-11, (h,l,i,hr,lr,gain))
                deviations+=1
        facecount+=1
    require(facecount==240, 'validation failed')
    result={'status':'PASS - finite floating corroboration only','retention_checks':count,'worst_retention_residual':worst,'worst_total_loss':totalworst,'saturation_profiles':facecount,'face_underreports':deviations,'worst_underreport_gain':worstgain,'candidate_profiles_skipped_before_exact_face_completion':skips,'lambda':LAMBDA,'raw_constant':C*C,'proof':'SATURATION_RETENTION_THEOREM.txt','includes':'mixed local orientations; whole-owner underreports; cap crossings; zeros; arbitrary unused hardware on zero-output branches'}
    (BASE/'saturation-retention-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':run()
