"""Exact quotient-certificate checker, independent of numerical discovery."""
from fractions import Fraction as Q
from pathlib import Path
import argparse,hashlib,json

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def acted(a,g):
    result=[0]*len(a)
    for j in range(len(a)):result[g[j]]=a[j]
    return tuple(result)

def check(path):
    raw=path.read_bytes();p=json.loads(raw);d=p['d'];n=p['n'];s=p['s'];K=p['factor_index']
    edges={tuple(sorted(e)) for e in p['edges']};G=set(map(tuple,p['automorphisms']))
    require(tuple(range(d)) in G,'missing group identity')
    require(all(len(g)==d and set(g)==set(range(d)) for g in G),'not permutations')
    for g in G:
        require({tuple(sorted(g[j] for j in e)) for e in edges}==edges,'non-technology automorphism')
        require(all(tuple(g[h[j]] for j in range(d)) in G for h in G),'group not closed')
    require(all(0<len(e)<=3 and len(set(e))==len(e) for e in edges),'arity')
    states=p['profiles'];maps=p['qmap'];key_to_var={};var_to_key={}
    require(len(states)==len(maps),'mapping count')
    for a,ix in zip(states,maps):
        require(len(a)==d and all(type(v)==int and v>=0 for v in a) and sum(a)<n,'owner counts')
        require(len(ix)==d+1 and all(type(v)==int and 0<=v<K for v in ix),'variable map')
        images=[(acted(a,g),g) for g in G];canon=min(t for t,g in images)
        gs=[g for t,g in images if t==canon]
        keys=[(canon,min(g[j] for g in gs)) for j in range(d)]+[(canon,d)]
        for key,var in zip(keys,ix):
            require(key_to_var.setdefault(key,var)==var,'same orbit split into inconsistent variables')
            require(var_to_key.setdefault(var,key)==key,'different orbits identified')
    values={}
    for key,o in p['oracles'].items():
        k=int(key);a=states[k];x=list(map(Q,o['primal']));y=list(map(Q,o['dual']));v=Q(o['value'])
        original_edges=list(map(tuple,p['edges']))
        require(len(x)==len(original_edges) and len(y)==d and all(t>=0 for t in x+y),'oracle shape/sign')
        require(all(sum(x[t] for t,e in enumerate(original_edges) if j in e)<=a[j] for j in range(d)),'production primal')
        require(all(sum(y[j] for j in e)>=1 for e in edges),'production dual')
        require(sum(x)==v==sum(a[j]*y[j] for j in range(d)),'production gap')
        values[k]=v
    combo={};rhs=Q(0)
    def add(i,v):combo[i]=combo.get(i,Q(0))+v
    for item in p['certificate']:
        m=Q(item['multiplier']);tag=item['row'];require(m>=0,'negative multiplier');typ,k=tag[:2]
        require(0<=k<len(states),'profile index');a=states[k];q=maps[k]
        if typ=='budget':
            require(len(tag)==2 and k in values,'budget lacks exact production')
            for j,t in enumerate(a+[n-sum(a)]):add(q[j],m*t)
            add(K,-m*values[k])
        elif typ=='coverage':
            require(len(tag)==3,'coverage shape');e=tuple(sorted(tag[2]));require(e in edges and all(a[j]>0 for j in e),'invalid supported edge')
            for j in e:add(q[j],-m)
            rhs-=m
        elif typ=='tcwm':
            require(len(tag)==5,'transition shape');h,i,count=tag[2:]
            require(0<=h<len(states) and 0<=i<d,'transition index');b=states[h];r=maps[h]
            require(b==[a[j]+(j==i) for j in range(d)],'not an actual fixed zero-owner restoration')
            mult=a+[n-sum(a)-1]
            require(len(count)==d+1 and all(type(t)==int and 0<=t<=mult[j] for j,t in enumerate(count)),'coalition multiplicity')
            require(1+sum(count)<=s,'coalition too large')
            add(q[d],m);add(r[i],-m)
            for j,t in enumerate(count):add(q[j],m*t);add(r[j],-m*t)
        else:raise RuntimeError('unknown inequality')
    require(combo.get(K,Q(0))<0 and all(v>=0 for j,v in combo.items() if j!=K),'dual coefficient failure')
    bound=rhs/combo[K]
    require(bound==Q(p['exact_lower']),'bound mismatch')
    require(rhs==Q(p['rhs']),'RHS mismatch')
    require({j:v for j,v in combo.items() if v}=={int(j):Q(v) for j,v in p['combo_nonzero'].items()},'coefficient replay mismatch')
    return {'file':path.name,'sha256':hashlib.sha256(raw).hexdigest(),'PASS':True,'owners':n,'protected':s,'resource_group_order':len(G),'profiles_in_certificate_packet':len(states),'certificate_rows':len(p['certificate']),'exact_lower':str(bound),'decimal_lower':float(bound)}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('paths',nargs='+');args=ap.parse_args()
    for path in args.paths:print(json.dumps(check(Path(path)),sort_keys=True))
