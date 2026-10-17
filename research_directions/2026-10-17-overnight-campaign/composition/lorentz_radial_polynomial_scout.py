from pathlib import Path
import runpy
ns=runpy.run_path(str(Path(__file__).with_name('CONE_CHECK_LORENTZ_PHI.py')))
Q,c,b=ns['Q'],ns['c'],ns['b']
def clean(p):
 while len(p)>1 and p[-1]==0:p.pop()
 return p
def add(p,q):
 a=[Q(0)]*max(len(p),len(q))
 for i,v in enumerate(p):a[i]=a[i]+v
 for i,v in enumerate(q):a[i]=a[i]+v
 return clean(a)
def neg(p):return [-v for v in p]
def sub(p,q):return add(p,neg(q))
def mul(p,q):
 a=[Q(0)]*(len(p)+len(q)-1)
 for i,u in enumerate(p):
  for j,v in enumerate(q):a[i+j]=a[i+j]+u*v
 return clean(a)
def sc(p,k):return [k*v for v in p]
def power(p,n):
 a=[Q(1)]
 for _ in range(n):a=mul(a,p)
 return a
def div(p,q):
 p=p.copy();out=[Q(0)]*max(1,len(p)-len(q)+1)
 while len(p)>=len(q) and p!=[Q(0)]:
  i=len(p)-len(q);k=p[-1]/q[-1];out[i]=k
  p=sub(p,[Q(0)]*i+sc(q,k))
 return clean(out),clean(p)
def show(p):return [(str(x.a),str(x.b)) for x in p]
one=[Q(1)];s=[Q(0),Q(1)];D=[c,Q(1)];Ds=power(D,2);L=[Q(1),Q(0),Q(-1)]
U=add(D,sc(Ds,b));K=add([c],sc(Ds,b));FF=mul(s,U)
AA=sc(mul(L,sub(power(U,2),power(K,2))),Q(1)/4)
BB=sub(mul(K,sub(mul(s,Ds),FF)),sc(mul(mul(L,power(K,2)),s),Q(1)/2))
CC=sub(add(sub(power(D,4),power(FF,2)),mul(mul(K,sub(mul(s,Ds),FF)),s)),sc(add(mul(mul(L,power(K,2)),power(s,2)),mul(L,power(U,2))),Q(1)/4))
DD=sub(sc(mul(AA,CC),Q(4)),power(BB,2))
print('degree',len(DD)-1,'raw',show(DD))
for fact in [s,[Q(1),Q(-1)],D,[c,Q(0),Q(1)]]:
 count=0
 while True:
  out,rem=div(DD,fact)
  if rem!=[Q(0)]:break
  DD=out;count+=1
 print('factor',show(fact),'multiplicity',count)
print('remaining',show(DD))
print('coeff signs',[v.sign() for v in DD])
# f_new/s-f_old/s common numerator.
oldD=[c,b]
N=sub(mul(add(one,sc(D,b)),oldD),D)
print('fund improvement num',show(N))
