from fractions import Fraction as F
from pathlib import Path
import json
from exact_three import selector, optimize, require, Q
import z3


def market(L, omit_reverse=False):
    labels, colors = [], []
    ids = {}
    for l in range(L+1):
        for i in range(3):
            for name, c in [('U',i+(l%2)),('V',i+(1-l%2)),('D',i+2)]:
                ids[name,l,i] = len(labels)
                labels.append(f'{name}_{l}_{i}')
                colors.append(c%3)
    for i in range(3):
        ids['G',0,i] = len(labels)
        labels.append(f'G_{i}')
        colors.append(i)
    edges = {}
    def add(keys,w):
        e = tuple(sorted(ids[key] for key in keys))
        require(len(set(e))==3 and set(colors[a] for a in e)==set(range(3)), 'not a valid triple')
        require(e not in edges, 'repeated edge')
        edges[e]=w
    for l in range(L+1):
        for i in range(3):
            add([('U',l,i),('V',l,i),('D',l,i)],1)
            add([('U',l,i),('V',l,i),('G',0,(i+2)%3)],1)
            if l:
                j,k = [q for q in range(3) if q!=i]
                add([('U',l,i),('V',l-1,j),('V',l-1,k)],2)
                if not omit_reverse:
                    add([('V',l,i),('U',l-1,j),('U',l-1,k)],1)
    p = [z3.Real(s) for s in labels]
    T = 3*(L+1)
    core = [q>=0 for q in p]+[sum(p)==T]+[sum(p[i] for i in e)>=w for e,w in edges.items()]
    return labels, colors, ids, edges, p, core, T


def verify(L):
    labels, colors, ids, edges, p, core, T = market(L)
    edge_list = list(edges)
    take = [z3.Int(f'take_{j}') for j in range(len(edges))]
    match = [z3.Or(q==0,q==1) for q in take]
    match += [sum(take[j] for j,e in enumerate(edge_list) if i in e)<=1 for i in range(len(p))]
    matching_total = optimize(match,sum(take[j]*edges[e] for j,e in enumerate(edge_list)),True)
    require(matching_total==T,'integral matching total')
    x,xstages = selector(core,p,True)
    z,zstages = selector(core,p,False)
    expected = []
    for label in labels:
        fields=label.split('_')
        name=fields[0]
        if name in ['U','V']:
            level=int(fields[1]); u=F(2**level,2**L+1)
            expected.append(u if name=='U' else 1-u)
        else: expected.append(F(0))
    require(x==expected and z==expected,'full selectors mismatch')
    target=ids['V',L,0]
    ideal=optimize(core,p[target],True)
    require(ideal==1,'coordinate maximum mismatch')
    equations=[]
    for l in range(L+1):
        for i in range(3):
            equations += [p[ids['D',l,i]]==0,p[ids['U',l,i]]+p[ids['V',l,i]]==1]
            if l:
                j,k=[q for q in range(3) if q!=i]
                equations += [p[ids['U',l,i]]==p[ids['U',l-1,j]]+p[ids['U',l-1,k]]]
    equations += [p[ids['G',0,i]]==0 for i in range(3)]
    solver=z3.Solver();solver.set(timeout=60000);solver.add(*core,z3.Not(z3.And(*equations)))
    require(solver.check()==z3.unsat,'core outside recurrence system')
    result=dict(L=L,n=len(p),side_sizes=[colors.count(i) for i in range(3)],T=T,positive_triples=len(edges),integral_matching_optimum=str(matching_total),target=labels[target],target_ideal=str(ideal),target_leximin=str(x[target]),rho='0',Lmin=list(map(str,x)),Lmax=list(map(str,z)),Lmin_stages=xstages,Lmax_stages=zstages)
    print('PASS',L,'n=',len(p),'ratio=',x[target],flush=True)
    return result


if __name__=='__main__':
    records=[verify(L) for L in [0,1,2,3]]
    _,_,ids,_,p,core,_=market(2,omit_reverse=True)
    solver=z3.Solver();solver.set(timeout=60000)
    solver.add(*core,p[ids['U',1,0]]!=p[ids['U',0,1]]+p[ids['U',0,2]])
    require(solver.check()==z3.sat,'negative control did not break recurrence')
    witness={str(q):str(solver.model().eval(q)) for q in p}
    payload=dict(cases=records,negative_control=dict(description='Omitting complementary reverse triples permits points outside the recurrence core',witness=witness))
    Path(__file__).with_name('coordinate_amplification_checks.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print('PASS negative control',flush=True)
