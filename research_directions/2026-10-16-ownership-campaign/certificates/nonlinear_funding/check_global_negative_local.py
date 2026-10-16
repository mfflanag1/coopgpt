#!/usr/bin/env python3
"""90-digit finite checks across caps; analytic proof is the companion note."""
from decimal import Decimal, localcontext
from pathlib import Path
import hashlib
import json
import random

BASE = Path(__file__).resolve().parent
D = Decimal
TOL = D('1e-65')


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def primitive(a, b):
    sa, sb = sum(a), sum(b)
    if min(sa, sb) == 0:
        return [D(0)] * len(a)
    short, long = (a, b) if sa <= sb else (b, a)
    t = min(sa, sb)
    caps = [min(x, t) for x in long]
    q = (1 - sum(caps) / t).exp() / 2
    return [(1 - q) * x + q * y for x, y in zip(short, caps)]


def run():
    rng = random.Random(2026101606)
    e = D(1).exp()
    counts = {'profiles': 0, 'actual_identity_checks': 0,
              'cross_cap_jensen_checks': 0, 'subgradient_support_checks': 0,
              'simultaneous_cap_jump_checks': 0}
    for m in (1, 2, 5, 11):
        for trial in range(20):
            # Three actual pure-grid owners guarantee the restoration threshold.
            # Distinct local-only and hardware-only opponents cross their caps.
            h, l, q0, qlo = [], [], [], []
            for j in range(m):
                t = D(1) / m
                own_h = D(rng.randrange(6, 15)) / 20
                own_l = D(rng.randrange(1, 4)) / 20
                remainder = 1 - own_h
                h.append([own_h*t, remainder*t/2, remainder*t/2,
                          D(0), D(0), D(0), D(0), D(0)])
                l.append([own_l*t, D(0), D(0), 4*t/5, 4*t/5,
                          D(0), D(0), D(0)])
                q0.append((-D(3)/5).exp()/2)
                qlo.append(q0[-1]*(-own_l).exp())
            a = [sum(row[k] for row in h) for k in range(8)]
            mid = [(lo+hi)/2 for lo, hi in zip(qlo, q0)]

            def responses(q):
                z = [D(0)]*8
                x = []
                affine = [[D(0)]*m for _ in range(8)]
                for j in range(m):
                    t = D(1)/m
                    u = -t*(q[j]/q0[j]).ln()
                    require(-TOL <= u <= l[j][0]+TOL, 'Report recovery failed')
                    reports = l[j][:]
                    reports[0] = max(D(0), min(u, l[j][0]))
                    branch = primitive(h[j], reports)
                    z = [zk+bk for zk, bk in zip(z, branch)]
                    x.append(h[j][0]+t-u)
                    for k in range(1, 8):
                        affine[k][j] = min(l[j][k], t)-h[j][k]
                return z, x, affine

            zm, _, _ = responses(mid)
            p = [D(0), 1-zm[1], D(0), 1-zm[3], D(0), D(1), D(1), D(1)]
            require(all(v >= 0 for v in p), 'Negative grid report')
            full_z, _, _ = responses(qlo)
            full_s = sum(min(pk+zk, D(1)) for pk, zk in zip(p, full_z))
            require(full_s >= D(3)/2+e*full_z[0], 'ER threshold missing')
            require(full_z[0] < a[0], 'Negative full gap missing')

            def evaluate(q, tie_choice=D(1)/2):
                z, x, affine = responses(q)
                b = [pk+zk for pk, zk in zip(p, z)]
                s = sum(min(bk, D(1)) for bk in b)
                w = a[0]-b[0]
                require(w > 0 and s >= 1, 'Negative/outer regime lost')
                loss = w*(-s).exp()
                actual = primitive(a, b)[0]
                require(abs(actual-(a[0]-e*loss/2)) <= TOL,
                        'Objective differs from actual nested payment')
                counts['actual_identity_checks'] += 1
                v = [D(0)]*m
                for k in range(1, 8):
                    theta = tie_choice if abs(b[k]-1) <= TOL else D(b[k] < 1)
                    for j in range(m):
                        v[j] += theta*affine[k][j]
                grad = [(-s).exp()*((1+w)*xj-w*vj) for xj, vj in zip(x, v)]
                pattern = tuple(k for k in range(1, 8) if b[k] > 1+TOL)
                return loss, grad, pattern, b, w, x, affine

            for sample in range(15):
                # Every line connects opposite sides of both constructed caps.
                left = D(rng.randrange(1, 16))/32
                right = D(rng.randrange(17, 32))/32
                qa = [lo+left*(hi-lo) for lo, hi in zip(qlo, q0)]
                qb = [lo+right*(hi-lo) for lo, hi in zip(qlo, q0)]
                fa, ga, pa, *_ = evaluate(qa)
                fb, gb, pb, *_ = evaluate(qb)
                require(pa != pb, 'Test did not cross actual caps')
                weight = D(rng.randrange(1, 16))/16
                qc = [(1-weight)*x+weight*y for x, y in zip(qa, qb)]
                fc, *_ = evaluate(qc)
                require(fc <= (1-weight)*fa+weight*fb+TOL,
                        'Cross-cap global Jensen failed')
                counts['cross_cap_jensen_checks'] += 1
                require(fb+TOL >= fa+sum(g*(y-x) for g,x,y in zip(ga,qa,qb)),
                        'Smooth global support failed')
                counts['subgradient_support_checks'] += 1
                for theta in (D(0), D(1)/2, D(1)):
                    fm, gm, _, *_ = evaluate(mid, theta)
                    for target, ftarget in ((qa,fa),(qb,fb)):
                        require(ftarget+TOL >= fm+sum(g*(y-x) for g,x,y in zip(gm,mid,target)),
                                'Cap-face subgradient support failed')
                        counts['subgradient_support_checks'] += 1

            fm, _, _, bm, wm, xm, affine = evaluate(mid)
            direction = [hi-lo for lo,hi in zip(qlo,q0)]
            slopes = [sum(c*v for c,v in zip(affine[k],direction)) for k in range(8)]
            cminus = D(0)
            cplus = D(0)
            for k in range(1,8):
                if abs(bm[k]-1) <= TOL:
                    cminus += max(slopes[k],D(0))
                    cplus += min(slopes[k],D(0))
                elif bm[k] < 1:
                    cminus += slopes[k]
                    cplus += slopes[k]
            require(cminus > cplus, 'Constructed cap jump not strict')
            xdir = sum(x*v for x,v in zip(xm,direction))
            factor = fm/wm
            lminus = factor*((1+wm)*xdir-wm*cminus)
            lplus = factor*((1+wm)*xdir-wm*cplus)
            require(lplus > lminus and abs(lplus-lminus-fm*(cminus-cplus)) <= TOL,
                    'Upward simultaneous derivative jump identity failed')
            counts['simultaneous_cap_jump_checks'] += 1
            counts['profiles'] += 1
    names = ('GLOBAL_NEGATIVE_LOCAL_CONVEXITY.txt',
             'NEGATIVE_GAP_CONVEX_LOCAL_EXTENSION.txt',
             'JOINT_RESPONSE_CONVEX_LOCAL_FRONTIER.txt')
    return {'status': 'PASS',
            'arithmetic': '90-digit Decimal finite corroboration, not a proof or certified optimizer',
            **counts,
            'source_sha256': {name:hashlib.sha256((BASE/name).read_bytes()).hexdigest() for name in names}}


if __name__ == '__main__':
    with localcontext() as ctx:
        ctx.prec = 90
        print(json.dumps(run(), indent=2, sort_keys=True))
