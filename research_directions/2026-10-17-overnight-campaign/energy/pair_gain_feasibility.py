"""Discovery only: anonymous binary min2 pair-OUT with gain-only budget."""
from itertools import product, combinations_with_replacement
from collections import Counter
from pathlib import Path
import json,sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix

n=int(sys.argv[1]) if len(sys.argv)>1 else 3
s=int(sys.argv[2]) if len(sys.argv)>2 else 2
states=[t for t in product(range(n+1),repeat=4) if sum(t)==n]
swap=(0,2,1,3)
def canonical(state,t):
    sw=tuple(state[swap[j]] for j in range(4))
    return min((state,t),(sw,swap[t]))
keys=sorted({canonical(state,t) for state in states for t in range(4) if state[t]})
index={key:i for i,key in enumerate(keys)}
kindex=len(index)
constraints=[]; rhs=[]; labels=[]
def ix(state,t): return index[canonical(state,t)]
def add(row,b,label):
    constraints.append({j:v for j,v in row.items() if v});rhs.append(b);labels.append(label)
def plus(row,j,v): row[j]=row.get(j,0)+v
for state in states:
    a,b=state[1]+state[3],state[2]+state[3]
    total=min(a,b); stand=state[3]; gain=total-stand
    row={kindex:-gain}
    for t in range(4):
        if state[t]: plus(row,ix(state,t),state[t])
    add(row,stand,['budget',state])
    for counts in product(*(range(c+1) for c in state)):
        if not sum(counts): continue
        value=min(counts[1]+counts[3],counts[2]+counts[3])
        row={}
        for t in range(4):
            if counts[t]: plus(row,ix(state,t),-counts[t])
        add(row,-value,['coverage',state,counts])
    for size in range(1,s+1):
        for types in combinations_with_replacement(range(4),size):
            histogram=Counter(types)
            if any(histogram[t]>state[t] for t in histogram): continue
            lows=[[l for l in range(4) if l&t==l] for t in types]
            for lowtypes in product(*lows):
                if lowtypes==types: continue
                lowstate=list(state)
                removed=[0,0]
                for hi,lo in zip(types,lowtypes):
                    lowstate[hi]-=1;lowstate[lo]+=1
                    removed[0]+=(hi&1)-(lo&1)
                    removed[1]+=((hi>>1)&1)-((lo>>1)&1)
                lowstate=tuple(lowstate)
                row={}
                for t in types: plus(row,ix(state,t),-1)
                for t in lowtypes: plus(row,ix(lowstate,t),1)
                add(row,-min(removed),['outside',state,types,lowstate,lowtypes,removed])
a=lil_matrix((len(constraints),kindex+1),dtype=float)
for i,row in enumerate(constraints):
    for j,v in row.items(): a[i,j]=v
objective=np.zeros(kindex+1);objective[kindex]=1
res=linprog(objective,A_ub=a.tocsr(),b_ub=np.array(rhs),bounds=[(0,None)]*kindex+[(1,None)],method='highs',options={'time_limit':45})
out={'n':n,'collusion_size':s,'variables':kindex+1,'constraints':len(constraints),'status':res.status,'message':res.message}
if res.success:
    out['gain_factor']=res.fun
    out['payments']=[{'state':key[0],'type':key[1],'pay':float(res.x[j])} for key,j in index.items()]
    out['dual']=[{'label':labels[j],'multiplier':float(v)} for j,v in enumerate(res.ineqlin.marginals) if abs(v)>1e-9]
path=Path(__file__).with_name(f'pair_gain_binary_n{n}_s{s}.json')
path.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['payments','dual']},indent=2))
