#!/usr/bin/env python3
from fractions import Fraction as Q
import json

def check(condition, message):
    if not condition:
        raise RuntimeError(message)

edges = [(0,1),(1,2),(2,3)]
weights = [Q(1),Q(14,5),Q(4)]

def kkt(c,p,lam,W,active):
    deg=[Q(0)]*4
    for e,(u,v) in enumerate(edges):
        check(lam[e]>=0,'nonnegative multiplier')
        if active[e]:
            check(p[u]+p[v]>=weights[e],'component dual feasibility')
            check(lam[e]*(p[u]+p[v]-weights[e])==0,'complementarity')
        else:
            check(lam[e]==0,'inactive edge multiplier')
        deg[u]+=lam[e]
        deg[v]+=lam[e]
    for v in range(4):
        if W[v] is None:
            check(p[v]==0 and deg[v]==0,'isolated vertex')
        else:
            check(deg[v]==c[v]*min(2*p[v]/W[v],Q(1)),'exact KKT')

p2=[Q(3,10),Q(7,10),Q(21,10),Q(19,10)]
kkt([Q(2),Q(1),Q(1),Q(1)],p2,[Q(3,10),Q(1,20),Q(19,20)],[Q(4)]*4,[True]*3)
p5=[Q(1,10),Q(9,10),Q(2),Q(2)]
kkt([Q(5),Q(1),Q(1),Q(1)],p5,[Q(1),Q(0),Q(1)],[Q(1),Q(1),Q(4),Q(4)],[True,False,True])
check(p5[1]+p5[2]>weights[1],'disconnected actual tight pattern')

global5=[Q(1,6),Q(5,6),Q(2),Q(2)]
kkt([Q(5),Q(1),Q(1),Q(1)],global5,[Q(5,12),Q(0),Q(1)],[Q(4)]*4,[True]*3)
check(global5[1]+global5[2]>weights[1],'connected pattern impossible at5')
component123=[Q(0),Q(2,5),Q(12,5),Q(8,5)]
kkt([Q(2),Q(1),Q(1),Q(1)],component123,[Q(0),Q(1,5),Q(4,5)],[None,Q(4),Q(4),Q(4)],[False,True,True])
check(component123[0]+component123[1]<weights[0],'missing01 impossible')
check(Q(1)-Q(1,4)+Q(2)<weights[1],'disconnected pattern impossible at2')
gain=2*p2[0]-5*p5[0]
check(gain==Q(1,10),'strict profitable withholding')
print(json.dumps({'status':'PASS','arithmetic':'exact rational','profit_weights':weights,
 'small_report':[2,1,1,1],'large_report':[5,1,1,1],
 'small_prices':p2,'large_prices':p5,'withholding_gain':gain,
 'scope':'two-profile obstruction to tight-component-normalized Huber self-consistency'},default=str,indent=2))
