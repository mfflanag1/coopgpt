#!/usr/bin/env python3
"""Independent exact Model-A split-local-owner candidate check; stdlib only.

All profiles are an explicitly supplied Cartesian capacity grid. All coalitions
are enumerated. All adjacent own-coordinate reports are compared; transitivity
covers every same-owner componentwise comparison inside this Cartesian domain.
Finite passing results are calibration, never a universal upper-bound proof.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse, hashlib, json


def require(condition, message):
    if not condition: raise ValueError(message)


def worth(profile, mask, blocks):
    """Independent direct production expression with nonmember resources zero."""
    m=len(blocks); k=max(blocks)+1
    p=profile[0] if mask&(1<<k) else F()
    h=[profile[1+j] if mask&(1<<(k+1+j)) else F() for j in range(m)]
    local=[profile[1+m+j] if mask&(1<<blocks[j]) else F() for j in range(m)]
    ell=[min(x,y) for x,y in zip(h,local)]
    return sum(ell)+min(p,sum(h)-sum(ell))


def values(profile, blocks):
    m=len(blocks); k=max(blocks)+1
    p=profile[0]; h=profile[1:1+m]; local=profile[1+m:]
    ell=tuple(min(x,y) for x,y in zip(h,local)); residual=tuple(x-y for x,y in zip(h,ell))
    L=sum(ell); Q=sum(residual); H=sum(h); R=min(p,Q); G=min(p,H); T=L+R; M=T-G
    E=tuple(sum(ell[j] for j in range(m) if blocks[j]==a) for a in range(k))
    return ell,residual,L,Q,H,R,G,T,M,E


def candidate(profile, blocks, theta=F(1)):
    k=max(blocks)+1
    ell,residual,L,Q,H,R,G,T,M,E=values(profile,blocks)
    if not L: return (F(),)*k+(G,)+(F(),)*len(blocks)
    x=tuple(l*min(F(1),max(F(),(profile[0]-Q+r)/L)) for l,r in zip(ell,residual))
    X=sum(x); c=G-max(F(),X-L/4)
    a=tuple(e*M/L for e in E)
    base=(F(),)*k+(R,)+ell
    full=a+(c,)+x
    return tuple(theta*y+(1-theta)*z for y,z in zip(full,base))


def run(blocks, levels, theta):
    require(set(blocks)==set(range(max(blocks)+1)),'Blocks must be contiguous nonempty labels')
    require(tuple(sorted(set(levels)))==levels,'Levels strictly increasing')
    require(all(x>=0 for x in levels),'Capacities nonnegative')
    require(0<=theta<=1,'Theta in [0,1]')
    m=len(blocks); k=max(blocks)+1; n=k+1+m; d=2*m+1
    profiles=list(product(levels,repeat=d)); lookup={b:i for i,b in enumerate(profiles)}
    payments=[candidate(b,blocks,theta) for b in profiles]
    owner=(k,)+tuple(range(k+1,k+1+m))+blocks
    counts={'profiles':len(profiles),'coalitions':0,'adjacent_own_reports':0,'floors':0,'zero_value_profiles':0}
    max_factor=F(); maximizer=None
    for q,b in enumerate(profiles):
        y=payments[q]; T=worth(b,(1<<n)-1,blocks)
        require(all(x>=0 for x in y),'Negative payment')
        if not T:
            require(sum(y)==0,'Nonzero payment at T=0'); counts['zero_value_profiles']+=1
        else:
            factor=sum(y)/T
            if factor>max_factor:max_factor=factor;maximizer=(b,y)
            require(factor<=1+theta/4,f'Budget fails at {b}: {y}')
        for mask in range(1<<n):
            lhs=sum(y[i] for i in range(n) if mask&(1<<i)); rhs=worth(b,mask,blocks)
            require(lhs>=rhs,f'Coalition failure profile={b},mask={mask},payment={y},slack={lhs-rhs}')
            counts['coalitions']+=1
        for a in range(k):
            marginal=T-worth(b,((1<<n)-1)^(1<<a),blocks)
            require(y[a]>=theta*marginal,f'Floor failure profile={b},local={a}')
            counts['floors']+=1
        for coordinate in range(d):
            pos=levels.index(b[coordinate])
            if pos+1<len(levels):
                changed=list(b);changed[coordinate]=levels[pos+1]
                high=payments[lookup[tuple(changed)]];i=owner[coordinate]
                require(high[i]>=y[i],f'Incentive failure profile={b},higher={changed},owner={i}')
                counts['adjacent_own_reports']+=1
    def strings(xs):return list(map(str,xs))
    return {'status':'PASS','blocks':list(blocks),'levels':strings(levels),'theta':str(theta),'counts':counts,'max_observed_factor':str(max_factor),'maximizer':{'profile':strings(maximizer[0]),'payments':strings(maximizer[1])} if maximizer else None,'scope':'Exact finite Cartesian domain only; all coalitions and adjacent own-coordinate reports. No universal upper inferred.','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--blocks',default='0,1');ap.add_argument('--levels',default='0,1,2');ap.add_argument('--theta',default='1');ap.add_argument('--output',type=Path)
    args=ap.parse_args();result=run(tuple(map(int,args.blocks.split(','))),tuple(map(F,args.levels.split(','))),F(args.theta));out=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.write_text(out)
    print(out,end='')
