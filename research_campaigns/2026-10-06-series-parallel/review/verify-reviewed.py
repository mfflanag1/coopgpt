"""Exact small checks for the TTSP theorem; not a proof of universal claims.

The graph/mincut check is independent of the composition-tree cap calculation.
Payments use exact truncated-power CDF arithmetic for independent random leaves.
No sampling, floating-point optimization or assert-dependent checks are used.
"""
from fractions import Fraction as Q
from math import comb, factorial
from functools import lru_cache
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def clean(a):
    return {k: v for k, v in a.items() if v}


def add_term(a, key, value):
    a[key] = a.get(key, Q(0)) + value


def uniform(d):
    return {(Q(0), 0): Q(1)} if not d else {(Q(0), 1): 1/d, (d, 1): -1/d}


def atom(d):
    return {(d, 0): Q(1)}


def cdf_product(f, g):
    h = {}
    for (a, p), u in f.items():
        for (b, q), v in g.items():
            m = max(a, b)
            for i in range(p+1):
                for j in range(q+1):
                    add_term(h, (m, i+j), u*v*comb(p, i)*comb(q, j)
                             *(m-a)**(p-i)*(m-b)**(q-j))
    return clean(h)


def minimum(f, g):
    h = dict(f)
    for k, v in g.items():
        add_term(h, k, v)
    for k, v in cdf_product(f, g).items():
        add_term(h, k, -v)
    return clean(h)


def derivative(f):
    atoms, density = {}, {}
    for (a, p), v in f.items():
        if p == 0:
            atoms[a] = v
        else:
            density[a, p-1] = v*p
    return atoms, density


def convolution(f, g):
    af, df = derivative(f)
    ag, dg = derivative(g)
    atoms, density = {}, {}
    for a, u in af.items():
        for b, v in ag.items():
            add_term(atoms, a+b, u*v)
        for (b, p), v in dg.items():
            add_term(density, (a+b, p), u*v)
    for b, v in ag.items():
        for (a, p), u in df.items():
            add_term(density, (a+b, p), u*v)
    for (a, p), u in df.items():
        for (b, q), v in dg.items():
            add_term(density, (a+b, p+q+1), u*v*Q(factorial(p)*factorial(q), factorial(p+q+1)))
    h = {(a, 0): u for a, u in atoms.items()}
    for (a, p), u in density.items():
        add_term(h, (a, p+1), u/Q(p+1))
    return clean(h)


def cdf_value(f, x):
    return sum(v*(x-a)**p for (a, p), v in f.items() if x >= a)


def expectation(f, upper):
    require(cdf_value(f, upper+1) == 1, 'CDF normalization above support')
    return upper-sum(v*(upper-a)**(p+1)/Q(p+1)
                     for (a, p), v in f.items() if a < upper)


def leaves(tree):
    return (tree,) if isinstance(tree, int) else leaves(tree[1])+leaves(tree[2])


def value(tree, c):
    if isinstance(tree, int):
        return c[tree]
    a, b = value(tree[1], c), value(tree[2], c)
    return min(a, b) if tree[0] == 'S' else a+b


def caps(tree, c):
    result = {}
    def visit(t, bound):
        if isinstance(t, int):
            result[t] = c[t] if bound is None else min(c[t], bound)
            return
        for child, sibling in ((t[1], t[2]), (t[2], t[1])):
            limit = bound
            if t[0] == 'S':
                v = value(sibling, c)
                limit = v if limit is None else min(limit, v)
            visit(child, limit)
    visit(tree, None)
    return tuple(result[i] for i in range(len(c)))


def tree_cuts(tree):
    if isinstance(tree, int):
        return {1 << tree}
    a, b = tree_cuts(tree[1]), tree_cuts(tree[2])
    return a | b if tree[0] == 'S' else {x | y for x in a for y in b}


def graph(tree):
    parent, edges = [], {}
    def new():
        parent.append(len(parent))
        return len(parent)-1
    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x
    def merge(a, b):
        parent[find(b)] = find(a)
    def visit(t):
        if isinstance(t, int):
            a, b = new(), new()
            edges[t] = (a, b)
            return a, b
        a, b = visit(t[1])
        c, d = visit(t[2])
        if t[0] == 'S':
            merge(b, c)
            return a, d
        merge(a, c)
        merge(b, d)
        return a, b
    s, t = visit(tree)
    ids = {v: i for i, v in enumerate(sorted({find(x) for x in parent}))}
    es = tuple((ids[find(edges[i][0])], ids[find(edges[i][1])]) for i in range(len(edges)))
    return len(ids), es, ids[find(s)], ids[find(t)]


@lru_cache(None)
def vertex_cuts(n, edges, s, t):
    require(s != t, 'distinct terminals required')
    cs = set()
    for m in range(1 << n):
        if not m >> s & 1 or m >> t & 1:
            continue
        cs.add(sum(1 << i for i, (a, b) in enumerate(edges)
                   if m >> a & 1 and not m >> b & 1))
    return tuple(sorted(cs))


def cut_sum(c, mask):
    return sum((x for i, x in enumerate(c) if mask >> i & 1), Q(0))


def mincut(c, cs):
    return min(cut_sum(c, a) for a in cs)


def graph_caps(c, g):
    n, es, s, t = g
    result = []
    for i, (a, b) in enumerate(es):
        limits = [c[i]]
        if a != s:
            limits.append(mincut(c, vertex_cuts(n, es, s, a)))
        if b != t:
            limits.append(mincut(c, vertex_cuts(n, es, b, t)))
        result.append(min(limits))
    return tuple(result)


def distribution(tree, d, fixed=None):
    if isinstance(tree, int):
        return atom(fixed[1]) if fixed is not None and fixed[0] == tree else uniform(d[tree])
    a, b = distribution(tree[1], d, fixed), distribution(tree[2], d, fixed)
    return minimum(a, b) if tree[0] == 'S' else convolution(a, b)


@lru_cache(None)
def payments(tree, c, global_cap=False):
    t = value(tree, c)
    if not t:
        return (Q(0),)*len(c)
    d = tuple(min(x, t) for x in c) if global_cap else caps(tree, c)
    return tuple(expectation(distribution(tree, d, (i, d[i])), t)
                 - expectation(distribution(tree, d, (i, Q(0))), t) for i in range(len(c)))



def old_cap_closed_form(n, epsilon, delta):
    # Independent simplex-tail/moment formula from GLOBAL_CAP_OBSTRUCTION.txt.
    t, total = epsilon+delta, n-delta
    def moment(r):
        if r == 0:
            return Q(1)
        return epsilon**r/Q(r+1)-Q(r)*epsilon**(r+1)/Q((r+1)*(r+2))/total
    m = n+1
    reflected = sum(Q(comb(m, r))*(-1)**r*t**(m-r)*moment(r) for r in range(m+1))
    return Q(n, 2)-moment(1)+(moment(m)-reflected)/Q(factorial(m))


def fold(op, items):
    a = items[0]
    for b in items[1:]:
        a = (op, a, b)
    return a


NETWORKS = {
    'parallel4': fold('P', list(range(4))),
    'series4': fold('S', list(range(4))),
    'layered2x2': ('S', ('P', 0, 1), ('P', 2, 3)),
    'nested5': ('S', ('P', 0, ('S', 1, 2)), ('P', 3, 4)),
    'parallel_paths6': ('P', ('S', 0, 1), ('P', ('S', 2, 3), ('S', 4, 5))),
    'nested6': ('S', ('P', 0, ('S', 1, 2)), ('P', 3, ('S', 4, 5))),
    'alternating7': ('P', ('S', ('P', 0, 1), ('P', 2, 3)), ('S', 4, ('P', 5, 6))),
}


def run():
    # Analytic calibration independent of the TTSP theorem.
    require(expectation(uniform(Q(2)), Q(2)) == 1, 'uniform mean')
    require(expectation(minimum(uniform(Q(1)), uniform(Q(1))), Q(1)) == Q(1, 3), 'min uniforms')
    require(expectation(convolution(uniform(Q(2)), uniform(Q(3))), Q(5)) == Q(5, 2), 'sum uniforms')
    require(expectation(minimum(atom(Q(1, 2)), uniform(Q(1))), Q(1)) == Q(3, 8), 'atom truncation')
    for k in range(1, 6):
        t = fold('S', list(range(k)))
        require(payments(t, (Q(1),)*k) == (Q(1, k),)*k, 'serial uniform symmetry')

    totals = dict(graphs=0, profiles=0, coalition_checks=0, monotone_pairs=0, cocut_checks=0)
    records = []
    for name, tree in NETWORKS.items():
        n = len(leaves(tree))
        require(set(leaves(tree)) == set(range(n)), 'fixed owner labels')
        g = graph(tree)
        allcuts = vertex_cuts(*g)
        minimal = {a for a in allcuts if not any(b != a and b & a == b for b in allcuts)}
        require(minimal == tree_cuts(tree), 'graph versus tree minimal cuts')
        profiles = set()
        for base in [(Q(1),)*n, tuple(Q(i+1, 2) for i in range(n))]:
            profiles.add(base)
            for i in range(n):
                for x in (Q(0), Q(1, 3), Q(1), Q(3)):
                    c = list(base)
                    c[i] = x
                    profiles.add(tuple(c))
        profiles.add((Q(0),)*n)
        results = {}
        for c in sorted(profiles):
            d = caps(tree, c)
            require(d == graph_caps(c, g), 'graph versus tree effective capacities')
            t = mincut(c, allcuts)
            require(t == value(tree, c), 'grand max flow')
            z = payments(tree, c)
            require(all(x >= 0 for x in z), 'negative payment')
            for mask in range(1 << n):
                cv = min(cut_sum(c, mask & a) for a in allcuts)
                dv = min(cut_sum(d, mask & a) for a in allcuts)
                require(cv == dv, 'coalition value changed by cap')
                require(cut_sum(z, mask) >= cv, 'coalition underpaid')
                totals['coalition_checks'] += 1
            if len(minimal) == 1:
                require(sum(z) == t, 'one-cut efficiency')
            r = 3
            while len(minimal)*Q(3, r)**r > 1:
                r += 1
            require(sum(z) <= (r+1)*t, 'certified coarse tail bound')
            results[c] = z
            totals['profiles'] += 1
        # Compare every retained unilateral pair, not only neighboring reports.
        for c, z in results.items():
            for q, w in results.items():
                changed = [i for i in range(n) if c[i] != q[i]]
                if len(changed) != 1:
                    continue
                i = changed[0]
                if c[i] >= q[i]:
                    continue
                require(z[i] <= w[i], 'own-report monotonicity')
                a, b = caps(tree, c), caps(tree, q)
                for cut in minimal:
                    if cut >> i & 1:
                        for j in range(n):
                            if j != i and cut >> j & 1:
                                require(a[j] == b[j], 'co-cut dependence')
                                totals['cocut_checks'] += 1
                totals['monotone_pairs'] += 1
        totals['graphs'] += 1
        records.append({'name': name, 'owners': n, 'minimal_cuts': len(minimal), 'profiles': len(results)})

    # A predeclared exact falsifier for globally capping all edges at T.
    bad = ('S', ('P', 0, ('S', 1, 2)), fold('P', [3, 4, 5, 6]))
    low = tuple(map(Q, [38, 1, 41, 10, 10, 10, 10]))
    high = tuple(map(Q, [39, 1, 41, 10, 10, 10, 10]))
    a, b = payments(bad, low, True)[0], payments(bad, high, True)[0]
    require(a == 10*old_cap_closed_form(4, Q(1, 10), Q(1, 10)), 'old low payment independent formula')
    require(b == 10*old_cap_closed_form(4, Q(1, 10), Q(0)), 'old high payment independent formula')
    for n in (4, 5, 8, 16):
        require(old_cap_closed_form(n, Q(1, 10), Q(1, 10))
                > old_cap_closed_form(n, Q(1, 10), Q(0)), 'growing-owner obstruction')
    require(a > b, 'global-cap falsifier must reject monotonicity')
    x, y = payments(bad, low)[0], payments(bad, high)[0]
    require(x <= y, 'effective cap must pass the falsifier')
    return {'status': 'passed', 'arithmetic': 'exact fractions, no assertions',
            'coverage': totals, 'networks': records,
            'global_cap_counterexample': {'low': list(map(str, low)), 'high': list(map(str, high)),
                                         'old_low_payment': str(a), 'old_high_payment': str(b),
                                         'drop': str(a-b), 'new_low_payment': str(x), 'new_high_payment': str(y)},
            'limitation': 'Finite implementation checks; universal claims require the written proof.'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
