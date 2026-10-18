"""Independent exact checker; standard library only, no optimization dependency."""
from fractions import Fraction as Q
from pathlib import Path
import argparse, json, hashlib

def require(ok,message):
    if not ok:raise RuntimeError(message)

def check(path):
    raw=path.read_bytes();p=json.loads(raw)
    d,n,s=p['d'],p['n'],p['s'];states=p['states'];edges=list(map(tuple,p['edges']))
    require(all(0<len(e)<=3 and len(set(e))==len(e) and all(0<=j<d for j in e) for e in edges),'invalid activity')
    stride=d+1;K=stride*len(states);values=[]
    require(p['factor_index']==K,'factor index')
    for a,o in zip(states,p['oracles'],strict=True):
        require(len(a)==d and all(type(v)==int and v>=0 for v in a) and sum(a)<n,'actual-owner counts')
        x=list(map(Q,o['primal']));q=list(map(Q,o['dual']));v=Q(o['value'])
        require(len(x)==len(edges) and len(q)==d,'oracle shape')
        require(all(t>=0 for t in x+q),'oracle nonnegativity')
        require(all(sum(x[k] for k,e in enumerate(edges) if j in e)<=a[j] for j in range(d)),'oracle primal')
        require(all(sum(q[j] for j in e)>=1 for e in edges),'oracle dual')
        require(sum(x)==v==sum(a[j]*q[j] for j in range(d)),'oracle objective gap')
        values.append(v)
    combo={};rhs=Q(0);support=0
    def add(j,v):combo[j]=combo.get(j,Q(0))+v
    for item in p['certificate']:
        m=Q(item['multiplier']);tag=item['row'];require(m>=0,'negative multiplier');support+=bool(m)
        typ,k=tag[:2];require(0<=k<len(states),'profile index');a=states[k]
        if typ=='budget':
            require(len(tag)==2,'budget shape')
            for j,count in enumerate(a+[n-sum(a)]):add(k*stride+j,m*count)
            add(K,-m*values[k])
        elif typ=='coverage':
            require(len(tag)==3,'coverage shape');e=tuple(tag[2]);require(e in edges and all(a[j]>0 for j in e),'unsupported coverage')
            for j in e:add(k*stride+j,-m)
            rhs-=m
        elif typ=='tcwm':
            require(len(tag)==5,'TCWM shape');h,i,count=tag[2:]
            require(0<=h<len(states) and 0<=i<d,'transition index')
            b=states[h];require(b==[a[j]+(j==i) for j in range(d)],'not one fixed zero-owner restoration')
            mult=a+[n-sum(a)-1]
            require(len(count)==stride and all(type(t)==int and 0<=t<=mult[j] for j,t in enumerate(count)),'invalid coalition member count')
            require(1+sum(count)<=s,'coalition exceeds protection')
            add(k*stride+d,m);add(h*stride+i,-m)
            for j,t in enumerate(count):add(k*stride+j,m*t);add(h*stride+j,-m*t)
        else:raise RuntimeError('unknown row '+typ)
    require(combo.get(K,Q(0))<0,'nonnegative factor coefficient')
    require(all(v>=0 for j,v in combo.items() if j!=K),'negative remaining payment coefficient')
    lower=rhs/combo[K]
    require(lower==Q(p['exact_lower']),'claimed lower mismatch')
    claimed={int(k):Q(v) for k,v in p['combo_nonzero'].items()}
    require({k:v for k,v in combo.items() if v}==claimed,'recorded coefficient mismatch')
    require(rhs==Q(p['rhs']),'right side mismatch')
    return dict(file=path.name,sha256=hashlib.sha256(raw).hexdigest(),PASS=True,exact_lower=str(lower),decimal_lower=float(lower),certificate_rows=support,profiles=len(states),owners=n,protected=s)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('paths',nargs='+');args=ap.parse_args()
    for p in args.paths:print(json.dumps(check(Path(p)),sort_keys=True))
