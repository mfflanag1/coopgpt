"""Independent standard-library checks for fixed certificates and the cut recipe.
Run: python3 -B -O verify_certificates.py. No optimizer is imported.
"""
from collections import deque
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def path_in_residual(edges, f, source, target, mask=None):
    mask = (1 << len(edges))-1 if mask is None else mask
    queue = deque([source])
    prev = {source: None}
    while queue and target not in prev:
        u = queue.popleft()
        for j,(a,b,c) in enumerate(edges):
            if not (mask >> j & 1):
                continue
            candidates = []
            if a == u and f[j] < c:
                candidates.append((b,1))
            if b == u and f[j] > 0:
                candidates.append((a,-1))
            for v,direction in candidates:
                if v not in prev:
                    prev[v]=(u,j,direction)
                    queue.append(v)
    if target not in prev:
        return None
    path=[]
    v=target
    while v!=source:
        u,j,direction=prev[v]
        path.append((j,direction))
        v=u
    return path[::-1]


def flow_value(edges,f,source='s'):
    return sum(f[j] for j,(u,v,c) in enumerate(edges) if u==source)-sum(f[j] for j,(u,v,c) in enumerate(edges) if v==source)


def validate_flow(edges,f,value,source='s',sink='t'):
    require(all(0<=f[j]<=c for j,(u,v,c) in enumerate(edges)), 'Invalid flow capacity')
    for vertex in {v for e in edges for v in e[:2]}:
        net=flow_value(edges,f,vertex)
        require(net==(value if vertex==source else -value if vertex==sink else 0),'Invalid flow conservation')


def max_flow(edges,mask=None):
    f=[0]*len(edges)
    while True:
        path=path_in_residual(edges,f,'s','t',mask)
        if path is None:
            break
        delta=min(edges[j][2]-f[j] if d==1 else f[j] for j,d in path)
        require(delta>0,'Zero augmentation')
        for j,d in path:
            f[j]+=d*delta
    value=flow_value(edges,f)
    validate_flow(edges,f,value)
    return value,f


def coalition_values(edges):
    return [max_flow(edges,mask)[0] for mask in range(1 << len(edges))]


def pay(x,mask):
    return sum((x[j] for j in range(len(x)) if mask >> j & 1),F(0))


def verify_cover(x,values,floors):
    require(all(x[j]>=floors[j] for j in range(len(x))),'Payoff floor violation')
    require(all(pay(x,mask)>=v for mask,v in enumerate(values)),'Coalition payoff violation')


def verify_lp(cert,c,floor,values,efficient):
    m=len(c)
    x=list(map(F,cert['x']))
    w=[(mask,F(q)) for mask,q in cert['weights']]
    require(len({mask for mask,q in w})==len(w),'Duplicate dual index')
    require(all(0<=mask<len(values) and q>=0 for mask,q in w),'Invalid dual coalition')
    nu=F(cert['efficiency_price'])
    mu=list(map(F,cert['lower_prices']))
    require(efficient or nu==0,'Spurious efficiency multiplier')
    require(len(x)==len(mu)==m and min(mu)>=0,'Invalid vector or dual sign')
    verify_cover(x,values,floor)
    require(not efficient or sum(x)==values[-1],'Core efficiency violation')
    for j in range(m):
        require(sum((q for mask,q in w if mask>>j&1),F(0))+nu+mu[j]==c[j],'Dual coefficient mismatch')
    primal=sum((F(c[j])*x[j] for j in range(m)),F(0))
    dual=sum((values[mask]*q for mask,q in w),F(0))+nu*values[-1]+sum((a*b for a,b in zip(mu,floor)),F(0))
    require(primal==dual==F(cert['objective']),'Certificate duality mismatch')
    return x


def verify_capacities():
    data=json.loads((ROOT/'CAPACITY_PROBES.json').read_text())
    require([c['id'] for c in data['cases']]==['F06','F07','F08','F09','F10'],'Unregistered capacity cases')
    output=[]
    for case in data['cases']:
        edges=case['edges']
        values=coalition_values(edges)
        m=len(edges)
        require(values[-1]==case['T'] and len(values)==case['coalitions'],'Flow values mismatch')
        h=list(map(F,case['H']))
        require(len(case['ideal_certificates'])==m,'Missing ideal certificate')
        for i,cert in enumerate(case['ideal_certificates']):
            x=verify_lp(cert,[-int(i==j) for j in range(m)],[F(0)]*m,values,True)
            require(x[i]==h[i],'Ideal objective mismatch')
        x=verify_lp(case['protected_certificate'],[1]*m,[v/3 for v in h],values,False)
        require(sum(x)-values[-1]==F(case['subsidy']),'Subsidy mismatch')
        require(F(case['ratio'])==F(case['subsidy'])/values[-1],'Ratio mismatch')
        for role,record in case['joint_attainment'].items():
            ids=[j for j,(u,v,c) in enumerate(edges) if (u=='s' if role=='source' else v=='t')]
            require(record['status']=='EXACT_FEASIBLE' and record['indices']==ids,'Unverified joint claim')
            z=list(map(F,record['x']))
            verify_cover(z,values,[F(0)]*m)
            require(sum(z)==values[-1] and all(z[j]==h[j] for j in ids),'Joint witness mismatch')
        damaged=dict(case['protected_certificate'])
        damaged['objective']=str(F(damaged['objective'])+1)
        rejected=False
        try:
            verify_lp(damaged,[1]*m,[v/3 for v in h],values,False)
        except ValueError:
            rejected=True
        require(rejected,'Damaged dual objective accepted')
        output.append({'id':case['id'],'coalitions':len(values),'T':values[-1],
                       'subsidy':case['subsidy'],'exact_ideal_certificates':m,
                       'exact_joint_witnesses':2,'negative_controls_rejected':1})
    return output


def residual_reachable(edges,f,source,reverse=False):
    seen={source}
    changed=True
    while changed:
        changed=False
        for j,(u,v,c) in enumerate(edges):
            arcs=[]
            if f[j]<c: arcs.append((u,v))
            if f[j]>0: arcs.append((v,u))
            for a,b in arcs:
                if reverse: a,b=b,a
                if a in seen and b not in seen:
                    seen.add(b)
                    changed=True
    return seen


def reroute_check(edges,f,path,k,value,source='s',sink='t'):
    if k==0:
        return 0
    target=edges[path[k]][0]
    residual=path_in_residual(edges,f,source,target)
    require(residual is not None,'Prefix not residual-reachable')
    require(all(j not in path for j,d in residual),'Residual prefix touches selected path')
    z=f[:]
    for j in path: z[j]-=1
    for j,d in residual: z[j]+=d
    for j in path[k:]: z[j]+=1
    validate_flow(edges,z,value,source,sink)
    require(all(z[j]==0 for j in path[:k]),'Prefix not eliminated')
    return 1


def unit_recipe(case_id,edges):
    m=len(edges)
    require(all(c==1 for u,v,c in edges),'Recipe requires unit capacities')
    vertices={v for e in edges for v in e[:2]}
    values=coalition_values(edges)
    total,f=max_flow(edges)
    require(total>0,'No flow')
    h=[F(total-values[((1<<m)-1)^(1<<j)]) for j in range(m)]
    require(set(h)<={F(0),F(1)},'Nonbinary deletion cap')
    paths=[]
    unused=f[:]
    while any(unused):
        path=[]
        u='s'
        visited={u}
        while u!='t':
            j=next(j for j,(a,b,c) in enumerate(edges) if a==u and unused[j])
            path.append(j)
            u=edges[j][1]
            require(u not in visited,'Flow path cycle')
            visited.add(u)
        require(len(path)<=3,'Out-of-class path')
        for j in path: unused[j]-=1
        paths.append(path)
    require(len(paths)==total,'Incomplete path decomposition')
    s0=residual_reachable(edges,f,'s')
    s1=vertices-residual_reachable(edges,f,'t',True)
    require(s0<=s1 and 't' not in s1,'Residual cut nesting')
    boundary=lambda side: {j for j,(u,v,c) in enumerate(edges) if u in side and v not in side}
    k0,k1=boundary(s0),boundary(s1)
    require(len(k0)==len(k1)==total,'Cuts not minimum')
    cut_vectors=[]
    for cut in [k0,k1]:
        x=[F(int(j in cut)) for j in range(m)]
        verify_cover(x,values,[F(0)]*m)
        cut_vectors.append(x)
    reroutes=0
    reverse_edges=[(v,u,c) for u,v,c in edges]
    for path in paths:
        a=[i for i,j in enumerate(path) if j in k0]
        b=[i for i,j in enumerate(path) if j in k1]
        require(len(a)==len(b)==1 and a[0]<=b[0],'Cut crossing failure')
        k,l=a[0],b[0]
        require(all(h[j]==0 for j in path[:k]+path[l+1:]),'Nonzero outside ideal')
        reroutes+=reroute_check(edges,f,path,k,total)
        reroutes+=reroute_check(reverse_edges,f,path[::-1],len(path)-1-l,total,'t','s')
    inner=sorted(vertices-{'s','t'})
    min_cuts=[]
    for bits in range(1<<len(inner)):
        cut=boundary({'s'}|{u for j,u in enumerate(inner) if bits>>j&1})
        if len(cut)==total: min_cuts.append(cut)
    require(all(any(j in cut for cut in min_cuts) for j in range(m) if h[j]),'Binary ideal not cut-attained')
    remaining={j for j in range(m) if h[j] and j not in k0|k1}
    r=len(remaining)
    require(r<=total,'Residual count bound failure')
    if not remaining:
        z=[(a+b)/2 for a,b in zip(*cut_vectors)]
        bound=F(0)
        cut2=[]
    else:
        chosen=min(remaining)
        cut2=next(cut for cut in min_cuts if chosen in cut)
        z=[(cut_vectors[0][j]+cut_vectors[1][j]+int(j in cut2))/3 for j in range(m)]
        bound=F(r-1,3)
    y=[max(z[j],h[j]/3) for j in range(m)]
    verify_cover(y,values,[v/3 for v in h])
    require(sum(y)-total<=bound<=F(total-1,3),'Finite bound violated')
    return {'id':case_id,'edges':edges,'coalitions':len(values),'T':total,'r':r,
            'K0':sorted(k0),'K1':sorted(k1),'K2':sorted(cut2),
            'rerouting_certificates':reroutes,'allocation':list(map(str,y)),
            'construction_subsidy':str(sum(y)-total),'r_bound':str(bound)}


if __name__=='__main__':
    cap=verify_capacities()
    initial=json.loads((ROOT/'INITIAL_CHECKS.json').read_text())
    units=[]
    for case in initial['results'][:3]:
        units.append(unit_recipe(case['id'],[(u,v,1) for u,v in case['edges']]))
    mixed=[('s','v',1),('s','v',1),('v','t',1),('s','w',1),('w','t',1),('w','t',1),('s','t',1),('s','d',1)]
    units.append(unit_recipe('F11',mixed))
    units.append(unit_recipe('F12',mixed+[('s','L',1),('L','R',1),('R','t',1)]))
    require(units[-2]['r']==0 and 0<units[-1]['r']<units[-1]['T'],'Required r branches absent')
    require(sum(c['rerouting_certificates'] for c in units)>=4,'Prefix/suffix rerouting coverage absent')
    print(json.dumps({'status':'PASS','capacity_cases':cap,'unit_recipe_cases':units,
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'data_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['INITIAL_CHECKS.json','CAPACITY_PROBES.json']},
        'scope':'Fixed-case exact corroboration, not a universal proof or novelty assessment.'},indent=2))
