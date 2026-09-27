"""Exact raw-core/cut equivalence and explicit path-cycle checks; no floating point."""
from collections import deque
from fractions import Fraction as F
from itertools import product, permutations
from pathlib import Path
import json
import z3
from probe import solve, frac

ROOT=Path(__file__).resolve().parent
def require(ok,msg):
    if not ok:raise RuntimeError(msg)
def no(cons):
    s=z3.Solver();s.set(timeout=30000);s.add(cons)
    require(s.check()==z3.unsat,'Expected exact unsat')
def cover(point,edges,matrices,m,k,T):
    require(min(point)>=0 and sum(point)==T,'Core total')
    for t in product(range(m),repeat=k):
        require(sum(point[v*m+t[v]] for v in range(k))>=sum(A[t[a]][t[b]] for (a,b),A in zip(edges,matrices)),'Full-team cover')

def tree_case(row):
    edges=row['edges'];m=row['m'];k=row['k'];mats=row['matrices']
    children={v:[] for v in range(k)};labels={0:list(range(m))};new=[]
    for (a,b),A in zip(edges,mats):
        require(a in labels,'Root order needed')
        children[a].append(b)
        pp=max(permutations(range(m)),key=lambda p:sum(A[labels[a][j]][p[j]] for j in range(m)))
        labels[b]=list(pp)
        new.append([[A[labels[a][i]][labels[b][j]] for j in range(m)]for i in range(m)])
    d={(a,b):[A[j][j] for j in range(m)]for (a,b),A in zip(edges,new)}
    subtree={}
    def descend(v):
        subtree[v]=[v]+[u for c in children[v] for u in descend(c)]
        return subtree[v]
    descend(0)
    p=[[z3.Real(f'p{v}_{j}')for j in range(m)]for v in range(k)]
    U={v:[z3.Sum([p[u][j]for u in subtree[v]])-sum(d[a,b][j]for a,b in edges if a in subtree[v] and b in subtree[v]) for j in range(m)]for v in range(1,k)}
    T=sum(sum(v)for v in d.values())
    nonneg=[x>=0 for pp in p for x in pp]
    full=[z3.Sum([p[v][t[v]]for v in range(k)])>=sum(A[t[a]][t[b]]for (a,b),A in zip(edges,new)) for t in product(range(m),repeat=k)]
    raw=nonneg+[z3.Sum([x for pp in p for x in pp])==T]+full
    diag=[z3.Sum([p[v][j]for v in range(k)])==sum(vals[j]for vals in d.values()) for j in range(m)]
    cuts=[U[b][i]-U[b][j]>=A[j][i]-A[j][j]for (a,b),A in zip(edges,new)for i,j in product(range(m),repeat=2)]
    reduced=nonneg+diag+cuts
    no(raw+[z3.Not(z3.And(reduced))]);no(reduced+[z3.Not(z3.And(raw))])
    result={'graph':row['graph'],'m':m,'k':k,'equivalence_queries':2,'T':T}
    if row['graph']!='path':return result
    sol=solve(edges,new,m,k);x=list(map(F,sol['x']));H=list(map(F,sol['H']))
    cover(x,edges,new,m,k,T)
    potentials={('anchor',0):F(0)}
    for r in range(1,k):
        for j in range(m):potentials[r,j]=sum(x[v*m+j] for v in range(r,k))-sum(d[a,b][j]for a,b in edges if a>=r)
    arcs=[];anchor=('anchor',0)
    for j in range(m):
        arcs.append((anchor,(1,j),d[0,1][j],j))
        for r in range(1,k-1):arcs.append(((r,j),(r+1,j),d[r,r+1][j],r*m+j))
        arcs.append(((k-1,j),anchor,0,(k-1)*m+j))
    for (a,b),A in zip(edges,new):
        for i,j in product(range(m),repeat=2):
            if i!=j:arcs.append(((b,i),(b,j),A[j][j]-A[j][i],None))
    slacks=[F(c)+potentials[u]-potentials[v]for u,v,c,_ in arcs]
    require(min(slacks)>=0,'Potential feasibility')
    cert=[]
    for ei,(tail,head,c,player) in enumerate(arcs):
        if player is None:continue
        require(slacks[ei]==x[player],'Payoff identity')
        eligible=[i for i,(_,_,_,f)in enumerate(arcs)if (f is None and slacks[i]==0)or(f is not None and x[f]<=x[player])]
        parent={head:None};todo=deque([head])
        while todo and tail not in parent:
            node=todo.popleft()
            for i in eligible:
                a,b,_,_=arcs[i]
                if a==node and b not in parent:parent[b]=(node,i);todo.append(b)
        require(tail in parent,'Missing eligible cycle')
        seq=[];node=tail
        while node!=head:
            prev,i=parent[node];seq.append(i);node=prev
        cyc=[ei]+list(reversed(seq));verts=[arcs[i][0]for i in cyc]
        require(len(verts)==len(set(verts)),'Cycle not simple')
        require(all(arcs[a][1]==arcs[b][0]for a,b in zip(cyc,cyc[1:]+cyc[:1])),'Broken cycle')
        ids=[arcs[i][3]for i in cyc if arcs[i][3] is not None]
        require(len(ids)==k and len(set(ids))==k,'Wrong payoff-arc count')
        const=sum(arcs[i][2]for i in cyc)
        require(const==sum(x[i]for i in ids)<=k*x[player] and H[player]<=const,'Wrong bound')
        cert.append({'player':player,'cycle':cyc,'payoffs':ids,'constant':const})
    result.update({'matrices':new,'x':sol['x'],'H':sol['H'],'arcs':arcs,'certificates':cert})
    return result

def cycle_certificate(row):
    edges=row['edges'];m=row['m'];k=row['k'];A=row['matrices'];T=row['T']
    x=list(map(F,row['x']));cover(x,edges,A,m,k,T)
    p=[z3.Real(f'y{i}')for i in range(m*k)]
    raw=[v>=0 for v in p]+[z3.Sum(p)==T]
    raw += [z3.Sum([p[v*m+t[v]]for v in range(k)])>=sum(B[t[a]][t[b]]for (a,b),B in zip(edges,A))for t in product(range(m),repeat=k)]
    tau=min(x);target=min((i for i in range(m*k)if F(row['H'][i])>0),key=lambda i:x[i]/F(row['H'][i]));H=F(row['H'][target])
    q=lambda v:z3.Q(v.numerator,v.denominator)
    no(raw+[v>q(tau)for v in p])
    require(x[target]==tau,'Target not on first floor')
    no(raw+[v>=q(tau)for v in p]+[p[target]>q(tau)])
    no(raw+[p[target]>q(H)])
    s=z3.Solver();s.add(raw+[p[target]==q(H)]);require(s.check()==z3.sat,'Ideal not attained')
    y=[frac(s.model().eval(v))for v in p];cover(y,edges,A,m,k,T)
    require(tau/H<F(1,k),'Not a strict counterexample')
    teams=list(product(range(m),repeat=k))
    worth=lambda t:sum(B[t[a]][t[b]]for (a,b),B in zip(edges,A))
    lam=[z3.Real(f'lambda{i}')for i in range(len(teams))]
    loads=[z3.Sum([lam[e]for e,t in enumerate(teams)if v*m+t[v]==i])for i in range(k*m)for v in [i//m]]
    s=z3.Solver();s.add([v>=0 for v in lam]+[v<=1 for v in loads])
    s.add(z3.Sum([lam[e]*q(F(worth(t))-k*tau)for e,t in enumerate(teams)])==q(F(T)-k*m*tau),loads[target]<1)
    require(s.check()==z3.sat,'No positive-target deficit dual')
    dual=[{'team':list(t),'weight':str(frac(s.model().eval(lam[e])))}for e,t in enumerate(teams)if frac(s.model().eval(lam[e]))>0]
    pp=list(permutations(range(m)))
    matching=next([list((i,)+tuple(p[i]for p in perms))for i in range(m)]for perms in product(pp,repeat=k-1)if sum(worth((i,)+tuple(p[i]for p in perms))for i in range(m))==T)
    return {**row,'target':target,'floor':str(tau),'ideal_witness':list(map(str,y)),'residual_dual':dual,'optimal_matching':matching,'raw_exclusions':3,'scope':'Refutes 1/4 for this four-cycle; does not prove vanishing or determine c(C4)'}

def main():
    target=ROOT/'VERIFICATION.json';target.write_text('{"status":"RUNNING"}\n')
    records=json.loads((ROOT/'PROBE.json').read_text())['records']
    selected=[]
    for name in ('path','star'):
        for m in (2,3):selected += [r for r in records if r['graph']==name and r['m']==m][:4]
    selected += [{'graph':'path','k':k,'m':1,'edges':[(r,r+1)for r in range(k-1)],'matrices':[[[int(r==0)]]for r in range(k-1)]}for k in (2,3,4,5,6)]
    selected += [{'graph':'path','k':4,'m':2,'edges':[(r,r+1)for r in range(3)],'matrices':[[[1,0],[0,0]],[[0,0],[0,0]],[[0,0],[0,0]]]}]
    results=[tree_case(r)for r in selected]
    cyclic=cycle_certificate(json.loads((ROOT/'BEST.json').read_text())['cycle'])
    (ROOT/'FOUR_CYCLE_CERTIFICATE.json').write_text(json.dumps(cyclic,indent=2)+'\n')
    target.write_text(json.dumps({'status':'PASS','tree_cases':results,'equivalence_queries':2*len(results),'path_player_certificates':sum(len(r.get('certificates',[]))for r in results),'cycle_exclusions':3,'scope':'Finite exact corroboration of symbolic proof; non-exhaustive searches'},indent=2)+'\n')
    print(json.dumps({'status':'PASS','tree_cases':len(results),'cycle_ratio':cyclic['ratio'],'path_player_certificates':sum(len(r.get('certificates',[]))for r in results)}))
if __name__=='__main__':main()
