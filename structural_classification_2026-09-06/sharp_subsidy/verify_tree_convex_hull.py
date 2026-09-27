"""Exact row-cut checks and a certificate outside the integral matching hull."""
from fractions import Fraction as F
from collections import defaultdict
from itertools import product
import json
from verify_tree_integrality import instance
from uniform_template import construct
from verify_variable_p import check as check_packing

def require(ok,msg):
 if not ok:raise ValueError(msg)

def main():
 m,P,own,U,parents=instance();r=len(P)
 degree=[sum(s*m+j in own for s in range(3))for j in range(m)]
 child={}
 for i in U:
  sector=i//m;child[i]=[]
  for j in range(m):
   if degree[j]!=2 or sector*m+j not in own:continue
   parent=parents[i][j]-m
   child[i].append(next(e for e,t in enumerate(P)if j in t and e!=parent))
 row_checks=0
 for i in U:
  sector,root=divmod(i,m)
  for bits in product((0,1),repeat=r):
   maximum=[max((bits[e]for e,t in enumerate(P)if j in t),default=0)for j in range(m)]
   if any(maximum[j]!=bits[parents[i][j]-m]for j in range(m)if j!=root):continue
   pair_capacity=[1-max((bits[own[a*m+j]]for a in range(3)if a!=sector and a*m+j in own),default=0)for j in range(m)]
   lower_loss=max(0,m-1-sum(bits)-sum(pair_capacity))
   cost=sum(bits[e]for e in child[i])
   require(lower_loss>=cost,'linear cut for integral row state');row_checks+=1
 data=construct(m,P);data['parameter']='1';entries=check_packing(data);p=defaultdict(F);total=defaultdict(F);diag=defaultdict(F)
 for i,t,value in data['packings']:
  t=tuple(t);v=F(value);total[i]+=v
  if t in P:p[i,P.index(t)]+=v
  if len(set(t))==1:diag[i,t[0]]+=v
 for sector in range(3):
  for e in range(r):require(sum(p[i,e]for i in U if i//m==sector)==1,'sector totals')
 violations=[]
 for i in U:
  E=m-1-sum(diag[i,j]for j in range(m))-2*sum(p[i,e]for e in range(r))
  require(E==0,'control on maximal-diagonal face')
  loss=m-1-total[i];cost=sum(p[i,e]for e in child[i])
  if cost>loss:violations.append({'row':i,'cut_violation':str(cost-loss)})
 require(len(violations)==12 and all(F(d['cut_violation'])==F(2,3)for d in violations),'specified fractional separation')
 print(json.dumps({'status':'PASS','binary_row_states':row_checks,'fractional_control_entries':entries,'rows_outside_integral_hull':len(violations),'each_linear_cut_violation':'2/3','scope':'specified same-sector support; E=0 face','witnesses':violations}))
if __name__=='__main__':main()
