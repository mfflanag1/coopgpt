#!/usr/bin/env python3
from fractions import Fraction as Q
from pathlib import Path
import argparse,json

def require(test,msg):
 if not test:raise ValueError(msg)

def phi(pools,repair=False):
 k=len(pools);C=list(map(sum,pools));T=min(C);answer=[]
 for j,pool in enumerate(pools):
  b=min(C[t] for t in range(k) if t!=j)
  coeff=sum((1-(b if repair else T)/C[t] for t in range(k) if t!=j),Q(0))/(k-1)
  answer.append([max(Q(0),x-C[j]+T)*coeff+T*x/((k-1)*C[j]) for x in pool])
 return answer

p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
lo=phi([[Q(4,5)],[Q(1)],[Q(1)]])[0][0];hi=phi([[Q(1)],[Q(1)],[Q(1)]])[0][0]
require(lo==Q(14,25) and hi==Q(1,2) and lo>hi,'Phi own-monotonicity witness')
a=phi([[Q(1)],[Q(1)]*3,[Q(1)]*3],True);coalition=sum(x[0] for x in a)
require(coalition==Q(5,6) and coalition<1,'repair coverage witness')
envelopes=[]
for k in (2,3,8,100):
 x=Q(k,2*(k-1));pay=phi([[x]]+[[Q(1)] for _ in range(k-1)])[0][0]
 require(pay==Q(k*k,4*(k-1)**2),'envelope quadratic maximum')
 envelopes.append({'k':k,'maximizer':str(x),'total':str(k*pay)})
result={'status':'EXACT_FAILURE_WITNESSES_VERIFIED','original_payment_before':str(lo),'original_payment_after':str(hi),'repair_coalition_payment':str(coalition),'repair_coalition_worth':'1','envelope_specializations':envelopes,'corrected_large_R_total_limit':'k+1/(k-1)','large_R_derivation':'Short pool marginal tends1; other k-1 marginals sum to k-2; all proportional terms sum k/(k-1).','scope':'Only the failure witnesses and budget correction are retained. The delegate bounded-domain G claim and partial forcing lemma are not integrated.'}
args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
