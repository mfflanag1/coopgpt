"""Standard-library verifier, independently builds all certificate coefficients."""
import json
from fractions import Fraction as F
from itertools import product, combinations
from pathlib import Path


def require(ok, why):
    if not ok: raise ValueError(why)


def linear_solve(rows):
    a=[list(map(F,row))for row in rows];n=len(a)
    for col in range(n):
        pivot=next((i for i in range(col,n)if a[i][col]),None)
        if pivot is None:return None
        a[col],a[pivot]=a[pivot],a[col]
        den=a[col][col];a[col]=[v/den for v in a[col]]
        for i in range(n):
            if i==col:continue
            factor=a[i][col];a[i]=[v-factor*w for v,w in zip(a[i],a[col])]
    return [row[-1]for row in a]


def packing_vertices(teams):
    out={tuple(F(0)for _ in teams)};bases=0
    for size in range(1,7):
        for support in combinations(range(8),size):
            for tight in combinations(range(6),size):
                bases+=1
                rows=[[int(teams[e][i//2]==i%2)for e in support]+[1]for i in tight]
                sol=linear_solve(rows)
                if sol is None or any(v<0 for v in sol):continue
                lam=[F(0)]*8
                for e,v in zip(support,sol):lam[e]=v
                if any(sum(lam[e]for e,t in enumerate(teams)if t[i//2]==i%2)>1 for i in range(6)):continue
                out.add(tuple(lam))
    return out,bases


def check(row,teams):
    lam=list(map(F,row['packing']));du=list(map(F,row['inequality_dual']));de=list(map(F,row['equality_dual']))
    require(len(lam)==8 and len(du)==48 and len(de)==7,'dimensions')
    require(all(v<=0 for v in du) and sum(de)>=-1,'dual sign/value')
    obj=[F(0)]*48;lhs=[F(0)]*48
    for e,(a,b,c) in enumerate(teams):
        for p in [2*a+b,4+2*a+c,8+2*b+c]:obj[p]-=lam[e]
    for i in range(6):
        degree=sum(lam[e]for e,t in enumerate(teams)if t[i//2]==i%2)
        obj[12+6*i+i]=-(1-degree)/3
        for e,(a,b,c) in enumerate(teams):
            coeff=du[8*i+e]
            for p in [2*a+b,4+2*a+c,8+2*b+c]:lhs[p]+=coeff
            for p in [a,2+b,4+c]:lhs[12+6*i+p]-=coeff
        for j in range(6):lhs[12+6*i+j]+=de[i+1]
    for j in range(2):
        for p in [3*j,4+3*j,8+3*j]:lhs[p]+=de[0]
    require(all(a<=b for a,b in zip(lhs,obj)),'dual coefficient comparison')


def run():
    data=json.loads(Path(__file__).with_name('TWO_LABEL_CERTIFICATES.json').read_text())
    teams=list(product(range(2),repeat=3));vertices,bases=packing_vertices(teams)
    rows=data['certificates'];seen={tuple(map(F,row['packing']))for row in rows}
    require(seen==vertices and len(rows)==len(vertices),'incomplete or repeated vertex coverage')
    for row in rows:check(row,teams)
    # A false dual objective must be rejected, even if metadata says PASS.
    bad=dict(rows[0]);bad['equality_dual']=['-2']+['0']*6
    try:check(bad,teams)
    except ValueError:pass
    else:raise ValueError('negative control accepted')
    print(json.dumps({'status':'PASS','independent_standard_library_verifier':True,'bases':bases,'vertices':len(vertices),'fractional_vertices':sum(any(v.denominator>1 for v in p)for p in vertices),'negative_controls':1}))


if __name__=='__main__':run()
