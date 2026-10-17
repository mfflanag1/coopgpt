#!/usr/bin/env python3
from fractions import Fraction as Q
import json

def require(condition,message):
    if not condition:raise RuntimeError(message)
edges=((0,3),(1,3),(1,4),(2,4),(2,5),(0,5))
profiles=((0,1,1,1,0,1),(0,1,1,1,1,1),(1,0,1,1,0,1),
          (1,0,1,1,1,0),(1,1,0,0,1,1),(1,1,1,1,1,0))
signs=(-1,1,1,-1,-1,1)

def value(cap,weights,mask=63):
    optimum=Q(0)
    for used in range(64):
        if used&~mask:continue
        degree=[0]*6;profit=Q(0)
        for j,(u,v) in enumerate(edges):
            if used>>j&1:
                degree[u]+=1;degree[v]+=1;profit+=weights[j]
        if all(x<=y for x,y in zip(degree,cap)):
            optimum=max(optimum,profit)
    return optimum
unit=[]
for mask in range(64):
    bits=[(mask>>j)&1 for j in range(6)]
    a,b,c,d,e,f=bits
    values=[value(cap,[Q(1)]*6,mask) for cap in profiles]
    functional=sum(s*v for s,v in zip(signs,values))
    formula=max(b+d,b+e,c+e)+max(a+e,f)+max(a+c,a+d,b+d)-sum(bits)
    require(functional==formula,'path formula versus independent enumeration')
    require(functional>=0,'unit cone inequality')
    unit.append(functional)
weighted=[]
for epsilon in [Q(1,1000),Q(1,10),Q(1,2),Q(1),Q(2),Q(100)]:
    weights=[Q(1)]*5+[Q(1)+epsilon]
    values=[value(cap,weights) for cap in profiles]
    require(values==[Q(2),Q(2),max(Q(2),Q(1)+epsilon),Q(2),Q(2)+epsilon,Q(2)],'weighted profile formula')
    functional=sum(s*v for s,v in zip(signs,values))
    require(functional==-min(epsilon,Q(1))<0,'strict weighted separation')
    weighted.append({'epsilon':epsilon,'profile_values':values,'functional':functional})
print(json.dumps({'status':'PASS','arithmetic':'exact rational','unit_subgraphs':64,
 'unit_functional_minimum':min(unit),'unit_functional_maximum':max(unit),
 'weighted_cases':weighted,'scope':'same-resource positive-unit representation obstruction; not a universal mechanism lower bound'},
 default=str,indent=2))
