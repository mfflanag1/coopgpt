"""QF_LRA first-face certificate synthesis; feasibility only, no global theorem from UNSAT."""
import json, sys, time
from itertools import product
from pathlib import Path
import z3

m=int(sys.argv[1]) if len(sys.argv)>1 else 3
target_sector=int(sys.argv[2]) if len(sys.argv)>2 else 1
timeout=int(sys.argv[3]) if len(sys.argv)>3 else 60000
graph=sys.argv[4] if len(sys.argv)>4 else 'star'
threshold=int(sys.argv[5]) if len(sys.argv)>5 else 4
if graph not in ('star','cycle') or m<1 or target_sector not in range(4) or threshold<=0:
    raise ValueError('Invalid graph, size, target sector, or threshold')
k=4;n=k*m;target=target_sector*m
root=Path(__file__).resolve().parent
output=root/f'{graph}_m{m}_sector{target_sector}_above{threshold}.json'
def failed(kind,value,tb):
    output.write_text(json.dumps({'status':'FAILED','error':str(value),'graph':graph,'m':m,'target_sector':target_sector,'threshold':threshold})+'\n')
    sys.__excepthook__(kind,value,tb)
sys.excepthook=failed
output.write_text(json.dumps({'status':'RUNNING','m':m,'target_sector':target_sector})+'\n')
edges=[(0,1),(0,2),(0,3)] if graph=='star' else [(0,1),(1,2),(2,3),(0,3)]
A=[[[z3.Real(f'A{e}_{i}_{j}')for j in range(m)]for i in range(m)]for e in range(len(edges))]
x=[z3.Real(f'x{i}')for i in range(n)];y=[z3.Real(f'y{i}')for i in range(n)]
teams=list(product(range(m),repeat=k));weights=[sum(A[e][t[a]][t[b]]for e,(a,b)in enumerate(edges))for t in teams]
T=sum(A[e][i][i]for e in range(len(edges))for i in range(m))
lam=[z3.Real(f'lambda{j}')for j in range(len(teams))]
loads=[z3.Sum([lam[j]for j,t in enumerate(teams)if t[i//m]==i%m])for i in range(n)]
s=z3.Solver();s.set(timeout=timeout)
s.add([v>=0 for B in A for row in B for v in row]);s.add([v<=20 for B in A for row in B for v in row])
s.add([v>=1 for v in x]);s.add([v>=0 for v in y]);s.add(z3.Sum(x)==T,z3.Sum(y)==T,x[target]==1,y[target]>threshold)
for j,t in enumerate(teams):
    sx=z3.Sum([x[v*m+t[v]]for v in range(k)])
    sy=z3.Sum([y[v*m+t[v]]for v in range(k)])
    s.add(sx>=weights[j],sy>=weights[j],lam[j]>=0,z3.Or(lam[j]==0,sx==weights[j]))
for i in range(n):s.add(loads[i]<=1,z3.Or(loads[i]==1,x[i]==1))
s.add(loads[target]<1)
start=time.time();result=s.check()
record={'status':str(result),'graph':graph,'threshold':threshold,'m':m,'target_sector':target_sector,'target':target,'timeout_ms':timeout,'elapsed_seconds':time.time()-start,'scope':'Fixed size, positive first-face target, pair entries in [0,20], normalization tau=1. Unknown is not UNSAT.'}
if result==z3.sat:
    model=s.model()
    def val(v):return str(model.eval(v,model_completion=True))
    record.update({'edges':edges,'matrices':[[[val(v)for v in row]for row in B]for B in A],'x':list(map(val,x)),'y':list(map(val,y)),'T':val(T),'dual':[{'team':t,'weight':val(lam[j])}for j,t in enumerate(teams)if model.eval(lam[j],model_completion=True).as_fraction()>0],'loads':list(map(val,loads))})
else:record['reason_unknown']=s.reason_unknown() if result==z3.unknown else None
output.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({key:record[key]for key in ('status','m','target_sector','elapsed_seconds')}),flush=True)
