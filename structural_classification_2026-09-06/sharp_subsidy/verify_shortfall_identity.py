"""Exact raw-capacity identity, including inactive and full-column branches."""
import json,sys

def main():
 if '--smt' not in sys.argv:
  print(json.dumps({'status':'SKIPPED','reason':'optional --smt; see SHORTFALL_IDENTITY_AUDIT.md'}));return
 import z3
 Q=lambda a,b=1:z3.RealVal(a)/b
 a,B,x,t=z3.Reals('alpha B x t')
 mx=lambda u,v:z3.If(u>=v,u,v)
 mn=lambda u,v:z3.If(u<=v,u,v)
 beta=1-a;delta=mx(0,t-2*a);n=1-B+x
 raw=mx(0,x*delta-n*mn(x,beta)-(1-n)*mn(x,beta-delta))
 formula=mx(0,x*(B-x)-B*(1-t)-a*(x+B))
 assumptions=[a>0,a<=Q(1,2),t>0,t<1,B>=0,B<=Q(3,2),x>=0,x<=1,n>=0,n<=1,z3.Or(x<=beta,z3.And(x==1,B==1))]
 solver=z3.SolverFor('QF_NRA');solver.set(timeout=20000);solver.add(*assumptions,raw!=formula)
 if solver.check()!=z3.unsat:raise ValueError('identity false or undecided')
 control=z3.SolverFor('QF_NRA');control.set(timeout=20000);control.add(*assumptions,raw!=formula+1)
 if control.check()!=z3.sat:raise ValueError('damaged-formula control failed/undecided')
 print(json.dumps({'status':'PASS','raw_capacity_identity':'UNSAT counterexample','parameter_domain':'0<t<1; 0<alpha<=1/2; admissible normalized row counts','damaged_formula_control':'SAT','scope':'exact shortfall identity, not a standalone universal donor-budget proof'}))
if __name__=='__main__':main()
