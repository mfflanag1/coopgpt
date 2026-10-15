from pathlib import Path
from random import Random
import json
scope={}
exec(Path('/private/tmp/coopgpt-75m-20261015/constructive/verify_weighted_forest.py').read_text().split('r=Random(26321)')[0],scope)
value=scope['tree_value'];r=Random(9211)
for z in range(100000):
 n=r.randrange(3,12);edges=[(r.randrange(v),v) for v in range(1,n)];w=[1]*(n-1)
 c=[r.randrange(3) for _ in range(n)];d=[r.randrange(3) for _ in range(n)]
 b=[r.randrange(2) for _ in range(n)]
 add=lambda x,y:[a+b for a,b in zip(x,y)]
 marginal=lambda x:value(n,edges,add(x,b),w)-value(n,edges,x,w)
 mc,md,mcd=marginal(c),marginal(d),marginal(add(c,d))
 if mcd>mc+md:
  print(json.dumps({'case':z,'edges':edges,'c':c,'d':d,'b':b,'marginals':[mc,md,mcd]}));break
else:print('NO FAILURE')
