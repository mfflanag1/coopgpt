from itertools import permutations
from cyclic_weights import solve
import sys

def pattern(kind):
 if kind=='k33':n=6;edges=[(i,j)for i in range(3)for j in range(3,6)]
 elif kind=='prism':n=6;edges=[(0,1),(1,2),(0,2),(3,4),(4,5),(3,5),(0,3),(1,4),(2,5)]
 elif kind=='cube':n=8;edges=[(i,j)for i in range(8)for j in range(i+1,8)if (i^j)in (1,2,4)]
 else:raise ValueError(kind)
 adj=[[k for k,e in enumerate(edges)if i in e]for i in range(n)]
 chosen={}
 def visit(v):
  if v==n:return True
  for p in permutations(range(3)):
   cand=dict(zip(adj[v],p))
   if any(cand[k]==chosen[u][k]for k in adj[v]for u in edges[k]if u<v):continue
   chosen[v]=cand
   if visit(v+1):return True
  chosen.pop(v,None);return False
 if not visit(0):raise ValueError('no sectors')
 P=[]
 for k,(i,j) in enumerate(edges):
  a,b=chosen[i][k],chosen[j][k];t=[None]*3;t[a]=i;t[b]=j;t[3-a-b]=n+k;P.append(tuple(t))
 return n+len(edges),P
if __name__=='__main__':
 kind=sys.argv[1];m,P=pattern(kind);solve(m,P,'MULTICYCLE_'+kind)
