"""Exact finite checks for the conditioned-zero Bernoulli mechanism.

The all-profile and asymptotic conclusions require the accompanying proof.
These checks enumerate all masks/coalitions on a reproducible small-DAG suite,
including ties, zero capacities, parallel owners and interacting bridges.
Checks remain active under python -O. Standard library only.
"""
from fractions import Fraction as Q
from pathlib import Path
from itertools import combinations
import importlib.util
import json
import random


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def log_bounds(x, terms=80):
    """Rational enclosure of log(x) for rational x>=1 by atanh series."""
    require(x >= 1, 'log enclosure domain')
    z = (x-1)/(x+1)
    lower = 2*sum((z**(2*j+1)/Q(2*j+1) for j in range(terms)), Q(0))
    error = 2*z**(2*terms+1)/Q(2*terms+1)/(1-z*z)
    return lower, lower+error


def run():
    dependency = Path(__file__).resolve().parents[2] / '2026-10-06-monotone-envelope/verification/verify.py'
    spec = importlib.util.spec_from_file_location('flow_verify', dependency)
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    rng = random.Random(71070713)
    cases = []
    for n in range(2, 5):
        possible = list(combinations(range(n), 2))
        for G in range(1, 1 << len(possible)):
            edges = [e for i, e in enumerate(possible) if G >> i & 1]
            paths = v.paths(n, edges)
            if paths and set().union(*map(set, paths)) == set(range(len(edges))):
                cases.append((n, edges))
    cases += [
        (4, [(0,1),(0,2),(1,2),(1,3),(2,3),(1,3)]),
        (5, [(0,1),(0,2),(1,2),(1,3),(2,3),(2,4),(3,4)]),
        (6, [(0,1),(0,2),(1,2),(1,3),(2,4),(3,4),(3,5),(4,5)]),
    ]
    counts = dict(graphs=0, profiles=0, mask_flow_identities=0,
                  full_minimum_family_invariances=0, active_cap_strictness=0,
                  conditional_own_monotonicity=0, coalition_coverage=0,
                  mask_membership_comparisons=0, budget_domination=0,
                  exact_chernoff_comparisons=0, certified_log_budget_checks=0)
    for n, edges in cases:
        m = len(edges)
        cuts = v.cutsets(n, edges)
        require(cuts == v.path_blockers(v.paths(n, edges)), 'cut enumeration')
        all_masks = range(1 << m)
        profiles = [[Q(0)] * m, [Q(1)] * m,
                    [Q(rng.randrange(7), 3) for e in edges]]
        def families(D):
            answer = []
            for S in all_masks:
                vals = [(v.weighted_sum(D, C & S), C) for C in cuts]
                minimum = min(x for x, C in vals)
                answer.append(tuple(C for x, C in vals if x == minimum))
            return answer
        def payments(D, fam, q):
            z = [Q(0)] * m
            conditional = [Q(0)] * m
            for S in all_masks:
                C = fam[S][0]  # fixed increasing bitmask priority
                probability = (1-q) ** S.bit_count() * q ** (m-S.bit_count())
                for e in range(m):
                    if C >> e & 1:
                        z[e] += D[e] * probability
                        if not (S >> e & 1):
                            conditional[e] += D[e] * probability / q
            return z, conditional
        for c in profiles:
            D = v.effective(n, edges, c)
            T = v.maxflow(n, edges, c)
            fam = families(D)
            values = []
            for S in all_masks:
                raw = [x if S >> e & 1 else Q(0) for e, x in enumerate(c)]
                normalized = [x if S >> e & 1 else Q(0) for e, x in enumerate(D)]
                value = v.maxflow(n, edges, raw)
                require(value == v.maxflow(n, edges, normalized), 'masked feasible value')
                require(value == v.weighted_sum(D, fam[S][0] & S), 'masked cut value')
                values.append(value)
                counts['mask_flow_identities'] += 1
                for e in range(m):
                    S0 = S & ~(1 << e)
                    S1 = S0 | (1 << e)
                    if D[e] > 0 and fam[S1][0] >> e & 1:
                        require(fam[S0][0] >> e & 1, 'conditioning membership domination')
                    counts['mask_membership_comparisons'] += 1
            original = {}
            for q in (Q(1,3), Q(1,2), Q(2,3)):
                z, p = payments(D, fam, q)
                require(all(ze <= pe <= ze/q for ze, pe in zip(z,p)), 'pointwise sandwich')
                require(sum(p) <= sum(z)/q, 'budget sandwich')
                original[q] = p
                counts['budget_domination'] += 1
                if T > 0:
                    # lambda=log2: the tail comparison can be tested exactly
                    # by raising to the denominator of rational rho_C.
                    beta = q+(1-q)/2
                    for C in cuts:
                        rho = v.weighted_sum(D,C)/T
                        prob = sum(((1-q)**S.bit_count()*q**(m-S.bit_count())
                                    for S in all_masks if v.weighted_sum(D,C&S)<=T), Q(0))
                        require(prob**rho.denominator <= 2**rho.denominator*beta**rho.numerator,
                                'exact Chernoff cut bound')
                        counts['exact_chernoff_comparisons'] += 1
                    logKlo = log_bounds(Q(len(cuts)))[0]
                    log2lo = log_bounds(Q(2))[0]
                    alphahi = log_bounds(1/beta)[1]
                    # This rational RHS is a LOWER bound on the theorem RHS;
                    # passing it certifies the actual logarithmic inequality.
                    rhs = (logKlo+log2lo+1)/(q*alphahi)
                    require(sum(p) <= T*rhs, 'certified finite logarithmic budget')
                    counts['certified_log_budget_checks'] += 1
                if T == 0:
                    require(not any(p), 'zero value payments')
                for S in all_masks:
                    require(v.weighted_sum(p,S) >= values[S], 'coalition coverage')
                    counts['coalition_coverage'] += 1
            for e, ce in enumerate(c):
                cz = list(c)
                cz[e] = Q(0)
                D0 = v.effective(n, edges, cz)
                # Test genuinely positive reports even when original ce=0.
                high = max(ce, Q(1))
                ch = list(c)
                ch[e] = high
                Dh = v.effective(n, edges, ch)
                fh = families(Dh)
                highp = {q: payments(Dh,fh,q)[1] for q in original}
                previous = {q: Q(0) for q in original}
                for t in sorted(set((high/7, high/2, high, ce))-{Q(0)}):
                    ct = list(c)
                    ct[e] = t
                    Dt = v.effective(n, edges, ct)
                    ft = families(Dt)
                    require(Dt[e] == min(t,Dh[e]), 'own effective cap hinge')
                    for a, b, d in zip(D0, Dt, Dh):
                        require((b > a) == (d > a), 'strict support at positive report')
                        require(b >= a + (t/high)*(d-a), 'convex flow interpolation')
                        counts['active_cap_strictness'] += 1
                    for S in all_masks:
                        if not (S >> e & 1):
                            require(ft[S] == fh[S], 'entire conditional minimum family invariant')
                            counts['full_minimum_family_invariances'] += 1
                    for q in original:
                        pe = payments(Dt,ft,q)[1][e]
                        require(previous[q] <= pe <= highp[q][e], 'all-positive own monotonicity')
                        if Dt[e] and Dh[e]:
                            require(pe/Dt[e] == highp[q][e]/Dh[e], 'conditional coefficient independent of own report')
                        previous[q] = pe
                        counts['conditional_own_monotonicity'] += 1
            counts['profiles'] += 1
        counts['graphs'] += 1
    # An exact negative control: the unconditioned Bernoulli base is NOT
    # own-monotone even on two serial parallel-edge pools. The repaired
    # payment must detect and remove this violation, rather than merely pass
    # on examples where the original rule was already monotone.
    def control(x):
        caps = [x,Q(1,2),Q(1,2),Q(1,2)]
        es = [(0,1),(0,1),(1,2),(1,2)]
        d = v.effective(3,es,caps)
        cs = v.cutsets(3,es)
        z = Q(0)
        p = Q(0)
        for S in range(16):
            C = min(cs,key=lambda C:(v.weighted_sum(d,C&S),C))
            if C & 1:
                z += d[0]/16
                if not S & 1:
                    p += d[0]/8
        return z,p
    low, high = control(Q(49,100)), control(Q(51,100))
    require(low == (Q(539,1600),Q(343,800)), 'negative-control low payment')
    require(high == (Q(51,200),Q(357,800)), 'negative-control high payment')
    require(low[0] > high[0] and low[1] < high[1], 'negative control detects base failure')
    counts['negative_controls'] = 1
    return dict(status='PASS', **counts,
                scope='Exact finite rational masks, all coalitions and selected unilateral reports. Written proof establishes all-profile truthfulness and logarithmic budget; no asymptotic theorem is inferred from this suite.')


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
