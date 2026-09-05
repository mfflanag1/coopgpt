"""Exercise package rejection of UNKNOWN and nonrational optimum answers."""
from pathlib import Path
from unittest.mock import patch
import json,sys,z3
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'replay_verification'))
import exact_assignment as ea,exact_three as et,verify_independent as vi,verify_extensions as ve
records=[]
def rejected(label,call,kind=RuntimeError):
    try:call()
    except kind as error:records.append({'test':label,'status':'REJECTED','message':str(error)})
    else:raise RuntimeError('unexpected acceptance: '+label)
x=z3.Real('fault_x')
with patch.object(z3.Optimize,'check',return_value=z3.unknown):
    for mod in (ea,et):rejected(mod.__name__+' Optimize UNKNOWN',lambda m=mod:m.optimize([x>=0,x<=1],x,True))
with patch.object(z3.Optimize,'check',return_value=z3.unsat):
    for mod in (ea,et):rejected(mod.__name__+' Optimize UNSAT',lambda m=mod:m.optimize([x>=0,x<=1],x,True))
for mod in (ea,et):
    rejected(mod.__name__+' unbounded optimum',lambda m=mod:m.optimize([x>=0],x,True))
    rejected(mod.__name__+' infinitesimal supremum',lambda m=mod:m.optimize([x>=0,x<1],x,True))
    rejected(mod.__name__+' inconsistent constraints',lambda m=mod:m.optimize([x>1,x<0],x,True))
with patch.object(z3.Solver,'check',return_value=z3.unknown):
    rejected('triple feasibility UNKNOWN',lambda:et.core([[[1]]]))
    rejected('independent UNSAT gate UNKNOWN',lambda:vi.verdict([x>=0],z3.unsat,'fault'))
    rejected('independent SAT gate UNKNOWN',lambda:vi.verdict([x>=0],z3.sat,'fault'))
    rejected('general graph feasibility UNKNOWN',lambda:ve.graph_check('fault',2,{(0,1):1}))
# SAT cannot satisfy a requested UNSAT result or vice versa.
with patch.object(z3.Solver,'check',return_value=z3.sat):
    rejected('SAT rejected for no-violation obligation',lambda:vi.verdict([x>=0],z3.unsat,'fault'))
with patch.object(z3.Solver,'check',return_value=z3.unsat):
    rejected('UNSAT rejected for feasible-witness obligation',lambda:vi.verdict([x>=0],z3.sat,'fault'))
(ROOT/'fault_injection_results.json').write_text(json.dumps({'status':'PASS','tests':records},indent=2)+'\n')
print('PASS',len(records),'fault cases')
