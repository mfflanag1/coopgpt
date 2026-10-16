#!/usr/bin/env python3
"""Independent high-precision checks of the concentrated-hardware improvement.

These Decimal evaluations corroborate the analytic lower bound; they are not
exact transcendental certificates or a substitute for the asymptotic proof.
The finite calibration and a fractional-ratio profile are materialized with
every branch-specific actual hardware owner, as in the frozen construction.
"""
from decimal import Decimal as D, getcontext, ROUND_CEILING
from fractions import Fraction as F
import json

getcontext().prec = 100
ZERO, ONE, TWO = D(0), D(1), D(2)
TOL = D('1e-85')


def require(condition, label):
    if not condition:
        raise RuntimeError(label)


def close(x, y, label):
    require(abs(x-y) < TOL, label)


def primitive(first, second):
    f, s = sum(first, ZERO), sum(second, ZERO)
    if min(f, s) == 0:
        return [ZERO] * len(first)
    short, long = (first, second) if f <= s else (second, first)
    total = min(f, s)
    caps = [min(x, total) for x in long]
    ratio = sum(caps, ZERO)/total
    q = (ONE-ratio).exp()/TWO
    return [(ONE-q)*x+q*y for x, y in zip(short, caps)]


def materialized(n=8, branches=8, fraction=ZERO, chosen_hardware_count=3000):
    nD, rD = D(n), D(branches)
    rho = nD+fraction
    T = ONE/nD
    q = (ONE-rho).exp()/TWO
    eps = q*T
    minimum = int(((ONE-q)/q).to_integral_value(rounding=ROUND_CEILING))
    m = minimum if chosen_hardware_count is None else chosen_hardware_count
    require(m>=minimum,'productive hardware fragmentation sufficient')
    hardware_count=m*branches
    fractional_count=int(fraction>0)
    count = hardware_count+n+fractional_count+2
    h, ell = [], []
    for j in range(branches):
        row=[ZERO]*count
        row[j*m:(j+1)*m]=[T/(D(m)*rD)]*m
        h.append(row)
        ell.append([ZERO]*hardware_count+[T/rD]*n
                   +([T*fraction/rD] if fractional_count else [])+[ZERO]*2)
    a = ONE-T
    h.append([ZERO]*hardware_count+[a]+[ZERO]*(n-1+fractional_count+2))
    ell.append([ZERO]*count)
    local = [ZERO]*count
    hardware = [sum((row[i] for row in h), ZERO) for i in range(count)]
    for hj, lj in zip(h, ell):
        local = [x+y for x, y in zip(local, primitive(hj, lj))]
    close(sum(hardware, ZERO), ONE, 'hardware normalization')
    close(max(local), eps, 'full diffuse ceiling attained')
    Z = T+(rho-ONE)*eps
    close(sum(local, ZERO), Z, 'full local total')
    grid = [ZERO]*(count-2)+[ONE-Z/TWO]*2
    opposing = [p+z for p,z in zip(grid, local)]
    close(sum(opposing, ZERO), TWO, 'full outer ratio two')
    require(max(opposing)<ONE, 'all full opposing accounts uncapped')
    require(all(hardware[i]+grid[i]+sum((row[i] for row in ell), ZERO)>0
                for i in range(count)), 'every actual owner active')
    raw = primitive(hardware, opposing)
    c = (-ONE).exp()/TWO
    close(sum(raw, ZERO), ONE+c, 'raw factor C')
    recipient = hardware_count
    changed = [row[:] for row in ell]
    for row in changed:
        row[recipient] = ZERO
    new_local = [ZERO]*count
    for hj, lj in zip(h, changed):
        new_local = [x+y for x,y in zip(new_local, primitive(hj, lj))]
    delta = eps*((ONE.exp()-ONE)*rho-(TWO*ONE.exp()-ONE))
    close(sum(new_local, ZERO)-Z, delta, 'actual local total increase')
    close(new_local[recipient], ZERO, 'deviator local account zero')
    new_opposing = [p+z for p,z in zip(grid, new_local)]
    require(max(new_opposing)<ONE, 'all deviated opposing accounts uncapped')
    new_raw = primitive(hardware, new_opposing)
    gain = new_raw[recipient]-raw[recipient]
    predicted = c*(a*(ONE-(-delta).exp())-eps)
    close(gain, predicted, 'actual own payment gain formula')
    require(gain>0, 'profitable actual deviation')
    return {'n':n,'rho':str(rho),'productive_branches':branches,'actual_owner_count':count,
            'epsilon':str(eps),'actual_own_gain':str(gain),
            'exhibited_aggregate_gain':str(gain),
            'normalized_exhibited_gain':str(gain/(eps*(-eps.ln())))}


def main():
    rows=[]
    e=ONE.exp(); c=ONE/(TWO*e)
    for n in [9,16,32,64]:
        nd=D(n);q=(ONE-nd).exp()/TWO;T=ONE/nd;eps=q*T;a=ONE-T
        delta=eps*((e-ONE)*nd-(TWO*e-ONE))
        gain=c*(a*(ONE-(-delta).exp())-eps)
        require(gain>0,'asymptotic fixture positive')
        rows.append({'n':n,'epsilon':str(eps),
                     'normalized_exhibited_gain':str(gain/(eps*(-eps.ln())))})
    print(json.dumps({'status':'PASS','scope':'100-digit Decimal finite corroboration of actual fixed-owner deviations; analytic proof is separate.',
                      'materialized_actual_profiles':[materialized(),materialized(9,2,D('0.5'),None)],
                      'asymptotic_displays':rows,'limiting_coefficient':str(c*(e-ONE))},indent=2))


if __name__=='__main__':
    main()
