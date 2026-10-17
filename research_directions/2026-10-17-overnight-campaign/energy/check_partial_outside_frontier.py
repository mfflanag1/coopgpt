#!/usr/bin/env python3
"""Analytic-piece floating diagnostics for the sharp partial-OUT frontier."""
import itertools
import json
import math
import random
from pathlib import Path


def root_a0():
    lo, hi = 1e-5, .5
    for _ in range(80):
        mid = (lo + hi) / 2
        if -math.log(mid) + 2 * mid > 2:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


class Law:
    def __init__(self, a):
        self.a = a
        lo, hi = a, 1 - 1e-14
        for _ in range(80):
            mid = (lo + hi) / 2
            gap = math.log((1 - a) / (1 - mid)) - (1 + mid - a - a*a)
            if gap < 0:
                lo = mid
            else:
                hi = mid
        self.b = (lo + hi) / 2
        self.mu = 1 / (1 + self.b + a - a*a)
        self.beta = self.mu * (1 + self.b)

    def integrate(self, lo, hi):
        if hi <= self.a + 1e-15:
            mass = 2 * self.mu * (hi - lo)
            first = self.mu * (hi*hi - lo*lo)
        elif lo >= self.a - 1e-15:
            mass = self.mu * math.log((1-lo)/(1-hi))
            first = mass - self.mu * (hi-lo)
        else:
            a, b = self.integrate(lo, self.a)
            c, d = self.integrate(self.a, hi)
            return a+c, b+d
        return mass, first

    def q(self, t):
        split = min(t, self.b)
        mass, first = self.integrate(0, split)
        return first/t + 1-mass

    def outside(self, t):
        if t >= self.b:
            return self.mu*(1+t)
        mass, first = self.integrate(t, self.b)
        return self.mu*(1+t)+mass-first


def value(rows, x):
    return min(sum(a*b for a,b in zip(row,x)) for row in rows)


def face(rows, x, j, law, direction=None):
    lines=[(row[j]*x[j],sum(row[k]*x[k] for k in range(len(x)) if k!=j)) for row in rows]
    cuts=[0.0,law.a,law.b]
    for (a,b),(aa,bb) in itertools.combinations(lines,2):
        if b!=bb:
            root=(aa-a)/(b-bb)
            if 0<root<law.b:
                cuts.append(root)
    cuts=sorted(set(cuts))
    total=derivative=0.0
    for lo,hi in zip(cuts,cuts[1:]):
        mid=(lo+hi)/2
        r=min(range(len(rows)),key=lambda r:lines[r][0]+mid*lines[r][1])
        mass,first=law.integrate(lo,hi)
        a,b=lines[r]
        total+=a*mass+b*first
        if direction is not None:
            derivative+=rows[r][j]*direction[j]*mass
            derivative+=sum(rows[r][k]*direction[k] for k in range(len(x)) if k!=j)*first
    return total,derivative


def prices(rows,x,law):
    return [face(rows,x,j,law)[0]/z if z>0 else 0.0 for j,z in enumerate(x)]


def dot(x,y):
    return sum(a*b for a,b in zip(x,y))


def main():
    rng=random.Random(630151)
    a0=root_a0()
    laws=[Law(a0*k/10) for k in range(11)]
    counts=dict(scalar_checks=0,profiles=0,derivative_corners=0,
                finite_deviations=0,boundary_cases=0)
    worst=dict(derivative_gap=0.0,finite_gap=0.0,coverage_gap=0.0)
    for law in laws:
        mass,mean=law.integrate(0,law.b)
        assert abs(mass-1)<2e-14 and abs(mean-law.mu)<2e-14
        if law.a:
            assert abs(law.a*law.q(law.a)-(law.a-law.mu*law.a**2))<2e-14
        assert abs(law.b*law.q(law.b)-law.mu)<2e-14
        for k in range(1,2001):
            t=k/2000
            assert law.q(t)+law.mu*t>=1-2e-13
            assert law.outside(t)>=law.beta-2e-13
            counts['scalar_checks']+=1
        for _ in range(100):
            dim=rng.randint(2,7)
            rows=[[rng.choice([0,0,.25,.5,1,2,5]) for _ in range(dim)]
                  for _ in range(rng.randint(1,8))]
            x=[10**rng.uniform(-1.5,1.5) for _ in range(dim)]
            direction=[10**rng.uniform(-1.5,1.5) for _ in range(dim)]
            terms=[face(rows,x,j,law,direction) for j in range(dim)]
            av=[terms[j][0]*direction[j]/x[j] for j in range(dim)]
            bv=[terms[j][1] for j in range(dim)]
            rhs=law.beta*value(rows,direction)
            scale=max(1.0,rhs,sum(av),sum(bv))
            for bits in itertools.product((0,1),repeat=dim):
                gap=sum(bv[j] if bits[j] else av[j] for j in range(dim))-rhs
                worst['derivative_gap']=min(worst['derivative_gap'],gap/scale)
                assert gap>=-1e-10*scale,(law.__dict__,rows,x,direction,bits,gap)
                counts['derivative_corners']+=1
            assert sum(h for h,_ in terms)<=(1+law.mu*(dim-1))*value(rows,x)+1e-10*max(1,value(rows,x))
            counts['profiles']+=1
            for _ in range(3):
                owners=[[rng.choice([0,0,1,2,4]) for _ in range(dim)]
                        for _ in range(rng.randint(2,7))]
                coalition=[i for i in range(len(owners)) if rng.randrange(2)]
                high=[sum(b[j] for b in owners) for j in range(dim)]
                held=[sum(owners[i][j] for i in coalition) for j in range(dim)]
                removed=[sum(owners[i][j]*rng.choice([0,.25,.5,1]) for i in coalition) for j in range(dim)]
                low=[a-b for a,b in zip(high,removed)]
                retained=[a-b for a,b in zip(held,removed)]
                ph,pl=prices(rows,high,law),prices(rows,low,law)
                yy,zz=dot(held,ph),dot(retained,pl)
                fd=value(rows,removed)
                scale=max(1,yy,zz,fd)
                gap=yy-zz-law.beta*fd
                worst['finite_gap']=min(worst['finite_gap'],gap/scale)
                assert gap>=-1e-10*scale,(law.__dict__,rows,owners,coalition,removed,gap)
                cover=yy-value(rows,held)
                worst['coverage_gap']=min(worst['coverage_gap'],cover/scale)
                assert cover>=-1e-10*scale
                counts['finite_deviations']+=1
                counts['boundary_cases']+=int(any(z==0 for z in high+low))
    for left,right in zip(laws,laws[1:]):
        assert left.mu>right.mu and left.beta>right.beta
    result=dict(status='PASS',evidence='floating analytic-piece diagnostics; not proof',
                a0=a0,beta0=laws[-1].beta,counts=counts,worst_normalized_gaps=worst,
                frontier=[law.__dict__ for law in laws])
    Path(__file__).with_name('partial_outside_frontier_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='frontier'},indent=2))


if __name__=='__main__':
    main()
