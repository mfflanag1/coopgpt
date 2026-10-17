import sys,json,numpy as np
sys.path.insert(0,'/private/tmp/coopgpt-overnight-20261017/unrestricted')
from projection_envelope_milp import diagonal
out=[]
for L in range(3,11):
 edges=[(a,a+s) for a in range(L) for s in [1,2] if a+s<=L]
 adj={a:[(j,b) for j,(aa,b) in enumerate(edges) if aa==a] for a in range(L)}
 def paths(a):
  if a==L:return [[]]
  return [[j]+p for j,b in adj[a] for p in paths(b)]
 pp=paths(0);n=1+len(edges)
 A=np.array([[1]+[int(j in p) for j in range(n-1)] for p in pp],float)
 for variant in ['unit','length']:
  b=np.ones(len(A)) if variant=='unit' else A.sum(axis=1)/max(A.sum(axis=1))
  val=diagonal(A,b,limit=2)
  if val is not None:
   rec={'L':L,'variant':variant,'n':n,'rows':len(A),**val};out.append(rec)
   print(json.dumps({'L':L,'variant':variant,'n':n,'rows':len(A),'squared':val['squared_ratio'],'sum':val['sum_ratio'],'M':val['M']}),flush=True)
   if val['squared_ratio']>1+1e-7:print(json.dumps({'counter':rec,'A':A.tolist(),'b':b.tolist()}),flush=True);raise SystemExit
print(json.dumps({'complete':True,'count':len(out)}),flush=True)
