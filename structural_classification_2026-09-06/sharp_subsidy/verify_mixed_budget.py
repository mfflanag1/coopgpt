"""Optional exact real-arithmetic audit of all six mixed-donor budget estimates."""
import sys,json

def main():
 if '--smt' not in sys.argv:
  print(json.dumps({'status':'SKIPPED','reason':'optional --smt requires z3; conventional proof is MIXED_DONOR_UPPER.md'}));return
 import z3
 B=z3.Real('B');Q=lambda a,b=1:z3.RealVal(a)/z3.RealVal(b)
 f1=B*B/4-B/5;f2=B*B/2-2*B/5;f3=2*B*B/3-3*B/5
 small=(3-2*B)/5;large=4*B/5-Q(3,5)
 claims=[(0,1,small-f1-Q(3,20)),(0,1,small-f2-Q(1,10)),(0,1,small-f3-Q(2,15)),(1,Q(3,2),large-f1-Q(3,20)),(1,Q(3,2),large-(3*B/5-Q(1,2))-Q(1,10)),(1,Q(3,2),large-f3)]
 for lo,hi,p in claims:
  s=z3.SolverFor('QF_NRA');s.add(B>=lo,B<=hi,p<0)
  if s.check()!=z3.unsat:raise ValueError('scalar budget audit failed')
 print(json.dumps({'status':'PASS','exact_real_budget_queries':len(claims),'counterexamples':'UNSAT'}))
if __name__=='__main__':main()
