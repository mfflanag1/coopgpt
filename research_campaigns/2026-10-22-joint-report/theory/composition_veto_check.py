#!/usr/bin/env python3
"""Exact arithmetic checks for composition_veto_transport.txt, no solver."""
from fractions import Fraction as F
import json


def worth(u,mask):
    return min(sum(u[i] for i in (0,1) if mask>>i&1),
               sum(u[i] for i in (2,3) if mask>>i&1))


def transition(m,R):
    delta=F(1,8*m-6)
    v=F(1,2)-delta
    beta=F(9*m-7,8*m-6)
    assert beta==1+F(m-1,8*m-6)
    profiles=[(1,1,1,1),(R,1,1,1),(1,1,1,R)]
    controllers=[(v,F(1,2),F(1,2),v),
                 (v,v/2,1-v/2,1-v/2),
                 (1-v/2,1-v/2,v/2,v)]
    one_helper=[(delta,0,0,delta),(0,0,0,0),(0,0,0,0)]
    for u,a,h in zip(profiles,controllers,one_helper):
        assert R>=max(u) and all(z>=0 for z in (*a,*h))
        assert sum(a)+m*sum(h)==beta*worth(u,15)==2*beta
        # A complete group requires its controller and at least one helper;
        # their minimum payment is a_j+h_j. All extra owners are nonnegative.
        for mask in range(1,16):
            assert sum(a[j]+h[j] for j in range(4) if mask>>j&1)>=worth(u,mask)
    assert controllers[0][0]==controllers[1][0]
    assert controllers[0][3]==controllers[2][3]
    if m>1:
        assert 8*beta==9-2*(beta-1)/(m-1)
        A=sum(controllers[0]);H=m*sum(one_helper[0])
        assert A+H/m==2 and H/m==2*(beta-1)/(m-1)
    else:
        assert beta==1
    return beta


def fractional_failure():
    u=(4,1,4,1)
    x=(F(3,4),F(0),F(13,4),F(1))
    assert sum(x)==worth(u,15)==5
    for mask in range(1,16):
        assert sum(x[i] for i in range(4) if mask>>i&1)>=worth(u,mask)
    actual_output=min(F(1),F(1))
    actual_payment=x[1]+x[2]/4
    assert actual_output==1 and actual_payment==F(13,16)<1
    return {'outer_total':'5','outer_coalitions_checked':15,
            'actual_coalition_output':'1','actual_coalition_payment':'13/16'}


if __name__=='__main__':
    cases=[]
    for m in (1,2,3,4,8,16,64,1024):
        for R in (F(2),F(5,2),F(4),F(2**m)):
            beta=transition(m,R)
        cases.append({'m':m,'beta':str(beta),'report_ranges_checked':4})
    assert transition(2,F(4))==F(11,10)
    print(json.dumps({'transition_cases':cases,'total_cases':32,
                      'fractional_failure':fractional_failure()},indent=2))
