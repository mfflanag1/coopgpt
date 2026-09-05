"""Exact entire cores and full lexicographic selectors for triple markets."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product, permutations
import z3


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def Q(value):
    value = F(value)
    return z3.Q(value.numerator, value.denominator)


def rational(value):
    value = z3.simplify(value)
    if z3.is_int_value(value):
        return F(value.as_long())
    require(z3.is_rational_value(value), 'non-rational or unbounded optimum')
    return F(value.numerator_as_long(), value.denominator_as_long())


def optimize(constraints, objective, upward):
    solver = z3.Optimize()
    solver.set(timeout=60000)
    solver.add(*constraints)
    handle = solver.maximize(objective) if upward else solver.minimize(objective)
    require(solver.check() == z3.sat, 'optimization failed or UNKNOWN')
    return rational(handle.value())


def selector(constraints, players, upward):
    fixed = {}
    stages = []
    while len(fixed) < len(players):
        free = [i for i in range(len(players)) if i not in fixed]
        prefix = constraints + [players[i] == Q(v) for i, v in fixed.items()]
        level = z3.FreshReal('level')
        caps = [players[i] >= level if upward else players[i] <= level for i in free]
        value = optimize(prefix + caps, level, upward)
        face = prefix + [players[i] >= Q(value) if upward else players[i] <= Q(value) for i in free]
        pinned = [i for i in free if optimize(face, players[i], upward) == value]
        require(bool(pinned), 'no coordinate fixed on optimal face')
        fixed.update({i: value for i in pinned})
        stages.append(dict(level=str(value), players=pinned))
    return [fixed[i] for i in range(len(players))], stages


def core(weights, full=False):
    dims = len(weights), len(weights[0]), len(weights[0][0])
    require(all(len(row)==dims[1] for row in weights), 'ragged tensor')
    require(all(len(row)==dims[2] for layer in weights for row in layer), 'ragged tensor')
    require(all(F(v)>=0 for layer in weights for row in layer for v in row), 'negative weight')
    m,k,l = dims
    @lru_cache(None)
    def value(a,b,c):
        if not a or not b or not c:
            return F(0)
        i = (a & -a).bit_length()-1
        rest = a & ~(1<<i)
        best = value(rest,b,c)
        for j in range(k):
            if not b>>j&1:
                continue
            for h in range(l):
                if c>>h&1:
                    best = max(best, F(weights[i][j][h])+value(rest,b&~(1<<j),c&~(1<<h)))
        return best
    total = value((1<<m)-1,(1<<k)-1,(1<<l)-1)
    players = [z3.FreshReal('p') for _ in range(m+k+l)]
    constraints = [p>=0 for p in players]+[sum(players)==Q(total)]
    if full:
        for a,b,c in product(range(1<<m),range(1<<k),range(1<<l)):
            ids = [i for i in range(m) if a>>i&1]+[m+j for j in range(k) if b>>j&1]+[m+k+h for h in range(l) if c>>h&1]
            if ids:
                constraints.append(sum(players[i] for i in ids)>=Q(value(a,b,c)))
    else:
        constraints.extend(players[i]+players[m+j]+players[m+k+h]>=Q(weights[i][j][h]) for i,j,h in product(range(m),range(k),range(l)))
    solver=z3.Solver(); solver.add(*constraints)
    status=solver.check()
    require(status in (z3.sat,z3.unsat), 'core feasibility UNKNOWN')
    return players,constraints,total,status==z3.sat


def check(weights, full=False):
    players,constraints,total,feasible=core(weights,full)
    result=dict(weights=weights,T=str(total),core_nonempty=feasible,full_coalitions=full)
    if not feasible or total==0:
        return result
    x,xst=selector(constraints,players,True)
    z,zst=selector(constraints,players,False)
    rho=sum(abs(a-b) for a,b in zip(x,z))/total
    maxima=[optimize(constraints,p,True) for p in players]
    ratios=[a/b for a,b in zip(x,maxima) if b]
    result.update(Lmin=list(map(str,x)),Lmax=list(map(str,z)),rho=str(rho),core_maxima=list(map(str,maxima)),min_coordinate_fraction=str(min(ratios)),Lmin_stages=xst,Lmax_stages=zst)
    return result


def lucas_test(weights):
    """Select an optimal perfect matching, relabel it diagonally, apply Lucas."""
    opts=[]
    for b,c in product(permutations(range(2)),repeat=2):
        opts.append((sum(weights[i][b[i]][c[i]] for i in range(2)),b,c))
    total,b,c=max(opts)
    a=[[[weights[i][b[j]][c[h]] for h in range(2)] for j in range(2)] for i in range(2)]
    slack1=2*a[0][0][0]+a[1][1][1]-a[0][0][1]-a[0][1][0]-a[1][0][0]
    slack2=a[0][0][0]+2*a[1][1][1]-a[1][1][0]-a[1][0][1]-a[0][1][1]
    return total,slack1>=0 and slack2>=0,[slack1,slack2]
