"""Integer witnesses for a one-pair weakening of the zero-subsidy ring."""
from pathlib import Path
import json

def construct(b):
 if not isinstance(b,int)or b<2:raise ValueError('b>=2 required')
 m=4*b;P=[(j,(j+1)%b,b+j)for j in range(b)]+[(2*b+2*j,2*b+2*j+1,j)for j in range(b)]
 pairs=[[[int(a==c)for c in range(m)]for a in range(m)]for _ in range(3)]
 for a,c,d in P:pairs[0][a][c]=2;pairs[1][a][d]=1;pairs[2][c][d]=2
 pairs[0][0][1]=0;soft=b;hard=P[1:]
 def colors(root,s):
  color={root:s};pending=list(hard)
  while pending:
   changed=False
   for e in list(pending):
    seen=[j for j in e if j in color]
    if not seen:continue
    if len(seen)!=1:raise ValueError('main support not a tree')
    for a,j in enumerate(e):
     if j not in color:color[j]=a
    pending.remove(e);changed=True
   if not changed:raise ValueError('disconnected main tree')
  if set(color)!=set(range(m))-{soft}:raise ValueError('main labels')
  return color
 ca=colors(0,0);cb=colors(1,1)
 if [ca[0],ca[1],cb[0],cb[1]]!=[0,0,1,1]:raise ValueError('cycle endpoint colors')
 witnesses=[]
 for s in range(3):
  for root in range(m):
   if root!=soft:
    c=colors(root,s);c[soft]=2;pay=[int(a==s)+2*int(c[j]==a)for a in range(3)for j in range(m)]
   else:
    pay=[]
    for a in range(3):
     for j in range(m):
      if j==soft:pay.append(3*int(a==s))
      elif s==0:pay.append(int(a==0)+int(ca[j]==a)+int(cb[j]==a))
      elif s==1:pay.append(int(a==1)+2*int(cb[j]==a))
      else:pay.append(int(a==2)+2*int(ca[j]==a))
   witnesses.append(pay)
 y=[1]*(3*m)
 for e in hard:y[e[0]]+=2
 return {'b':b,'m':m,'P':P,'pairs':pairs,'T':3*m,'H':[3]*(3*m),'subsidy':4*b-2,'core_witnesses':witnesses,'protected_y':y}

def run():
 cases=[construct(b)for b in (2,3,4,6,8)]
 Path(__file__).with_name('BROKEN_RING_CERTIFICATES.json').write_text(json.dumps(cases)+'\n')
 print(json.dumps({'cases':len(cases),'parameters':[d['b']for d in cases]}))
if __name__=='__main__':run()
