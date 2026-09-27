"""An actual zero-subsidy market defeats the enriched ideal-difference relaxation."""
from pathlib import Path
from fractions import Fraction as Q
from itertools import permutations
import json
from verify_cyclic_frontier import geometry, full_market, require


def run():
 d=json.loads(Path(__file__).with_name('IDEAL_DIFFERENCE_COUNTEREXAMPLE.json').read_text());m=d['m'];T=d['T'];P=d['P']
 require(m==8 and T==32,'market inventory')
 edges,idx,teams=geometry(m,P);weights=list(map(Q,d['weights']));require(len(weights)==len(edges) and min(weights)>0,'supported pair weights')
 require([list(t)for t,_ in teams]==d['teams'],'original dual row ordering')
 diagonal_table=[[2,1,1],[1,2,1],[1,2,1],[2,1,1],[2,1,1],[2,1,1],[1,2,1],[1,2,1]]
 require([[weights[idx[(s,j,j)]]for s in range(3)]for j in range(m)]==diagonal_table,'diagonal table')
 require([[weights[idx[e]]for e in ((0,a,b),(1,a,c),(2,b,c))]for a,b,c in P]==[[2,3,2],[3,2,2],[3,2,2],[2,3,2]],'P pair table')
 displayed=[3,3,0,3,0,0,3,0,1,0,1,1,3,3,0,1,0,1,3,0,1,1,1,3]
 require(sum(displayed)==T and all(sum(displayed[i]for i in t)>=sum(weights[e]for e in es)for t,es in teams),'displayed original core')
 displayed_y=[7,7,1,7,1,1,7,1,4,1,1,4,10,10,1,1,1,4,10,1,1,1,4,10]
 require([Q(v)for v in d['protected_y']]==[Q(v,3)for v in displayed_y],'displayed protected payoff')
 truth={k:d[k]for k in ('m','P','ideal_upper_duals')}
 for key in ('weights','H','protected_y'):truth[key]=[str(Q(v)/T)for v in d[key]]
 truth['core_witnesses']=[[str(Q(v)/T)for v in x]for x in d['core_witnesses']]
 diagonal_rows=[k for k,(t,_)in enumerate(teams)if t[0]==t[1]-m==t[2]-2*m]
 truth['subsidy_dual']={'lambda':[[k,'1']for k in diagonal_rows],'mu':['0']*(3*m)};truth['subsidy']='0'
 pattern={'m':m,'P':P,'primal_scale':T,'primal_integers':d['weights']}
 result=full_market(truth,pattern)
 diagonal=[sum(weights[idx[(s,j,j)]]for s in range(3))for j in range(m)]
 require(diagonal==[4]*m,'diagonal values')
 hat=list(map(Q,d['hypothetical_ideals']));require(hat==[4]*(3*m),'hypothetical ideals')
 W=sum(weights[idx[e]]for a,b,c in P for e in ((0,a,b),(1,a,c),(2,b,c)))
 used={s*m+j for t in P for s,j in enumerate(t)};U=set(range(3*m))-used;R=T-W
 require(W==28 and R==4 and len(U)==12,'matching worth and unmatched count')
 require(all(0<=hat[s*m+j]<=diagonal[j]for s in range(3)for j in range(m)),'diagonal ideal cap')
 require(all(hat[i]<=R for i in U),'residual ideal cap')
 require(all(hat[i]>=Q(d['H'][i])for i in range(3*m)),'hypothetical vector must dominate actual ideals')
 completion_count=0
 for team,es in teams:
  labels=tuple(j-s*m for s,j in enumerate(team))
  if len(set(labels))!=2:continue
  repeated=next(j for j in labels if labels.count(j)==2);sector=next(s for s,j in enumerate(labels)if j!=repeated)
  require(hat[sector*m+labels[sector]]-hat[sector*m+repeated]>=sum(weights[e]for e in es)-diagonal[repeated],'completion ideal difference')
  completion_count+=1
 pairs=[(0,1),(0,2),(1,2)]
 def budget(s,j):return sum(weights[idx[(p,j,j)]]for p,st in enumerate(pairs)if s in st)
 for s in range(3):
  for a in range(m):
   for b in range(m):require(hat[s*m+a]-hat[s*m+b]<=budget(s,a),'global ideal range bound')
 team_count=0
 for t in P:
  value=sum(weights[idx[e]]for e in ((0,t[0],t[1]),(1,t[0],t[2]),(2,t[1],t[2])))
  for s,v,u in permutations(range(3)):
   a,b,c=t[s],t[v],t[u]
   require(hat[u*m+c]-hat[u*m+b]>=value-diagonal[b]-budget(s,a),'P-induced ideal difference')
   team_count+=1
 fake=W+sum(hat[i]/3 for i in U)-T
 actual=W+sum(Q(d['H'][i])/3 for i in U)-T
 require(fake==12 and actual==0,'obstruction values')
 require(all(Q(d['H'][i])==1 for i in U),'actual unmatched ideals')
 # A damaged asserted maximum must be rejected by primal/dual equality.
 bad=dict(truth);bad['H']=truth['H'][:];bad['H'][next(iter(U))]='1/8'
 try:full_market(bad,pattern)
 except ValueError:pass
 else:raise ValueError('false ideal maximum accepted')
 print(json.dumps({'status':'PASS','T':T,'W':str(W),'actual_subsidy':result['exact_witness_market_subsidy'],'hypothetical_normalized_obstruction':str(fake/T),'actual_unmatched_ideals':1,'completion_difference_checks':completion_count,'global_range_checks':3*m*m,'P_induced_difference_checks':team_count,'negative_controls':1,'scope':'difference-only necessary conditions do not certify actual ideal attainability; not a counterexample to one-third'}))

if __name__=='__main__':run()
