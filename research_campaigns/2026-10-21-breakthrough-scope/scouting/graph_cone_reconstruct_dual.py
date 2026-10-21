"""Reconstruct selected cone-LP rows and a nonnegative dual exactly."""
from fractions import Fraction as Q
from functools import lru_cache
import itertools,json,sys
from pathlib import Path

source=Path(sys.argv[1]);d=json.loads(source.read_text())
Cs=[tuple(Q(x).limit_denominator(1000000) for x in c) for c in d['shapes']]
normals=[(1,1,0),(1,-1,0),(1,0,1),(1,0,-1)]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def value(c):return c[0]-max(abs(c[1]),c[2])
def solve(mat,n):
    mat=[list(row) for row in mat];ri=0;piv=[]
    for c in range(n):
        pi=next((k for k in range(ri,len(mat)) if mat[k][c]),None)
        if pi is None:continue
        mat[ri],mat[pi]=mat[pi],mat[ri];v=mat[ri][c];mat[ri]=[x/v for x in mat[ri]]
        for k in range(len(mat)):
            if k!=ri and mat[k][c]:
                v=mat[k][c];mat[k]=[x-v*y for x,y in zip(mat[k],mat[ri])]
        piv.append(c);ri+=1
    assert all(any(row[:-1]) or not row[-1] for row in mat)
    x=[Q(0)]*n
    for r,c in enumerate(piv):x[c]=mat[r][-1]
    return x,len(piv)
@lru_cache(None)
def vertices(C):
    A=normals+[tuple(-x for x in r) for r in normals]
    rhs=[Q(0)]*4+[-dot(r,C) for r in normals]
    out=set()
    for ids in itertools.combinations(range(8),3):
        try:v,rank=solve([list(map(Q,A[i]))+[rhs[i]] for i in ids],3)
        except AssertionError:continue
        if rank==3 and all(dot(r,v)>=b for r,b in zip(A,rhs)):out.add(tuple(v))
    return tuple(out)
rebuilt=[];budget_index=3*len(Cs)
for raw in d['dual']:
    m=raw['meta'];kind,j=m[:2];row={};rhs=Q(0)
    def add(k,x):row[k]=row.get(k,Q(0))+x
    if kind=='coverage_reserve':row={3*j:Q(-1)};rhs=Q(-1)
    elif kind=='coverage_middle':row={3*j:Q(-1),3*j+2:Q(1)};rhs=Q(-1)
    elif kind=='ray':row={3*j:Q(-1),3*j+1:Q(m[2]),3*j+2:Q(m[3])}
    elif kind=='reflection':
        sign=Q(raw['coeffs'][str(3*j+1)])
        assert sign in (Q(-1),Q(1)) and Cs[j][1]==0
        row={3*j+1:sign}
    elif kind=='budget':row={3*j+k:x for k,x in enumerate(Cs[j])};row[budget_index]=-value(Cs[j])
    elif kind=='restore':
        _,hi,lo,lamfloat,Afloat,signs,gain=m
        C=Cs[hi];L=tuple(Q(s)*x for s,x in zip(signs,Cs[lo]))
        maxscale=min(dot(r,C)/dot(r,L) for r in normals if dot(r,L)>0)
        frac=Q(1,2) if abs(lamfloat/float(maxscale)-.5)<1e-6 else Q(1)
        lam=maxscale*frac
        candidates=[tuple(lam*x for x in v) for v in vertices(L)]
        A=min(candidates,key=lambda a:max(abs(float(x)-y) for x,y in zip(a,Afloat)))
        assert max(abs(float(x)-y) for x,y in zip(A,Afloat))<1e-8
        D=tuple(x-lam*y for x,y in zip(C,L))
        for k in range(3):add(3*lo+k,Q(signs[k])*A[k]);add(3*hi+k,-A[k]-D[k])
        rhs=-value(D) if d['contract']=='OUT' else Q(0)
    else:raise ValueError(kind)
    row={k:v for k,v in row.items() if v}
    assert abs(float(rhs)-raw['rhs'])<1e-8
    for k in set(row)|set(map(int,raw['coeffs'])):
        assert abs(float(row.get(k,0))-raw['coeffs'].get(str(k),0))<1e-8
    rebuilt.append((row,rhs,m))
cols=sorted(set().union(*(row for row,_,_ in rebuilt)))
mat=[[row.get(j,Q(0)) for row,_,_ in rebuilt]+[Q(-1 if j==budget_index else 0)] for j in cols]
weights,rank=solve(mat,len(rebuilt));assert all(w>=0 for w in weights)
for j in cols:assert sum(w*row.get(j,0) for w,(row,_,_) in zip(weights,rebuilt))==(-1 if j==budget_index else 0)
bound=-sum(w*b for w,(_,b,_) in zip(weights,rebuilt))
report={'scope':'exact finite lower for homogeneous common-cone-price architecture; canonical mechanism frontier unchanged','source':str(source),'bound':str(bound),'decimal':float(bound),'rank':rank,'rows':[{'coefficients':{str(k):str(v) for k,v in row.items()},'rhs':str(b),'weight':str(w),'meta':m} for w,(row,b,m) in zip(weights,rebuilt)]}
output=source.with_name(source.stem+'_exact.json');output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
