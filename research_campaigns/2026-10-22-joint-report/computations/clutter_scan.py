#!/usr/bin/env python3
"""Bounded discovery scan; no finite result is an asymptotic claim."""
from itertools import combinations
from pathlib import Path
import json, random
from joint_lp import solve

HERE = Path(__file__).parent
rng = random.Random(20261022)
n = 6
triples = list(combinations(range(n), 3))
families = []
families.append(('cycle_pairs', [[int(j in (i, (i+1)%n)) for j in range(n)] for i in range(n)]))
families.append(('cycle_triples', [[int((j-i)%n<3) for j in range(n)] for i in range(n)]))
families.append(('all_triples', [[int(j in row) for j in range(n)] for row in triples]))
for z in range(24):
    chosen = rng.sample(triples, rng.randint(3, 12))
    families.append((f'random_{z}', [[int(j in row) for j in range(n)] for row in chosen]))

results=[]
for name, forms in families:
    out=solve(forms, (1,8))
    item={'name':name, 'status_scope':'FLOATING DISCOVERY ONLY', **out}
    results.append(item)
    print(json.dumps(item), flush=True)
    (HERE/'clutter_scan.json').write_text(json.dumps(results,indent=2)+'\n')

best=max((r for r in results if 'float_beta' in r), key=lambda r:r['float_beta'])
exact=solve(best['forms'],(1,8),HERE/'clutter_best.json')
print(json.dumps({'best_name':best['name'],**exact}),flush=True)
