#!/usr/bin/env python3
"""Exact-incentive FPTAS for rational two-sparse fractional production.

Public technology uses binary records (u,v,a,b,w) and unary records (v,a,w).
The fixed public graph is built once. All computation uses Fraction arithmetic.
A size guard raises rather than truncating; remove/increase it for the abstract
polynomial construction. Full OUT mode does not assert original marginal floors.
"""
from fractions import Fraction as Q
from math import factorial, lcm
from pathlib import Path
import importlib.util, argparse, json
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('unit_huber',HERE/'exact_huber_solver.py')
huber=importlib.util.module_from_spec(spec);spec.loader.exec_module(huber)

def require(condition,message):
    if not condition:raise ValueError(message)

def residualize(n,binary,unary=()):
    require(isinstance(n,int) and n>=1,'positive integer resource count required')
    gamma=[Q(0)]*n
    for v,a,w in unary:
        a,w=Q(a),Q(w)
        require(isinstance(v,int) and 0<=v<n and a>0 and w>=0,'invalid unary activity')
        gamma[v]=max(gamma[v],w/a)
    residual=[]
    for u,v,a,b,w in binary:
        a,b,w=Q(a),Q(b),Q(w)
        require(isinstance(u,int) and isinstance(v,int) and 0<=u<n and 0<=v<n and u!=v,'invalid binary endpoints')
        require(a>0 and b>0 and w>=0,'invalid binary coefficient/profit')
        profit=w-a*gamma[u]-b*gamma[v]
        if profit>0:residual.append((u,v,a,b,profit))
    return tuple(gamma),tuple(residual)

def public_lift(n,binary,epsilon,unary=(),mode='tcwm',copy_limit=20000):
    epsilon=Q(epsilon)
    require(0<epsilon<=1,'epsilon must lie in (0,1]')
    require(mode in ('tcwm','full_out'),'mode must be tcwm or full_out')
    gamma,acts=residualize(n,binary,unary)
    eta=2*epsilon/3 if mode=='tcwm' else epsilon/2
    M=[Q(0)]*n
    for u,v,a,b,w in acts:M[u]=max(M[u],w/a);M[v]=max(M[v],w/b)
    # Clearing each complete row yields a conservative integral entry bound H.
    H=1
    for row in [(Q(1),x) for x in M]+[(a,b,w) for u,v,a,b,w in acts]:
        denominator=1
        for x in row:denominator=lcm(denominator,x.denominator)
        H=max(H,*(abs(int(x*denominator)) for x in row))
    D=factorial(n)*H**n;delta=Q(1,D)
    grids=[];bins=[];by=[[] for _ in range(n)]
    for v,maximum in enumerate(M):
        if maximum==0:grids.append((Q(0),));continue
        require(maximum>=delta,'Cramer minimum upper-bound consistency')
        grid=[Q(0)];point=delta
        while point<maximum:
            grid.append(point);point*=1+eta
            if copy_limit is not None and len(bins)+len(grid)-1>copy_limit:
                raise ValueError('copy_limit exceeded; no graph/payment was truncated')
        grid.append(maximum);grids.append(tuple(grid))
        for lo,hi in zip(grid,grid[1:]):
            by[v].append(len(bins));bins.append((v,lo,hi))
        if copy_limit is not None and len(bins)>copy_limit:
            raise ValueError('copy_limit exceeded; no graph/payment was truncated')
    edges=set()
    for u,v,a,b,w in acts:
        for i in by[u]:
            for j in by[v]:
                if a*bins[i][1]+b*bins[j][1]<w:edges.add(tuple(sorted((i,j))))
    factor=Q(3,2)+epsilon if mode=='tcwm' else 2+epsilon
    return {'n':n,'mode':mode,'epsilon':epsilon,'eta':eta,'gamma':gamma,
            'activities':acts,'M':M,'integer_entry_bound':H,'determinant_bound':D,
            'delta':delta,'grids':grids,'bins':bins,'edges':sorted(edges),
            'funding_factor_bound':factor,'marginal_floors_asserted':False}

def evaluate(lift,owners,with_certificate=False):
    n=lift['n'];owners=[tuple(map(Q,o)) for o in owners]
    require(all(len(o)==n and all(x>=0 for x in o) for o in owners),'invalid owner report')
    c=[sum(o[v] for o in owners) for v in range(n)]
    bins=lift['bins'];cap=[(hi-lo)*c[v] for v,lo,hi in bins]
    if bins:
        cert=huber.certificate(cap,lift['edges']) if with_certificate else None
        price=cert['p'] if cert is not None else huber.price(cap,lift['edges'])
    else:price=();cert=None
    if lift['mode']=='full_out':price=tuple(min(2*p,Q(1)) for p in price)
    effective=list(lift['gamma'])
    for (v,lo,hi),p in zip(bins,price):effective[v]+=(hi-lo)*p
    payments=[sum(a*b for a,b in zip(o,effective)) for o in owners]
    result={'payments':payments,'resource_prices':effective,'total_payment':sum(payments),
            'funding_factor_bound':lift['funding_factor_bound'],'lift_vertices':len(bins),
            'lift_edges':len(lift['edges']),'mode':lift['mode']}
    if cert is not None:result['unit_certificate']=cert
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('input',type=Path)
    parser.add_argument('--copy-limit',type=int,default=20000);args=parser.parse_args()
    data=json.loads(args.input.read_text())
    lift=public_lift(data['n'],data['binary'],data['epsilon'],data.get('unary',()),
                     data.get('mode','tcwm'),args.copy_limit)
    result=evaluate(lift,data['owners'],with_certificate=False)
    result['public_grid']={'integer_entry_bound':lift['integer_entry_bound'],
       'determinant_bound':lift['determinant_bound'],'delta':lift['delta'],'eta':lift['eta']}
    print(json.dumps(result,default=str,indent=2))
if __name__=='__main__':main()
