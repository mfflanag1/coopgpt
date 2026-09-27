"""Exact Farkas arithmetic for the coefficientwise discovery model."""
from pathlib import Path
from fractions import Fraction as F
import json
from affine_block_model import build

def check(d):
 rows,rhs,eq,erhs,n=build(d['same']);nr=len(rows);rs=rows+eq;bs=rhs+erhs
 total=[F(0)]*n;bound=F(0);seen=set()
 for j,raw in d['multipliers']:
  if not isinstance(j,int)or not 0<=j<len(rs)or j in seen:raise ValueError('bad constraint index')
  seen.add(j);w=F(raw)
  if j<nr and w<0:raise ValueError('negative inequality multiplier')
  bound+=w*bs[j]
  for k,v in rs[j].items():total[k]+=w*v
 if bound>=0 or any(v<0 for v in total):raise ValueError('not a Farkas contradiction')
 if bound!=F(d['bound'])or len(seen)!=d['support']:raise ValueError('metadata mismatch')
 return len(seen)

def run():
 ds=json.loads(Path(__file__).with_name('AFFINE_BLOCK_DUALS.json').read_text())
 if [d['same']for d in ds]!=[False,True]:raise ValueError('inventory')
 counts=[check(d)for d in ds]
 bad=dict(ds[0]);bad['multipliers']=[]
 try:check(bad)
 except ValueError:pass
 else:raise ValueError('empty dual accepted')
 print(json.dumps({'status':'PASS','cases':2,'dual_supports':counts,'right_sides':['-1','-1'],'negative_controls':1,'scope':'coefficientwise affine discovery model; broader conventional proof separate'}))
if __name__=='__main__':run()
