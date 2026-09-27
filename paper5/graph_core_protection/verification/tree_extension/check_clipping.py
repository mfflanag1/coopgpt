"""Exact clipping-lemma checks against all original full-team inequalities."""
from fractions import Fraction as F
from itertools import permutations,product
from pathlib import Path
import json,random
import z3
from raw_core import solve,frac

ROOT=Path(__file__).resolve().parent
def require(ok,msg):
    if not ok:raise RuntimeError(msg)
def check_point(point,edges,A,k,m,T):
    require(len(point)==k*m and min(point)>=0 and sum(point)==T,'Nonnegative efficient payoff')
    for t in product(range(m),repeat=k):require(sum(point[v*m+t[v]]for v in range(k))>=sum(B[t[a]][t[b]]for (a,b),B in zip(edges,A)),'Raw team uncovered')

def clip(edges,A,k,m,T,x,y,root,beta):
    adj={v:[]for v in range(k)}
    for a,b in edges:adj[a].append(b);adj[b].append(a)
    children={v:[]for v in range(k)};order=[root];parent={root:None};labels={root:list(range(m))};d={}
    def matrix(a,b):
        if (a,b)in edges:return A[edges.index((a,b))]
        B=A[edges.index((b,a))];return [list(row)for row in zip(*B)]
    for a in order:
        for b in adj[a]:
            if b==parent[a]:continue
            parent[b]=a;children[a].append(b);order.append(b);B=matrix(a,b)
            perm=max(permutations(range(m)),key=lambda p:sum(B[labels[a][j]][p[j]]for j in range(m)))
            labels[b]=list(perm);d[a,b]=[B[labels[a][j]][perm[j]]for j in range(m)]
    require(sum(sum(v)for v in d.values())==T,'Tree matching total disagrees with integral raw total')
    subs={v:[v]for v in range(k)}
    for v in reversed(order[1:]):subs[parent[v]]+=subs[v]
    points=[]
    for p in (x,y):points.append({v:[p[v*m+labels[v][j]]for j in range(m)]for v in range(k)})
    X,Y=points
    cuts=[]
    for P in points:
        cuts.append({v:[sum(P[u][j]for u in subs[v])-sum(vals[j]for (a,b),vals in d.items()if a in subs[v]and b in subs[v])for j in range(m)]for v in order[1:]})
    UX,UY=cuts
    Z={v:[min(UX[v][j],UY[v][j]+len(subs[v])*beta)for j in range(m)]for v in order[1:]};Z[root]=[F(0)]*m
    out=[F(0)]*(k*m)
    for v in range(k):
        for j in range(m):
            val=Z[v][j]-sum(Z[b][j]for b in children[v])+sum(d[v,b][j]for b in children[v]);out[v*m+labels[v][j]]=val
            if v==root:
                require(val>=X[v][j] and val>=Y[v][j]-(k-1)*beta,'Root clipping bounds')
            else:require(val>=min(X[v][j],Y[v][j]+beta),'Descendant clipping bound')
    check_point(out,edges,A,k,m,T)
    return out

def main():
    output=ROOT/'CLIPPING_RESULTS.json';output.write_text('{"status":"RUNNING"}\n')
    rng=random.Random(6062328);cases=[]
    for k in range(2,7):
        for shape in ('path','star','binary'):
            edges=([(v,v+1)for v in range(k-1)]if shape=='path'else ([(0,v)for v in range(1,k)]if shape=='star'else [((v-1)//2,v)for v in range(1,k)]))
            m=3 if k==4 else 2
            A=[[[rng.randrange(4)for _ in range(m)]for _ in range(m)]for _ in edges]
            row=solve(edges,A,m,k);require(row is not None,'Tree unexpectedly empty')
            T=row['T'];x=list(map(F,row['x']));H=list(map(F,row['H']));require(all(h<=k*v for h,v in zip(H,x)),'Tree bound fails')
            p=[z3.Real(f'p{i}')for i in range(k*m)]
            raw=[v>=0 for v in p]+[z3.Sum(p)==T]+[z3.Sum([p[v*m+t[v]]for v in range(k)])>=sum(B[t[a]][t[b]]for (a,b),B in zip(edges,A))for t in product(range(m),repeat=k)]
            ideals=[]
            for root in range(k):
                s=z3.Solver();s.add(raw+[p[root*m]==z3.Q(H[root*m].numerator,H[root*m].denominator)]);require(s.check()==z3.sat,'Ideal witness missing')
                y=[frac(s.model().eval(v))for v in p];check_point(y,edges,A,k,m,T);ideals.append(y)
            clips=0;improvements=0
            for root,y in enumerate(ideals):
                for base in (x,ideals[(root+1)%k]):
                    alpha=base[root*m]
                    beta=(alpha+H[root*m]/k)/2 if H[root*m]>k*alpha else alpha+F(1,7)
                    out=clip(edges,A,k,m,T,base,y,root,beta);clips+=1
                    require(all(out[i]>=base[i]if base[i]<=alpha else out[i]>alpha for i in range(k*m)),'Lex threshold safety')
                    if H[root*m]>k*alpha:
                        require(out[root*m]>alpha and sorted(out)>sorted(base),'Claimed lex improvement fails');improvements+=1
            cases.append({'shape':shape,'k':k,'m':m,'edges':edges,'matrices':A,'T':T,'x':row['x'],'H':row['H'],'clip_checks':clips,'strict_lex_improvements':improvements})
    result={'status':'PASS','scope':'Finite exact tests of constructive lemma against raw full-team covers, not an exhaustive theorem','seed':6062328,'cases':cases,'clip_checks':sum(c['clip_checks']for c in cases),'strict_lex_improvements':sum(c['strict_lex_improvements']for c in cases)}
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in ('status','clip_checks','strict_lex_improvements')}))
if __name__=='__main__':main()
