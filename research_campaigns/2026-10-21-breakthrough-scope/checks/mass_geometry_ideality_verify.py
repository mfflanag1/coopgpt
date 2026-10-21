#!/usr/bin/env python3
"""Exact Q6 ideality and incident-deletion obstruction; stdlib only."""
from fractions import Fraction as F
from itertools import combinations
import json
from pathlib import Path

def solve(a,b):
    m=[[F(x) for x in row]+[F(y)] for row,y in zip(a,b)]
    n=len(b)
    for j in range(n):
        pivot=next((i for i in range(j,n) if m[i][j]),None)
        if pivot is None:return None
        m[j],m[pivot]=m[pivot],m[j]
        v=m[j][j];m[j]=[x/v for x in m[j]]
        for i in range(n):
            if i!=j:
                v=m[i][j];m[i]=[x-v*y for x,y in zip(m[i],m[j])]
    return tuple(row[-1] for row in m)

sets=[(0,2,4),(0,3,5),(1,2,5),(1,3,4)]
rows=[tuple(int(j in r) for j in range(6)) for r in sets]
identity=[tuple(int(i==j) for j in range(6)) for i in range(6)]
a=rows+identity;b=[1]*4+[0]*6
vertices=set()
for support in combinations(range(10),6):
    x=solve([a[j] for j in support],[b[j] for j in support])
    if x is not None and all(sum(F(c)*y for c,y in zip(r,x))>=v for r,v in zip(a,b)):
        vertices.add(x)
expected=set(tuple(F(int(j in s)) for j in range(6)) for s in sets+[(0,1),(2,3),(4,5)])
assert vertices==expected and all(v in (0,1) for x in vertices for v in x)
# The nonnegative recession cone has integral extreme rays (coordinate units),
# so binary vertices certify this rational pointed covering polyhedron integral.
x=tuple(F(1,2) if j in (1,3,5) else F(0) for j in range(6))
assert all(sum(F(c)*y for c,y in zip(r,x))==1 for r in rows[1:])
active=rows[1:]+[identity[j] for j in (0,2,4)]
assert solve(active,[1]*3+[0]*3)==x
v=(F(1,2),)*6
residual=tuple((v[j]-F(rows[0][j],2))/F(1,2) for j in range(6))
assert residual==tuple(F(int(j in (1,3,5))) for j in range(6))
assert residual not in [tuple(F(y) for y in row) for row in rows]
gram=[[sum(x*y for x,y in zip(a,b)) for b in rows] for a in rows]
assert gram==[[3 if i==j else 1 for j in range(4)] for i in range(4)]
result={"status":"PASS", "active_sets_enumerated":210,"vertices":[[str(v) for v in x] for x in sorted(vertices)],"deleted_row_1based":[1,3,5],"fractional_vertex":[str(y) for y in x],"completion_residual":[str(y) for y in residual],"gram":gram}
out=Path(__file__).with_suffix('.json');out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
