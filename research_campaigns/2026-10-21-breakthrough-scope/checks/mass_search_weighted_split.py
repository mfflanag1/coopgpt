#!/usr/bin/env python3
"""Independent audit and bounded row-add splitting of the 29/20 seed.

For pattern p with multiplicity M_p and N=sum M_p, let w_p=M_p/N.
G=sum w_p p p^T is the actual clone Gram matrix divided by N. A normalized
dual alpha gives the same coordinate theta_p=p.alpha to each clone. Write
R=min_simplex alpha^T G alpha. The full cover has rho=1/(N R), and actual
normalized t=1/L equals N times the weighted LP t. Thus
H=rho sum_clones theta^2=sum_p w_p theta_p^2/R.

Nonempty rows are essential. In that case every simplex alpha has positive
quadratic value, so R>0. The support inequalities imply t>=alpha^T G alpha
>=R>0; an explicit positive t lower bound is unnecessary mathematically.
Zero weights represent removed clone classes and must not leave an empty row.

Here A={0,2} has multiplicity2, B={0,3} multiplicity2, C={1,2,3}
multiplicity1. A fifth row receives each class's fraction0,1/2,or1.
The 27 choices are recorded; the all-zero choice is rejected as an empty row.
All valid weighted witnesses and full projections are Fraction-certified,
and each optimized pattern is compared with the frozen ordinary-clone MILP.
Finite LP/MILP bounds remain numerical; exact checks certify exhibited values.
"""
import argparse
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import time

import numpy as np
import root_weighted_patterns as root
import normalized_mass_search as clones


def rational(x):return F(float(x)).limit_denominator(1000000)


def certify(P,weights,result):
    m=P.shape[1];p=[[int(x) for x in row] for row in P]
    G=[[sum(weights[j]*p[j][r]*p[j][s] for j in range(len(p))) for s in range(m)] for r in range(m)]
    def potential(alpha):return [sum(G[r][s]*alpha[s] for s in range(m)) for r in range(m)]
    a=list(map(rational,result['full_alpha']));ga=potential(a);R=sum(a[r]*ga[r] for r in range(m))
    full_ok=sum(a)==1 and all(x>=0 for x in a) and R>0 and all(v>=R for v in ga) and all(a[r]*(ga[r]-R)==0 for r in range(m))
    witnesses=[]
    for own,raw in zip(p,result['witnesses']):
        alpha=list(map(rational,raw['alpha']));t=rational(raw['t']);pp=potential(alpha)
        ok=sum(alpha)==1 and all(x>=0 for x in alpha) and t>0
        ok=ok and all(pp[r]>=t for r in range(m) if not own[r])
        ok=ok and all(pp[r]<=t for r in range(m) if own[r] and alpha[r]>0)
        ok=ok and all(pp[r]==t for r in range(m) if not own[r] and alpha[r]>0)
        theta=sum(alpha[r]*own[r] for r in range(m))
        witnesses.append({'certified':ok,'alpha':list(map(str,alpha)),'t_weighted':str(t),'theta':str(theta)})
    H=sum(weights[j]*F(w['theta'])**2 for j,w in enumerate(witnesses))/R
    return {'certified':full_ok and all(w['certified'] for w in witnesses),'full':{'certified':full_ok,'alpha':list(map(str,a)),'R':str(R)},'witnesses':witnesses,'H':str(H)}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    base=[([1,0,1,0],F(2)),([1,0,0,1],F(2)),([0,1,1,1],F(1))]
    results=[];started=time.monotonic()
    payload={'audit':__doc__,'root_source_sha256':hashlib.sha256(Path(root.__file__).read_bytes()).hexdigest(),'frozen_clone_source_sha256':hashlib.sha256(Path(clones.__file__).read_bytes()).hexdigest(),'results':results,'planned_cases':27}
    for fractions in itertools.product((F(0),F(1,2),F(1)),repeat=3):
        patterns=[];multiplicity=[]
        for (p,mul),fraction in zip(base,fractions):
            for bit,share in ((0,1-fraction),(1,fraction)):
                if share>0:patterns.append(p+[bit]);multiplicity.append(mul*share)
        P=np.array(patterns,float);weights=[w/F(5) for w in multiplicity]
        name='split_'+ '_'.join(str(f).replace('/','-') for f in fractions)
        if not all(P.T@np.array(list(map(float,weights)))>0):
            results.append({'name':name,'fractions':list(map(str,fractions)),'valid':False,'reason':'empty fifth row; uniform demand1 is infeasible'})
            continue
        value=root.evaluate(weights,P);cert=certify(P,weights,value);assert cert['certified'],(name,cert)
        # Doubling these multiplicities gives an ordinary ten-owner cover.
        expanded=[];representatives=[]
        for p,mul in zip(patterns,multiplicity):
            representatives.append(len(expanded));assert (2*mul).denominator==1
            expanded.extend([p]*int(2*mul))
        A=np.array(expanded,float).T;assert A.shape[1]==10
        full=clones.full_projection(A)
        R=F(cert['full']['R']);rho=F(1,10)/R
        assert full['valid'] and abs(full['rho']-float(rho))<1e-7
        baseline=(np.array(list(map(lambda x:float(F(x)),cert['full']['alpha']))),float(10*R))
        ordinary=[clones.optimize_owner(A,i,seconds=5,baseline=baseline) for i in representatives]
        discrepancy=max(abs(o['theta']-float(F(c['theta']))) for o,c in zip(ordinary,cert['witnesses']))
        assert all(o['valid'] for o in ordinary) and discrepancy<1e-7,(name,discrepancy)
        report={'name':name,'fractions':list(map(str,fractions)),'valid':True,'patterns':patterns,'multiplicities':list(map(str,multiplicity)),'weights':list(map(str,weights)),'weighted':value,'exact':cert,'ordinary_clone_matrix_rows':clones.row_lists(A),'ordinary_owner_representatives':representatives,'ordinary_optimizations':ordinary,'clone_rho_exact':str(rho),'weighted_clone_max_theta_discrepancy':discrepancy}
        results.append(report);payload['elapsed']=time.monotonic()-started
        valid=[r for r in results if r['valid']];best=max(valid,key=lambda r:F(r['exact']['H']));payload['best']={'name':best['name'],'H':best['exact']['H']}
        Path(args.output).write_text(json.dumps(payload,indent=2)+'\n')
        print(json.dumps({'name':name,'H':cert['H'],'H_float':float(F(cert['H'])),'certified':cert['certified'],'clone_agreement':discrepancy<1e-7}),flush=True)
        if F(cert['H'])>2:break
    payload['elapsed']=time.monotonic()-started;Path(args.output).write_text(json.dumps(payload,indent=2)+'\n')


if __name__=='__main__':main()
