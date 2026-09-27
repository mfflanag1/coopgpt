"""Independent raw core/first-face audit; candidate generator and budget ignored."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib
import json
import z3

source=Path(__file__).resolve().parents[1]/'experiment'/'candidate.json'
raw=source.read_bytes();record=json.loads(raw)
A,B,C=[[[F(v) for v in row] for row in M] for M in record['matrices']]
m=len(A)

def require(ok,msg):
    if not ok: raise RuntimeError(msg)

require(m==21 and all(len(M)==m and all(len(row)==m for row in M) for M in (A,B,C)), 'dimensions')
require(all(v>=0 and v.denominator==1 for M in (A,B,C) for row in M for v in row), 'nonnegative integer pair values')
triples=[((i,m+j,2*m+k), A[i][j]+B[i][k]+C[j][k]) for i,j,k in product(range(m),repeat=3)]
weights=dict(triples)
matching=[(i,m+j,2*m+k) for i,j,k in record['matching']]
require(len(matching)==m and sorted(v for team in matching for v in team)==list(range(3*m)), 'integral matching partition')
T=sum(weights[team] for team in matching)
require(T==87,'matching total87')
points={name:tuple(map(F,record[name])) for name in ('x','y')}
for name,p in points.items():
    require(len(p)==3*m and min(p)>=0 and sum(p)==T,name+' nonnegative efficiency')
    for team,w in triples:
        require(sum(p[i] for i in team)>=w, name+' violated triple '+str(team))
target=record['target'];require(target==6,'target identity')
require(min(points['x'])==1 and points['x'][target]==1,'first-floor witness')
require(points['y'][target]==9,'ideal witness')

p=z3.Reals(' '.join('p'+str(i) for i in range(3*m)))
base=[v>=0 for v in p]+[z3.Sum(p)==z3.RealVal(str(T))]
base += [sum(p[i] for i in team)>=z3.RealVal(str(w)) for team,w in triples]
queries=[]

def reject(extra,label):
    s=z3.Solver();s.set(timeout=45000);s.add(*base,*extra)
    status=s.check()
    if status==z3.sat:
        raise RuntimeError(label+' was SAT: '+str(s.model()))
    require(status==z3.unsat,label+': '+str(status))
    queries.append({'query':label,'status':str(status)})

reject([v>1 for v in p],'global floor strictly greater than1')
reject([v>=1 for v in p]+[p[target]>1],'target greater than1 on entire first face')
reject([p[target]>9],'target whole-core ideal greater than9')
print(json.dumps({'status':'PASS','source':str(source),'source_sha256':hashlib.sha256(raw).hexdigest(),
                  'sector_size':m,'players':3*m,'triple_covers_checked':2*len(triples),
                  'matching_teams':len(matching),'matching_weights':[str(weights[t]) for t in matching],
                  'T':str(T),'first_floor':'1','target':target,'target_full_leximin':'1',
                  'target_ideal':'9','target_ratio':'1/9','queries':queries,
                  'solver':z3.get_version_string(),'unknown_policy':'Any status other than UNSAT raises',
                  'scope':'Both raw feasible covers, integral worth, first floor, target fixed on full first face, whole-core target ideal; no other full-selector coordinates asserted',
                  'unused_fields':['budget','floor_support','predicted_ideal']},indent=2))
