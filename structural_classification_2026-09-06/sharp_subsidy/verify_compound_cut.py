"""Independent exact block-cut evaluation and full-packing positive control."""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
import json
from two_hub_block_certificate import structure
from verify_variable_p import require,topology
from verify_root_mass import verify as verify_equality

def evaluate(d,equal_hubs=False):
 m=d['m'];P=d['P'];require(m>0 and all(len(e)==3 and len(set(e))==3 and all(isinstance(j,int)and 0<=j<m for j in e)for e in P),'team domain');used=[s*m+j for e in P for s,j in enumerate(e)];require(len(used)==len(set(used)),'matching overlap');degrees,connected,cycles=topology(d);require(connected and cycles==0 and all(1<=v<=3 for v in degrees),'tree domain');own,degree,block,rb,L,hubs,ports,toward=structure(m,P);B=len(L);types=[(b,t,s)for b in range(B)for t in range(3)if L[b][t]for s in range(3)if s!=t];require([tuple(t)for t in d['types']]==types,'type inventory');values=list(map(F,d['values']));require(len(values)==len(types)*B,'weight count');p=[values[k*B:(k+1)*B]for k in range(len(types))];lookup={v:k for k,v in enumerate(types)};g=len(hubs)
 require(all(0<=v<=1 for v in values),'weight bounds')
 for b in range(B):
  for s in range(3):require(sum(L[b0][t]*p[k][b]for k,(b0,t,a)in enumerate(types)if a==s)==1,'sector balance')
 for k,(b0,t,s)in enumerate(types):
  for h,bs in enumerate(ports):require(all(p[k][b]<=p[k][toward[b0][h]]for b in bs),'root monotonicity')
 delta={(b,t):1-sum(p[lookup[b,t,s]][b]for s in range(3)if s!=t)for b in range(B)for t in range(3)if L[b][t]};require(all(v>=0 for v in delta.values()),'negative deficit')
 supply=[sum(rb[b]*p[k][b]for b in range(B))-delta[b0,t]for k,(b0,t,s)in enumerate(types)];require(all(v>=0 for v in supply),'negative supply')
 R=sum(L[b][t]*p[k][b]for k,(b,t,s)in enumerate(types));require(R==g+2,'minimum root mass')
 A=[sum(L[b0][t]*p[k][toward[b0][h]]for k,(b0,t,s)in enumerate(types))for h in range(g)];require(all(a<=4 for a in A)and sum(4-a for a in A)==1,'hub slack')
 if equal_hubs:require(A==[F(7,2),F(7,2)],'equal hub loads')
 cuts={}
 for s in range(3):
  for mask in range(1<<B):
   cols=[b for b in range(B)if mask>>b&1];need=sum(L[b][s]*delta.get((b,s),0)for b in cols);have=sum(L[b0][t]*min(supply[k],sum(L[b][s]*p[k][b]for b in cols))for k,(b0,t,a)in enumerate(types)if a==s);cuts[s,mask]=(need,have)
 return cuts,B,L

def counter(d):
 cuts,B,L=evaluate(d,True)
 for s in range(3):
  for mask in [1<<b for b in range(B)]+[(1<<B)-1]:require(cuts[s,mask][0]<=cuts[s,mask][1],'singleton or full cut fails')
 mask=sum(1<<b for b in d['columns']);need,have=cuts[d['sector'],mask];gap=need-have
 require(gap>0 and gap>=F(d['certified_gap_lower_bound']),'compound cut not violated')
 return {'sector':d['sector'],'blocks':d['columns'],'demand':str(need),'capacity':str(have),'gap':str(gap),'cuts_checked':len(cuts)}

def extract(d):
 m=d['m'];P=[tuple(e)for e in d['P']];own,degree,block,rb,L,hubs,ports,toward=structure(m,P);weights=defaultdict(F)
 for i,e,w in d['packings']:
  if tuple(e)in P:weights[i,P.index(tuple(e))]+=F(w)
 types=[(b,t,s)for b in range(len(L))for t in range(3)if L[b][t]for s in range(3)if s!=t];values=[]
 for b,t,s in types:
  roots=[j for j in range(m)if degree[j]==1 and t*m+j in own and block[own[t*m+j]]==b];first=s*m+roots[0]
  for c in range(len(L)):
   es=[e for e in range(len(P))if block[e]==c];w=weights[first,es[0]]
   require(all(weights[s*m+j,e]==w for j in roots for e in es),'type/block inconsistency');values.append(str(w))
 return {'m':m,'P':P,'types':types,'values':values}

def run():
 root=Path(__file__).parent;d=json.loads((root/'COMPOUND_CUT_COUNTEREXAMPLE.json').read_text());result=counter(d)
 good=json.loads((root/'COMPOUND_CUT_CONTROL.json').read_text());require(good['P']==d['P'],'control support');checked=verify_equality(good);cuts,_,_=evaluate(extract(good));require(all(a<=b for a,b in cuts.values()),'positive control cuts')
 bad=dict(d);bad['values']=['0']*len(d['values'])
 try:counter(bad)
 except ValueError:pass
 else:raise ValueError('invalid zero weights accepted')
 print(json.dumps({'status':'PASS','counterexample':result,'positive_control_entries':checked['entries'],'positive_control_cuts':len(cuts),'negative_controls':1,'scope':'hub balance and singleton/full cuts do not ensure transfer completion'}))
if __name__=='__main__':run()
