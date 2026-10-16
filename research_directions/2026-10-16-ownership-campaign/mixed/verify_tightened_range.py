#!/usr/bin/env python3
import math,random,json
from verify_envelope_bounds import require,evaluate
from verify_explicit_range_rule import range_rule
from tightened_range_reference import tightened_range_rule

def main():
    rng=random.Random(661412);checks=0;max_ratio=0;max_gap=0
    for case in range(1800):
        n=rng.randint(1,8);d=rng.randint(1,5);vals=[0,0,.125,.25,.5,1,2,8]
        rows=[[rng.choice(vals) for _ in range(1+2*d)] for _ in range(n)]
        if case%3==0:
            for r in rows:r[0]=0
        old,_,v=range_rule(rows);new,_,_=tightened_range_rule(rows);tol=1e-10*max(1,v['H'],v['P']+v['M'])
        require(all(v['N'][i]-tol<=new[i]<=old[i]+tol for i in range(n)),'pointwise sandwich failed');checks+=1
        require(sum(new)<=1.75*v['F']+tol,'transferred budget failed');checks+=1
        if v['F']>0:max_ratio=max(max_ratio,sum(new)/v['F']);max_gap=max(max_gap,(sum(old)-sum(new))/v['F'])
        for i in range(n):
            for trial in range(12):
                reduced=[r.copy() for r in rows]
                if trial<len(rows[i]):reduced[i][trial]=0
                else:reduced[i]=[x*rng.choice([0,.25,.5,.75,1]) for x in rows[i]]
                other,_,_=tightened_range_rule(reduced)
                require(other[i]<=new[i]+tol,'tightened rule own-monotonicity failed');checks+=1
    for m in [1,2,5,10,100]:
        rows=[[0,1/m,0] for _ in range(m)]+[[0,0,1/m] for _ in range(m)]+[[1,0,0]]
        R,_,_=tightened_range_rule(rows)
        expected=1.5-.25/math.e+.25*math.exp(-1/(2*m))
        require(abs(sum(R)-expected)<1e-10,'tightened lower-family formula failed');checks+=1
    print(json.dumps(dict(status='PASS',profiles=1800,finite_checks=checks,max_sampled_tightened_ratio=max_ratio,max_sampled_old_minus_new_ratio=max_gap,scope='finite diagnostics; monotonicity and uniform funding transferred by written proof')))
if __name__=='__main__':main()
