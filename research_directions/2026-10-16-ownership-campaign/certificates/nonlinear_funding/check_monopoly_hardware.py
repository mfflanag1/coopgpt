#!/usr/bin/env python3
"""Independent finite corroboration for the monopoly hardware proof."""
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import random

BASE = Path(__file__).resolve().parent
D = Decimal
TOL = D('1e-65')


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def dec(x):
    return D(x.numerator)/D(x.denominator) if isinstance(x, Fraction) else D(x)


def primitive(a, b):
    a, b = list(map(dec, a)), list(map(dec, b))
    sa, sb = sum(a), sum(b)
    if min(sa, sb) == 0:
        return [D(0)] * len(a)
    short, long = (a,b) if sa <= sb else (b,a)
    total = min(sa,sb)
    caps = [min(x,total) for x in long]
    q = (1-sum(caps)/total).exp()/2
    return [(1-q)*x+q*y for x,y in zip(short,caps)]


def nested(h, l, p):
    n = len(p)
    hw = [D(0)] * n
    local = [D(0)] * n
    for hrow, lrow in zip(h,l):
        pay = primitive(hrow,lrow)
        hw = [x+dec(y) for x,y in zip(hw,hrow)]
        local = [x+y for x,y in zip(local,pay)]
    return primitive(hw,[dec(x)+y for x,y in zip(p,local)])


def run():
    rng = random.Random(2026101602)
    vals = [Fraction(0), Fraction(1,4), Fraction(1,2), Fraction(1), Fraction(2), Fraction(7)]
    monotonic_checks = 0
    local_checks = 0
    restoration_checks = 0
    sign_checks = 0
    dominance_checks = 0
    for n in (1,2,5,11):
        for trial in range(250):
            hvals = [rng.choice(vals) for _ in range(3)]
            h = [[hh]+[Fraction(0)]*(n-1) for hh in hvals]
            l = [[rng.choice(vals) for _ in range(n)] for _ in range(3)]
            p = [rng.choice(vals) for _ in range(n)]
            j = trial % 3
            hi = [row[:] for row in h]
            hi[j][0] += rng.choice(vals)
            before, after = nested(h,l,p)[0], nested(hi,l,p)[0]
            require(after + TOL >= before, 'Monopoly hardware monotonicity violation')
            local_before, local_after = primitive(h[j],l[j]), primitive(hi[j],l[j])
            require(all(y+TOL>=x for x,y in zip(local_before,local_after)), 'Local vector monotonicity violation')
            monotonic_checks += 1
            local_checks += n

            # Start from a full owner-bundle underreport, restore hardware and
            # grid but retain its reduced local reports, as in the theorem.
            hu, lu, pu = [row[:] for row in h], [row[:] for row in l], p[:]
            for j in range(3):
                hu[j][0] *= Fraction(rng.randrange(5),4)
                lu[j][0] *= Fraction(rng.randrange(5),4)
            pu[0] *= Fraction(rng.randrange(5),4)
            raw_under = nested(hu,lu,pu)[0]
            raw_restored = nested(h,lu,p)[0]
            require(raw_restored+TOL>=raw_under, 'Exact restoration inequality violation')
            restoration_checks += 1

            if n > 1:
                j = 1+trial % (n-1)
                changed = [row[:] for row in l]
                for branch in changed:
                    branch[j] *= Fraction(rng.randrange(5),4)
                before_local = [sum(primitive(hr,lr)[k] for hr,lr in zip(h,l)) for k in range(n)]
                after_local = [sum(primitive(hr,lr)[k] for hr,lr in zip(h,changed)) for k in range(n)]
                for k in range(n):
                    if k in (0,j):
                        require(after_local[k]<=before_local[k]+TOL, 'Local sign decrease violated')
                    else:
                        require(after_local[k]+TOL>=before_local[k], 'Local sign increase violated')
                    sign_checks += 1

            dominance_p = p[:]
            dominance_p[0] = sum(row[0] for row in h)
            full_pay = nested(h,l,dominance_p)
            for j in range(n):
                hu, lu, pu = [row[:] for row in h], [row[:] for row in l], dominance_p[:]
                for branch in range(3):
                    hu[branch][j] *= Fraction(rng.randrange(5),4)
                    lu[branch][j] *= Fraction(rng.randrange(5),4)
                pu[j] *= Fraction(rng.randrange(5),4)
                under_pay = nested(hu,lu,pu)[j]
                require(under_pay<=full_pay[j]+TOL, 'Dominance-class envelope equality violated')
                dominance_checks += 1

    family = []
    for r in (1,2,7,19):
        n = 3*r+1
        h, full_local, reduced_local = [], [], []
        for j in range(r):
            h.append([Fraction(1,r)]+[Fraction(0)]*(n-1))
            row = [Fraction(0)]*n
            row[0] = Fraction(1,r)
            for k in range(3):
                row[1+3*j+k] = Fraction(1,r)
            full_local.append(row)
            reduced = row[:]
            reduced[0] = Fraction(1,2*r)
            reduced_local.append(reduced)
        h.append([Fraction(1)]+[Fraction(0)]*(n-1))
        anchor = [Fraction(1,2)]+[Fraction(0)]*(n-1)
        full_local.append(anchor)
        reduced_local.append(anchor[:])
        full = nested(h,full_local,[0]*n)[0]
        reduced = nested(h,reduced_local,[0]*n)[0]
        expected_full = D(3)/2 + D(3)*D(-3).exp()/4
        expected_reduced = D(3)/2 + D('-2.5').exp()/2
        require(abs(full-expected_full)<=TOL, 'Counterfamily full formula mismatch')
        require(abs(reduced-expected_reduced)<=TOL, 'Counterfamily deviation formula mismatch')
        require(reduced>full, 'Strict local underreport gain missing')
        family.append({'owners':n,'productive_branches':r+1,
                       'full':str(full),'underreport':str(reduced),'gain':str(reduced-full)})
    # Exact rational certificate for the sole transcendental sign in (11):
    # e > 1+1+1/2 > 9/4, hence 2*sqrt(e)>3.
    lower_e = sum(Fraction(1,d) for d in (1,1,2))
    require(lower_e>Fraction(9,4), 'Exact sign certificate failed')
    sharp = []
    for branches in (1,3,9):
        h = [[Fraction(1,branches)]+[0]*branches for _ in range(branches)]
        l = [row[:] for row in h]
        p = [1]+[Fraction(1,branches)]*branches
        total = sum(nested(h,l,p))
        require(abs(total-(1+D(-1).exp()/2))<=TOL, 'Sharp dominance-class budget mismatch')
        sharp.append({'productive_branches':branches,'owners':branches+1,'total':str(total)})
    source = 'MONOPOLY_HARDWARE_COORDINATE_RESTORATION.txt'
    return {'status':'PASS','arithmetic':'Decimal precision90; finite corroboration except stated rational sign check',
            'hardware_coordinate_checks':monotonic_checks,'local_recipient_checks':local_checks,
            'whole_bundle_restoration_checks':restoration_checks,'counterfamily':family,
            'nonhardware_local_response_sign_checks':sign_checks,
            'dominance_class_whole_bundle_checks':dominance_checks,'sharp_dominance_values':sharp,
            'exact_rational_sign_certificate':str(lower_e)+' > 9/4',
            'source_sha256':{source:hashlib.sha256((BASE/source).read_bytes()).hexdigest()}}


if __name__ == '__main__':
    with localcontext() as ctx:
        ctx.prec = 90
        print(json.dumps(run(),indent=2,sort_keys=True))
