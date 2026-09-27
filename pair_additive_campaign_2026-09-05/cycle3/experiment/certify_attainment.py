"""Immediate exact nomination of the first finite1/6 cell."""
import json
from fractions import Fraction as F
from pilot import ROOT,exact_check,save,require

records=json.loads((ROOT/'records.json').read_text())
record=next(r for r in records if r['label']=='triangle_roles002_weight1')
exact=exact_check(record)
require(exact['min_fraction']==F(1,6),'finite attainment did not survive exact check')
save('finite_attainment_exact.json',exact)
print('EXACT FINITE ATTAINMENT',exact['min_fraction'],'target',exact['target'],'x',exact['x'][exact['target']],'H',exact['H'][exact['target']],flush=True)
