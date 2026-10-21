#!/usr/bin/env python3
"""Stdlib exact verifier: graphic matroid normalized H can exceed 1.

This does not violate H<=2 or the original diagonal conjecture. The instance
is the entire spanning-tree base family of K5 minus adjacent edges01,02.
The focal raw coordinate equals its full value, but its normalized dual
mass is larger because the witness total dual mass falls.
"""
import argparse
from fractions import Fraction as F
import itertools
import json
from pathlib import Path


def verify_kkt(rows,q,lam,rhs):
    assert len(rows)==len(lam)==len(rhs)
    assert all(x>=0 for x in q+lam)
    assert [sum((lam[r] for r,S in enumerate(rows) if j in S),F(0)) for j in range(len(q))]==q
    for r,S in enumerate(rows):
        value=sum(q[j] for j in S)
        assert value>=rhs[r]
        assert lam[r]*(value-rhs[r])==0
    return sum(x*x for x in q)


def spanning_trees(edges,N):
    answer=[]
    for S in itertools.combinations(range(len(edges)),N-1):
        reached={0}
        for _ in range(N):
            for j in S:
                a,b=edges[j]
                if a in reached or b in reached:reached|={a,b}
        if len(reached)==N:answer.append(list(S))
    return answer


def verify(source):
    report=next(r for r in source['results'] if r['name']=='graphic_K5_delete_adjacent2')
    edges=[tuple(e) for e in report['construction']['edges']];rows=report['rows']
    assert edges==[(0,3),(0,4),(1,2),(1,3),(1,4),(2,3),(2,4),(3,4)]
    assert rows==spanning_trees(edges,5) and len(rows)==40
    full=report['full']['fraction_certificate'];q0=list(map(F,full['q']));lam0=list(map(F,full['lambda']))
    rho=verify_kkt(rows,q0,lam0,[F(1)]*40)
    assert q0==[F(1,4)]*8 and rho==F(1,2)
    own=next(o for o in report['owners'] if o['owner']==0)['exact']
    q=list(map(F,own['q']));lam=list(map(F,own['lambda']));rhs=list(map(F,own['rhs']))
    assert all(0<=b<=1 for b in rhs)
    assert all(rhs[r]==1 for r,S in enumerate(rows) if 0 not in S)
    norm=verify_kkt(rows,q,lam,rhs);L=sum(lam);theta=q[0]/L
    assert theta==F(28,55) and L==F(55,112) and norm==L
    assert q[0]==q0[0] and theta>q0[0]/rho
    H_one=rho*(theta*theta+7*F(1,2)**2)
    assert H_one==F(24311,24200)>1
    # Swap vertices3 and4; verify the induced coordinate and row actions.
    swap={0:0,1:1,2:2,3:4,4:3};index={e:j for j,e in enumerate(edges)}
    owner_perm=[index[tuple(sorted((swap[a],swap[b])))] for a,b in edges]
    row_index={tuple(S):r for r,S in enumerate(rows)}
    row_perm=[row_index[tuple(sorted(owner_perm[j] for j in S))] for S in rows]
    assert owner_perm[0]==1
    q1=[F(0)]*8;lam1=[F(0)]*40;rhs1=[F(0)]*40
    for j,k in enumerate(owner_perm):q1[k]=q[j]
    for r,s in enumerate(row_perm):lam1[s]=lam[r];rhs1[s]=rhs[r]
    verify_kkt(rows,q1,lam1,rhs1)
    assert all(rhs1[r]==1 for r,S in enumerate(rows) if 1 not in S)
    assert q1[1]/sum(lam1)==theta
    H_two=rho*(2*theta*theta+6*F(1,2)**2)
    assert H_two==F(12211,12100)>1
    return {'certified':True,'scope':'Graphic matroid normalized H=1 is false; neither H>2 nor original diagonal counterexample.',
            'edges':edges,'all_spanning_tree_rows':rows,'focal_owner':0,'focal_edge':edges[0],
            'full_q':list(map(str,q0)),'rho':str(rho),
            'witness_q':list(map(str,q)),'witness_L':str(L),'witness_theta':str(theta),
            'full_theta':'1/2','strict_coordinate_gap':str(theta-F(1,2)),
            'witness_nonzero_lambda':[{'row_index':r,'row':rows[r],'lambda':str(v)} for r,v in enumerate(lam) if v],
            'witness_rhs':list(map(str,rhs)),
            'H_one_modified_owner':str(H_one),'H_two_symmetric_modified_owners':str(H_two),
            'symmetry_owner_permutation':owner_perm,'symmetry_row_permutation':row_perm,
            'raw_focal_coordinate_increased':False}


def main():
    here=Path(__file__).parent
    parser=argparse.ArgumentParser();parser.add_argument('--input',default=str(here/'mass_search_matroid_guard.json'));parser.add_argument('--output',default=str(here/'mass_search_matroid_certificate.json'));args=parser.parse_args()
    result=verify(json.loads(Path(args.input).read_text()));Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('certified','scope','witness_theta','full_theta','strict_coordinate_gap','H_one_modified_owner','H_two_symmetric_modified_owners')},indent=2))


if __name__=='__main__':main()
