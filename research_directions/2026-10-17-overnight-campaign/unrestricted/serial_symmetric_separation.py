"""Adversarial LP over symmetric min-linear technologies at a fixed profile."""
import random,json
from pathlib import Path
import numpy as np
from scipy.optimize import linprog

def attack(c,S):
    c=np.array(sorted(c),dtype=float);n=len(c);S=set(S)
    levels=sorted(set(c[c>0]));pts=[np.minimum(c,t) for t in levels]
    target=np.array(sorted(c[i] if i in S else 0 for i in range(n)))
    pts.append(target);m=len(pts);nv=m+m*n
    # Variable v_j and ordered slope w_j; f=min over all permutations of w_j.
    rows=[];rhs=[];eq=[];erhs=[]
    for j,p in enumerate(pts):
        a=np.zeros(nv);a[j]=1;a[m+j*n:m+(j+1)*n]=-p;eq.append(a);erhs.append(0)
        for k,q in enumerate(pts):
            a=np.zeros(nv);a[k]=1;a[m+j*n:m+(j+1)*n]=-q;rows.append(a);rhs.append(0)
        for i in range(n-1):
            a=np.zeros(nv);a[m+j*n+i+1]=1;a[m+j*n+i]=-1;rows.append(a);rhs.append(0)
    a=np.zeros(nv);a[len(levels)-1]=1;eq.append(a);erhs.append(1)
    obj=np.zeros(nv);obj[-m*n-1]=-1 # target v indexed m-1
    obj=np.zeros(nv);obj[m-1]=-1
    for j,t in enumerate(levels):
        share=sum(c[i]>=t for i in S)/sum(c>=t)
        obj[j]+=share
        if j>0:obj[j-1]-=share
    sol=linprog(obj,A_ub=rows,b_ub=rhs,A_eq=eq,b_eq=erhs,bounds=(0,None),method='highs')
    if not sol.success:raise RuntimeError(sol.message)
    return {'profile':c.tolist(),'coalition':sorted(S),'max_violation':-float(sol.fun),
            'values':sol.x[:m].tolist(),'weights':sol.x[m:].reshape(m,n).tolist()}
def run():
    rng=random.Random(8173);worst=0;done=0
    for n in range(3,15):
        for rep in range(200):
            c=sorted(rng.choices(range(1,31),k=n));S=[i for i in range(n) if rng.random()<.5]
            if not S or len(S)==n:continue
            r=attack(c,S);done+=1;worst=max(worst,r['max_violation'])
            if r['max_violation']>1e-7:
                print(json.dumps(r));Path(__file__).with_suffix('.json').write_text(json.dumps(r,indent=2)+'\n');return
        print(n,done,worst,flush=True)
    Path(__file__).with_suffix('.json').write_text(json.dumps({'status':'no positive LP witness; discovery only','profiles':done,'worst':worst},indent=2)+'\n')
if __name__=='__main__':run()
