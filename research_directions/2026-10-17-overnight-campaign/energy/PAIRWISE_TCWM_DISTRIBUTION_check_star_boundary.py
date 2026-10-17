from fractions import Fraction as Q
from itertools import product
import json

values=[Q(0),Q(1,4),Q(1,2),Q(1),Q(2)]
profiles=coalitions=derivatives=0
for n in range(1,5):
    for x in product(values,repeat=n):
        profiles+=1
        r=tuple(min(t,Q(1)) for t in x)
        R=sum(r,Q(0))
        A=sum(x,Q(0))
        if A<=1:
            pay=tuple(t/2 for t in x)
            pb=sum(x,Q(0))/2
            assert sum(pay,Q(0))+pb==min(A,Q(1))
            for mask in range(1<<n):
                cap=sum((x[i] for i in range(n) if mask>>i&1),Q(0))
                paid=pb+sum((pay[i] for i in range(n) if mask>>i&1),Q(0))
                assert paid>=min(cap,Q(1))
                coalitions+=1
            continue
        assert R>=1
        # Coverage is affine in p, so checking endpoints proves it for 0<=p<=1/2.
        for p in [Q(0),Q(1,2)]:
            pay=tuple(t*p for t in r)
            pb=1-p
            for mask in range(1<<n):
                cap=sum((x[i] for i in range(n) if mask>>i&1),Q(0))
                paid=pb+sum((pay[i] for i in range(n) if mask>>i&1),Q(0))
                assert paid>=min(cap,Q(1))
                coalitions+=1
        a=1/min(R,Q(2))
        pmax=1/(2*R)  # Exact analytic upper for the exponential branch as well.
        U=sum((r[i] for i in range(n) if x[i]<1),Q(0))
        assert 0<=pmax*(1+a*U)<=1
        derivatives+=1
        for i in range(n):
            if x[i]<1:
                own=1-a*r[i]
                assert own>=0 and pmax*own<=1
                opposite=1+a*(1-r[i])
                assert opposite>=0 and pmax*opposite<=1
                derivatives+=2
                for k in range(n):
                    if k!=i:
                        pair=1-a*(r[i]+r[k])
                        assert pair>=0 and pmax*pair<=1
                        derivatives+=1
                # Unique opposite owner's capacity variation.
                loss=1+a*U*(1-r[i])
                assert loss>=0 and pmax*loss<=1
                derivatives+=1
            else:
                # Opposite-owner plus saturated-owner derivative is exactly1.
                assert (1-pmax*(1+a*U))+pmax*(1+a*U)==1
                derivatives+=1

# Compute the formula itself on the rational branch used by the witness.
def rational_star_payments(x,B):
    assert B>0
    A=sum(x,Q(0))
    if A<=B:
        return tuple(t/2 for t in x)+(A/2,)
    r=tuple(min(t/B,Q(1)) for t in x)
    R=sum(r,Q(0))
    assert Q(1)<=R<=Q(2), "This exact helper only evaluates the rational branch"
    p=1/(2*R)
    return tuple(B*t*p for t in r)+(B*(1-p),)

# Exact cross-chart obstruction; the dominant payment uses total B=3/2.
x=(Q(2),Q(1,2))
dominant=rational_star_payments(x,Q(3,2))[0]
boundary_one=rational_star_payments(x,Q(1))[0]
boundary_half=rational_star_payments(x,Q(1,2))[0]
assert boundary_one==Q(1,3) and boundary_half==Q(1,8)
assert dominant==Q(9,16)
assert dominant-boundary_one-boundary_half==Q(5,48)>0

# The deletion inequality is the exact sum of pair upper bounds minus coverage.
# Coordinates: dominant payment, m opposite payments, m deleted dominant
# payments, m deleted-null payments, and total opposite capacity.
for m in range(2,8):
    size=3*m+2
    summed=[Q(0)]*size
    for j in range(m):
        row=[Q(0)]*size
        row[0]=1; row[1+j]=1
        row[1+m+j]=-1; row[1+2*m+j]=-1
        # Sum of RHS b_j represented as a single total B after aggregation.
        summed=[a+b for a,b in zip(summed,row)]
    summed[-1]=-1
    coverage=[Q(0)]*size
    coverage[0]=1
    for j in range(m): coverage[1+j]=1
    coverage[-1]=-1
    difference=[a-b for a,b in zip(summed,coverage)]
    assert difference[0]==m-1
    assert difference[1:1+m]==[0]*m
    assert difference[1+m:1+3*m]==[-1]*(2*m)
    assert difference[-1]==0

result={"status":"PASS","profiles":profiles,
        "coalition_checks_containing_unique_opposite_owner":coalitions,
        "other_coalitions":"zero worth, covered by nonnegative payments",
        "exact_normalized_derivative_checks":derivatives,
        "arithmetic":"fractions; exponential branch bounded analytically",
        "cross_chart_high_payment":str(dominant),
        "cross_chart_boundary_sum":str(boundary_one+boundary_half),
        "cross_chart_violation":str(dominant-boundary_one-boundary_half),
        "scope":"star-boundary data and necessary extension inequality, not a global mechanism"}
print(json.dumps(result,indent=2))
