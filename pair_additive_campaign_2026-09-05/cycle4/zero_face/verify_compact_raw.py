"""Check the normalized seven-team restriction without assuming core projection."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib
import json
import sys
import z3

source=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]/'experiment'/'reduced_candidate.json'
raw=source.read_bytes();r=json.loads(raw)

def require(ok,msg):
    if not ok: raise RuntimeError(msg)

matrices=[[[F(v) for v in row] for row in M] for M in r['matrices']]
require(len(matrices)==3 and all(len(M)==7 and all(len(row)==7 for row in M) for M in matrices),'three7by7matrices')
require(all(v>=0 and v.denominator==1 for M in matrices for row in M for v in row),'nonnegative integer pairs')
A,B,C=matrices
triples=[((i,7+j,14+k),A[i][j]+B[i][k]+C[j][k]) for i,j,k in product(range(7),repeat=3)]
weights=dict(triples)
matching=[(i,7+j,14+k) for i,j,k in r['matching']]
require(len(matching)==7 and sorted(v for t in matching for v in t)==list(range(21)),'perfect matching')
T=sum(weights[t] for t in matching);require(T==15,'matching value15')
fields=('floor_witness','ideal_witness') if 'floor_witness' in r else ('x','y')
points={name:list(map(F,r[field])) for name,field in zip(('x','y'),fields)}
for name,v in points.items():
    require(len(v)==21 and min(v)>=0 and sum(v)==T,name+' nonnegative efficiency')
    for team,w in triples: require(sum(v[i] for i in team)>=w,name+' triple '+str(team))
target=r['target'];require(target==3,'target first-sector index3')
require(min(points['x'])==F(1,3) and points['x'][target]==F(1,3),'floor witness')
require(points['y'][target]==3,'target ideal witness')
p=z3.Reals(' '.join('q'+str(i) for i in range(21)))
base=[v>=0 for v in p]+[z3.Sum(p)==15]+[sum(p[i] for i in team)>=z3.RealVal(str(w)) for team,w in triples]
queries=[]

def reject(extra,label):
    s=z3.Solver();s.set(timeout=45000);s.add(*base,*extra);status=s.check()
    if status==z3.sat: raise RuntimeError(label+' SAT: '+str(s.model()))
    require(status==z3.unsat,label+': '+str(status))
    queries.append({'query':label,'status':str(status)})

level=z3.RealVal('1/3')
reject([v>level for v in p],'first floor above1/3')
reject([v>=level for v in p]+[p[target]>level],'target above1/3 on full first face')
reject([p[target]>3],'whole-core target ideal above3')
print(json.dumps({'status':'PASS','source':str(source.resolve()),'sha256':hashlib.sha256(raw).hexdigest(),
                  'players':21,'triple_covers_checked':2*len(triples),'matching_weights':[str(weights[t]) for t in matching],
                  'T':'15','first_floor':'1/3','target':target,'target_full_leximin':'1/3','target_ideal':'3',
                  'target_ratio':'1/9','queries':queries,'solver':z3.get_version_string(),
                  'unknown_policy':'Every non-UNSAT result raises',
                  'scope':'Standalone compact full core and target first-face/ideal certificates; no whole-core preservation under restriction and no other selector coordinates asserted'},indent=2))
