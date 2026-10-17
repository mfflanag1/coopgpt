from fractions import Fraction as Q
from pathlib import Path
import sys,json,random
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common_cap_full_outside_mechanism import coalition_payment,production,Radical
rng=random.Random(93017);counts={'full_floor':0,'full_OUT_C1':0,'funding_order':0,'recurrence':0}
for k in range(1,8):
    for trial in range(700):
        M=rng.randrange(1,24);d=1+k*M
        other=[Q(rng.randrange(7),rng.choice((1,2,3))) for _ in range(d)]
        own=[Q(rng.randrange(7),rng.choice((1,2,3))) for _ in range(d)]
        more=[Q(rng.randrange(4),rng.choice((1,2,3))) for _ in range(d)]
        c=[a+b for a,b in zip(other,own)]
        y=coalition_payment(c,own,k,Q(1))
        floor=production(c,k)-production(other,k)
        assert y.compare(floor)>=0
        counts['full_floor']+=1
        hi=[a+b for a,b in zip(c,more)];ownhi=[a+b for a,b in zip(own,more)]
        new=coalition_payment(hi,ownhi,k,Q(1))
        assert new.compare(Radical(y.a+production(more,k),y.b,y.q,y.k))>=0
        counts['full_OUT_C1']+=1
        # Funding1+k M^((k-1)/k) has a radical bound; use a conservative exact
        # integer ceiling to check the implementation without rounded comparisons.
        ceil=1
        while ceil**k<M**(k-1):ceil+=1
        assert coalition_payment(c,c,k,Q(1)).compare((1+k*ceil)*production(c,k))<=0
        counts['funding_order']+=1
    product=Q(1)
    for M in range(1,101):
        if M>1:product*=Q(k*M,k*(M-1)+1)
        for theta in (Q(0),Q(1,10),Q(1,2),Q(1)):
            t=k*theta
            for m in range(2,M+1):t*=Q(k*m,k*(m-1)+1)
            assert t==k*theta*product
            counts['recurrence']+=1
out={'status':'PASS','checks':counts,'private_arities':list(range(1,8)),
     'branches_up_to':23,'arithmetic':'exact rational and certified algebraic comparisons',
     'limits':'Funding numerical exponent uses a certified integer ceiling in tests; exact sharper bound is analytic.'}
Path(__file__).with_name('COMMON_CAP_FLOOR_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
