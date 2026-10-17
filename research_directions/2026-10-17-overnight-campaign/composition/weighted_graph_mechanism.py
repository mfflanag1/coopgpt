#!/usr/bin/env python3
"""Exact rational weighted mechanism via established antidiagonal unfolding.

Fractional production; fixed owners; payment-only coalition underreports.
Pseudo-polynomial in normalized integer profits, not original binary input.
The graph reduction is known (Kao et al. 2001; Hashemi/Wrzos-Kaminska2024).
"""
from fractions import Fraction as Q
from math import lcm
from pathlib import Path
import importlib.util,json,argparse
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('unit_huber',HERE/'exact_huber_solver.py')
unit=importlib.util.module_from_spec(spec);spec.loader.exec_module(unit)
def require(c,m):
 if not c:raise RuntimeError(m)
def weighted_prices(capacities,edges,profits,copy_limit=100000):
 c=tuple(map(Q,capacities));w=tuple(map(Q,profits));es=tuple(map(tuple,edges));n=len(c)
 require(all(z>=0 for z in c),'negative capacity')
 require(len(es)==len(w),'edge/profit lengths')
 require(all(z>=0 for z in w),'negative public profit')
 require(all(len(e)==2 and 0<=e[0]<n and 0<=e[1]<n and e[0]!=e[1] for e in es),'edge endpoints')
 require(len({tuple(sorted(e)) for e in es})==len(es),'duplicate original edges')
 q=1
 for z in w:q=lcm(q,z.denominator)
 k=[int(q*z) for z in w];W=max(k,default=0)
 if W==0:return {'prices':[Q(0)]*n,'value':Q(0),'funding':Q(0),'denominator':q,'copy_count':0,'lift_edge_count':0}
 require(n*W<=copy_limit,'expanded graph exceeds explicit copy_limit; pseudo-polynomial representation')
 le=[]
 for (u,v),z in zip(es,k):
  for a in range(z):le.append((u*W+a,v*W+z-1-a))
 lc=[c[v] for v in range(n) for a in range(W)]
 cert=unit.certificate(lc,le)
 p=[sum(cert['p'][v*W:(v+1)*W])/q for v in range(n)]
 value=sum(cert['lambda'])/q;funding=sum(x*y for x,y in zip(c,p))
 require(all(p[u]+p[v]>=z for (u,v),z in zip(es,w)),'original weighted dual cover')
 require(funding<=Q(3,2)*value,'weighted funding bound')
 return {'prices':p,'value':value,'funding':funding,'denominator':q,
  'copy_count':n*W,'lift_edge_count':len(le),'unit_certificate':cert}
def payments(owner_bundles,edges,profits,copy_limit=100000):
 own=[tuple(map(Q,b)) for b in owner_bundles]
 require(bool(own),'provide at least one actual owner')
 n=len(own[0]);require(all(len(b)==n and all(z>=0 for z in b) for b in own),'owner bundle domains')
 c=[sum(b[v] for b in own) for v in range(n)]
 result=weighted_prices(c,edges,profits,copy_limit)
 result['owner_payments']=[sum(z*p for z,p in zip(b,result['prices'])) for b in own]
 require(sum(result['owner_payments'])==result['funding'],'same-owner payment accounting')
 return result
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('input',type=Path);args=parser.parse_args()
 data=json.loads(args.input.read_text());result=payments(data['owner_bundles'],data['edges'],data['profits'],data.get('copy_limit',100000))
 print(json.dumps(result,default=str,indent=2))
