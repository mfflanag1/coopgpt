"""Independent standard-library exact verifier for the eight registered cases.
Discovery uses cut enumeration; this checker constructs maxflows and matching cuts.
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
    # A feasible flow and an equal-capacity cut certify the coalition value.
    # Recompute reachability independently of the augmenting-path BFS.
    allowed = (1 << len(edges))-1 if mask is None else mask
    reachable = {'s'}
    changed = True
    while changed:
        changed = False
        for j,(u,v,c) in enumerate(edges):
            if not (allowed >> j & 1):
                require(f[j] == 0, 'Flow uses an absent coalition arc')
                continue
            if u in reachable and f[j] < c and v not in reachable:
                reachable.add(v)
                changed = True
            if v in reachable and f[j] > 0 and u not in reachable:
                reachable.add(u)
                changed = True
    require('t' not in reachable, 'Computed flow is augmentable')
    cut_capacity = sum(c for j,(u,v,c) in enumerate(edges)
                       if allowed >> j & 1 and u in reachable and v not in reachable)
    require(value == cut_capacity, 'Max-flow/min-cut certificate mismatch')
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


def validate_class(edges):
    require(all(isinstance(c,int) and c>=0 for u,v,c in edges),'Noninteger fixture capacity')
    vertices={v for u,v,c in edges}|{u for u,v,c in edges}
    indeg={v:sum(b==v for a,b,c in edges) for v in vertices}
    todo=[v for v in vertices if indeg[v]==0]
    ordered=[]
    while todo:
        u=todo.pop(); ordered.append(u)
        for a,b,c in edges:
            if a==u:
                indeg[b]-=1
                if indeg[b]==0: todo.append(b)
    require(len(ordered)==len(vertices),'Fixture is cyclic')
    longest={'s':0}
    for u in ordered:
        if u in longest:
            for a,b,c in edges:
                if a==u: longest[b]=max(longest.get(b,-1),longest[u]+1)
    require(0<longest.get('t',0)<=3,'Fixture violates path-length class')


def rejected(fn):
    try: fn()
    except (ValueError,IndexError): return 1
    raise ValueError('Negative control was accepted')


def validate_manifest(registry, data):
    require(registry['budget']==len(registry['cases'])==8, 'Invalid registered budget')
    require(data['status']=='PASS' and data['solver_retries']==0, 'Invalid discovery status')
    cases=data['cases']
    require(0<len(cases)<=registry['budget'], 'Empty or over-budget discovery')
    if len(cases)<registry['budget']:
        require(any(z['status']=='EXACT_OBSTRUCTION'
                    for z in cases[-1]['joint_attainment'].values()),
                'Incomplete discovery without a terminal obstruction')


def main():
    import copy
    registry=json.loads((ROOT/'INSTANCES.json').read_text())
    data=json.loads((ROOT/'DISCOVERY.json').read_text())
    require(data['registry_sha256']==hashlib.sha256((ROOT/'INSTANCES.json').read_bytes()).hexdigest(),'Registry modified')
    require(data['script_sha256']==hashlib.sha256((ROOT/'discover.py').read_bytes()).hexdigest(),'Discovery script modified')
    validate_manifest(registry, data)
    cases=data['cases']
    bad=copy.deepcopy(data); bad['cases']=[]
    manifest_controls=rejected(lambda:validate_manifest(registry,bad))
    bad=copy.deepcopy(data); bad['cases']=[cases[0]]*(registry['budget']+1)
    manifest_controls+=rejected(lambda:validate_manifest(registry,bad))
    out=[]
    for k,case in enumerate(cases):
        reg=registry['cases'][k]
        require(case['id']==reg['id'] and case['edges']==reg['edges'],'Unregistered fixture')
        edges=case['edges']; validate_class(edges)
        values=coalition_values(edges); m=len(edges)
        require(values[-1]==case['T']>0 and len(values)==case['coalitions'],'Value mismatch')
        h=list(map(F,case['H']))
        require(len(h)==len(case['ideal_certificates'])==m,'Missing ideal certificate')
        for j,c in enumerate(case['ideal_certificates']):
            x=verify_lp(c,[-int(i==j) for i in range(m)],[F(0)]*m,values,True)
            require(x[j]==h[j],'Ideal mismatch')
        require(set(case['joint_attainment'])=={'source','sink'},'Missing endpoint')
        endpoints={}
        for role,z in case['joint_attainment'].items():
            ids=[j for j,(u,v,c) in enumerate(edges) if (u=='s' if role=='source' else v=='t')]
            require(z['indices']==ids,'Endpoint index mismatch')
            x=verify_lp(z['certificate'],[-int(i in ids) for i in range(m)],[F(0)]*m,values,True)
            best=sum((x[j] for j in ids),F(0)); target=sum((h[j] for j in ids),F(0))
            require(best==F(z['max_sum']) and target==F(z['sum_ideals']),'Support mismatch')
            require(best<=target and target-best==F(z['gap']),'Gap mismatch')
            expected='EXACT_FEASIBLE' if best==target else 'EXACT_OBSTRUCTION'
            require(z['status']==expected,'Invalid status')
            if best==target: require(all(x[j]==h[j] for j in ids),'Nonjoint witness')
            if expected=='EXACT_OBSTRUCTION': require(k==len(cases)-1,'Continued after obstruction')
            endpoints[role]=expected
        floor=[v/3 for v in h]
        x=verify_lp(case['protected_certificate'],[1]*m,floor,values,False)
        require(sum(x)-values[-1]==F(case['subsidy']),'Subsidy mismatch')
        require(F(case['ratio'])==F(case['subsidy'])/values[-1],'Ratio mismatch')
        cert=case['protected_certificate']; n=0
        bad=copy.deepcopy(cert); bad['objective']=str(F(bad['objective'])+1)
        n+=rejected(lambda:verify_lp(bad,[1]*m,floor,values,False))
        bad=copy.deepcopy(cert); bad['x'][0]='-1'
        n+=rejected(lambda:verify_lp(bad,[1]*m,floor,values,False))
        bad=copy.deepcopy(cert); bad['weights'].append([len(values),'1'])
        n+=rejected(lambda:verify_lp(bad,[1]*m,floor,values,False))
        out.append({'id':case['id'],'coalitions':len(values),'ideals':m,'endpoints':endpoints,'subsidy':case['subsidy'],'negative_controls_rejected':n})
    print(json.dumps({'status':'PASS','cases':out,'manifest_negative_controls_rejected':manifest_controls,'scope':'Finite exact checks only; no universal or priority inference.','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'data_sha256':hashlib.sha256((ROOT/'DISCOVERY.json').read_bytes()).hexdigest()},indent=2))


if __name__=='__main__': main()
