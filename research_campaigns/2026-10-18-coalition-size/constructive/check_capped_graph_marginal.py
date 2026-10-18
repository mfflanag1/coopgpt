from fractions import Fraction as Q
from itertools import combinations
from random import Random
from pathlib import Path
import json

OUT=Path(__file__).with_suffix('.json')

def val(rows):
    return min(rows[0], min(rows[1], rows[2])+min(rows[3], rows[4]))

def pays(bs,s):
    n=len(bs); p=Q(1,s); P=sum(b[0] for b in bs)
    totals=[sum(b[k] for b in bs) for k in range(5)]
    G=min(totals[1],totals[2])+min(totals[3],totals[4])
    h=min(Q(1),Q(G,P)) if P else Q(1)
    y=[]
    for i in range(n):
        others=[j for j in range(n) if j!=i]; u=Q(0)
        for mask in range(1<<(n-1)):
            inds=[others[k] for k in range(n-1) if mask>>k&1]
            k=len(inds); prob=p**k*(1-p)**(n-1-k)
            c=[sum(bs[j][a] for j in inds) for a in range(5)]; c[0]=P
            d=[c[a]+(bs[i][a] if a else 0) for a in range(5)]
            u+=prob*(val(d)-val(c))
        y.append(bs[i][0]*h+u/p)
    return y

checks={'coverage':0,'single_owner_restorations':0,'protected_coalition_comparisons':0,
        'funding':0,'explicit_star_values':0,'coefficient_signs':0}
rng=Random(320261018)
for trial in range(30):
    bs=[[rng.randrange(3) for _ in range(5)] for _ in range(4)]
    if trial==0: bs=[[0]*5 for _ in range(4)]
    for s in range(1,5):
        y=pays(bs,s); V=val([sum(b[a] for b in bs) for a in range(5)])
        assert all(x>=0 for x in y)
        assert sum(y)<=(1+2*s*s)*V
        checks['funding']+=1
        for mask in range(16):
            inds=[j for j in range(4) if mask>>j&1]
            v=val([sum(bs[j][a] for j in inds) for a in range(5)])
            assert sum(y[j] for j in inds)>=v
            checks['coverage']+=1
        for j in range(4):
            for a in range(5):
                hi=[b[:] for b in bs]; hi[j][a]+=1; z=pays(hi,s)
                checks['single_owner_restorations']+=1
                for mask in range(16):
                    if mask>>j&1 and mask.bit_count()<=s:
                        assert sum(z[i]-y[i] for i in range(4) if mask>>i&1)>=0
                        checks['protected_coalition_comparisons']+=1

# Direct enumerate disjoint-edge samples; the cap-only owner has no effect.
for N in range(1,5):
    for s in range(2,6):
        p=Q(1,s); n=2*N
        for i in range(n):
            others=[j for j in range(n) if j!=i]; u=Q(0)
            for mask in range(1<<(n-1)):
                S={others[k] for k in range(n-1) if mask>>k&1}; k=len(S)
                def g(T): return int(any(2*e in T and 2*e+1 in T for e in range(N)))
                u+=p**k*(1-p)**(n-1-k)*(g(S|{i})-g(S))
            assert u==p*(1-p*p)**(N-1)
            checks['explicit_star_values']+=1

for n in range(2,9):
    for s in range(2,n+1):
        p=Q(1,s)
        for c in range(1,s+1):
            for k in range(c):
                assert (1-p*c+k)/(1-p)>=0
                checks['coefficient_signs']+=1

result={'status':'PASS','checks':checks,
 'exact_factors_N_s_squared':{str(s):str(1+2*s*s*(1-Q(1,s*s))**(s*s-1)) for s in range(2,7)},
 'scope':'Finite exact checks supplement the all-real proof; no subquadratic or full-OUT claim.'}
OUT.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
