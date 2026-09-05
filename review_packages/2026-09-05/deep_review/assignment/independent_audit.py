"""Fresh 2026-09-05 review checks. Imports no package generators or selectors.
All accepting SMT answers must be exactly SAT/UNSAT; no float arithmetic.
"""
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
import json, random, time
import z3
OUT=Path(__file__).resolve().parent

def require(ok, label):
    if not ok: raise RuntimeError(label)
def Q(x):
    x=F(x);return z3.Q(x.numerator,x.denominator)
def rat(x):
    x=z3.simplify(x)
    if z3.is_int_value(x): return F(x.as_long())
    require(z3.is_rational_value(x),f'nonrational answer: {x}')
    return F(x.numerator_as_long(),x.denominator_as_long())
def query(cs, expected, label):
    s=z3.Solver();s.set(timeout=60000);s.add(*cs)
    status=s.check();require(status==expected,f'{label}: {status}')
    return status

def sorted_vars(p):
    # Fresh ranks constrained by a bijective permutation, independent of
    # the package's repeated floors and insertion-sort expression circuit.
    n=len(p); ranks=[z3.FreshReal('rank') for _ in p]
    perm=[z3.FreshInt('perm') for _ in p]
    cs=[z3.Distinct(*perm)]+[z3.And(i>=0,i<n) for i in perm]
    cs += [z3.Or(*[z3.And(perm[j]==i,ranks[j]==p[i]) for i in range(n)]) for j in range(n)]
    cs += [ranks[j]<=ranks[j+1] for j in range(n-1)]
    return ranks,cs

def full_selector(cs,p,up):
    ranks,sortcs=sorted_vars(p);o=z3.Optimize();o.set(timeout=60000);o.add(*(cs+sortcs))
    order=ranks if up else ranks[::-1]
    hs=[o.maximize(r) if up else o.minimize(r) for r in order]
    status=o.check();require(status==z3.sat,f'full rank optimization: {status}')
    values=[rat(h.value()) for h in hs]
    # Check both attained face and absence of a better sorted sequence with
    # a plain Solver, rather than accepting Optimize bounds on trust alone.
    face=cs+sortcs+[a==Q(b) for a,b in zip(order,values)]
    s=z3.Solver();s.set(timeout=60000);s.add(*face)
    require(s.check()==z3.sat,'rank optimum unattained')
    model=s.model();point=[rat(model.eval(a)) for a in p]
    prefix=[];better=[]
    for a,b in zip(order,values):
        better.append(z3.And(*prefix,a>Q(b) if up else a<Q(b)))
        prefix.append(a==Q(b))
    query(cs+sortcs+[z3.Or(*better)],z3.unsat,'strict rank improvement')
    query(face+[z3.Or(*[a!=Q(b) for a,b in zip(p,point)])],z3.unsat,'labeled selector uniqueness')
    return point

def graph(n,values):
    E=list(combinations(range(n),2));w=dict(zip(E,map(F,values)))
    @lru_cache(None)
    def worth(mask):
        if not mask:return F(0),0
        v=(mask&-mask).bit_length()-1;rest=mask&~(1<<v)
        candidates=[worth(rest)]
        for u in range(v+1,n):
            if rest>>u&1:
                t,k=worth(rest&~(1<<u));a=w[v,u]
                candidates.append((t+a,k+(a>0)))
        t=max(t for t,k in candidates)
        return t,min(k for s,k in candidates if s==t)
    T,k=worth((1<<n)-1)
    if not T:return {'n':n,'type':'zero'}
    p=[z3.FreshReal('g') for _ in range(n)]
    cs=[sum(p)==Q(T)]+[sum(p[i] for i in range(n) if mask>>i&1)>=Q(worth(mask)[0]) for mask in range(1,1<<n)]
    s=z3.Solver();s.set(timeout=60000);s.add(*cs);status=s.check()
    require(status in (z3.sat,z3.unsat),'graph feasibility unknown')
    if status==z3.unsat:return {'n':n,'type':'empty'}
    x=full_selector(cs,p,True);z=full_selector(cs,p,False)
    query(cs+[z3.Or(*[p[i]>Q(2*x[i]) for i in range(n)])],z3.unsat,'coordinate half violation')
    bound=F(0) if k==1 else F(k,k+1)
    distance=sum(z3.If(p[i]>=Q(x[i]),p[i]-Q(x[i]),Q(x[i])-p[i]) for i in range(n))
    query(cs+[a<=Q(max(z)) for a in p]+[distance>Q(T*bound)],z3.unsat,'some minimax violates bound')
    rho=sum(abs(a-b) for a,b in zip(x,z))/T
    return {'n':n,'type':'nonempty','k':k,'rho':str(rho),'fixed_zero_coordinates':sum(a==0 and b==0 for a,b in zip(x,z))}

def fresh_raw(L,R,shifted=True):
    color={};e={};match=[]
    def player(name,c):require(name not in color,'duplicate player');color[name]=c%3;return name
    G=[player(('G',i),i) for i in range(3)];pairs={}
    def team(vertices,weight,matched=False):
        require(len(set(vertices))==3 and {color[v] for v in vertices}=={0,1,2},'coloring')
        key=tuple(sorted(vertices,key=repr));require(key not in e,'duplicate triple');e[key]=weight
        if matched:match.append(key)
    for b in range(L+R+1):
        level=min(b,L);odd=level%2
        for i in range(3):
            u=player(('U',b,i),i+odd);v=player(('V',b,i),i+1-odd);d=player(('D',b,i),i+2)
            pairs[b,i]=(u,v,d);s=1+int(shifted and b==0)
            team((u,v,d),s,True);team((u,v,G[(i+2)%3]),s)
    if shifted:
        for i in range(3):team((pairs[0,i][0],G[(i+1)%3],G[(i+2)%3]),1)
    for level in range(1,L+1):
        for i in range(3):
            others=[j for j in range(3) if j!=i]
            team((pairs[level,i][0],*(pairs[level-1,j][1] for j in others)),2)
            team((pairs[level,i][1],*(pairs[level-1,j][0] for j in others)),3 if shifted and level==1 else 1)
    for b in range(L+1,L+R+1):
        for i in range(3):
            team((pairs[b,i][0],pairs[L,i][1],G[(i+2)%3]),1)
            team((pairs[b,i][1],pairs[L,i][0],G[(i+2)%3]),1)
    T=sum(e[a] for a in match);covered=[v for a in match for v in a]
    require(len(set(covered))==len(covered),'integral matching overlaps')
    P={name:z3.FreshReal('raw') for name in color};p=list(P.values())
    cs=[v>=0 for v in p]+[sum(p)==T]+[sum(P[v] for v in a)>=w for a,w in e.items()]
    den=2**L+(2 if shifted else 1);eta=F(2 if shifted else 1,den)
    X={n:F(0) for n in color};Z=X.copy();dummy=set(G)
    for (b,i),(u,v,d) in pairs.items():
        q=F(2**min(b,L),den);X[u]=q+int(shifted and b==0);X[v]=1-q
        Z[u]=F(int(shifted and b==0)) if shifted else X[u]
        Z[v]=F(1) if shifted else X[v];dummy.add(d)
    for point in [X,Z]:
        require(sum(point.values())==T,'cover sum')
        require(all(a>=0 for a in point.values()),'cover negative')
        require(all(sum(point[v] for v in a)>=w for a,w in e.items()),'cover violation')
    query(cs+[z3.Or(*[P[d]>0 for d in dummy])],z3.unsat,'positive dummy')
    active=set(color)-dummy
    query(cs+[P[n]>Q(eta) for n in active],z3.unsat,'better positive floor')
    query(cs+[P[n]>=Q(eta) for n in active]+[z3.Or(*[P[n]!=Q(X[n]) for n in color])],z3.unsat,'nonunique positive floor')
    M=max(Z.values());query(cs+[p<Q(M) for p in P.values()],z3.unsat,'better maximum')
    query(cs+[p<=Q(M) for p in P.values()]+[z3.Or(*[P[n]!=Q(Z[n]) for n in color])],z3.unsat,'nonunique minimax')
    # Full raw-core equality with unrestricted, possibly asymmetric roots.
    root=[P[pairs[0,i][0]]-int(shifted) for i in range(3)]
    q=root;form=[P[d]==0 for d in dummy]
    for b in range(L+1):
        for i in range(3):
            u,v,d=pairs[b,i];form += [P[u]==q[i]+int(shifted and b==0),P[v]==1-q[i],q[i]>=0,q[i]<=1]
        if b<L:q=[sum(q[j] for j in range(3) if j!=i) for i in range(3)]
    for b in range(L+1,L+R+1):
        for i in range(3):u,v,d=pairs[b,i];form += [P[u]==q[i],P[v]==1-q[i]]
    query(cs+[z3.Not(z3.And(*form))],z3.unsat,'raw outside parametrization')
    query(form+[z3.Not(z3.And(*cs))],z3.unsat,'parametrization outside raw')
    top=P[pairs[L,0][1]];query(cs+[top>1],z3.unsat,'ideal above one');require(Z[pairs[L,0][1]]==1 if shifted else True,'ideal witness')
    query(cs+[top==1],z3.sat,'ideal one feasible')
    if L>=2 and shifted:
        for c in range(3):
            tv=next(P[pairs[L,i][1]] for i in range(3) if color[pairs[L,i][1]]==c)
            ru=P[pairs[0,c][0]]
            query(cs+[tv==1,ru>1],z3.unsat,'sector exclusion')
            query(cs+[ru>1],z3.sat,'root improvement feasible')
    if shifted:
        A=[G[0],pairs[0,0][0]];B=[G[1],pairs[0,0][1]];C=[G[2],pairs[0,0][2]]
        mixed=sum((-1)**(3-a-b-c)*e.get(tuple(sorted([A[a],B[b],C[c]],key=repr)),0) for a,b,c in product(range(2),repeat=3))
        require(mixed==1,'mixed difference')
        require(len(e)==12*(L+R)+9,'sparsity')
    require(len(p)==9*(L+R)+12,'dimension count')
    rho=sum(abs(X[n]-Z[n]) for n in color)/T
    require(rho==(F(2*((R+2)*2**L-1),(2**L+2)*(L+R+2)) if shifted else 0),'rho')
    return dict(L=L,R=R,shifted=shifted,n=len(p),T=T,rho=str(rho),checks='matching/cover, both core inclusions, both singleton optimal faces, ideal payoff, exclusions')

def main():
    started=time.time();result={'z3':z3.get_version_string(),'graph':[],'triple':[]}
    # Full 3-vertex weights 0..3; 4-vertex weights 0..2. All players included.
    for n,radix in [(2,4),(3,4),(4,3)]:
        for vals in product(range(radix),repeat=n*(n-1)//2):result['graph'].append(graph(n,vals))
        print('graph complete',n,len(result['graph']),flush=True)
    rng=random.Random(918762)
    for n,count in [(5,30),(6,15)]:
        for _ in range(count):
            cover=[F(rng.randrange(5),rng.randrange(1,4)) for i in range(n)]
            if n%2:cover[-1]=F(0)
            vals=[(cover[i]+cover[j]) if j==i+1 and i%2==0 else max(F(0),cover[i]+cover[j]-F(rng.randrange(4),2)) for i,j in combinations(range(n),2)]
            result['graph'].append(graph(n,vals))
        print('rational graphs complete',n,flush=True)
    for L,R in [(1,0),(1,4),(2,0),(2,3),(3,1),(4,16),(5,7),(8,2),(12,0)]:
        result['triple'].append(fresh_raw(L,R,True));print('raw shifted',L,R,flush=True)
    for L in (0,1,2,4,7):result['triple'].append(fresh_raw(L,0,False));print('raw unshifted',L,flush=True)
    result['graph_summary']={k:sum(r['type']==k for r in result['graph']) for k in ('zero','empty','nonempty')}
    result['seconds']=time.time()-started
    result['status']='PASS';(OUT/'independent_audit_results.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',result['graph_summary'],result['seconds'],flush=True)
if __name__=='__main__':main()
