from fractions import Fraction as Q
from pathlib import Path
import random,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common_cap_arity_mechanism import Radical,parameter,coalition_payment,production,integer_root

def check(t,s):
    if not t:raise RuntimeError(s)
for k in range(1,9):
    for n in range(100):
        x=integer_root(n,k)
        check(x**k<=n<(x+1)**k,'integer-root certificate')
# Equality and sign routes that avoid unresolved two-root algebraic equalities.
check(Radical(Q(-2),Q(1),Q(8),3).compare(0)==0,'one cubic equality')
check(Radical(0,Q(1),Q(16),4).compare(Radical(0,Q(2),Q(1),4))==0,'two quartic equality')
rng=random.Random(1973);counts={'funding':0,'coverage':0,'TCWM':0,'lower_algebra':0}
for k in range(1,8):
    for trial in range(700):
        M=rng.randrange(1,22);d=1+k*M;C=parameter(M,k)
        outsider=[Q(rng.randrange(6),rng.choice((1,2,3))) for _ in range(d)]
        own=[Q(rng.randrange(6),rng.choice((1,2,3))) for _ in range(d)]
        restore=[Q(rng.randrange(4),rng.choice((1,2,3))) for _ in range(d)]
        low=[a+b for a,b in zip(outsider,own)]
        high=[a+b for a,b in zip(low,restore)]
        ownhi=[a+b for a,b in zip(own,restore)]
        check(coalition_payment(high,high,k).compare((C+k)*production(high,k))<=0,'funding')
        check(coalition_payment(high,ownhi,k).compare(production(ownhi,k))>=0,'coverage')
        check(coalition_payment(high,ownhi,k).compare(coalition_payment(low,own,k))>=0,'TCWM')
        for name in ('funding','coverage','TCWM'):counts[name]+=1
    # Exact general-arity product/finite-instance root of the recurrence bound.
    product=Q(1)
    for M in range(1,121):
        if M>1:product*=Q(k*M,k*(M-1)+1)
        for R in (1,2,3,7,17):
            bound=product*R/(R*R+product)
            check(bound==product/Q(R)*(1-bound/Q(R)),'finite lower rearrangement')
            counts['lower_algebra']+=1
out={'status':'PASS','checks':counts,'private_arities':list(range(1,8)),
     'random_branches_up_to':21,'arithmetic':'exact fractions and certified kth-root sign intervals',
     'limits':'No general two-radical equality oracle; unresolved comparisons raise. Finite checks supplement the analytic proof.'}
Path(__file__).with_name('COMMON_CAP_ARITY_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
