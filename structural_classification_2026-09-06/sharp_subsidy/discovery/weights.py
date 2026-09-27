from probe import lp,independent_triangle
import json
for q in [1,2,4,8]:
 for a in [.25,.5,.75,1,1.25,1.5,2]:
  g=independent_triangle(q)
  for M in g['matrices'][:2]:
   for i,row in enumerate(M):
    for j,v in enumerate(row):M[i][j]=v*a/2
  r=lp(g['matrices'],g['m'],2*a*q+2*q+1)
  print(json.dumps({'q':q,'a':a,**r}),flush=True)
