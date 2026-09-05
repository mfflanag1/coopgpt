#!/usr/bin/env python3
"""Independent bounded falsification of the released asymptotic argument.
No imports from the package verifier. Every scientific gate raises explicitly.
"""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json, time, z3
OUT=Path(__file__).resolve().parent
records={"runtime":{"z3":z3.get_version_string()},"scope":"Independent finite checks, not an all-parameter formal proof"}
def gate(test,msg):
    if not test: raise RuntimeError(msg)
def zv(v):
    v=Q(v); return z3.Q(v.numerator,v.denominator)
def verdict(cs):
    s=z3.Solver();s.set(timeout=60000);s.add(cs); v=s.check()
    gate(v != z3.unknown, 'UNKNOWN: '+s.reason_unknown())
    return str(v),s

def gauss(A):
    n=len(A); B=[[Q(a) for a in row]+[Q(1)] for row in A]; det=Q(1)
    for k in range(n):
        piv=next((i for i in range(k,n) if B[i][k]),None)
        if piv is None:return None,Q(0)
        if piv!=k:B[piv],B[k]=B[k],B[piv];det=-det
        c=B[k][k];det*=c;B[k]=[a/c for a in B[k]]
        for i in range(n):
            if i!=k and B[i][k]:
                c=B[i][k]; B[i]=[a-c*b for a,b in zip(B[i],B[k])]
    return [row[-1] for row in B],det

def raw_core(U,V,prefix):
    n=len(U); y=[z3.Real(f'{prefix}_{i}') for i in range(n)]
    vals=[];cs=[]
    for membership in product([0,1],repeat=n):
        ix=[i for i,bit in enumerate(membership) if bit]
        bound=min(sum((U[i] for i in ix),Q(0)),sum((V[i] for i in ix),Q(0)))
        expr=z3.Sum([y[i] for i in ix]) if ix else zv(0)
        cs.append(expr==zv(bound) if len(ix)==n else expr>=zv(bound))
        vals.append((ix,bound))
    for G in (U,V):
        gate(all(sum((G[i] for i in ix),Q(0))>=bound for ix,bound in vals),'infeasible generator')
    return y,cs

def segment_check(d,r,prefix):
    H=Q(r)-sum(d);U=[H]+d+[Q(0)]*r;V=[Q(0)]*(len(d)+1)+[Q(1)]*r
    y,cs=raw_core(U,V,prefix);t=1-y[-1]
    equations=[yi==zv(vi)+t*zv(ui-vi) for yi,ui,vi in zip(y,U,V)]
    v,_=verdict(cs+[z3.Or(t<0,t>1,z3.Not(z3.And(equations)))])
    gate(v=='unsat','whole-core counterexample: '+prefix)
    alpha=min(d); ta=1/(1+alpha); tb=1/(1+H)
    X=[ta*u+(1-ta)*v for u,v in zip(U,V)];Z=[tb*u+(1-tb)*v for u,v in zip(U,V)]
    for P,isfloor in [(X,True),(Z,False)]:
        level=min(P) if isfloor else max(P)
        face=[yi>=zv(level) if isfloor else yi<=zv(level) for yi in y]
        v,_=verdict(cs+face+[z3.Or([yi!=zv(pi) for yi,pi in zip(y,P)])])
        gate(v=='unsat','nonunique claimed optimal face: '+prefix)
        strict=[yi>zv(level) if isfloor else yi<zv(level) for yi in y]
        v,_=verdict(cs+strict);gate(v=='unsat','strictly better objective: '+prefix)
    distance=sum(abs(x-z) for x,z in zip(X,Z))/r
    gate(2-distance==2*(alpha/(1+alpha)+1/(1+H)),'deficit mismatch')
    return {'p':len(d),'r':r,'H':str(H),'alpha':str(alpha),'rho':str(distance),'coalitions':2**len(U)}

start=time.time()
# An exploratory run toward n=32 timed out in the piecewise minimum query.
# This retained bounded version makes no claim beyond n=10.
# For a distinct opposing pair, permute the two directional witnesses to 0 and 1.
# Only their necessary inequalities are assumed, not any generator construction.
rows=[]
for n in range(2,11):
    x=[z3.Real(f'x{n}_{i}') for i in range(n)];z=[z3.Real(f'z{n}_{i}') for i in range(n)]
    cs=[v>=0 for v in x+z]+[z3.Sum(x)==1,z3.Sum(z)==1]
    cs += [x[0]<=v for v in x]+[z[1]>=v for v in z]+[z[0]<=x[0],x[1]>=z[1],x[0]<z[1]]
    overlap=z3.Sum([z3.If(a<=b,a,b) for a,b in zip(x,z)])
    cs += [overlap < zv(Q(1,n-1))]
    ans,_=verdict(cs);gate(ans=='unsat',f'overlap violation at n={n}')
    rows.append({'n':n,'violation_query':ans})
    print('Direct overlap n='+str(n)+': '+ans,flush=True)
records['overlap_witness_queries']=rows
print('Independent overlap falsification n=2..10: UNSAT',flush=True)

def sorted_expr(xs):
    out=[]
    for x in xs:
        carry=x; result=[]
        for a in out:
            result.append(z3.If(carry<=a,carry,a));carry=z3.If(carry<=a,a,carry)
        out=result+[carry]
    return out
rows=[]
for n in range(2,6):
    x=[z3.Real(f'ux{n}_{i}') for i in range(n)];z=[z3.Real(f'uz{n}_{i}') for i in range(n)]
    sz=sorted_expr(z); sm=sorted_expr([(a+b)/2 for a,b in zip(x,z)])
    cs=[x[i]<=x[i+1] for i in range(n-1)]+[a==b for a,b in zip(x,sz)]+[z3.Or([a!=b for a,b in zip(x,z)])]
    lex_better=z3.Or([z3.And([sm[j]==x[j] for j in range(i)]+[sm[i]>x[i]]) for i in range(n)])
    ans,_=verdict(cs+[z3.Not(lex_better)]);gate(ans=='unsat','midpoint uniqueness counterexample')
    rows.append({'n':n,'failure_query':ans})
records['sorted_midpoint_uniqueness_queries']=rows
print('Independent sorted midpoint uniqueness n=2..5: UNSAT',flush=True)

# All 0/1 square matrices through p=4, not just Fibonacci incidence matrices.
# For p=4, identical sorted d define the same game up to donor permutation,
# so one raw-core check per distinct sorted d suffices for this finite census.
rows=[];stats=[]
for p in range(1,5):
    num=0;positive=0;seen=set()
    for bits in product([0,1],repeat=p*p):
        A=[list(bits[i*p:(i+1)*p]) for i in range(p)];d,det=gauss(A)
        if d is None:continue
        num+=1
        if min(d)<=0:continue
        positive+=1
        key=tuple(sorted(d))
        if p==4 and key in seen:continue
        seen.add(key)
        r=(sum(d).numerator+sum(d).denominator-1)//sum(d).denominator+1
        rec=segment_check(d,r,f'A{p}_{positive}');rec.update({'A':A,'d':list(map(str,d)),'det':str(det)})
        rows.append(rec)
    stats.append({'p':p,'matrices':2**(p*p),'invertible':num,'positive_inverse_one':positive,'distinct_sorted_positive_solutions':len(seen)})
    print('All matrices p='+str(p)+': '+str(stats[-1]),flush=True)
records['general_matrix_stats']=stats;records['general_matrix_core_checks']=rows

# Independently formed Fibonacci incidence matrices and exact elimination.
fib=[0,1]
for i in range(2,1000):fib.append(fib[-1]+fib[-2])
rows=[]
for m in range(2,41):
    A=[]
    for i in range(m):
        row=[0]*(2*m);row[i]=row[m+i]=1;A.append(row)
    for i in range(m-2):
        row=[0]*(2*m);row[i+1]=row[i+2]=row[m+i]=1;A.append(row)
    row=[0]*(2*m);row[m-2]=row[2*m-1]=1;A.append(row)
    row=[0]*(2*m);row[0]=row[1]=1;A.append(row)
    d,det=gauss(A);F=fib[m+1]
    target=[Q(fib[m-i],F) for i in range(m)];target += [1-a for a in target]
    gate(d==target and abs(det)==F,'Fibonacci elimination failed')
    rows.append({'m':m,'determinant':str(det),'denominator':F,'minimum':str(min(d))})
records['fibonacci_exact_elimination']=rows
print('Independent Fibonacci elimination m=2..40: exact expected solution and |det|=F',flush=True)

# Missing small regimes and unequal H, checked with direct coalition enumerator.
rows=[]
for m,r in [(2,5),(2,6),(3,6),(4,6)]:
    F=fib[m+1];a=[Q(fib[m-i],F) for i in range(m)];d=a+[1-v for v in a]
    rows.append(dict(m=m,**segment_check(d,r,f'fib_{m}_{r}')))
records['additional_fibonacci_core_checks']=rows
print('Independent extra raw coalition cases passed',flush=True)

# Exact discontinuity endpoints suffice to challenge the stated all-n choice.
rows=[]
for L in range(7,129):
    low=max(128,2**(L-1)+1);high=2**L
    for n in sorted({low,high}):
        gate((n-1).bit_length()==L,'wrong logarithm interval')
        m=4*L;r=n-8*L-1
        gate(r>=m+1 and fib[m+1]>=n*n,'all-n admissibility failed')
        true=Q(2,fib[m+1]+1)+Q(2,r-m+1)
        upper=Q(2,n-12*L)+Q(2,n*n+1)
        gate(Q(2,n-1)<=true<=upper,'finite inequality mismatch')
    rows.append({'L':L,'least_n':str(low),'largest_n':str(high),'least_admissibility_slack':str(low-12*L-2)})
records['logarithm_boundary_checks']=rows
rows=[]
for n in [128,129,256,1000,10**6,10**12,10**30,10**60]:
    m=next(m for m in range(2,len(fib)-1) if fib[m+1]>=n*n)
    F=fib[m+1];r=n-2*m-1
    gate(r>=m+1 and n*n<=F<2*n*n,'integer regime failed')
    gate(r*F<2*n**3,'total bound failed')
    rows.append({'n':str(n),'m':m,'F':str(F),'scaled_total':str(r*F),'max_coordinate_bits':((r-m)*F).bit_length()})
records['integer_representation_checks']=rows
records['elapsed_seconds']=time.time()-start;records['status']='PASS'
(OUT/'independent_results.json').write_text(json.dumps(records,indent=2)+'\n')
print('ALL INDEPENDENT CHECKS PASS; seconds='+str(records['elapsed_seconds']),flush=True)
