#!/usr/bin/env python3
"""Independent Fraction-only CEA audit, n=3/r=2, explicit refined regions.

No author implementation is imported. Provides all-real coverage/nonnegativity
dual certificates, exact funding identities, constant-gradient incentive tests,
and exhaustive distinct ternary-grid finite comparisons with actual owners.
"""
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib
import json

N=3
R=2
M=N*R
COALITIONS=[C for k in range(1,N+1) for C in combinations(range(N),k)]


def dot(a,b):return sum((x*y for x,y in zip(a,b)),Q(0))
def basis(k):return tuple(Q(j==k) for j in range(M))
def col(i,a):return R*i+a
def minus(v):return tuple(-x for x in v)


def waterfill(claims, estate):
    claims=tuple(claims)
    assert 0<=estate<=sum(claims)
    order=sorted(claims)
    consumed=Q(0)
    for k,cap in enumerate(order):
        level=(estate-consumed)/(len(claims)-k)
        if level<=cap:
            awards=tuple(min(c,level) for c in claims)
            assert level>=0 and sum(awards)==estate
            return awards,level
        consumed+=cap
    raise AssertionError('No water level')


def payment(b):
    estate=min(sum(b[col(i,a)] for i in range(N)) for a in range(R))
    pool=[waterfill([b[col(i,a)] for i in range(N)],estate)[0] for a in range(R)]
    return tuple(sum(pool[a][i] for a in range(R)) for i in range(N)),estate


def regions():
    result=[]
    counts=Counter()
    for h in range(R):
        a=1-h
        for mask in range((1<<N)-1):
            S={i for i in range(N) if mask>>i&1}
            q=N-len(S)
            total_h=tuple(Q(j%R==h) for j in range(M))
            total_a=tuple(Q(j%R==a) for j in range(M))
            L=tuple((total_h[j]-Q(j//R in S and j%R==a))/q for j in range(M))
            H=[];g=[]
            for j in range(M):
                H.extend([basis(j),minus(basis(j))]);g.extend([Q(1),Q(0)])
            H.append(tuple(x-y for x,y in zip(total_h,total_a)));g.append(Q(0))
            level_row=len(H)
            H.append(minus(L));g.append(Q(0))
            for i in range(N):
                normal=tuple(x-y for x,y in zip(basis(col(i,a)),L))
                H.append(normal if i in S else minus(normal));g.append(Q(0))
            gradients=[]
            nonnegative_certificates=[]
            for i in range(N):
                other=basis(col(i,a)) if i in S else L
                gradient=tuple(x+y for x,y in zip(basis(col(i,h)),other))
                gradients.append(gradient)
                u=[Q(0)]*len(H)
                u[2*col(i,h)+1]=1
                u[2*col(i,a)+1 if i in S else level_row]+=1
                assert all(sum(u[l]*H[l][j] for l in range(len(H)))==-gradient[j] for j in range(M))
                assert dot(u,g)==0 and min(u)>=0
                nonnegative_certificates.append(u)
                counts['all_real_nonnegative_duals']+=1
            assert all(sum(gradients[i][j] for i in range(N))==2*total_h[j] for j in range(M))
            counts['all_real_factor2_funding_identities']+=1
            # A strict rational interior witness proves this is a full-dimensional cell.
            level=Q(1,5)
            E=len(S)*Q(1,10)+q*level
            interior=[Q(0)]*M
            for i in range(N):
                interior[col(i,h)]=E/N
                interior[col(i,a)]=Q(1,10) if i in S else Q(3,10)
            assert dot(L,interior)==level
            assert all(dot(row,interior)<bound for row,bound in zip(H,g))
            coverage=[]
            for C in COALITIONS:
                coalition=set(C)
                ac=tuple(sum(gradients[i][j] for i in C) for j in range(M))
                u=[Q(0)]*len(H)
                for i in C:
                    u[2*col(i,a)+1 if i in S else level_row]+=1
                p=[Q(a0==h) for a0 in range(R)]
                Sctp=tuple(p[j%R] if j//R in coalition else Q(0) for j in range(M))
                assert all(sum(u[l]*H[l][j] for l in range(len(H)))-Sctp[j]==-ac[j] for j in range(M))
                assert sum(p)>=1 and min(p)>=0 and min(u)>=0 and dot(u,g)==0
                coverage.append({'coalition':C,'u':u,'p':p})
                counts['all_real_coverage_duals']+=1
                # Expand all actual coalitions directly; no order-statistic code.
                for j in range(M):
                    if j//R in coalition:
                        assert ac[j]>=0
                        counts['TCWM_coordinate_tests']+=1
                for owner0,owner1 in product(C,repeat=2):
                    assert ac[col(owner0,0)]+ac[col(owner1,1)]>=1
                    counts['OUT_assignment_tests']+=1
            result.append({'bottleneck':h,'saturated_owners':sorted(S),'H':H,'g':g,
                           'water_level_coefficients':L,'gradients':gradients,
                           'strict_interior_witness':interior,
                           'nonnegativity_duals':nonnegative_certificates,
                           'coverage_duals':coverage})
    assert len(result)==14
    return result,counts


def main():
    cells,counts=regions()
    alphabet=(Q(0),Q(1,2),Q(1))
    profiles=list(product(alphabet,repeat=M))
    cache={b:payment(b) for b in profiles}
    for b in profiles:
        y,E=cache[b]
        assert min(y)>=0 and sum(y)==2*E
        if E==0:assert y==(0,0,0)
        counts['profiles']+=1
        counts['zero_output_profiles']+=int(E==0)
        membership=0
        for cell in cells:
            if all(dot(row,b)<=bound for row,bound in zip(cell['H'],cell['g'])):
                membership+=1
                assert tuple(dot(a,b) for a in cell['gradients'])==y
                counts['region_formula_checks']+=1
        assert membership>0
        counts['profiles_on_overlaps']+=int(membership>1)
        for C in COALITIONS:
            worth=min(sum(b[col(i,a)] for i in C) for a in range(R))
            assert sum(y[i] for i in C)>=worth
            counts['finite_coverage_checks']+=1
            choices=[tuple(v for v in alphabet if v>=b[j]) if j//R in C else (b[j],)
                     for j in range(M)]
            for high in product(*choices):
                yp,Ep=cache[high]
                gain=sum(yp[i]-y[i] for i in C)
                outside=min(sum(high[col(i,a)]-b[col(i,a)] for i in C) for a in range(R))
                assert gain>=outside
                # Stronger finite consequence of the same bottleneck segmentation.
                assert gain>=Ep-E
                counts['finite_OUT_comparisons']+=1
                counts['positive_outside_worth']+=int(outside>0)
                counts['comparisons_with_unchanged_members']+=int(any(
                    all(high[col(i,a)]==b[col(i,a)] for a in range(R)) for i in C))
    old,lo=waterfill((Q(1),Q(10),Q(10)),Q(6))
    new,hi=waterfill((Q(10),Q(10),Q(10)),Q(7))
    assert hi<lo and new[0]>old[0]
    out={'status':'PASS','timestamp_utc':datetime.now(timezone.utc).isoformat(),
         'scope':'Single minimum, three actual mixed owners/two resource pools; finite rational refined regions and exact ternary-grid endpoint audit.',
         'checks':dict(counts),'cells':cells,
         'decreasing_level_fixture':{'old_claims':[1,10,10],'new_claims':[10,10,10],
             'old_estate':6,'new_estate':7,'old_awards':old,'new_awards':new,
             'old_level':lo,'new_level':hi},
         'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    encode=lambda v:str(v) if isinstance(v,Q) else (_ for _ in ()).throw(TypeError(type(v).__name__))
    output=Path(__file__).with_suffix('.json')
    output.write_text(json.dumps(out,default=encode,indent=2)+'\n')
    print(json.dumps({'status':'PASS','checks':dict(counts),'output':str(output)}))


if __name__=='__main__':main()
