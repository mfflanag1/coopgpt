#!/usr/bin/env python3
"""Finite diagnostic checks; written proof handles unrestricted real domains."""
import random,json,math
from verify_envelope_bounds import evaluate,primitive,require
from tightened_range_reference import tightened_range_rule
from owner_floor_reference import floor_range_rule,floors

def main():
    rng=random.Random(161039);checks=0;max_ratio=0;max_gap=0;grid_checks=0
    for case in range(1400):
        n=rng.randint(1,8);d=rng.randint(1,5);vals=[0,0,0,.125,.25,.5,1,2,8]
        rows=[[rng.choice(vals) for _ in range(1+2*d)] for _ in range(n)]
        if case%3==0:
            for r in rows:r[0]=0
        if case%7==0:rows[-1]=[rng.choice([.25,1,8])]+[0]*(2*d)
        R,witnesses,bases,mf,K,v=floor_range_rule(rows);bar,_,_=tightened_range_rule(rows)
        tol=1e-10*max(1,v['H'],K)
        require(all(v['N'][i]-tol<=R[i]<=bar[i]+tol for i in range(n)),'pointwise sandwich');checks+=1
        require(sum(R)<=1.75*v['F']+tol,'funding transfer');checks+=1
        if v['F']>0:max_ratio=max(max_ratio,sum(R)/v['F']);max_gap=max(max_gap,(sum(bar)-sum(R))/v['F'])
        for i in range(n):
            w=witnesses[i];base=bases[i]
            require(all(w[k]>=base[k]-tol for k in range(n)) and w[i]<=v['B'][i]+tol and sum(w)<=K+tol,'optimizer attainer feasibility');checks+=1
            require(abs(primitive(v['a'],w)[0][i]-R[i])<=tol,'direct primitive attainer value');checks+=1
            if not any(rows[i][1:]):
                require(abs(R[i]-v['N'][i])<=tol,'grid-only exactness');checks+=1;grid_checks+=1
            for k in range(n):
                if k==i:continue
                endpoint=[r.copy() for r in rows]
                for j in range(d):
                    if rows[k][1+j]>=rows[k][1+d+j]:endpoint[i][1+d+j]=0
                    else:endpoint[i][1+j]=0
                require(abs(evaluate(endpoint)['z'][k]-mf[i][k])<=tol,'floor endpoint equality');checks+=1
            for trial in range(8):
                reduced=[r.copy() for r in rows]
                if trial<len(rows[i]):reduced[i][trial]=0
                else:reduced[i]=[x*rng.choice([0,.25,.5,.75,1]) for x in rows[i]]
                other,_,_,lowmf,_,rv=floor_range_rule(reduced)
                require(other[i]<=R[i]+tol,'own-report monotonicity');checks+=1
                require(all(rv['z'][k]>=mf[i][k]-tol for k in range(n) if k!=i),'floor dominates arbitrary underreport');checks+=1
                require(all(lowmf[i][k]>=mf[i][k]-tol for k in range(n) if k!=i),'floor box inclusion antitonicity');checks+=1
                require(rv['N'][i]<=R[i]+tol,'physical nested report below floor range');checks+=1
    family=[]
    for m in [1,2,5,10,50,100]:
        rows=[[0,1/m,0] for _ in range(m)]+[[0,0,1/m] for _ in range(m)]+[[1,0,0]]
        R,_,_,_,_,v=floor_range_rule(rows)
        require(abs(R[-1]-.5/math.e)<1e-11,'balanced-family grid exactness');checks+=1
        family.append([m,sum(R),R[0]*m,R[m]*m,R[-1]])
    print(json.dumps(dict(status='PASS',profiles=1400,finite_checks=checks,grid_exactness_checks=grid_checks,max_sampled_ratio=max_ratio,max_sampled_bar_minus_floor=max_gap,balanced_family=family,scope='finite diagnostic corroboration; universal conclusions rest on written proofs')))
if __name__=='__main__':main()
