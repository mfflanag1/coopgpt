from fractions import Fraction as Q
from pathlib import Path
import random,json,sys,itertools
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common_cap_full_outside_mechanism import Radical,parameter,coalition_payment,production

def check(t,s):
    if not t:raise RuntimeError(s)
counts={'funding':0,'coverage':0,'full_OUT':0,'exact_floor_failure':0}
rng=random.Random(4201710)
for k in range(1,8):
    for trial in range(1000):
        M=rng.randrange(1,27);d=1+k*M;C=parameter(M,k)
        out=[Q(rng.randrange(6),rng.choice((1,2,3))) for _ in range(d)]
        lowown=[Q(rng.randrange(6),rng.choice((1,2,3))) for _ in range(d)]
        restore=[Q(rng.randrange(6),rng.choice((1,2,3))) for _ in range(d)]
        low=[a+b for a,b in zip(out,lowown)]
        high=[a+b for a,b in zip(low,restore)]
        highown=[a+b for a,b in zip(lowown,restore)]
        yp=coalition_payment(high,highown,k)
        ym=coalition_payment(low,lowown,k)
        outside=production(restore,k)
        target=Radical(ym.a+outside,ym.b,ym.q,ym.k)
        check(yp.compare(target)>=0,'full OUT')
        check(coalition_payment(high,high,k).compare((C+k)*production(high,k))<=0,'funding')
        check(yp.compare(production(highown,k))>=0,'coverage')
        for name in ('funding','coverage','full_OUT'):counts[name]+=1
# Exact switches/zero faces with a coalition restoring complete activities.
for k in (1,2,3,4):
    M=3;d=1+k*M;C=parameter(M,k)
    for P in (Q(0),Q(1),C,Q(3)*C):
        for branchcaps in itertools.product((Q(0),Q(1),Q(2)),repeat=M):
            low=[P]+[x for b in branchcaps for x in [b]*k]
            for j in range(M):
                restore=[Q(0)]*d;restore[0]=Q(1)
                for l in range(k):restore[1+j*k+l]=Q(1)
                high=[a+b for a,b in zip(low,restore)]
                # Coalition initially owns half of every existing row.
                own=[a/2 for a in low];ownhi=[a+b for a,b in zip(own,restore)]
                ym=coalition_payment(low,own,k);yp=coalition_payment(high,ownhi,k)
                check(yp.compare(Radical(ym.a+1,ym.b,ym.q,ym.k))>=0,'zero/tied activity OUT')
                counts['full_OUT']+=1
# Explicit non-floor claim: one indispensable private owner gets1/C<1.
k=2;M=2;C=Q(2);c=[Q(1),Q(1),Q(1),Q(0),Q(0)];s=[Q(0),Q(1),Q(0),Q(0),Q(0)]
y=coalition_payment(c,s,k,C)
check(y.compare(Q(1,2))==0 and y.compare(1)<0,'participation floor counterexample')
counts['exact_floor_failure']+=1
out={'status':'PASS','checks':counts,'private_arities':list(range(1,8)),
     'random_branches_up_to':26,'arithmetic':'exact fractions and certified kth-root sign intervals',
     'limits':'Unresolved two-root comparisons raise; finite checks corroborate the directional all-profile proof.'}
Path(__file__).with_name('COMMON_CAP_FULL_OUTSIDE_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
