#!/usr/bin/env python3
"""Exact rational cover/lift/payment checks; no LP solver or float arithmetic."""
from fractions import Fraction as Q
from pathlib import Path
import json,random,hashlib
from verify_owner_compatibility import covers,root_forest,graph,need

def cycle_cover(edges,cycles,n):
 alpha=max((Q(len(c),len(c)-1) for c in cycles),default=Q(1));points={Q(),Q(1)}
 for cyc in cycles:
  points.update(Q(k,len(cyc)) for k in range(len(cyc)+1))
 points=sorted(points);out=[]
 for a,b in zip(points,points[1:]):
  t=(a+b)/2;removed={cyc[int(len(cyc)*t)] for cyc in cycles};H=set(edges)-removed;adj=[set() for _ in range(n)]
  for i,j in H:adj[i].add(j);adj[j].add(i)
  need(root_forest(adj) is not None,'cycle deletion did not produce forest');out.append((alpha*(b-a),H,adj))
 need(sum(w for w,H,adj in out)==alpha,'total cover weight')
 for e in edges:need(sum(w for w,H,adj in out if e in H)>=1,'edge coverage')
 return alpha,out

def windmill(lengths):
 edges=set();cycles=[];n=1
 for size in lengths:
  verts=[0]+list(range(n,n+size-1));n+=size-1;cyc=[]
  for i in range(size):cyc.append(tuple(sorted((verts[i],verts[(i+1)%size]))))
  edges.update(cyc);cycles.append(cyc)
 return edges,cycles,n

def lift(elig,physical):
 rows=[(i,r) for i in range(len(elig)) for r in range(len(elig[0])) if elig[i][r]];idx={z:k for k,z in enumerate(rows)};activities=[]
 for r,s in physical:
  for i in range(len(elig)):
   for j in range(len(elig)):
    if elig[i][r] and elig[j][s]:activities.append((idx[i,r],idx[j,s],None if i==j else tuple(sorted((i,j)))))
 return rows,activities

def case_definition(kind):
 if kind=='shared_triangle':
  return [[1,1]]*3,[(0,1)],[(0,1),(1,2),(0,2)], [[(0,1),(1,2),(0,2)]]
 if kind=='two_pool':
  return [[1,0],[1,0],[0,1],[0,1]],[(0,1)],[(0,2),(1,2),(1,3),(0,3)], [[(0,2),(1,2),(1,3),(0,3)]]
 lengths=kind
 edges,cycs,n=windmill(lengths);sequence=[0]
 for cyc in cycs:
  # Recover traversal because windmill vertices were allocated consecutively.
  verts=sorted(set(v for e in cyc for v in e));sequence+=verts[1:]+[0]
 # One same-owner activity exercises self-variant retention.
 sequence.insert(1,0)
 elig=[[sequence[r]==i for r in range(len(sequence))] for i in range(n)]
 physical=[(r,r+1) for r in range(len(sequence)-1)]
 return elig,physical,edges,cycs

def main():
 rng=random.Random(162017);count=dict(cover_families=0,cover_forests=0,mechanism_profiles=0,coalitions=0,lift_equalities=0,own_bundle_reports=0);factors=[]
 for lengths in [[],[3],[4],[5],[7],[3,4,5],[4]*20,[7]*250,list(range(3,32))]:
  edges,cycs,n=windmill(lengths);alpha,decomp=cycle_cover(edges,cycs,n);count['cover_families']+=1;count['cover_forests']+=len(decomp);factors.append(dict(cycle_lengths=lengths,owners=n,forests=len(decomp),factor=str(alpha)))
 for kind in ['two_pool','shared_triangle',[3],[4],[5],[3,4],[4,4]]:
  elig,physical,edges,cycs=case_definition(kind);n=len(elig);v=len(elig[0]);actual=graph(elig,physical);actualedges={(i,j) for i in range(n) for j in actual[i] if i<j};need(actualedges==set(edges),'fixed compatibility graph mismatch')
  alpha,decomp=cycle_cover(set(edges),cycs,n);rows,acts=lift(elig,physical);origcovers=covers(v,physical);fullcovers=covers(len(rows),[(a,b) for a,b,e in acts]);prepared=[]
  for weight,H,adj in decomp:
   cv=covers(len(rows),[(a,b) for a,b,e in acts if e is None or e in H]);par,order=root_forest(adj);prepared.append((weight,cv,par,order))
  def origvalue(b,mask):
   cap=[sum(b[i][r] for i in range(n) if mask>>i&1) for r in range(v)]
   return min(sum(cap[r] for r in c) for c in origcovers)
  def liftedvalue(b,mask,cv):
   cap=[b[i][r] if mask>>i&1 else Q() for i,r in rows]
   return min(sum(cap[r] for r in c) for c in cv)
  def mechanism(b):
   pay=[Q()]*n
   for weight,cv,par,order in prepared:
    subsets=[1<<i for i in range(n)];values=[Q()]*n
    for i in reversed(order):
     children=[j for j in range(n) if par[j]==i]
     for j in children:subsets[i]|=subsets[j]
     values[i]=liftedvalue(b,subsets[i],cv)
     pay[i]+=weight*(values[i]-sum(values[j] for j in children))
   return pay
  for trial in range(24):
   b=[[Q(rng.randrange(8),rng.randrange(1,4)) if elig[i][r] else Q() for r in range(v)] for i in range(n)];y=mechanism(b);T=origvalue(b,(1<<n)-1)
   need(all(z>=0 for z in y) and T<=sum(y)<=alpha*T,'cover mechanism nonnegative funding')
   for mask in range(1<<n):
    val=origvalue(b,mask);need(liftedvalue(b,mask,fullcovers)==val,'owner-pair lift coalition equality');count['lift_equalities']+=1
    need(sum(y[i] for i in range(n) if mask>>i&1)>=val,'actual coalition coverage');count['coalitions']+=1
   for i in range(n):
    for step in range(3):
     low=[r.copy() for r in b];low[i]=[z*rng.choice([Q(),Q(1,3),Q(2,3),Q(1)]) for z in low[i]]
     need(mechanism(low)[i]<=y[i],'actual bundle monotonicity');count['own_bundle_reports']+=1
   count['mechanism_profiles']+=1
 report=dict(status='EXACT RATIONAL PASS',counts=count,cover_factors=factors,scope='Finite exact corroboration; unrestricted theorem is in OWNER_FOREST_COVER.txt',script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 Path(__file__).with_name('owner_forest_cover_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
