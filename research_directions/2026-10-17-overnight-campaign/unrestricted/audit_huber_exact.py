if not __debug__:
    raise RuntimeError('Run this exact checker without Python -O; assertions are required.')
"""Independent exact finite corroboration of the Huber-price candidate.

Uses no convex optimizer. It enumerates candidate tight-edge component formulas
and picks the exact minimum Huber objective among feasible candidates. The
candidate's component lemma proves exhaustive coverage, but this script computes
patterns independently. This is corroboration, not a universal proof verifier.
"""
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
from pathlib import Path
import random,json,time

def require(ok,msg):
    if not ok: raise RuntimeError(msg)
def h(t):return t*t if t<=Q(1,2) else t-Q(1,4)

@lru_cache(None)
def patterns(n,edges):
    out=set();noniso={v for e in edges for v in e}
    for mask in range(1<<len(edges)):
        adj=[[] for _ in range(n)]
        for j,(u,v) in enumerate(edges):
            if mask>>j&1:adj[u].append(v);adj[v].append(u)
        if any(not adj[v] for v in noniso):continue
        seen=set();blocks=[]
        for root in range(n):
            if root in seen or root not in noniso:continue
            col={root:0};stack=[root];seen.add(root);odd=False
            while stack:
                u=stack.pop()
                for v in adj[u]:
                    if v not in col:col[v]=1-col[u];seen.add(v);stack.append(v)
                    elif col[v]==col[u]:odd=True
            a=tuple(sorted(v for v in col if col[v]==0));b=tuple(sorted(v for v in col if col[v]))
            blocks.append(('half',tuple(sorted(col))) if odd else ('bi',a,b))
        out.add(tuple(sorted(blocks)))
    return tuple(out)

def optimizer_positive(c,edges):
    n=len(c);best=None;bestp=None;minimizers=set()
    for pat in patterns(n,tuple(edges)):
        candidates=[]
        for block in pat:
            if block[0]=='half':candidates.append([{v:Q(1,2) for v in block[1]}]);continue
            _,a,b=block;A=sum(c[v] for v in a);B=sum(c[v] for v in b)
            opts=[{v:Q(1,2) for v in a+b}]
            if A>=B:
                t=B/(2*A);opts.append({**{v:t for v in a},**{v:1-t for v in b}})
            if B>=A:
                t=A/(2*B);opts.append({**{v:1-t for v in a},**{v:t for v in b}})
            candidates.append(opts)
        for selection in product(*candidates):
            p=[Q(0)]*n
            for d in selection:
                for v,t in d.items():p[v]=t
            if any(p[u]+p[v]<1 for u,v in edges):continue
            val=sum(x*h(y) for x,y in zip(c,p))
            if best is None or val<best:best,bestp,minimizers=val,p,{tuple(p)}
            elif val==best:minimizers.add(tuple(p))
    require(bestp is not None,'no feasible candidate')
    require(len(minimizers)==1,'nonunique global optimum among exact patterns')
    return bestp

@lru_cache(None)
def optimizer(c,edges):
    positive=[i for i,x in enumerate(c) if x>0];pos={v:i for i,v in enumerate(positive)}
    induced=tuple((pos[u],pos[v]) for u,v in edges if u in pos and v in pos)
    pp=optimizer_positive(tuple(c[i] for i in positive),induced)
    p=[Q(1)]*len(c)
    for i,v in enumerate(positive):p[v]=pp[i]
    return tuple(p)

@lru_cache(None)
def half_covers(n,edges):
    return tuple(tuple(Q(x,2) for x in p) for p in product(range(3),repeat=n)
                 if all(p[u]+p[v]>=2 for u,v in edges))
def production(c,edges):
    return min(sum(x*y for x,y in zip(c,p)) for p in half_covers(len(c),edges))

def run():
    rng=random.Random(178733);start=time.time();tested=0;ic=0;budget=0
    graphs={
      'edge':(2,((0,1),)),
      'path5':(5,tuple((i,i+1) for i in range(4))),
      'cycle5':(5,tuple((i,(i+1)%5) for i in range(5))),
      'square_diagonal':(4,((0,1),(1,2),(2,3),(0,3),(0,2))),
      'K4':(4,tuple((i,j) for i in range(4) for j in range(i+1,4))),
      'K3_3':(6,tuple((i,j) for i in range(3) for j in range(3,6))),
      'disconnected':(5,((0,1),(2,3))),
    }
    bygraph={}
    for name,(n,edges) in graphs.items():
        count=0
        for rep in range(140):
            c=tuple(Q(rng.randrange(0,10)) for _ in range(n));p=optimizer(c,edges)
            T=production(c,edges);paid=sum(x*y for x,y in zip(c,p))
            require(all(p[u]+p[v]>=1 for u,v in edges),'dual infeasible')
            require(T<=paid<=Q(3,2)*T,'funding violation');budget+=1
            own=tuple(Q(rng.randrange(int(x)+1)) for x in c)
            y=sum(x*t for x,t in zip(own,p))
            for j in range(n):
                delta=Q(rng.randrange(1,6),rng.randrange(1,5));cc=list(c);bb=list(own);cc[j]+=delta;bb[j]+=delta
                qq=optimizer(tuple(cc),edges);yy=sum(x*t for x,t in zip(bb,qq))
                require(yy>=y,'mixed-owner increase reduced payment')
                # Independently check the other owner's coverage for a sample
                # two-owner partition, besides universal dual feasibility.
                require(y>=production(own,edges),'owner singleton not covered')
                other=tuple(c[i]-own[i] for i in range(n))
                require(paid-y>=production(other,edges),'other singleton not covered')
                ic+=1
            tested+=1;count+=1
        bygraph[name]={'profiles':count,'full_positive_patterns':len(patterns(n,edges))}
    return {'status':'PASS_EXACT_FINITE_CORROBORATION','seed':178733,'profiles':tested,'budget_checks':budget,
            'mixed_owner_coordinate_comparisons':ic,'graphs':bygraph,'seconds':time.time()-start,
            'scope':'Exact rational finite examples; universal theorem requires written proof. Half-integral cover enumeration uses the standard fractional vertex-cover integrality theorem.'}

if __name__=='__main__':
    result=run();s=json.dumps(result,indent=2);print(s);Path(__file__).with_suffix('.json').write_text(s+'\n')
