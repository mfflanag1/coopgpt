#!/usr/bin/env python3
"""Finite direct-primitive Decimal corroboration of the signed-loss theorem."""
from decimal import Decimal,localcontext
from pathlib import Path
import hashlib,json,random
D=Decimal

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def primitive(a,b):
    sa,sb=sum(a),sum(b)
    if min(sa,sb)==0:return [D(0)]*len(a)
    short,long=(a,b) if sa<=sb else (b,a);t=min(sa,sb)
    caps=[min(x,t) for x in long];q=(1-sum(caps)/t).exp()/2
    return [(1-q)*x+q*y for x,y in zip(short,caps)]

def run():
    rng=random.Random(2026101703);e=D(1).exp();bound=4/e;tol=D('1e-55')
    count=shorts=longs=switches=0;maximum=D(0);witness=None
    for n in (2,3,5,9,17):
        for _ in range(2000):
            h=[D(rng.randrange(1,31)) for _ in range(n)]
            if rng.randrange(2):h[0]=D(0)
            h=[x/sum(h) for x in h]
            l=[D(rng.randrange(0,31)) for _ in range(n)];l[0]+=1
            rho=D(rng.randrange(200,4001))/1000
            l=[x*rho/sum(l) for x in l]
            new=l[:];new[0]*=D(rng.randrange(1001))/1000
            if rng.randrange(3)==0:new[0]=D(0)
            full=primitive(h,l);altered=primitive(h,new)
            loss=sum(full[1:])-sum(altered[1:])
            require(loss<=bound*full[0]+tol,'Signed other loss exceeded 4/e')
            require(altered[0]<=full[0]+tol,'Own monotonicity failed')
            if full[0]>0 and loss/full[0]>maximum:
                maximum=loss/full[0];witness={'h':[str(x) for x in h],'l':[str(x) for x in l],'new_local':str(new[0])}
            if sum(l)<=1:shorts+=1
            else:
                longs+=1
                if sum(new)<1:switches+=1
            count+=1
    return {'status':'PASS','arithmetic':'80-digit Decimal finite direct-primitive corroboration',
       'profiles':count,'original_local_short':shorts,'original_local_long':longs,'pool_switches':switches,
       'max_observed_signed_ratio':str(maximum),'bound_four_over_e':str(bound),'witness':witness,
       'source_sha256':hashlib.sha256(Path(__file__).with_name('SIGNED_OTHER_LOCAL_LOSS_FOUR_OVER_E.txt').read_bytes()).hexdigest()}
if __name__=='__main__':
    with localcontext() as ctx:
        ctx.prec=80
        print(json.dumps(run(),indent=2,sort_keys=True))
