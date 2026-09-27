from probe import lp
from pathlib import Path
import json
out=[]
for q in range(1,9):
 m=2*q+1;M=[[[int(i==j)for j in range(m)]for i in range(m)]for _ in range(3)];P=[]
 for s in range(q):
  a,b,c=s,q+s,(s-1 if s else 2*q);P.append((a,b,c));M[0][a][b]=2;M[1][a][c]=1;M[2][b][c]=2
 r=lp(M,m,3*m)
 print(json.dumps({'q':q,'matching':P,**r}),flush=True);out.append({'q':q,'matrices':M,'matching':P,**r})
 Path(__file__).with_name('chain_probe.json').write_text(json.dumps(out,indent=2)+'\n')
