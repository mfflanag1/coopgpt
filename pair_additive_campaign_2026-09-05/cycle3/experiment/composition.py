"""One seven-block composition gate; complete strict pair-additive core."""
import json,time,sys
from fractions import Fraction as F
from itertools import product
import numpy as np
from scipy.optimize import linprog
import pilot

ROOT=pilot.ROOT

def build(rotation=(2,0,1)):
    m=21
    matrices=[[[0]*m for _ in range(m)] for _ in range(3)]
    perms=[(0,1,2)]*3+[rotation]*3+[(0,1,2)]
    def add(s,i,t,j,value):
        if s>t:s,t,i,j=t,s,j,i
        matrices[{(0,1):0,(0,2):1,(1,2):2}[s,t]][i][j]+=value
    def original(block,s,role):return perms[block][s],3*block+role
    for block in range(7):
        for pair,(s,t) in enumerate(((0,1),(0,2),(1,2))):
            for i,j in product(range(3),repeat=2):
                gs,gi=original(block,s,i);gt,gj=original(block,t,j)
                add(gs,gi,gt,gj,int(pilot.BASE['ABC'[pair]][i][j]))
    for offset in (0,3):
        a=original(offset,0,0);d=original(offset+1,1,0);i=original(offset+2,2,2)
        for p,q in ((a,d),(a,i),(d,i)):add(*p,*q,1)
    left=original(1,0,1);right=original(4,0,1);central=original(6,1,0)
    for p,q in ((left,central),(left,right),(central,right)):add(*p,*q,1)
    teams=list(product(range(m),repeat=3))
    weights=[matrices[0][i][j]+matrices[1][i][k]+matrices[2][j][k] for i,j,k in teams]
    positive=[(t,w) for t,w in zip(teams,weights) if w]
    rows=np.zeros((len(positive),3*m))
    for row,((i,j,k),w) in zip(rows,positive):row[[i,m+j,2*m+k]]=-1
    matching=[]
    for block in range(7):
        for local in ((0,2,2),(1,0,1),(2,1,0)):
            team=[None]*3
            for s,role in enumerate(local):gs,gi=original(block,s,role);team[gs]=gi
            matching.append(team)
    pilot.require(sum(matrices[0][i][j]+matrices[1][i][k]+matrices[2][j][k] for i,j,k in matching)==56,'matching weight')
    return matrices,teams,weights,rows,-np.array([w for t,w in positive]),matching,perms

def main():
    rotation=tuple(map(int,sys.argv[1])) if len(sys.argv)>1 else (2,0,1)
    tag=''.join(map(str,rotation));prefix='composition' if tag=='201' else 'composition_'+tag
    started=time.monotonic();M,teams,w,A,b,matching,perms=build(rotation);n=63;T=56
    result=dict(label='seven_block_composition_rotation'+tag,m=21,rotation=list(rotation),matrices=M,matching=matching,matching_total=T,all_triples=len(teams),positive_triples=len(b))
    pilot.save(prefix+'_input.json',result)
    feasible=linprog(np.zeros(n),A_ub=A,b_ub=b,A_eq=[np.ones(n)],b_eq=[T],bounds=(0,None),method='highs')
    if not feasible.success:
        cover=linprog(np.ones(n),A_ub=A,b_ub=b,bounds=(0,None),method='highs')
        result.update(status='fixedtotal_infeasible_float',fractional_cover_total=cover.fun,cover_point=cover.x.tolist(),elapsed_seconds=time.monotonic()-started)
        pilot.save(prefix+'_float.json',result);print(result['status'],cover.fun,flush=True);return
    print('FEASIBLE T56',len(b),'positive triples',flush=True)
    x,xst=pilot.float_selector(A,b,T,True)
    print('FULL X',xst,flush=True)
    H=[]
    for i in range(n):
        q=linprog(-np.eye(n)[i],A_ub=A,b_ub=b,A_eq=[np.ones(n)],b_eq=[T],bounds=(0,None),method='highs')
        pilot.require(q.success,'ideal failure');H.append(q.x[i])
    target=min((i for i in range(n) if H[i]>1e-7),key=lambda i:x[i]/H[i])
    result.update(status='admitted_float',T=T,x=x,x_stages=xst,H=H,target=target,min_fraction=x[target]/H[target],central_b=19,central_b_fraction=x[19]/H[19],elapsed_seconds=time.monotonic()-started)
    pilot.save(prefix+'_float.json',result)
    print('RESULT target',target,'x',x[target],'H',H[target],'ratio',result['min_fraction'],'central',x[19],H[19],result['central_b_fraction'],'seconds',result['elapsed_seconds'],flush=True)

if __name__=='__main__':main()
