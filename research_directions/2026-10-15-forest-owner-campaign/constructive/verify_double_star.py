from fractions import Fraction as Q
from itertools import product
import json

def leaf_value(budget, caps, values):
    result=Q(0)
    for cap,value in sorted(zip(caps,values),key=lambda cv:-cv[1]):
        take=min(budget,cap)
        result+=take*value
        budget-=take
    return result

def direct(U,V,s,t,b,c,a):
    # Independent parametric optimization: central quantity z can be optimized
    # at endpoints or leaf-knapsack breakpoints; all arithmetic is rational.
    m=min(U,V)
    knots={Q(0),m}
    for center,caps,values in ((U,s,b),(V,t,c)):
        running=Q(0)
        for cap,value in sorted(zip(caps,values),key=lambda cv:-cv[1]):
            running+=cap
            if 0<=center-running<=m:
                knots.add(center-running)
    return max(a*z+leaf_value(U-z,s,b)+leaf_value(V-z,t,c) for z in knots)

def decomposition(U,V,s,t,b,c,a):
    total=(a-max(b,default=0)-max(c,default=0))*min(U,V)
    for center,other,caps,values in ((U,V,s,b),(V,U,t,c)):
        items=sorted(zip(caps,values),key=lambda cv:-cv[1])
        running=Q(0)
        for j,(cap,value) in enumerate(items):
            running+=cap
            next_value=items[j+1][1] if j+1<len(items) else Q(0)
            total+=(value-next_value)*min(center,other+running)
    return total

def main():
    cases=(
       ((Q(3),Q(1)),(Q(2),Q(1)),Q(5)),
       ((Q(3),Q(1)),(Q(2),Q(1)),Q(7)),
       ((Q(1),Q(3)),(Q(1),Q(2)),Q(5)),
       ((Q(3,2),Q(3,2)),(Q(2,3),Q(1,2)),Q(13,6)),
       ((Q(3),Q(1)),(),Q(3)),
    )
    checked=0
    for b,c,a in cases:
        for raw in product((Q(0),Q(1,2),Q(2)),repeat=2+len(b)+len(c)):
            U,V=raw[:2];s=raw[2:2+len(b)];t=raw[2+len(b):]
            lhs=direct(U,V,s,t,b,c,a)
            rhs=decomposition(U,V,s,t,b,c,a)
            if lhs!=rhs: raise RuntimeError((raw,b,c,a,lhs,rhs))
            checked+=1
    # Outside the domination hypothesis the same formula fails as expected.
    U=V=Q(1);s=t=(Q(1),);b=c=(Q(2),);a=Q(3)
    actual=direct(U,V,s,t,b,c,a)
    candidate=decomposition(U,V,s,t,b,c,a)
    if (actual,candidate)!=(Q(4),Q(3)):raise RuntimeError('negative control failed')
    print(json.dumps({'status':'PASS','exact_rational_profile_checks':checked,
      'technology_cases':len(cases),'outside_domain_negative_control':
      {'true_value':str(actual),'central_saturation_formula':str(candidate)},
      'scope':'finite identity corroboration; universal proof in DOUBLE_STAR.txt'},indent=2))
if __name__=='__main__':main()
