"""Independent exact harmonic equations and weak-duality certificate checker."""
from pathlib import Path
from fractions import Fraction as F
import json

def require(condition,message):
 if not condition:raise ValueError(message)

def check(data):
 m=data['m'];P=[tuple(t)for t in data['P']];r=len(P)
 require(m==25 and r==12,'specified size')
 require(all(len(t)==3 and len(set(t))==3 and all(type(j)is int and 0<=j<m for j in t)for t in P),'team format')
 own={s*m+j:e for e,t in enumerate(P)for s,j in enumerate(t)}
 require(len(own)==3*r,'partial matching')
 U=sorted(set(range(3*m))-set(own));u=len(U);h=u//3
 adj=[set()for _ in range(m+r)]
 for e,t in enumerate(P):
  for j in t:adj[j].add(m+e);adj[m+e].add(j)
 seen={0};todo=[0]
 while todo:
  for j in adj[todo.pop()]-seen:seen.add(j);todo.append(j)
 require(m==2*r+1 and len(seen)==m+r,'incidence tree')
 H={i:[F(v)for v in values]for i,values in data['harmonic']}
 require(len(data['harmonic'])==u and set(H)==set(U),'harmonic row identifiers')
 for i in U:
  require(len(H[i])==r and all(0<=v<=1 for v in H[i]),'probabilities')
  sector,root=divmod(i,m)
  labels=[]
  for j in range(m):
   if sector*m+j in U:labels.append(F(j==root))
   else:labels.append(sum(H[i][e-m]for e in adj[j])/len(adj[j]))
  require(all(3*H[i][e]==sum(labels[j]for j in t)for e,t in enumerate(P)),'Dirichlet harmonic equations')
 for sector in range(3):
  require(all(sum(H[i][e]for i in U if i//m==sector)==1 for e in range(r)),'sector absorption totals')
 stride=2*m+1;n=u*stride+4;tidx=n-4
 def d(k,j):return k*stride+j
 def q(k,j):return k*stride+m+j
 def R(k):return k*stride+2*m
 def theta(s):return n-3+s
 D=data['denominator'];require(type(D)is int and D>0,'denominator')
 lam={}
 for row,value in data['inequality']:
  require(type(row)is int and row>=0 and row not in lam and type(value)is int and value>=0,'dual inequality multipliers')
  lam[row]=F(value,D)
 nu=data['equality'];require(len(nu)==u and all(type(v)is int for v in nu),'equality multipliers');nu=[F(v,D)for v in nu]
 residual=[F(0)]*n;residual[tidx]=1;rhs=F(0);counts=[0,0]
 def row(items,b,eq=False):
  nonlocal rhs
  typ=int(eq);index=counts[typ];counts[typ]+=1
  value=nu[index]if eq else lam.get(index,F(0))
  rhs+=value*b
  for variable,coefficient in items:residual[variable]-=value*coefficient
 for k,i in enumerate(U):
  s,root=divmod(i,m);slope=sum(H[i])-F(r,h)
  row([(R(k),1)]+[(d(k,j),1)for j in range(m)]+[(theta(s),slope)],m-1-F(r,h),True)
  row([(q(k,j),1)for j in range(m)]+[(theta(s),slope)],m-1-F(r,h))
  for j in range(m):
   e=own.get(s*m+j);offset=F(1,h)if e is not None else F(0);a=H[i][e]-offset if e is not None else F(0)
   row([(d(k,j),1),(theta(s),a)],(0 if j==root else 1)-offset)
   row([(d(k,j),1),(q(k,j),-1)],0)
   for z in range(3):
    if z==s:continue
    f=own.get(z*m+j);off=F(1,h)if f is not None else F(0);v=H[i][f]-off if f is not None else F(0)
    row([(q(k,j),1),(theta(s),v)],1-off)
   row([(q(k,j),1),(d(k,j),-2),(R(k),-1),(theta(s),-a)],(0 if j==root else -1)+offset)
 for j in range(m):
  for s in range(3):row([(q(k,j)if i//m==s else d(k,j),-1)for k,i in enumerate(U)]+[(tidx,1)],-(u-5))
 require(all(index<counts[0]for index in lam),'row range')
 bounds=[1]*n
 for k in range(u):bounds[R(k)]=m-1
 bounds[tidx]=2
 correction=sum(max(F(0),v)*b for v,b in zip(residual,bounds));upper=rhs+correction
 require(upper<F(1),'no strict rejection of target')
 require(upper<F(967618,1000000),'published rounded-up bound')
 return dict(status='PASS',parameter_upper=str(upper),reported_upper='0.967618',residual_correction=str(correction),nonzero_dual_rows=len(lam),variables=n,inequalities=counts[0],harmonic_equations=u*r)

def main():
 data=json.loads(Path(__file__).with_name('HARMONIC_SECTOR_NO_GO.json').read_text());result=check(data)
 bad=dict(data);bad['inequality']=[];bad['equality']=[0]*len(data['equality'])
 try:check(bad)
 except ValueError:pass
 else:raise ValueError('empty dual accepted')
 bad=dict(data);bad['harmonic']=[[i,list(v)]for i,v in data['harmonic']];bad['harmonic'][0][1][0]='2'
 try:check(bad)
 except ValueError:pass
 else:raise ValueError('damaged probabilities accepted')
 from verify_variable_p import check as check_packing
 control=json.loads(Path(__file__).with_name('HARMONIC_FREE_CONTROL.json').read_text())
 require(control['m']==data['m'] and {tuple(t)for t in control['P']}=={tuple(t)for t in data['P']},'control uses another pattern')
 result['free_weight_certificate_entries']=check_packing(control)
 P={tuple(t)for t in control['P']};totals={t:F(0)for t in P}
 for i,t,v in control['packings']:
  t=tuple(t);s=i//control['m']
  if t in P:totals[t]+=F(v)
  else:require(t[(s+1)%3]==t[(s+2)%3],'control transfer sector')
 require(all(v==3 for v in totals.values()),'control P totals')
 result['free_weight_target']='1';result['negative_controls']=2;print(json.dumps(result))
if __name__=='__main__':main()
