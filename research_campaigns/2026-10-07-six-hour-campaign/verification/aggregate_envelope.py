"""Exact finite and symbolic-parameter checks for the aggregate obstruction.

No numerical estimate of the infinite-domain envelope is used. Small graph
prototypes independently check cuts and effective caps; the growing proof uses
the rational means/ranges and analytic concentration inequalities in the note.
"""
from fractions import Fraction as Q
from pathlib import Path
from itertools import product
from math import comb
import importlib.util,json


def mean_min(u,v,p):
    coeff=[Q(0)]*(2*p+1)
    for i in range(p+1):
        for j in range(p+1):
            coeff[i+j]+=Q((-1)**(i+j)*comb(p,i)*comb(p,j),1)/(u**i*v**j)
    return sum((a*u**(i+1)/(i+1) for i,a in enumerate(coeff)),Q(0))


def graph(m,count,k,R,simple=False):
    edges=[];caps=[];records=[];groups=[];nextnode=1;entry=0
    def add(u,v,c,kind,module,split=False):
        nonlocal nextnode
        indices=[]
        if split:
            mid=nextnode;nextnode+=1;segments=[(u,mid),(mid,v)]
        else:segments=[(u,v)]
        for edge in segments:
            indices.append(len(edges));edges.append(edge);caps.append(c)
            records.append((kind,module))
        return indices
    for j in range(count):
        A=nextnode;Bs=list(range(nextnode+1,nextnode+1+m));end=nextnode+1+m;nextnode=end+1
        e=add(entry,A,Q(1),'e',j);ys=[];gs=[];hs=[]
        for B in Bs:
            ys.append(add(entry,B,Q(6,5*m),'y',j,simple))
            gs.append(add(A,B,Q(2),'g',j))
            hs.append(add(B,end,Q(2),'h',j,simple))
        zs=[add(A,end,Q(2),'Z',j,simple) for _ in range(k)]
        groups.append((e,ys,gs,hs,zs));entry=end
    sink=nextnode;nextnode+=1
    final=[add(entry,sink,Q(1,R),'R',-1,simple) for _ in range(R)]
    # Reindex topologically: private subdivision vertices were allocated after
    # their endpoints; the flow oracle itself does not require a topological
    # numbering, but its default sink must be the final vertex.
    if sink!=nextnode-1:
        mapping={sink:nextnode-1,nextnode-1:sink}
        edges=[(mapping.get(u,u),mapping.get(v,v)) for u,v in edges]
    return nextnode,edges,caps,records,groups,final


def masks_from_options(options):
    return [sum(1<<e for choice in row for e in choice) for row in product(*options)]


def expected_cuts(groups,final):
    cuts=[]
    for e,ys,gs,hs,zs in groups:
        choices=[[[x] for x in y+h] for y,h in zip(ys,hs)]
        cuts+=masks_from_options([[e]]+choices)
        zoptions=[[[x] for x in z] for z in zs]
        branches=[[[x] for x in h]+[[x,g[0]] for x in y]
                  for y,g,h in zip(ys,gs,hs)]
        cuts+=masks_from_options(zoptions+branches)
    cuts+=masks_from_options([[[x] for x in path] for path in final])
    assert len(cuts)==len(set(cuts))
    return sorted(cuts)


def run():
    dependency=Path(__file__).resolve().parents[2]/'2026-10-06-monotone-envelope/verification/verify.py'
    spec=importlib.util.spec_from_file_location('flow_verify',dependency)
    v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
    prototypes=[];capchecks=0;cutchecks=0
    cases=[(2,1,2,3,False),(3,1,2,3,False),(4,1,2,3,False),
           (2,2,2,3,False),(3,2,2,3,False),(2,3,2,3,False),
           (2,1,1,2,True),(2,2,1,2,True)]
    for m,count,k,R,simple in cases:
        n,edges,c,records,groups,final=graph(m,count,k,R,simple)
        if simple:assert len(edges)==len(set(edges))
        cuts=expected_cuts(groups,final)
        target=count*(4**m*(1+2**k) if simple else 2**(m+1))+(2**R if simple else 1)
        assert len(cuts)==target
        # The second simple case has many subdivision vertices: cap checks
        # remain exact; avoid exponential vertex-cut enumeration there.
        if n<=16:
            assert v.cutsets(n,edges)==cuts;cutchecks+=1
        for focal in [-1]+list(range(count)):
            ct=list(c);q=Q(3,10*m)
            if focal>=0:ct[groups[focal][0][0]]=q
            D=v.effective(n,edges,ct)
            assert v.maxflow(n,edges,ct)==1
            want=[]
            for kind,j in records:
                local=q if j==focal else Q(1)
                want.append(Q(1,R) if kind=='R' else Q(6,5*m) if kind=='y'
                            else min(Q(1),local+Q(6,5*m)) if kind=='h' else local)
            assert D==want;capchecks+=len(D)
            assert min(v.weighted_sum(ct,C) for C in cuts)==1
            assert min(v.weighted_sum(D,C) for C in cuts)==1
        prototypes.append(dict(m=m,modules=count,Z_paths=k,R_paths=R,simple=simple,
                               vertices=n,owners=len(edges),K=target))
    algebra=0
    for r in range(4,61):
        m=400*r;a=Q(6,5);b=Q(3,10);t=b/m
        high=m*mean_min(a/m,Q(1),1);low=m*mean_min(a/m,(a+b)/m,1)
        assert high==Q(3,5)-Q(6,25*m)>=Q(59,100)
        assert low==Q(11,25)
        assert 2*Q(6,100)**2/(a*a/m)==Q(m,200)
        assert 2*Q(3,100)**2/(a*a/m)==Q(m,800)
        assert 2*(Q(3,2)-Q(53,100))**2/Q(9,10*m)==Q(9409*m,4500)>=2*m
        assert Q(47,100)+t<Q(48,100)<Q(49,100)
        assert Q(1,12*100000)/Q(1,100)**2==Q(1,120)
        error=Q(1,2**(r//2))+Q(1,2**r)+Q(1,2**(2*m-r))+Q(1,120)
        assert error<=Q(23,60)<Q(1,2)
        assert r+m+1==401*r+1
        m=1600*r;t=b/m
        high=m*mean_min(a/m,Q(1),2);low=m*mean_min(a/m,(a+b)/m,2)
        assert high==a/3-a*a/(6*m)+a**3/(30*m*m)>=Q(39,100)
        assert low==Q(166,625)
        assert 2*(Q(3,10)-low)**2/(a*a/m)==Q(1849*m,1125000)>=Q(m,800)
        assert 2*(Q(1)-Q(36,100))**2/Q(9,10*m)==Q(1024*m,1125)>=Q(m,2)
        assert Q(3,10)+t<Q(31,100)<Q(47,150)<Q(53,150)<Q(36,100)
        assert Q(1,18*2000)/Q(1,50)**2==Q(5,72)
        assert Q(1,16)+Q(1,256)+Q(1,16)+Q(5,72)==Q(457,2304)<Q(1,2)
        assert r+12*m==19201*r and r+2*m==3201*r and 19201*r>=2000
        algebra+=1
    return dict(status='PASS',graph_prototypes=prototypes,independent_vertex_cut_checks=cutchecks,
                exact_effective_capacity_checks=capchecks,parameter_cases=algebra,
                scope='Exact finite prototype flow/cut checks and rational concentration parameters; analytic proof supplies all-r probability and envelope conclusions.')


if __name__=='__main__':print(json.dumps(run(),indent=2))
