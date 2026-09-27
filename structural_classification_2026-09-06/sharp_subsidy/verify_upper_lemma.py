"""Optional independent real-arithmetic check of the global scalar inequality."""
from fractions import Fraction as F
import json,sys


def require(ok,msg):
 if not ok:raise ValueError(msg)


def run():
 t=F(13137,20000);a=(2-t)/3
 require(t>=0 and t*t+10*t-7<0 and a==F(26863,60000),'rational parameter algebra')
 result={'status':'PASS','rational_parameter':'13137/20000','rational_upper':str(a),'smt_requested':'--smt'in sys.argv,'smt_queries':0}
 if '--smt'in sys.argv:
  import z3
  x,n,t=z3.Reals('upper_x upper_n upper_t')
  solver=z3.SolverFor('QF_NRA');solver.set(timeout=30000)
  domain=[x>=0,x<=1,n>=0,n<=1,n>=2*x-1,t>=0,t*t+10*t-7<=0]
  failure=n*x+(1-n)*(1-t)-t*x<0
  solver.add(*domain,failure);verdict=solver.check()
  require(verdict==z3.unsat,'scalar theorem was not proved UNSAT: '+str(verdict))
  control=z3.SolverFor('QF_NRA');control.set(timeout=30000)
  control.add(x>=0,x<=1,n>=0,n<=1,n>=2*x-1,t==z3.RealVal('3/4'),failure)
  require(control.check()==z3.sat,'out-of-domain negative control failed')
  result.update({'scalar_counterexample':'UNSAT','outside_range_counterexample':'SAT','smt_queries':2})
 print(json.dumps(result))


if __name__=='__main__':run()
