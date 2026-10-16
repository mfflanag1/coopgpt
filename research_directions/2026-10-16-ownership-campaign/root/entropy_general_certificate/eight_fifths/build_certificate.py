"""Bounded adaptive proposal search; all accepted leaves checked with Fractions."""
from fractions import Fraction as F
from pathlib import Path
from math import isqrt
import importlib.util,json,time,argparse
import numpy as np
from scipy.optimize import linprog

BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('frozen_builder',BASE.parent/'build_certificate.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
PB,CB,DB=old.PB,old.CB,old.DB
cl,cu,CU,KU=old.cl,old.cu,old.CU,old.KU
KL=old.EL-1;alpha_low=1-cu
CAP_US=[F(i,40) for i in range(18,33)]
CAP_SS=[F(i,8) for i in range(1,9)]
ETAS=[F(2),F(8),F(32),F(128)]
TARGET=F(8,5)
qdata={u:(old.en(1/u-1,25)/2,old.en(1/u-1,24)/2) for u in CAP_US}
thi={s:old.en(1-s,24)/2 for s in CAP_SS}
beta_hi=(1/old.en(KU,25)-2)/(1-cu)

def ceil_sqrt(x):
 scale=10**12
 return F(isqrt(x.numerator*scale*scale//x.denominator)+1,scale)

def base_rows(lo,hi,dl,dh):
 aa,bb,_=old.rows(lo,hi,dl,dh)
 def add(row,rhs):aa.append(list(map(F,row)));bb.append(F(rhs))
 for weight in ETAS:
  D=1+1/(16*weight)
  add([D,0,F(1,2)+cl,cl-F(1,2),0],weight*dh+D)
 for u in CAP_US:
  ql,qh=qdata[u];al=1-qh*(1+1/u);ah=1-ql*(1+1/u)
  old.require(al>0,'cap A lower')
  lamhi=1-ql*(1+1/u-1/lo);phihi=(hi-1)*(1-ql*(1+1/u-1/hi))
  pup=KU*qh/lo;mup=KU*KU*(qh/lo)**2/(4*al)
  mulo=KL*KL*(ql/hi)**2/(4*ah)
  bup=qh*(1+1/u-1/hi)
  kap=max(F(0),pup-mulo)*bup/(bup+alpha_low*pup)
  for s in CAP_SS:
   constant=2-cl+dh/s;coef=(thi[s]-cl)/s-1
   add([-kap*coef,-mup,-lamhi,mup,1],phihi+kap*constant)
 # The simple profilewise exponential support, no numerically searched mu.
 qhi=old.en(lo-1,24)/2;betaC=beta_hi*CB
 add([qhi*betaC,-F(3,4)*qhi,-2*qhi,F(3,4)*qhi,1],
     2*qhi*(hi-1)+qhi*betaC*(1+KU*ceil_sqrt(cu*dh)))
 return aa,bb

def proposal(aa,bb,objective):
 lp=linprog(-np.array(objective,dtype=float),A_ub=np.array(aa,dtype=float),b_ub=np.array(bb,dtype=float),bounds=[(0,None)]*5,method='highs')
 if lp.success:
  weights=old.quantize(-lp.ineqlin.marginals)
  upper=old.weak(aa,bb,objective,weights)
  return upper,weights,list(map(float,lp.x))
 if lp.status==2:
  af=np.array(aa,dtype=float);bf=np.array(bb,dtype=float)
  dual=linprog(bf,A_ub=np.vstack((-af.T,np.ones((1,len(bb))))),b_ub=np.array([0]*5+[1]),bounds=[(0,None)]*len(bb),method='highs')
  old.require(dual.success,'Farkas proposal')
  weights=old.quantize(dual.x)
  upper=old.weak(aa,bb,[F(0)]*5,weights)-1
  old.require(upper<0,'Farkas exact')
  return None,weights,None
 raise RuntimeError('LP status '+str(lp.status))

STATS={'leaves':0,'geometric':0,'dual_empty':0,'uniform':0,'chord':0,'failed':0,'max_depth':0}
MAXIMUM=F(-1)

def solve(lo,hi,dl,dh,vl=F(0),vh=F(1),depth=0,rows=None):
 global MAXIMUM
 STATS['max_depth']=max(STATS['max_depth'],depth)
 if lo>PB+CU-dl:
  STATS['geometric']+=1;return {'empty':'geometric'}
 if rows is None:rows=base_rows(lo,hi,dl,dh)
 aa=rows[0]+[[F(0),F(0),F(1),F(0),F(0)],[F(0),F(0),F(-1),F(0),F(0)]]
 bb=rows[1]+[vh,-vl]
 b=old.en(hi-1+dh,25)/2
 objectives=[('uniform',[F(0),F(0),-F(4,5)*b,F(0),F(1)]),
             ('chord',[F(0),F(0),-b,b*F(4,15)*KU*KU*vh*vh,F(1)])]
 best=None
 for name,obj in objectives:
  upper,weights,x=proposal(aa,bb,obj)
  if upper is None:
   STATS['dual_empty']+=1;return {'empty':'dual','weights':[[k,str(w)] for k,w in weights]}
  if best is None or upper<best[0]:best=(upper,name,weights,x)
  if upper<TARGET:
   MAXIMUM=max(MAXIMUM,upper);STATS[name]+=1;STATS['leaves']+=1
   return {'objective':name,'weights':[[k,str(w)] for k,w in weights]}
 if depth>=12 or (hi-lo<=F(1,4096) and dh-dl<=F(1,16384) and vh-vl<=F(1,128)):
  STATS['failed']+=1
  return {'failed_upper':str(best[0]),'bounds':list(map(str,(lo,hi,dl,dh,vl,vh))),'primal':best[3]}
 if vh-vl>F(1,32):
  midpoint=(vl+vh)/2
  return {'split':'v','children':[solve(lo,hi,dl,dh,vl,midpoint,depth+1,rows),solve(lo,hi,dl,dh,midpoint,vh,depth+1,rows)]}
 if (dh-dl)*4>hi-lo:
  mid=(dl+dh)/2
  return {'split':'delta','children':[solve(lo,hi,dl,mid,vl,vh,depth+1),solve(lo,hi,mid,dh,vl,vh,depth+1)]}
 mid=(lo+hi)/2
 return {'split':'S','children':[solve(lo,mid,dl,dh,vl,vh,depth+1),solve(mid,hi,dl,dh,vl,vh,depth+1)]}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--ns',type=int,default=128);parser.add_argument('--nd',type=int,default=32);args=parser.parse_args()
 start=time.monotonic();cells=[]
 for si in range(args.ns):
  lo=1+F(si,args.ns);hi=1+F(si+1,args.ns)
  for di in range(args.nd):
   dl=DB*F(di,args.nd)**2;dh=DB*F(di+1,args.nd)**2
   cells.append(solve(lo,hi,dl,dh))
  if si%8==7:
   print(json.dumps({'S_done':si+1,**STATS,'max':float(MAXIMUM),'elapsed':time.monotonic()-start}),flush=True)
 result={'target':'8/5','NS':args.ns,'ND':args.nd,'delta_partition':'quadratic','S_upper':'2',
         'CAP_US':list(map(str,CAP_US)),'CAP_SS':list(map(str,CAP_SS)),'ETAS':list(map(str,ETAS)),
         'base_rows':len(base_rows(F(1),F(2),F(0),DB)[0]),'statistics':STATS,
         'max_upper':str(MAXIMUM),'cells':cells}
 name='certificate.json' if not STATS['failed'] else 'unresolved_certificate.json'
 (BASE/name).write_text(json.dumps(result,separators=(',',':')))
 print(json.dumps({'output':name,**STATS,'max':float(MAXIMUM),'elapsed':time.monotonic()-start},indent=2))

if __name__=='__main__':main()
