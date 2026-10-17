"""Find a mixed-owner failure for quadratic-region hypergraph prices."""
import numpy as np, random,json,itertools
from pathlib import Path
rng=random.Random(37123)
for n in range(5,31):
    allE=list(itertools.combinations(range(n),3))
    for rep in range(3000):
        m=rng.randrange(max(2,n//3),n)
        edges=rng.sample(allE,m);A=np.zeros((m,n))
        for j,e in enumerate(edges):A[j,list(e)]=1
        c=A.sum(axis=0)
        if min(c)==0 or np.linalg.matrix_rank(A)!=m:continue
        dinv=np.diag(1/c);P=np.eye(n)-dinv@A.T@np.linalg.inv(A@dinv@A.T)@A
        pos=np.maximum(P,0).sum(axis=1);e=int(np.argmax(pos))
        if pos[e]>1+1e-7:
            out={'status':'NUMERICAL_DERIVATIVE_WITNESS','n':n,'edges':edges,'capacities':c.tolist(),
                 'changed_coordinate':e,'positive_projection_sum':float(pos[e]),'projection_row':P[e].tolist(),
                 'owner_full_coordinates':[v for v in range(n) if P[v,e]>1e-8]}
            print(json.dumps(out));Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');raise SystemExit
    print('no witness n',n,flush=True)
