#!/usr/bin/env python3
"""Finite diagnostics for exact analytic box optimizer and mechanism refinement."""
import random,json,math
from verify_envelope_bounds import evaluate,primitive,require
from owner_floor_reference import floor_range_rule
from owner_box_reference import box_range_rule,optimize_box_owner

def main():
    rng=random.Random(161047);checks=0;max_ratio=0;max_gap=0
    for case in range(1800):
        n=rng.randint(1,9);d=rng.randint(1,5);vals=[0,0,0,.125,.25,.5,1,2,8]
        rows=[[rng.choice(vals) for _ in range(1+2*d)] for _ in range(n)]
        if case%3==0:
            for r in rows:r[0]=0
        if case%7==0:rows[-1]=[rng.choice([.25,1,8])]+[0]*(2*d)
        R,ws,lows,ups,K,v=box_range_rule(rows);floor,*_=floor_range_rule(rows);tol=1e-10*max(1,v['H'],K)
        require(all(v['N'][i]-tol<=R[i]<=floor[i]+tol for i in range(n)),'box sandwich');checks+=1
        require(sum(R)<=1.75*v['F']+tol,'box funding transfer');checks+=1
        if v['F']>0:max_ratio=max(max_ratio,sum(R)/v['F']);max_gap=max(max_gap,(sum(floor)-sum(R))/v['F'])
        for i in range(n):
            w=ws[i];lo=lows[i];up=ups[i]
            require(all(lo[k]-tol<=w[k]<=up[k]+tol for k in range(n)) and sum(w)<=K+tol,'box attainer feasibility');checks+=1
            require(abs(primitive(v['a'],w)[0][i]-R[i])<=tol,'box attainer direct primitive');checks+=1
            for trial in range(8):
                # Direct feasible auxiliary competitors independent of optimizer.
                aux=lo.copy();order=list(range(n));rng.shuffle(order);rem=max(0,K-sum(aux))
                for k in order:
                    move=min(rem,up[k]-lo[k])*rng.random();aux[k]+=move;rem-=move
                require(primitive(v['a'],aux)[0][i]<=R[i]+tol,'feasible auxiliary beats formula');checks+=1
                reduced=[r.copy() for r in rows]
                if trial<len(rows[i]):reduced[i][trial]=0
                else:reduced[i]=[x*rng.choice([0,.25,.5,.75,1]) for x in rows[i]]
                other,_,lo2,up2,_,rv=box_range_rule(reduced)
                require(other[i]<=R[i]+tol,'box own monotonicity');checks+=1
                require(rv['N'][i]<=R[i]+tol,'actual envelope below box');checks+=1
                for k in range(n):
                    if k!=i:
                        require(lo[k]-tol<=v['p'][k]+rv['z'][k]<=up[k]+tol,'physical local response outside recipient box');checks+=1
                        require(lo2[i][k]>=lo[k]-tol and up2[i][k]<=up[k]+tol,'box inclusion');checks+=1
    # Generic optimizer tests sever the link to local-production formulas.
    for case in range(12000):
        n=rng.randint(2,9);i=rng.randrange(n);a=[rng.randrange(20)/4 for _ in range(n)]
        lo=[rng.randrange(12)/4 for _ in range(n)];up=[x+rng.randrange(20)/4 for x in lo]
        beta=up[i];K=beta+sum(lo[k] for k in range(n) if k!=i)+rng.randrange(20)/4
        answer,w,_=optimize_box_owner(a,lo,up,beta,K,i);tol=1e-10*max(1,K,sum(a))
        require(all(lo[k]-tol<=w[k]<=up[k]+tol for k in range(n)) and sum(w)<=K+tol,'generic attainer domain');checks+=1
        require(abs(primitive(a,w)[0][i]-answer)<=tol,'generic attainer direct value');checks+=1
        for trial in range(10):
            aux=lo.copy();rem=K-sum(aux);order=list(range(n));rng.shuffle(order)
            for k in order:
                move=min(rem,up[k]-lo[k])*rng.random();aux[k]+=move;rem-=move
            require(primitive(a,aux)[0][i]<=answer+tol,'generic auxiliary beat formula');checks+=1
    print(json.dumps(dict(status='PASS',profiles=1800,generic_optimizer_profiles=12000,finite_checks=checks,max_sampled_box_ratio=max_ratio,max_sampled_floor_minus_box=max_gap,scope='finite floating diagnostics; no uniform improvement inferred')))
if __name__=='__main__':main()
