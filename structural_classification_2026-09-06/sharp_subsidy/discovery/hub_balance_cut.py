from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
import json,numpy as np
from scipy.optimize import linprog,least_squares
from scipy.sparse import coo_matrix
import two_hub_blocks as tb
from balanced_conductance import profiles

def pattern():
 m,P=tb.example(False,0)
 for _ in range(8):
  old=P[0];first=list(old);second=list(old);first[2]=m;second[1]=m;second[0]=m+1;P[0]=tuple(first);P.append(tuple(second));m+=2
 return m,P

def build():
 m,P=pattern();data=tb.structure(m,P);_,_,block,rb,L,hubs,ports,toward=data;B=len(L);types=[(b,t,s)for b in range(B)for t in range(3)if L[b][t]for s in range(3)if s!=t];lookup={v:k for k,v in enumerate(types)};n=len(types)*B
 def p(k,b):return k*B+b
 rows=[];rhs=[];eq=[];erhs=[]
 def put(items,b,equality=False):
  row=defaultdict(F)
  for i,v in items:row[i]+=F(v)
  (eq if equality else rows).append(dict(row));(erhs if equality else rhs).append(F(b))
 for k,(b0,t,s)in enumerate(types):
  partner=lookup[b0,t,3-t-s]
  for h,bs in enumerate(ports):
   for b in bs:put([(p(k,b),1),(p(k,toward[b0][h]),-1)],0)
  put([(p(k,b0),1),(p(partner,b0),1)],1)
  put([(p(k,b),-rb[b])for b in range(B)]+[(p(k,b0),-1),(p(partner,b0),-1)],-1)
 for b in range(B):
  for s in range(3):put([(p(k,b),L[b0][t])for k,(b0,t,a)in enumerate(types)if a==s],1,True)
 for h in range(len(hubs)):put([(p(k,toward[b0][h]),L[b0][t])for k,(b0,t,s)in enumerate(types)],F(7,2),True)
 put([(p(k,b),L[b][t])for k,(b,t,s)in enumerate(types)],4,True)
 return m,P,data,types,lookup,rows,rhs,eq,erhs,n
if __name__=='__main__':
 m,P,data,types,lookup,rows,rhs,eq,erhs,n=build();_,_,block,rb,L,hubs,ports,toward=data;B=len(L);sector=2;cols=sorted(set(block[e]for e in (0,1,3)))
 fit=least_squares(lambda z:profiles(data,z)[1]-3.5,np.zeros(2));ps,_=profiles(data,fit.x)
 coeff=defaultdict(F);constant=F(sum(L[b][sector]for b in cols));choices=[]
 for b in cols:
  if L[b][sector]:
   for a in range(3):
    if a!=sector:coeff[lookup[b,sector,a]*B+b]-=L[b][sector]
 for k,(b,t,s)in enumerate(types):
  if s!=sector:continue
  partner=lookup[b,t,3-t-s];delta=1-ps[s][b,b]-ps[3-t-s][b,b];supply=sum(rb[c]*ps[s][c,b]for c in range(B))-delta;cap=sum(L[c][s]*ps[s][c,b]for c in cols);mult=L[b][t]
  if supply<=cap:
   choices.append((k,'supply'));constant+=mult
   for c in range(B):coeff[k*B+c]-=mult*rb[c]
   coeff[k*B+b]-=mult;coeff[partner*B+b]-=mult
  else:
   choices.append((k,'capacity'))
   for c in cols:coeff[k*B+c]-=mult*L[c][s]
 def sparse(rs):
  ii=[];jj=[];vv=[]
  for i,row in enumerate(rs):
   for j,v in row.items():ii.append(i);jj.append(j);vv.append(float(v))
  return coo_matrix((vv,(ii,jj)),shape=(len(rs),n)).tocsr()
 c=np.array([-float(coeff[j])for j in range(n)]);r=linprog(c,A_ub=sparse(rows),b_ub=list(map(float,rhs)),A_eq=sparse(eq),b_eq=list(map(float,erhs)),bounds=(0,1))
 if not r.success:raise ValueError(r.message)
 from sympy import Matrix
 from sympy.polys.matrices import DomainMatrix
 active=[j for j,x in enumerate(r.x)if x>1e-8];system=[]
 def equation(row,b):system.append([row.get(j,0)for j in active]+[b])
 for row,b in zip(eq,erhs):equation(row,b)
 for row,b in zip(rows,rhs):
  if abs(sum(float(a)*r.x[j]for j,a in row.items())-float(b))<1e-7:equation(row,b)
 for j in active:
  if abs(r.x[j]-1)<1e-8:equation({j:1},1)
 mat,piv=DomainMatrix.from_Matrix(Matrix(system)).rref();mat=mat.to_Matrix();q=len(active)
 if q in piv:raise ValueError('inconsistent active equations')
 v=[F(0)]*n
 for j in active:v[j]=F(round(r.x[j]*10**9),10**9)
 free=[j for j in range(q)if j not in piv]
 for z,j in enumerate(piv):v[active[j]]=F(mat[z,q])-sum(F(mat[z,a])*v[active[a]]for a in free)
 if not all(0<=x<=1 for x in v)or not all(sum(v[j]*a for j,a in row.items())<=b for row,b in zip(rows,rhs))or not all(sum(v[j]*a for j,a in row.items())==b for row,b in zip(eq,erhs)):raise ValueError('rational reconstruction failed')
 gap=constant+sum(v[j]*a for j,a in coeff.items());print('m',m,'gap',str(gap),'cols',cols,flush=True)
 out={'m':m,'P':P,'types':types,'values':[str(x)for x in v],'sector':sector,'columns':cols,'selected_terms':choices,'certified_gap_lower_bound':str(gap),'block':block,'L':L,'r':rb}
 Path(__file__).with_name('HUB_BALANCE_CUT_COUNTEREXAMPLE.json').write_text(json.dumps(out)+'\n')
