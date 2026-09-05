"""Independent arrangement count in five explicit efficiency coordinates.
Every outside vertex is dominated by the paper's constructive seven-coalition
proof, independently of the package's interval-based dominator constructor.
"""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import json, math
OUT=Path(__file__).parent
A=tuple(map(F,(1,1,0,1,3,0))); B=tuple(map(F,(2,0,1,0,1,2))); d=tuple(b-a for a,b in zip(A,B))
def check(x,msg):
    if not x: raise RuntimeError(msg)
def worth(S):return min(sum(A[i] for i in S),sum(B[i] for i in S))
ss=[s for k in range(7) for s in combinations(range(6),k)]
def plane(row,rhs):
    # Restrict to y6=6-y1-...-y5 before deduplication.
    v=[row[i]-row[5] for i in range(5)]+[rhs-6*row[5]]
    scale=next(t for t in v[:5] if t)
    return tuple(t/scale for t in v)
planes=set()
for i in range(6):
    row=[F(i==j) for j in range(6)]
    for bound in (A[i],B[i],min(A[i],B[i])):planes.add(plane(row,bound))
for i in range(6):
    for j in range(6):
        if d[i]>0>d[j]:
            row=[F(0)]*6;row[i]=d[j];row[j]=-d[i]
            planes.add(plane(row,d[j]*A[i]-d[i]*A[j]))
planes=sorted(planes)
def solve(rows):
    # Forward elimination with deferred back substitution (no package solver).
    rows=[list(r) for r in rows]
    for col in range(5):
        pivot=next((j for j in range(col,5) if rows[j][col]),None)
        if pivot is None:return None
        rows[col],rows[pivot]=rows[pivot],rows[col]
        for j in range(col+1,5):
            if rows[j][col]:
                m=rows[j][col]/rows[col][col]
                for k in range(col,6):rows[j][k]-=m*rows[col][k]
    x=[F(0)]*5
    for col in reversed(range(5)):
        x[col]=(rows[col][5]-sum(rows[col][j]*x[j] for j in range(col+1,5)))/rows[col][col]
    return tuple(x+[6-sum(x)])
pts=set(); nonsingular=0
for basis in combinations(planes,5):
    p=solve(basis)
    if p is not None:pts.add(p);nonsingular+=1
imputations=[y for y in pts if all(y[i]>=min(A[i],B[i]) for i in range(6))]
core=[y for y in imputations if all(sum(y[i] for i in s)>=worth(s) for s in ss)]
cert=[]
pairs=[(0,1),(2,3),(4,5),(1,2),(0,3)]
for y in sorted(set(imputations)-set(core)):
    pair=next((p for p in pairs if sum(y[i] for i in p)<worth(p)),None)
    if pair:
        eps=worth(pair)-sum(y[i] for i in pair)
        i=pair[0];r=(y[i]+eps/2-A[i])/d[i];s=pair
    else:
        t=y[0]-1;u=y[5]
        check(y==(1+t,1-t,t,1-t,3-u,u),'pair avoidance reduction failed')
        check(u!=2*t,'outside core discrepancy zero')
        r=(t+u/2)/2;s=(0,2,4) if u>2*t else (1,3,5)
    x=tuple(A[i]+r*d[i] for i in range(6))
    check(0<=r<=1 and sum(x)==6 and all(sum(x[i] for i in t)>=worth(t) for t in ss),'constructed point not core')
    check(sum(x[i] for i in s)<=worth(s) and all(x[i]>y[i] for i in s),'not domination')
    cert.append({'y':list(map(str,y)),'coalition':[i+1 for i in s],'r':str(r),'x':list(map(str,x))})
res={'distinct_planes_in_efficiency_space':len(planes),'bases':math.comb(len(planes),5),'nonsingular_bases':nonsingular,'distinct_intersections':len(pts),'imputations':len(imputations),'core_vertices':list(map(lambda p:list(map(str,p)),sorted(core))),'outside_dominated':len(cert),'certificates':cert}
check((len(planes),nonsingular,len(pts),len(imputations),len(core),len(cert))==(21,8264,230,104,2,102),'reported counts mismatch')
(OUT/'arrangement_independent_results.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps({k:v for k,v in res.items() if k!='certificates'},indent=2))
