from pathlib import Path
import json,numpy as np
from scipy.optimize import least_squares
import two_hub_blocks as tb

def profiles(data,logs):
 own,degree,block,rb,L,hubs,ports,toward=data;B=len(L);g=len(hubs);L=np.array(L);N=L.sum(axis=1)[:,None]-L;K=np.exp(logs);ps=[]
 for s in range(3):
  Q=np.zeros((B+g,B+g))
  for h,bs in enumerate(ports):
   for b in bs:
    v=B+h;c=K[h];Q[b,b]+=c;Q[v,v]+=c;Q[b,v]-=c;Q[v,b]-=c
  for b in range(B):Q[b,b]+=N[b,s]
  ps.append(np.linalg.inv(Q)[:B,:B])
 A=np.array([sum(N[b,s]*ps[s][toward[b][h],b]for b in range(B)for s in range(3))for h in range(g)])
 return ps,A

def check(data,ps):
 _,_,_,rb,L,hubs,ports,toward=data;B=len(L);g=len(hubs);L=np.array(L);delta=np.array([[1-sum(ps[s][b,b]for s in range(3)if s!=t)for t in range(3)]for b in range(B)])
 worst=0;witness=None
 for s in range(3):
  types=[(b,t)for b in range(B)for t in range(3)if t!=s and L[b,t]>0];sup=[sum(rb[c]*ps[s][c,b]for c in range(B))-delta[b,t]for b,t in types]
  for (b,t),a in zip(types,sup):
   if a< -worst:worst=-a;witness=('negative supply',s,b,t)
  for mask in range(1<<B):
   cols=[b for b in range(B)if mask>>b&1];need=sum(L[b,s]*delta[b,s]for b in cols);have=sum(L[b,t]*min(a,sum(L[c,s]*ps[s][c,b]for c in cols))for (b,t),a in zip(types,sup));gap=need-have
   if gap>worst:worst=gap;witness=('cut',s,cols,need,have)
 return float(worst),witness,float(min(delta[b,t]for b in range(B)for t in range(3)if L[b,t]))

def run(name,m,P,data=None):
 if data is None:data=tb.structure(m,P)
 g=len(data[5]);target=4-1/g
 def residual(logs):return profiles(data,logs)[1]-target
 opt=least_squares(residual,np.zeros(g),bounds=(-15,20),xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=100)
 ps,A=profiles(data,opt.x);gap,wit,mind=check(data,ps);out={'name':name,'hubs':g,'conductances':np.exp(opt.x).tolist(),'hub_loads':A.tolist(),'target':target,'max_residual':float(max(abs(A-target))),'worst_cut_gap':gap,'witness':wit,'min_leaf_deficit':mind};print(json.dumps(out),flush=True);return out
if __name__=='__main__':
 out=[]
 for same in (False,True):
  for seed in range(3):out.append(run(f'{same}_{seed}',*tb.example(same,seed)))
 Path(__file__).with_name('BALANCED_CONDUCTANCE_DISCOVERY.json').write_text(json.dumps(out)+'\n')
