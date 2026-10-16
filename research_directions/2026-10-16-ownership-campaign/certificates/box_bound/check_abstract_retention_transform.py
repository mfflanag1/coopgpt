from math import exp
from random import Random
from pathlib import Path
import json
R=Random(16612277);c=.5/exp(1);C=1+c
best={'excess':-99.};count=0
for _ in range(12000):
 n=R.randrange(3,9);rho=R.choice([1.,1.05,1.1,1.25,1.5,1.75,1.9,1.99,2.])
 h=[R.random()**3 for i in range(n)];tot=sum(h);h=[v*rho/tot for v in h]
 if max(h)>=1:continue
 b=[R.random()**3 for i in range(n)];tot=sum(b);b=[v/tot for v in b]
 q=.5*exp(1-rho);raw=[(1-q)*x+q*y for x,y in zip(b,h)];pay=raw[:];ts=[1.]*n
 for j in range(100):
  t=(j+1)/100;qt=.5*exp(1-sum(min(v,t)for v in h)/t)
  for i in range(n):
   bt=min(t,max(0.,b[i]-(1-t)/3));z=(1-qt)*bt+qt*min(h[i],t)
   if z>pay[i]:pay[i]=z;ts[i]=t
 excess=sum(pay)-C
 if excess>best['excess']:best={'excess':excess,'rho':rho,'h':h,'b':b,'raw':raw,'envelope_grid':pay,'maximizers':ts,'sum_raw':sum(raw),'sum_envelope_grid':sum(pay)}
 count+=1
best['profiles']=count
Path('/private/tmp/coopgpt-ownership-20261016/certificates/box_bound/abstract_retention_transform.json').write_text(json.dumps(best,indent=2)+'\n')
print(json.dumps(best))
