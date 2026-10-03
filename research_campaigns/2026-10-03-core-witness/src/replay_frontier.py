from pathlib import Path
from fractions import Fraction as Q
from itertools import product
import json,importlib.util,hashlib
c=Path(__file__).resolve().parent.parent;root=c.parent.parent;old=root/'structural_classification_2026-09-06/sharp_subsidy'
checkpath=Path(__file__).with_name('check_certificate.py')
spec=importlib.util.spec_from_file_location('acceptance',checkpath);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
out=[]
for rec in json.loads((old/'CYCLIC_FRONTIER_CERTIFICATES.json').read_text()):
 d=rec['pattern'];m=d['m'];P=d['P'];D=d['denominator'];scale=d['primal_scale']
 def pairs(t):a,b,z=t;return ((0,a,b),(1,a,z),(2,b,z))
 E=sorted({e for t in P+[[j,j,j] for j in range(m)] for e in pairs(t)});off=len(E)
 U=sorted(set(range(3*m))-{s*m+j for t in P for s,j in enumerate(t)})
 teams=[t for t in product(range(m),repeat=3) if any(e in E for e in pairs(t))]
 vals=[Q(x,scale) for x in d['primal_integers']];w=dict(zip(E,vals[:off]));xs=[vals[off+k*3*m:off+(k+1)*3*m] for k in range(len(U))]
 mats=[[['0']*m for _ in range(m)] for _ in range(3)]
 for (s,a,b),x in w.items():mats[s][a][b]=str(x)
 lam=[]
 for row,z in d['inequality_multipliers']:
  k,j=divmod(row,len(teams));lam.append([U[k],*teams[j],str(Q(3*z,D))])
 nus=[Q(3*x,D) for x in d['equality_multipliers']]
 # Compute claimed upper from the old certified format's exact residuals.
 rw={e:Q(0) for e in E};rx=[[Q(0)]*(3*m) for _ in U]
 for t in P:
  for e in pairs(t):rw[e]+=3
 for k,i in enumerate(U):rx[k][i]+=1
 for i,a,b,z,mass in lam:
  q=Q(mass);k=U.index(i)
  for e in pairs((a,b,z)):
   if e in rw:rw[e]-=q
  for j in (a,m+b,2*m+z):rx[k][j]+=q
 for s in range(3):
  for j in range(m):rw[s,j,j]-=nus[0]
 for k in range(len(U)):
  for j in range(3*m):rx[k][j]-=nus[k+1]
 bound=(sum(nus)+sum(max(Q(0),z) for z in rw.values())+sum(max(Q(0),z) for row in rx for z in row))/3-1
 J=sum(w[e] for t in P for e in pairs(t))+sum(xs[k][i] for k,i in enumerate(U))/3-1
 new={'schema':'core-witness-v1','m':m,'P':P,'support':list(map(list,E)),'unmatched':U,'matrices':mats,'witness_targets':U,'witnesses':[list(map(str,row)) for row in xs],'primal_J':str(J),'dual':{'lambda':lam,'normalization':str(nus[0]),'totals':list(map(str,nus[1:])),'upper':str(bound)}}
 result=v.check(new);result['name']=rec['name'];out.append(result)
(c/'calibration/FRONTIER_REPLAY.json').write_text(json.dumps({'status':'PASS','source_sha256':hashlib.sha256((old/'CYCLIC_FRONTIER_CERTIFICATES.json').read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256(checkpath.read_bytes()).hexdigest(),'records':out,'scope':'schema conversion and independent arithmetic check of all34 retained fixed-support certificates; no new support'},indent=2)+'\n')
print(json.dumps({'status':'PASS','records':len(out),'full_team_checks':sum(z['num_cover_checks'] for z in out)}))
