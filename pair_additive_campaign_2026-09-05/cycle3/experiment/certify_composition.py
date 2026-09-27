"""Export rational LP duals, primal ideal witnesses, and complete leximin stages."""
from pathlib import Path
from fractions import Fraction as F
import json,sys,time
import numpy as np
from scipy.optimize import linprog
import composition,pilot

def rat(x):return F(float(x)).limit_denominator(1000000)
def sparse(values):return [[i,str(rat(v))] for i,v in enumerate(values) if abs(v)>1e-8]
def dual(result):
    return dict(inequalities=sparse(-result.ineqlin.marginals),equalities=sparse(-result.eqlin.marginals),lower=sparse(result.lower.marginals))

def main(tag):
    start=time.monotonic();prefix='composition' if tag=='201' else 'composition_'+tag
    raw=json.loads((pilot.ROOT/(prefix+'_float.json')).read_text())
    M,teams,w,A,b,matching,perms=composition.build(tuple(map(int,tag)));n=63;m=21
    E=np.zeros((len(matching),n))
    for row,(i,j,k) in zip(E,matching):row[[i,m+j,2*m+k]]=1
    e=np.array([M[0][i][j]+M[1][i][k]+M[2][j][k] for i,j,k in matching])
    x=[rat(v) for v in raw['x']];stages=[];fixed=[]
    for stage in raw['x_stages']:
        value=rat(stage['level']);players=stage['players'];free=[i for i in range(n) if i not in fixed]
        AA=np.vstack((A,-np.eye(n)[free]));bb=np.r_[b,[-float(value)]*len(free)]
        EE=np.vstack((E,np.eye(n)[fixed]));ee=np.r_[e,[float(x[i]) for i in fixed]]
        certificates=[]
        for i in players:
            result=linprog(-np.eye(n)[i],A_ub=AA,b_ub=bb,A_eq=EE,b_eq=ee,bounds=(0,None),method='highs')
            pilot.require(result.success and abs(result.x[i]-float(value))<1e-7,'pinned query')
            certificates.append(dict(player=i,dual=dual(result)))
        stages.append(dict(level=str(value),players=players,certificates=certificates));fixed+=players
    H=[];ideal_witnesses=[];ideal_certificates=[]
    for i in range(n):
        result=linprog(-np.eye(n)[i],A_ub=A,b_ub=b,A_eq=E,b_eq=e,bounds=(0,None),method='highs')
        pilot.require(result.success,'ideal query');H.append(rat(result.x[i]));ideal_witnesses.append([str(rat(v)) for v in result.x]);ideal_certificates.append(dual(result))
    # Human-readable sparse dual for maximizing the common first floor.
    objective=np.zeros(n+1);objective[-1]=-1
    AA=np.vstack((np.column_stack((A,np.zeros(len(b)))),np.column_stack((-np.eye(n),np.ones(n)))))
    result=linprog(objective,A_ub=AA,b_ub=np.r_[b,np.zeros(n)],A_eq=np.column_stack((E,np.zeros(len(e)))),b_eq=e,bounds=[(0,None)]*n+[(None,None)],method='highs')
    pilot.require(result.success,'floor query')
    certificate=dict(input_file=prefix+'_input.json',n=n,T=56,x=list(map(str,x)),x_stages=stages,H=list(map(str,H)),ideal_witnesses=ideal_witnesses,ideal_certificates=ideal_certificates,first_floor=str(rat(-result.fun)),first_floor_dual=dual(result),minimum_fraction=str(min(a/h for a,h in zip(x,H) if h)),central_b=19,central_b_fraction=str(x[19]/H[19]),elapsed_seconds=time.monotonic()-start)
    pilot.save(prefix+'_exact.json',certificate)
    print(tag,'exported rational certificates',certificate['minimum_fraction'],certificate['central_b_fraction'],round(certificate['elapsed_seconds'],3),flush=True)

if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else '201')
