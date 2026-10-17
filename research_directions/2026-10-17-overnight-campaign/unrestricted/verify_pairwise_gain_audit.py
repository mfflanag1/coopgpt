from fractions import Fraction as Q
from itertools import product
from collections import defaultdict

if not __debug__:raise RuntimeError('Assertions must remain enabled')

def add(a,b,scale=Q(1)):
    c=defaultdict(Q,a)
    for k,v in b.items():c[k]+=scale*v
    return {k:v for k,v in c.items() if v}

def marginal(z,i):
    other=[j for j in range(len(z)) if j!=i]
    result={};weight=Q(1,2**len(other))
    for mask in range(1<<len(other)):
        s=sum(z[j] for bit,j in enumerate(other) if mask>>bit&1)
        result=add(result,{s+z[i]:weight})
        result=add(result,{s:-weight})
    return result

def fold(poly):
    result={}
    for x,c in poly.items():
        if 0<=x<=2:continue
        if x<0:x,c=2-x,-c
        result=add(result,{x:c})
    return result

profiles=mergers=cancelling=0
for r in range(2,6):
    for z in product((-2,-1,1,2,3,4),repeat=r):
        if sum(z)!=2 or sum(-x for x in z if x<0)>2:continue
        profiles+=1
        B=[marginal(z,i) for i in range(r)]
        for i in range(r):
            for j in range(i+1,r):
                # Keep the merged coordinate even when zero, so the symbolic
                # Banzhaf identity is checked before any null omission.
                merged=(z[i]+z[j],)+tuple(z[k] for k in range(r) if k not in (i,j))
                assert add(B[i],B[j])==marginal(merged,0)
                assert sum(merged)==2 and sum(-x for x in merged if x<0)<=2
                if not merged[0]:
                    assert marginal(merged,0)=={}
                    cancelling+=1
                    if r==3:
                        assert sum(x!=0 for x in merged)==1
                        assert sum(-x for x in merged if x<0)==0
                mergers+=1
        if r==2:
            assert fold(B[0])==fold({z[0]:Q(1)})

z=(2,-1,-1,1,1)
B=[marginal(z,i) for i in range(5)]
raw={}
for i in range(3):raw=add(raw,B[i])
assert fold(raw)=={4:Q(-1,8)}

# Independently check the generous induction bounds, including cancellation.
E={1:Q(0),2:Q(0)}
for r in range(3,6):
    E[r]=Q(3,2)*(E[r-1]+1)
    assert E[r]==3*(Q(3,2)**(r-2)-1)
    if r>=4:assert 2<=E[r-1]+1
assert E[5]==Q(57,8)
assert 3*E[5]*2==Q(171,4)
assert Q(1,8)/(3*E[5]*2)==Q(1,342)

print({'status':'PASS','admissible_integer_profiles':profiles,
       'formal_Banzhaf_mergers':mergers,'zero_sum_mergers':cancelling,
       'coalition_potential_polynomial':{str(k):str(v) for k,v in fold(raw).items()},
       'lower_coefficient':str(Q(1,342)),
       'scope':'Independent exact polynomial cancellation and null-case recursion checks; analytic audit recorded separately.'})
