#!/usr/bin/env python3
"""Exact bounded search for failure of six-profile inequality under linear lifts."""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import random
import json
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('flow',HERE/'exact_huber_solver.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
base={(0,3),(1,3),(1,4),(2,4),(2,5),(0,5)}
profiles=((0,1,1,1,0,1),(0,1,1,1,1,1),(1,0,1,1,0,1),
          (1,0,1,1,1,0),(1,1,0,0,1,1),(1,1,1,1,1,0))
signs=(-1,1,1,-1,-1,1)
lefttypes=[(0,),(1,),(2,),(0,1),(1,2),(0,2)]
righttypes=[(3,),(4,),(5,),(3,4),(4,5),(3,5)]
rng=random.Random(617102026)
minimum=0;witness=None
for trial in range(10000):
    left=[];right=[]
    for side,types in [(left,lefttypes),(right,righttypes)]:
        for support in types:
            for _ in range(rng.randrange(3)):
                side.append({v:rng.randrange(1,5) for v in support})
    edges=[(i,j) for i,a in enumerate(left) for j,b in enumerate(right)
           if all((u,v) in base for u in a for v in b) and rng.random()<.65]
    vals=[]
    for cap in profiles:
        lc=[sum(a[v]*cap[v] for v in a) for a in left]
        rc=[sum(a[v]*cap[v] for v in a) for a in right]
        n=len(left)+len(right);s,t=n,n+1
        flow=mod.ExactFlow(n+2)
        for i,c in enumerate(lc):flow.add(s,i,c)
        for j,c in enumerate(rc):flow.add(len(left)+j,t,c)
        inf=sum(lc)+sum(rc)+1
        for i,j in edges:flow.add(i,len(left)+j,inf)
        vals.append(flow.solve(s,t))
    L=sum(s*v for s,v in zip(signs,vals))
    minimum=min(minimum,L)
    if L<0:
        witness={'trial':trial,'left_rows':left,'right_rows':right,'edges':edges,'profile_values':vals,'functional':L}
        break
print(json.dumps({'status':'EXACT FINITE SCOUT','trials':trial+1,'minimum':minimum,'witness':witness,
 'scope':'support-respecting nonnegative linear lifts only; target edge-profile identities not enforced'},indent=2))
