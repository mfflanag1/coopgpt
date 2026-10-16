"""Optimizer proposes sparse duals; every proposed bound is checked rationally."""
from fractions import Fraction as F
from math import factorial
from pathlib import Path
import argparse,json,time
import numpy as np
from scipy.optimize import linprog

BASE=Path(__file__).resolve().parent
PB=F(11,8); CB=F(148,125); DB=F(23,125)
EL=sum((F(1,factorial(k)) for k in range(9)),F(0))
EU=EL+F(1,factorial(9))*F(10,9)
cl=1/(2*EU);cu=1/(2*EL);CL=1+cl;CU=1+cu;KU=EU-1
US=[F(i,100) for i in range(35,96,2)]+[F(1,2)]
TS=[F(i,10) for i in range(10)]
SS=[F(i,16) for i in range(17)]
AS=[F(1,16),F(1,8),F(1,4),F(1,2),F(3,4),F(1),F(3,2),F(2)]

def require(v,s):
 if not v:raise RuntimeError(s)

def en(x,n):
 term=out=F(1)
 for k in range(1,n+1):term*=(-x)/k;out+=term
 return out

Q={u:(en(1/u-1,25)/2,en(1/u-1,24)/2) for u in US}
ROLE={t:(en(t,24),en(1/t,48) if t else F(0)) for t in TS}
ENT={s:(en(1-s,25)/2,en(1-s,24)/2) for s in SS}

def rows(lo,hi,dl,dh):
 aa=[];bb=[]
 def add(row,rhs):aa.append(list(map(F,row)));bb.append(F(rhs))
 add([1,-1,0,0,0],0);add([-CU,1,0,0,0],0)
 add([0,-1,0,0,0],PB-lo);add([-1,1,1,0,0],1)
 add([0,1,1,0,0],F(3,2));add([0,0,1,1,0],1)
 add([F(4,3),0,1,-1,0],F(4,3));add([0,-1,0,1,0],0)
 add([1,0,0,0,0],1);add([CL,-1,0,0,0],dh)
 add([-CU,1,0,0,0],-dl);add([0,0,0,0,1],3)
 for t in TS:
  e1,e2=ROLE[t]
  add([0,1,1-t,0,0],1+e1/2)
  add([-1-t*e2/2,1,1-t,0,0],1-t)
 require(F(429,1000)**2>cu,'sqrt c upper')
 for alpha in AS:
  r=KU*F(429,1000)/2
  add([2-r*alpha,0,1-cu,-cu,0],2+r*dh/alpha)
 for s in SS:
  tl,th=ENT[s];al=s+cl-th;ah=s+cu-tl
  add([al+F(1,2),0,al,cl-th,0],dh+ah+F(1,2))
 add([F(65,64),0,F(1,2)+cl,cl-F(1,2),0],4*dh+F(65,64))
 for u in US:
  ql,qh=Q[u];al=1-qh*(1+1/u);ah=1-ql*(1+1/u)
  require(al>0 and ql>0,'PD coefficient signs')
  lam=1-ql*(1+1/u-1/lo);eta=qh/lo
  mu=KU*KU*eta*eta/(4*al);p=KU*eta
  phi=(hi-1)*(1-ql*(1+1/u-1/hi))
  add([0,-p,-lam,p,1],phi)
  add([0,-mu-ah,-lam,mu,1],phi+ah*(PB-lo))
 saving=F(2,5)*en(hi-1+dh,25)
 require(saving>0,'saving positive')
 return aa,bb,[F(0),F(0),-saving,F(0),F(1)]

CAPS=[F(1),CB,F(1),CB,F(3)]

def weak(aa,bb,obj,weights):
 residual=[max(F(0),obj[j]-sum(w*aa[k][j] for k,w in weights)) for j in range(5)]
 return 1+sum(w*bb[k] for k,w in weights)+sum(r*c for r,c in zip(residual,CAPS))

def quantize(vals):
 return [(k,F(max(0,round(float(v)*10**12)),10**12)) for k,v in enumerate(vals) if float(v)>1e-13]

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--ns',type=int,default=128);parser.add_argument('--nd',type=int,default=16)
 parser.add_argument('--target',default='81/50');args=parser.parse_args()
 ns,nd=args.ns,args.nd;target=F(args.target);start=time.monotonic();out=[];maximum=F(-1);fail=0
 for si in range(ns):
  lo=1+(PB+CB-1)*si/ns;hi=1+(PB+CB-1)*(si+1)/ns
  for di in range(nd):
   dl=DB*di/nd;dh=DB*(di+1)/nd
   if lo>PB+CU-dl:
    out.append({'empty':'geometric'});continue
   aa,bb,obj=rows(lo,hi,dl,dh)
   af=np.array(aa,dtype=float);bf=np.array(bb,dtype=float)
   lp=linprog(-np.array(obj,dtype=float),A_ub=af,b_ub=bf,bounds=[(0,None)]*5,method='highs')
   if lp.success:
    weights=quantize(-lp.ineqlin.marginals)
    upper=weak(aa,bb,obj,weights)
    maximum=max(maximum,upper);fail+=upper>=target
    out.append({'weights':[[k,str(w)] for k,w in weights]})
   elif lp.status==2:
    dual=linprog(bf,A_ub=np.vstack((-af.T,np.ones((1,len(bb))))),b_ub=np.array([0]*5+[1]),bounds=[(0,None)]*len(bb),method='highs')
    require(dual.success,'Farkas proposal failed')
    weights=quantize(dual.x);upper=weak(aa,bb,[F(0)]*5,weights)-1
    require(upper<0,'Farkas exact replay failed')
    out.append({'empty':'dual','weights':[[k,str(w)] for k,w in weights]})
   else:raise RuntimeError('LP status '+str(lp.status))
  if si%16==15:print(json.dumps({'completed_S':si+1,'max':float(maximum),'above_target':fail,'elapsed':time.monotonic()-start}),flush=True)
 result={'target':str(target),'PB':str(PB),'NS':ns,'ND':nd,'rows':len(rows(F(1),F(2),F(0),DB)[0]),
         'US':[str(x) for x in US],'TS':[str(x) for x in TS],'SS':[str(x) for x in SS],'AS':[str(x) for x in AS],
         'max_upper':str(maximum),'above_target':fail,'cells':out,'elapsed':time.monotonic()-start}
 name='certificate.json' if fail==0 else 'diagnostic_certificate.json'
 (BASE/name).write_text(json.dumps(result,separators=(',',':')))
 print(json.dumps({k:v for k,v in result.items() if k!='cells' and k!='max_upper'}|{'max_upper_display':float(maximum),'output':name},indent=2))

if __name__=='__main__':main()
