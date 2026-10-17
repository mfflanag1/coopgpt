"""One bounded discovery LP: four fixed owners, min2, reports{0,1,2}^2."""
from itertools import product, combinations_with_replacement
from collections import Counter
from pathlib import Path
import json,sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
n=4
kmax=2
types=list(product(range(kmax+1),repeat=2))
numtypes=len(types)
swap=[types.index(t[::-1]) for t in types]
def compositions(total,k,prefix=()):
    if k==1:
        yield prefix+(total,)
    else:
        for x in range(total+1):yield from compositions(total-x,k-1,prefix+(x,))
states=list(compositions(n,numtypes))
def canonical(state,t):
    sw=tuple(state[swap[j]] for j in range(numtypes))
    return min((state,t),(sw,swap[t]))
keys=sorted({canonical(state,t) for state in states for t in range(numtypes) if state[t]})
index={key:i for i,key in enumerate(keys)}
kindex=len(index)
rr=[];cc=[];vv=[];rhs=[];labels=[]
def ix(state,t):return index[canonical(state,t)]
def add(row,b,label):
    rownum=len(rhs)
    for j,v in row.items():
        if v:rr.append(rownum);cc.append(j);vv.append(v)
    rhs.append(b);labels.append(label)
def plus(row,j,v):row[j]=row.get(j,0)+v
lowoptions=[[j for j,l in enumerate(types) if all(l[e]<=t[e] for e in range(2))] for t in types]
for state in states:
    totals=[sum(state[t]*types[t][e] for t in range(numtypes)) for e in range(2)]
    total=min(totals)
    stand=sum(state[t]*min(types[t]) for t in range(numtypes));gain=total-stand
    row={kindex:-gain}
    present=[t for t in range(numtypes) if state[t]]
    for t in present:plus(row,ix(state,t),state[t])
    add(row,stand,['budget',state])
    for counts in product(*(range(state[t]+1) for t in present)):
        if not sum(counts):continue
        worth=min(sum(c*types[t][e] for c,t in zip(counts,present)) for e in range(2))
        row={}
        for c,t in zip(counts,present):
            if c:plus(row,ix(state,t),-c)
        add(row,-worth,['coverage',state,[[t,c] for t,c in zip(present,counts) if c]])
    for size in [1,2]:
        for picked in combinations_with_replacement(present,size):
            ct=Counter(picked)
            if any(ct[t]>state[t] for t in ct):continue
            for lows in product(*(lowoptions[t] for t in picked)):
                if lows==picked:continue
                lowstate=list(state);removed=[0,0]
                for hi,lo in zip(picked,lows):
                    lowstate[hi]-=1;lowstate[lo]+=1
                    for e in range(2):removed[e]+=types[hi][e]-types[lo][e]
                lowstate=tuple(lowstate)
                row={}
                for t in picked:plus(row,ix(state,t),-1)
                for t in lows:plus(row,ix(lowstate,t),1)
                add(row,-min(removed),['outside',state,picked,lowstate,lows,removed])
a=coo_matrix((vv,(rr,cc)),shape=(len(rhs),kindex+1)).tocsr()
obj=np.zeros(kindex+1);obj[kindex]=1
res=linprog(obj,A_ub=a,b_ub=np.array(rhs),bounds=[(0,None)]*kindex+[(1,None)],method='highs',options={'time_limit':45})
out={'n':n,'report_levels':[0,1,2],'collusion_size':2,'variables':kindex+1,'constraints':len(rhs),'status':res.status,'message':res.message}
if res.success:
    out['gain_factor']=res.fun
    out['payments']=[{'state':key[0],'type':types[key[1]],'pay':float(res.x[j])} for key,j in index.items()]
    out['dual']=[{'label':labels[j],'multiplier':float(v)} for j,v in enumerate(res.ineqlin.marginals) if abs(v)>1e-9]
path=Path(__file__).with_name('pair_gain_ternary_n4_s2.json')
path.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['payments','dual']},indent=2))
