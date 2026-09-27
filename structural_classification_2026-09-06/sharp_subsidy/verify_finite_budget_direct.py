"""Coupled-count audit of the finite donor budget after the exact shortfall identity."""
import json,sys

def main():
 if '--smt' not in sys.argv:
  print(json.dumps({'status':'SKIPPED','reason':'optional --smt; see DIRECT_FINITE_BUDGET.md'}));return
 import z3
 Q=lambda a,b=1:z3.RealVal(a)/b
 a,B,x,y=z3.Reals('alpha B x y');zs=[x,y,B-x-y]
 expected={(b,q)for b in (0,1)for q in (1,2,3)};seen=set()
 for branch,q in sorted(expected):
  solver=z3.SolverFor('QF_NRA');solver.set(timeout=30000)
  solver.add(a>0,a<=Q(1,3),B>=0,B<=Q(3,2))
  for z in zs:solver.add(z>=0,z<=1-a,z>=B-1)
  t=Q(4,5)+a/20
  if branch==0:solver.add(B<=1+a);n3=0
  else:solver.add(B>=1+a);n3=B-1-a
  budget=(1-t)*(3-2*B)+(2-t)*n3
  f=[z*(B-z)-B*(1-t)-a*(z+B)for z in zs]
  solver.add(sum(f[:q])>budget)
  if solver.check()!=z3.unsat:raise ValueError('budget false or undecided: '+str((branch,q)))
  seen.add((branch,q))
 if seen!=expected:raise ValueError('incomplete case coverage')
 # Dropping all donor resources must be detected in a feasible count cell.
 control=z3.SolverFor('QF_NRA');control.set(timeout=30000)
 control.add(a>0,a<=Q(1,3),B>=1+a,B<=Q(3,2))
 for z in zs:control.add(z>=0,z<=1-a,z>=B-1)
 t=Q(4,5)+a/20
 control.add(sum(z*(B-z)-B*(1-t)-a*(z+B)for z in zs)>0)
 if control.check()!=z3.sat:raise ValueError('zero-budget negative control failed/undecided')
 print(json.dumps({'status':'PASS','coupled_count_queries':len(seen),'counterexamples':'UNSAT','zero_budget_control':'SAT','scope':'all nontrivial normalized count cells for finite correction; h=2 and full-column exceptions discharged in conventional coverage proof'}))
if __name__=='__main__':main()
