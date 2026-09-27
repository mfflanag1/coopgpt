"""Exact coefficient and optional real-domain checks of the finite correction."""
from pathlib import Path
from fractions import Fraction as F
import json,sys
from verify_mixed_donor import check

def main():
 root=Path(__file__).parent
 rows=json.loads((root/'FINITE_MIXED_DONOR_CERTIFICATES.json').read_text())
 previous=json.loads((root/'MIXED_DONOR_CERTIFICATES.json').read_text())
 if [(d['case'],d['m'],d['P'])for d in rows]!=[(d['case'],d['m'],d['P'])for d in previous]:raise ValueError('coverage mismatch')
 count=sum(check(d,finite=True)for d in rows)
 for d in rows:
  if F(d['obstruction_upper'])!=F(2,5)-F(1,60*(d['m']-len(d['P']))):raise ValueError('bound metadata')
 bad=dict(rows[0],packings=[])
 try:check(bad,finite=True)
 except ValueError:pass
 else:raise ValueError('empty packing accepted')
 queries=0
 if '--smt' in sys.argv:
  import z3
  B,h=z3.Reals('B h');Q=lambda a,b=1:z3.RealVal(a)/b
  eps=Q(1,20);small=(3-2*B)/5;large=4*B/5-Q(3,5)
  Fs=[B*B/4-B/5,B*B/2-2*B/5,2*B*B/3-3*B/5]
  claims=[]
  for q,f in enumerate(Fs,1):claims.append((0,1,h*(small-f)-eps*(3+(q-2)*B)))
  Fs=[Fs[0],3*B/5-Q(1,2),Fs[2]]
  for q,f in enumerate(Fs,1):
   X=B if q==3 else Q(0)
   claims.append((1,Q(3,2),h*(h*(large-f)+X+q*B-Q(6,5)-eps*(2+(q-1)*B))+eps))
  for lo,hi,gap in claims:
   solver=z3.SolverFor('QF_NRA');solver.add(h>=3,B>=lo,B<=hi,gap<0)
   if solver.check()!=z3.unsat:raise ValueError('finite budget counterexample or unknown')
   queries+=1
 print(json.dumps({'status':'PASS','cases':len(rows),'packing_entries':count,'exact_real_queries':queries,'bound':'2/5-1/(60h)','negative_controls':1}))
if __name__=='__main__':main()
