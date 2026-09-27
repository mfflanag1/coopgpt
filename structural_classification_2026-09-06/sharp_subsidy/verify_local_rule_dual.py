"""Exact dual upper bound for the local-incidence P-weight ansatz."""
from fractions import Fraction as F
from pathlib import Path
import json

def check(data):
 m=data['m'];P=[tuple(e)for e in data['P']];D=data['denominator'];r=len(P)
 if m!=67 or r!=33 or type(D)is not int or D<=0:raise ValueError('wrong case')
 owner={s*m+j:e for e,t in enumerate(P)for s,j in enumerate(t)}
 if len(owner)!=3*r:raise ValueError('matching overlap')
 U=sorted(set(range(3*m))-set(owner));u=len(U);stride=r+2*m+1;nv=u*stride+2
 residual=[0]*nv;residual[-2]=4*D;constant=0
 lam=dict(data['inequality']);nu=data['equality'];ui=ei=0
 if len(lam)!=len(data['inequality'])or any(type(k)is not int or type(v)is not int or v<0 for k,v in lam.items()):raise ValueError('bad multipliers')
 def add(items,rhs,eq=False):
  nonlocal constant,ui,ei
  if eq:
   if ei>=len(nu):raise ValueError('missing equality')
   z=nu[ei];ei+=1
  else:z=lam.get(ui,0);ui+=1
  if type(z)is not int:raise ValueError('noninteger multiplier')
  rhs4=F(rhs)*4
  if rhs4.denominator!=1:raise ValueError('rhs scale')
  constant+=z*rhs4.numerator
  for col,value in items:
   v4=F(value)*4
   if v4.denominator!=1:raise ValueError('coefficient scale')
   residual[col]-=z*v4.numerator
 def p(k,e):return k*stride+e
 def d(k,j):return k*stride+r+j
 def q(k,j):return k*stride+r+m+j
 def R(k):return k*stride+stride-1
 for k,i in enumerate(U):
  s,j0=divmod(i,m)
  add([(R(k),1)]+[(p(k,e),1)for e in range(r)]+[(d(k,j),1)for j in range(m)],m-1,True)
  add([(q(k,j),1)for j in range(m)]+[(p(k,e),1)for e in range(r)],m-1)
  for j in range(m):
   source=owner.get(s*m+j)
   add([(d(k,j),1)]+([(p(k,source),1)]if source is not None else[]),0 if j==j0 else 1)
   add([(d(k,j),1),(q(k,j),-1)],0)
   for a in range(3):
    if a!=s:
     e=owner.get(a*m+j);add([(q(k,j),1)]+([(p(k,e),1)]if e is not None else[]),1)
   add([(q(k,j),1),(d(k,j),-2),(R(k),-1)]+([(p(k,source),-1)]if source is not None else[]),0 if j==j0 else -1)
  for e,team in enumerate(P):
   count=sum(v%m in team for v in U);adj=j0 in team
   add([(p(k,e),1),(nv-1,-(1-F(u,count)if adj else 1))],F(3,count)if adj else 0,True)
 for e in range(r):add([(p(k,e),1)for k in range(u)],3,True)
 for j in range(m):
  for s in range(3):add([(q(k,j)if i//m==s else d(k,j),-1)for k,i in enumerate(U)]+[(nv-2,1)],-(u-5))
 if ei!=len(nu)or any(k<0 or k>=ui for k in lam):raise ValueError('multiplier dimensions')
 bounds=[1]*nv
 for k in range(u):bounds[R(k)]=m-1
 bounds[-2]=2
 correction=sum(max(0,z)*bound for z,bound in zip(residual,bounds));upper=F(constant+correction,4*D)
 if upper>=1:raise ValueError(f'upper bound does not exclude one-third target: {upper}')
 return {'status':'PASS','m':m,'parameter_upper':str(upper),'decimal':float(upper),'residual_correction':str(F(correction,4*D)),'variables':nv,'scope':'local-incidence ansatz only'}

if __name__=='__main__':
 data=json.loads(Path(__file__).with_name('MARGINAL_LOCAL_16_DUAL.json').read_text());result=check(data)
 bad=dict(data);bad['inequality']=[];bad['equality']=[0]*len(data['equality'])
 try:check(bad)
 except ValueError:pass
 else:raise ValueError('empty dual accepted')
 result['negative_controls']=1;print(json.dumps(result))
