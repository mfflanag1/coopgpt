"""Six inverse LPs with a fixed, exact first-floor budget and free pair weights."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import hashlib,json,time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix,csr_matrix

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parents[1]/'cycle3'/'experiment'
if not SOURCE.is_dir():SOURCE=Path('/private/tmp/coopgt-pairadd-cycle3/experiment')
def require(ok,msg):
    if not ok:raise RuntimeError(msg)
def save(name,obj):(ROOT/name).write_text(json.dumps(obj,indent=2,default=str)+'\n')
def rational(x):return F(float(x)).limit_denominator(1000000)

def formulate():
    raw=json.loads((SOURCE/'composition_input.json').read_text())
    cert=json.loads((SOURCE/'composition_exact.json').read_text())
    M=raw['matrices'];m=len(M[0]);n=3*m;teams=list(product(range(m),repeat=3))
    slots=[(p,i,j) for p in range(3) for i,j in product(range(m),repeat=2) if M[p][i][j]]
    slot_index={slot:i for i,slot in enumerate(slots)};k=len(slots);require(k==65,'support count')
    team_slots=[]
    for i,j,h in teams:team_slots.append([slot_index[p,a,b] for p,a,b in ((0,i,j),(1,i,h),(2,j,h)) if (p,a,b) in slot_index])
    team_index={team:i for i,team in enumerate(teams)}
    positive=[(team,cols) for team,cols in zip(teams,team_slots) if cols]
    matching=raw['matching'];matching_slots=[team_slots[team_index[tuple(t)]] for t in matching]
    budget=[F(0)]*k;floor=[]
    dual=cert['first_floor_dual']
    for idx,mult in dual['equalities']:
        for col in matching_slots[idx]:budget[col]+=9*F(mult)
    for idx,mult in dual['inequalities']:
        if idx<len(positive):
            for col in positive[idx][1]:budget[col]-=9*F(mult)
        else:floor.append((idx-len(positive),9*F(mult)))
    require(sum(v for i,v in floor)==9 and all(v.denominator==1 for v in budget),'primitive budget')
    require(len([i for i,v in floor if v==1])==6,'six target budget')
    dimension=k+2*n
    A=lil_matrix((2*len(teams),dimension),dtype=float)
    for copy in range(2):
        for row,((i,j,h),cols) in enumerate(zip(teams,team_slots)):
            rr=copy*len(teams)+row
            for col in cols:A[rr,col]=1
            for person in (i,m+j,2*m+h):A[rr,k+copy*n+person]=-1
    E=lil_matrix((2*len(matching)+1+len(floor),dimension),dtype=float);e=np.zeros(E.shape[0])
    for copy in range(2):
        for row,((i,j,h),cols) in enumerate(zip(matching,matching_slots)):
            rr=copy*len(matching)+row
            for col in cols:E[rr,col]=-1
            for person in (i,m+j,2*m+h):E[rr,k+copy*n+person]=1
    rr=2*len(matching)
    for col,v in enumerate(budget):E[rr,col]=float(v)
    e[rr]=9
    for offset,(i,v) in enumerate(floor,1):E[rr+offset,k+i]=1;e[rr+offset]=1
    bounds=[(0,None)]*k+[(1,None)]*n+[(0,None)]*n
    description=dict(source_input=str(SOURCE/'composition_input.json'),source_certificate=str(SOURCE/'composition_exact.json'),source_hashes={name:hashlib.sha256((SOURCE/name).read_bytes()).hexdigest() for name in ('composition_input.json','composition_exact.json')},m=m,n=n,pair_support=slots,matching=matching,budget=list(map(str,budget)),floor_support=[[i,str(v)] for i,v in floor],normalization='Primitive nine-unit budget B9(W)=9; x>=1 and all positive-budget coordinates x_i=1. No fixed total: both points obey every matching equality.',targets=[i for i,v in floor if v==1],target_bound=9,max_cells=6,all_triples=len(teams),primal_triple_rows=2*len(teams),free_pair_entries=k,total_variables=dimension)
    return description,M,teams,slots,A.tocsr(),np.zeros(A.shape[0]),E.tocsr(),e,bounds

def main():
    description,M,teams,slots,A,b,E,e,bounds=formulate();save('manifest.json',description)
    start=time.monotonic();records=[];k=len(slots);n=description['n']
    for target in description['targets']:
        c=np.zeros(k+2*n);c[k+n+target]=-1
        result=linprog(c,A_ub=A,b_ub=b,A_eq=E,b_eq=e,bounds=bounds,method='highs',options={'time_limit':60})
        require(result.success,'inverse optimization failed '+result.message)
        rec=dict(target=target,optimum_float=-result.fun,elapsed_seconds=time.monotonic()-start,solution=list(map(str,map(rational,result.x))),inequality_dual=list(map(str,map(rational,result.ineqlin.marginals))),equality_dual=list(map(str,map(rational,result.eqlin.marginals))),lower_dual=list(map(str,map(rational,result.lower.marginals))))
        records.append(rec);save('records.json',records)
        print('TARGET',target,'OPTIMUM',-result.fun,'SECONDS',rec['elapsed_seconds'],flush=True)
        if -result.fun>6+1e-7:
            matrices=[[[F(0)]*description['m'] for _ in range(description['m'])] for _ in range(3)]
            for (p,i,j),value in zip(slots,result.x[:k]):matrices[p][i][j]=rational(value)
            candidate=dict(matrices=matrices,target=target,x=list(map(rational,result.x[k:k+n])),y=list(map(rational,result.x[k+n:])),budget=description['budget'],floor_support=description['floor_support'],matching=description['matching'],predicted_ideal=rational(-result.fun))
            save('candidate.json',candidate);print('CANDIDATE ABOVE SIX SAVED',flush=True);break
    save('summary.json',dict(completed_cells=len(records),planned_cells=6,elapsed_seconds=time.monotonic()-start,status='candidate_above_six' if any(r['optimum_float']>6+1e-7 for r in records) else 'completed_six_target_gate'))

if __name__=='__main__':main()
