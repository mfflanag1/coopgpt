import two_hub_blocks as tb
import numpy as np,json
from pathlib import Path
from scipy.optimize import linprog
from scipy.sparse import vstack,csr_matrix
orig=tb.structure;records=json.loads(Path(__file__).with_name('BLOCK_STRESS_RESULTS.json').read_text());out=[]
for idx,rec in enumerate(records):
 same=rec['same'];m,P=tb.example(same,0);base=orig(m,P);L=rec['L'];rb=[sum(L[b])+sum(b in bs for bs in base[6])-2 for b in range(5)]
 tb.structure=lambda m,P:(*base[:3],rb,L,*base[5:])
 types,stride,rows,rhs,eq,erhs,bounds,A,E=tb.model(m,P);c=np.zeros(len(bounds))
 for k,(b,t,s)in enumerate(types):c[k*stride+b]=L[b][t]
 r=linprog(np.zeros(len(bounds)),A_ub=A,b_ub=rhs,A_eq=vstack([E,csr_matrix(c.reshape(1,-1))]),b_eq=erhs+[4],bounds=bounds,options={'time_limit':3})
 out.append({'same':same,'case':rec['case'],'status':r.status})
 tb.structure=orig
 if r.status:print('failed tight',same,rec['case'],r.status,flush=True);break
 if idx%100==0:print(idx,'tight feasible',flush=True)
Path(__file__).with_name('ROOT_MASS_STRESS.json').write_text(json.dumps(out)+'\n');print('tested',len(out),'failures',sum(d['status']!=0 for d in out),flush=True)
