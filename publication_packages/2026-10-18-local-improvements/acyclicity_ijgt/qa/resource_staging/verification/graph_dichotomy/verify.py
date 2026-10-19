from fractions import Fraction as F
from itertools import product,combinations
from pathlib import Path
import json,sys,copy
from family import construct
ROOT=Path(__file__).resolve().parent

def require(ok,msg):
    if not ok:raise RuntimeError(msg)

def check(r):
    q,m,K=r['q'],r['m'],r['K'];ell=len(r['cycle']);n=K*m
    require(q>=1 and m==3*q+1 and 3<=ell<=K,'dimensions')
    edges=[tuple(e)for e in r['edges']];A=r['matrices'];require(len(A)==len(edges),'matrix count')
    require(all(len(B)==m and all(len(row)==m and all(isinstance(v,int)and v in (0,1,2)for v in row)for row in B)for B in A),'matrix dimensions/alphabet')
    require(len(set(r['cycle']))==ell and all(tuple(sorted((r['cycle'][h],r['cycle'][(h+1)%ell])))in edges for h in range(ell)),'cycle is allowed')
    def ids(t):return [s*m+t[s]for s in range(K)]
    def w(t):return sum(A[h][t[a]][t[b]]for h,(a,b)in enumerate(edges))
    matching=r['matching'];require(sorted(i for t in matching for i in ids(t))==list(range(n)),'perfect partition')
    T=sum(map(w,matching));require(T==r['T']==6*q+1+4*q*(ell-3)>0,'grand worth formula')
    # Independent row-bound optimality certificate on each pair matrix.
    require(all(sum(B[i][i]for i in range(m))==sum(max(row)for row in B)or sum(B[i][i]for i in range(m))==sum(max(B[i][j]for i in range(m))for j in range(m))for B in A),'pairwise compatibility')
    p=list(map(F,r['x_floor']));y=list(map(F,r['y_ideal']));t=F(1,K*(q+1));target=r['target']
    require(len(p)==len(y)==n and min(p)>=t and min(y)>=0 and sum(p)==sum(y)==T,'payoff dimensions/positivity/efficiency')
    require(target==r['cycle'][2]*m and F(r['floor'])==F(r['ratio'])==t,'formula and target')
    covers=0
    for team in product(range(m),repeat=K):
        val=w(team)
        for point in (p,y):require(sum(point[i]for i in ids(team))>=val,'uncovered full team');covers+=1
    partial=r['partial_matching'];used=[i for team in partial for i in ids(team)];require(len(partial)==2*q and len(used)==len(set(used)),'partial partition')
    U=sorted(set(range(n))-set(used));require(sum(map(w,partial))==T-1 and len(U)==K*(q+1)and target in U,'unit budget/unmatched set')
    require(all(p[i]==t for i in U),'first-face attainment')
    tt=next(team for team in matching if target in ids(team));require(w(tt)==1 and y[target]==F(r['target_ideal'])==1,'ideal sandwich')
    return {'q':q,'K':K,'cycle_length':ell,'cycle':r['cycle'],'covers':covers,'T':T,'target_ratio':str(t),'target_ideal':'1','status':'PASS'}

def graph_checks():
    rows=[]
    for K in (3,4,5,6):
        all_edges=list(combinations(range(K),2));connected=trees=cyclic=0;lengths={}
        for mask in range(1<<len(all_edges)):
            edges=[e for j,e in enumerate(all_edges)if mask>>j&1];adj=[[]for _ in range(K)]
            for a,b in edges:adj[a].append(b);adj[b].append(a)
            seen=set();stack=[0]
            while stack:
                v=stack.pop()
                if v in seen:continue
                seen.add(v);stack.extend(adj[v])
            if len(seen)!=K:continue
            connected+=1
            if len(edges)==K-1:trees+=1;continue
            cyclic+=1;cycle=None
            # Independent simple-cycle search, not the family generator.
            def dfs(v,path):
                nonlocal cycle
                if cycle is not None:return
                for u in adj[v]:
                    if u==path[0]and len(path)>=3:cycle=path[:];return
                    if u not in path:dfs(u,path+[u])
            dfs(0,[0])
            if cycle is None:
                for start in range(1,K):
                    dfs(start,[start])
                    if cycle is not None:break
            require(cycle is not None,'cyclic connected graph lacks selected cycle')
            r=construct(1,K,cycle,edges)
            active={tuple(e)for e,B in zip(r['edges'],r['matrices'])if any(v for row in B for v in row)}
            ce={tuple(sorted((cycle[j],cycle[(j+1)%len(cycle)])))for j in range(len(cycle))}
            require(active==ce and active<=set(edges),'embedding support')
            lengths[len(cycle)]=lengths.get(len(cycle),0)+1
        require(trees==K**(K-2),'labeled tree calibration')
        rows.append({'K':K,'edge_masks':1<<len(all_edges),'connected':connected,'trees':trees,'cyclic':cyclic,'selected_cycle_lengths':lengths,'scope':'Graph embedding/support checks; not independent full-cover replay for every mask'})
    return rows

def smt(records):
    import z3
    rows=[]
    chosen=[r for r in records if (r['K'],len(r['cycle']),r['q'])in ((5,5,1),(5,5,2),(6,6,1),(6,4,1))]
    for r in chosen:
        m,K=r['m'],r['K'];p=[z3.Real(f'p{i}')for i in range(K*m)];t=F(r['floor']);z=z3.Q(t.numerator,t.denominator)
        cons=[v>=0 for v in p]+[z3.Sum(p)==r['T']]
        for team in product(range(m),repeat=K):
            val=sum(A[team[a]][team[b]]for (a,b),A in zip(r['edges'],r['matrices']));cons.append(z3.Sum([p[s*m+team[s]]for s in range(K)])>=val)
        for label,extra in [('larger floor',[v>z for v in p]),('target escapes first face',[v>=z for v in p]+[p[r['target']]>z]),('ideal exceeds one',[p[r['target']]>1])]:
            sol=z3.Solver();sol.set(timeout=30000);sol.add(cons+extra);ans=sol.check();require(ans==z3.unsat,f'{label}: {ans}')
            row={'K':K,'ell':len(r['cycle']),'q':r['q'],'query':label,'answer':'unsat'};rows.append(row);print(json.dumps(row),flush=True)
    return rows

def main():
    (ROOT/'VERIFICATION.json').write_text('{"status":"RUNNING"}\n')
    params=[(3,3,1),(4,4,2),(5,5,1),(5,5,2),(5,5,3),(6,6,1),(6,6,2),(7,7,1),(8,8,1),(5,3,1),(6,4,1),(7,5,1),(8,6,1)]
    records=[]
    for K,ell,q in params:
        cycle=list(range(ell))
        # Reverse/relabel nontrivial embeddings to test matrix transposition.
        if K>ell:cycle=list(reversed(range(K-ell,K)))
        r=construct(q,K,cycle,list(combinations(range(K),2))if K>ell else None);records.append(r)
    cases=[]
    for r in records:
        row=check(r);cases.append(row);print(json.dumps(row),flush=True)
    graphs=graph_checks();negative=[]
    for mode in ('wrong_path_bonus','partial_repeat','target_ideal','negative_payoff'):
        r=copy.deepcopy(records[2])
        if mode=='wrong_path_bonus':r['matrices'][-1][0][0]=2
        if mode=='partial_repeat':r['partial_matching'][1]=r['partial_matching'][0]
        if mode=='target_ideal':r['target_ideal']='2'
        if mode=='negative_payoff':r['x_floor'][0]='-1'
        try:check(r)
        except RuntimeError:negative.append(mode)
        else:raise RuntimeError('corruption accepted')
    extra=smt(records)if '--smt'in sys.argv else []
    (ROOT/'CERTIFICATES.json').write_text(json.dumps(records,indent=2)+'\n')
    out={'status':'PASS','cases':cases,'covers':sum(r['covers']for r in cases),'graph_embeddings':graphs,'negative_checks':negative,'raw_core_queries':extra}
    (ROOT/'VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':'PASS','covers':out['covers'],'raw_core_queries':len(extra)}))
if __name__=='__main__':
    try:main()
    except Exception as e:
        (ROOT/'VERIFICATION.json').write_text(json.dumps({'status':'FAILED','error':str(e)})+'\n');raise
