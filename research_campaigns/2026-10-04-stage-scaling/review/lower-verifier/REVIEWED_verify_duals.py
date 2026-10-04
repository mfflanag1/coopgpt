"""Independent exact verification of finite stage-scaling lower-bound witnesses."""
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json


def require(condition, reason):
    if not condition:raise ValueError(reason)


def verify(report):
    sizes=report['sizes'];require(len(sizes)>=2 and all(type(s) is int and s>0 for s in sizes),'valid pools')
    groups=[];offset=0
    for size in sizes:
        groups.append(tuple(range(offset,offset+size)));offset+=size
    n=offset;k=len(groups);coefs=defaultdict(F);rhs=F(0)
    def profile(raw):
        c=tuple(F(x) for x in raw);require(len(c)==n and min(c)>=0,'valid capacity profile');return c
    def worth(c,mask):
        return min(sum((c[i] for i in group if mask&(1<<i)),F(0)) for group in groups)
    require(bool(report['dual_support']),'nonempty dual')
    for row in report['dual_support']:
        c=profile(row['profile']);weight=F(row['multiplier']);require(weight>0,'positive weight')
        T=worth(c,(1<<n)-1);kind=row['kind']
        if kind=='budget':
            coefs['beta']+=weight*T;rhs-=weight*T
            for i in range(n):coefs[(c,i)]-=weight
        elif kind=='cover':
            mask=row['coalition'];require(type(mask) is int and 0<mask<(1<<n),'valid coalition')
            rhs+=weight*worth(c,mask)
            for i in range(n):
                if mask&(1<<i):coefs[(c,i)]+=weight
        elif kind=='monotone':
            low=profile(row['low_profile']);i=row['owner'];require(type(i) is int and 0<=i<n,'valid owner')
            require(c[i]>low[i] and all(c[j]==low[j] for j in range(n) if j!=i),'one-coordinate strict underreport')
            coefs[(c,i)]+=weight;coefs[(low,i)]-=weight
        elif kind=='bottleneck_floor':
            i=row['owner'];require(type(i) is int and 0<=i<n,'valid owner')
            group=next(g for g in groups if i in g)
            require(sum(c[j] for j in group)==T,'floor only in bottleneck pool')
            # Core witness x_j=c_j on this pool and zero elsewhere proves H_i>=c_i.
            coefs[(c,i)]+=k*weight;rhs+=weight*c[i]
        else:raise ValueError('unknown row')
    b=coefs.pop('beta',F(0));require(b>0,'positive beta coefficient')
    require(all(a<=0 for a in coefs.values()),'nonpositive payment residuals')
    lower=rhs/b;require(lower==F(report['objective_rational_guess']),'claimed lower bound')
    return dict(lower=str(lower),beta_coefficient=str(b),rhs=str(rhs),rows=len(report['dual_support']),floor_rows=sum(r['kind']=='bottleneck_floor' for r in report['dual_support']),support_profiles=len({tuple(r[key]) for r in report['dual_support'] for key in ('profile','low_profile') if key in r}))


def main():
    here=Path(__file__).parent;reports=[]
    for p in sorted(here.glob('lp-*.json')):
        r=json.loads(p.read_text());require(r['success'],'discovery succeeded')
        if not r['dual_support']:
            require(F(r['objective_rational_guess'])==0,'empty dual cannot establish positive bound')
            reports.append(dict(file=p.name,status='NO_NONTRIVIAL_DUAL',note='Numerical zero is not an all-profile upper bound.'))
        else:reports.append(dict(file=p.name,status='CERTIFIED',**verify(r)))
    reference=json.loads((here/'lp-calibration-2x2.json').read_text());rejections=[]
    def reject(label,change,reason):
        r=deepcopy(reference);change(r)
        try:verify(r)
        except ValueError as error:
            require(str(error)==reason,'unexpected rejection: '+label);rejections.append(dict(label=label,reason=str(error)));return
        raise ValueError('mutation accepted: '+label)
    reject('negative multiplier',lambda r:r['dual_support'][0].update(multiplier='-1'),'positive weight')
    reject('wrong lower bound',lambda r:r.update(objective_rational_guess='1/7'),'claimed lower bound')
    reject('empty support',lambda r:r.update(dual_support=[]),'nonempty dual')
    reject('invalid coalition',lambda r:next(x for x in r['dual_support'] if x['kind']=='cover').update(coalition=0),'valid coalition')
    reject('unknown row',lambda r:r['dual_support'][0].update(kind='invalid'),'unknown row')
    def alter(r):
        row=next(x for x in r['dual_support'] if x['kind']=='monotone');row['low_profile'][(row['owner']+1)%sum(r['sizes'])]=99
    reject('multiple reports changed',alter,'one-coordinate strict underreport')
    reject('negative capacity',lambda r:r['dual_support'][0]['profile'].__setitem__(0,-1),'valid capacity profile')
    result=dict(status='PASS',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),certificates=reports,mutations_rejected=rejections)
    (here/'EXACT_DUALS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
