from report_lp import solve,four_roles
from itertools import product

def domain(coords,levels=(0,1,2)):
 out=[]
 for xs in product(levels,repeat=len(coords)):
  row=[0]*5
  for j,x in zip(coords,xs):row[j]=x
  out.append(tuple(row))
 return out

# Same four-role class, new ratio resolution beyond the 0,1,2 calibration.
solve('four_roles_grid_0123',four_roles((0,1,2,3)))
# Two separate local-power owners, retaining coowned hardware and a shared grid.
solve('split_local_owners_012',[domain((0,1)),domain((0,1)),domain((2,)),domain((3,)),domain((4,))])
# Crossed mixed bundles create all six edges of actual-owner K4.
solve('mixed_crossed_K4_012',[domain((0,3)),domain((1,2)),domain((0,1)),domain((4,))])
# Self-producing mixed owners plus genuinely mixed local/grid supplier.
solve('mixed_selfproducers_012',[domain((0,2)),domain((1,3)),domain((0,1)),domain((2,3,4))])
