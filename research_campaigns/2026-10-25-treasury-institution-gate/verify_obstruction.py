"""Exact rational certificates for the elementary public-summary obstruction.

No empirical data or numerical optimizer. Coefficients lie in Q+Q sqrt(2)+Q sqrt(3);
strict signs use exact rational enclosures checked by squaring.
"""
from fractions import Fraction as F
from pathlib import Path
import itertools, json

P=Path(__file__).parent
den=10**15
R2=(F(1414213562373095,den),F(1414213562373096,den))
R3=(F(1732050807568877,den),F(1732050807568878,den))
assert R2[0]**2<2<R2[1]**2 and R3[0]**2<3<R3[1]**2
def rad(a=0,b=0,c=0):return tuple(map(F,(a,b,c)))
def add(x,y):return tuple(a+b for a,b in zip(x,y))
def sub(x,y):return tuple(a-b for a,b in zip(x,y))
def total(xs):
    z=rad()
    for x in xs:z=add(z,x)
    return z
def interval(x):
    lo=hi=x[0]
    for coefficient,(left,right) in zip(x[1:],(R2,R3)):
        lo+=coefficient*(left if coefficient>=0 else right)
        hi+=coefficient*(right if coefficient>=0 else left)
    return lo,hi
def nonnegative(x):
    assert x==rad() or interval(x)[0]>=0, x
def det(a):
    if len(a)==1:return a[0][0]
    return sum((-1)**j*a[0][j]*det([row[:j]+row[j+1:] for row in a[1:]]) for j in range(len(a)))
def string(x):return [str(z) for z in x]

A=[[F(int(i==j)) for j in range(3)] for i in range(3)]
B=[[F(1),F(1,2),F(-1,2)],[F(1,2),F(1),F(0)],[F(-1,2),F(0),F(1)]]
sqrt={F(0):rad(),F(1):rad(1),F(2):rad(0,1),F(3):rad(0,0,1)}
yA=[rad(1,0,F(-1,3))]*3
yB=[rad(F(1,2)),rad(2,0,-1),rad(F(1,2))]
savings=rad(3,0,-1);records=[]
for name,cov,y in [('A',A,yA),('B',B,yB)]:
    minors=[det([row[:k] for row in cov[:k]]) for k in (1,2,3)]
    assert all(m>0 for m in minors)
    assert [cov[i][i] for i in range(3)]==[1,1,1]
    assert sum(sum(row) for row in cov)==3
    assert total(y)==savings
    coalitions=[]
    for size in (1,2,3):
        for s in itertools.combinations(range(3),size):
            variance=sum(cov[i][j] for i in s for j in s)
            required=sub(rad(size),sqrt[variance])
            slack=sub(total([y[i] for i in s]),required);nonnegative(slack)
            coalitions.append({'books':[i+1 for i in s],'risk_squared':str(variance),
                               'savings_slack_coefficients_1_sqrt2_sqrt3':string(slack),
                               'exact_zero':slack==rad(),
                               'slack_interval':[str(x) for x in interval(slack)]})
    records.append({'model':name,'leading_principal_minors':list(map(str,minors)),
                    'allocation_coefficients_1_sqrt2_sqrt3':[string(v) for v in y],
                    'coalitions':coalitions})

# Model B's {1,3} constraint implies y2<=T-1. Its attained first level is below 1/2.
assert sub(savings,rad(1))==yB[1]
nonnegative(sub(rad(F(1,2)),yB[1]))
assert add(yB[0],yB[2])==rad(1)
# Model A's equal vector is infeasible in B on {1,3}.
invalid_slack=sub(add(yA[0],yA[2]),rad(1))
assert interval(invalid_slack)[1]<0
assert interval(sub(yA[1],yB[1]))[0]>0
out={'passed':True,'method':'Exact Fraction determinants, symbolic radical coefficients, rational root enclosures; no optimizer or institutional data.',
     'core_coalitions_checked':14,'common_singleton_variances':[1,1,1],'common_total_variance':3,
     'models':records,'equal_allocation_in_model_B_pair13_slack':string(invalid_slack),
     'selector_argument':'Written proof uses mean bound in A and binding pair13/efficiency bounds in B; certificate verifies feasible attained vectors and strict ordering.',
     'interpretation':'Elementary non-identification of the coalition core and each selector from marginal plus aggregate Gaussian distributions. Not a difference between selectors within a model; no novelty claim.'}
(P/'exact_checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'passed':True,'exact_coalitions':14,'model_B_minors':records[1]['leading_principal_minors'],'equal_vector_B_pair13_slack':string(invalid_slack)}))
