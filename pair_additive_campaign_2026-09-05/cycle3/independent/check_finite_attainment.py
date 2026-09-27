"""Independent raw full-core/selector checks of the saved finite1/6 witness."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import hashlib
import json
import z3

source=Path(__file__).resolve().parents[1]/'experiment'/'finite_attainment_exact.json'
record=json.loads(source.read_text())
A,B,C=record['matrices'];m=len(A);T=F(record['T'])


def require(value,message):
    if not value:raise RuntimeError(message)


require(m==9 and all(len(M)==m for M in (A,B,C)) and all(len(row)==m for M in (A,B,C) for row in M),'square equal sectors')
require(all(isinstance(v,int) and v>=0 for M in (A,B,C) for row in M for v in row),'nonnegative integer pair entries')
teams=[((i,m+j,2*m+k),A[i][j]+B[i][k]+C[j][k]) for i,j,k in product(range(m),repeat=3)]
# Use the separate natural local matching, not the saved solver matching.
matching=[(3*s,m+3*s+2,2*m+3*s+2) for s in range(3)]
matching += [(3*s+1,m+3*s,2*m+3*s+1) for s in range(3)]
matching += [(3*s+2,m+3*s+1,2*m+3*s) for s in range(3)]
weights=dict(teams)
require(sorted(u for team in matching for u in team)==list(range(27)),'matching partition')
require(sum(weights[team] for team in matching)==T,'matching value')
points={name:tuple(map(F,record[field])) for name,field in
        (('x','x'),('z','z'),('ideal_target','target_ideal_witness'))}
for name,point in points.items():
    require(len(point)==27,name+' all labeled coordinates')
    require(min(point)>=0 and sum(point)==T,name+' nonnegative efficiency')
    require(all(sum(point[u] for u in team)>=w for team,w in teams),name+' all729triple covers')
p=z3.Reals(' '.join('p'+str(i) for i in range(27)))
base=[v>=0 for v in p]+[z3.Sum(p)==z3.RealVal(str(T))]
base += [sum(p[u] for u in team)>=w for team,w in teams]
queries=[]


def impossible(constraints,bad,label):
    solver=z3.Solver();solver.set(timeout=30000);solver.add(*constraints,bad)
    result=solver.check()
    require(result==z3.unsat,label+': expected UNSAT, got '+str(result))
    queries.append({'query':label,'result':str(result)})


def selector(candidate,ascending,name):
    face=list(base);remaining=set(range(27))
    for level in sorted(set(candidate),reverse=not ascending):
        q=z3.RealVal(str(level));group=[u for u in remaining if candidate[u]==level]
        impossible(face,z3.And([p[u]>q if ascending else p[u]<q for u in remaining]),name+' better floor '+str(level))
        face += [p[u]>=q if ascending else p[u]<=q for u in remaining]
        impossible(face,z3.Or([p[u]!=q for u in group]),name+' forced coordinates '+str(level))
        face += [p[u]==q for u in group];remaining.difference_update(group)
    require(not remaining,'all coordinates examined')


selector(points['x'],True,'full ascending')
selector(points['z'],False,'full descending')
target=record['target'];require(target==4,'target b_1')
impossible(base,p[target]>2,'whole-core ideal target upper bound2')
require(points['ideal_target'][target]==2 and points['x'][target]==F(1,3),'target exact values')
rho=sum(abs(a-b) for a,b in zip(points['x'],points['z']))/T
require(rho==F(record['rho'])==F(5,9),'distance')
print(json.dumps({'status':'PASS','source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                  'players':27,'triple_checks':3*len(teams),'integral_T':str(T),
                  'target':target,'target_x':'1/3','target_H':'2','target_fraction':'1/6',
                  'rho':str(rho),'queries':queries,'solver':z3.get_version_string(),
                  'scope':'Raw finite core feasibility, complete selector stage certificates, and target ideal only; other listed ideals not audited',
                  'unknown_policy':'Every status other than UNSAT raises; no optimizer used'},indent=2))
