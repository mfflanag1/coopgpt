"""Exact finite calibrations for the bounded unicyclic attempt.

The all-size statements and scope limits are proved in BOUNDED_UNICYCLE_ATTEMPT.md.
These checks do not certify the general one-third conjecture.
"""
from collections import Counter
from fractions import Fraction as F
from itertools import product
import json
from tree_certificate import market, rooted_colors, check_cover, require
from broken_ring import construct as broken_ring


def topology(m, P):
    require(len({(s, e[s]) for e in P for s in range(3)}) == 3*len(P), 'P overlaps')
    graph = [set() for _ in range(m+len(P))]
    for k, e in enumerate(P):
        for j in e:
            graph[j].add(m+k)
            graph[m+k].add(j)
    seen = {0}
    pending = [0]
    while pending:
        for j in graph[pending.pop()]:
            if j not in seen:
                seen.add(j)
                pending.append(j)
    require(len(seen) == len(graph), 'disconnected')
    # Count incidences with multiplicity, including repeated-label P teams.
    return 3*len(P) - (m+len(P)) + 1


def run():
    cases = checks = 0
    for q in range(1, 6):
        m, pairs, P = market(q)
        require(topology(m, P) == 0, 'source is not a tree')
        unmatched = [[j for j in range(m) if all(e[s] != j for e in P)] for s in range(3)]
        a = unmatched[0][0]
        b = next(j for j in unmatched[1] if j != a)
        for clone_label in range(m):
            size = m+1
            labels = list(range(m)) + [clone_label]
            cloned = [[[M[i][j] for j in labels] for i in labels] for M in pairs]
            extended = P + [(a, b, m)]
            require(topology(size, extended) == 1, 'extension is not unicyclic')
            sparse = [[[0]*size for _ in range(size)] for _ in range(3)]
            for A, B, C in [(j,j,j) for j in range(size)] + extended:
                for k, i, j in [(0,A,B),(1,A,C),(2,B,C)]:
                    sparse[k][i][j] = cloned[k][i][j]
            for sector, root in product(range(3), range(m)):
                colors = rooted_colors(m, P, root, sector)
                x = [int(s == sector)+2*int(colors[j] == s) for s in range(3) for j in range(m)]
                lift = [x[s*m+j] for s in range(3) for j in labels]
                require(sum(lift) == 3*size, 'cloned total')
                check_cover(lift, cloned, size)
                check_cover(lift, sparse, size)
                checks += 2*size**3
                require(lift[sector*size+root] == 3, 'old ideal not attained')
                if root == clone_label:
                    require(lift[sector*size+m] == 3, 'clone ideal not attained')
            # Diagonal tightness caps every coordinate at 3. Thus the lifted
            # witnesses prove the complete H vector equals 3 in both markets.
            weight = lambda mats, e: mats[0][e[0]][e[1]]+mats[1][e[0]][e[2]]+mats[2][e[1]][e[2]]
            oldJ = F(sum(weight(pairs,e) for e in P)) + (3*m-3*len(P))-3*m
            newJ = F(sum(weight(sparse,e) for e in extended)) + (3*size-3*len(extended))-3*size
            h = m-len(P)
            loss = F(2,m)+F(1,3*h)+F(1,3*(h-1))
            require(newJ/(3*size) >= oldJ/(3*m)-loss, 'transfer lower bound')
            cases += 1
    split_cases = 0
    for b in range(2, 5):
        d = broken_ring(b)
        m, P, pairs = d['m'], d['P'], d['pairs']
        for j in range(b):
            # The first ring team uses cycle label j in sector A. Move that
            # incidence to its clone; retain the other cycle incidence at j.
            splitP = list(P)
            splitP[j] = (m, P[j][1], P[j][2])
            size = m+1
            require(topology(size, splitP) == 0, 'split is not a tree')
            labels = list(range(m))+[j]
            cloned = [[[M[a][c] for c in labels] for a in labels] for M in pairs]
            sparse = [[[0]*size for _ in range(size)] for _ in range(3)]
            for A, B, C in [(k,k,k) for k in range(size)] + splitP:
                for k, a, c in [(0,A,B),(1,A,C),(2,B,C)]:
                    sparse[k][a][c] = cloned[k][a][c]
            for x in d['core_witnesses']:
                lift = [x[s*m+a] for s in range(3) for a in labels]
                require(sum(lift) == 3*size, 'split total')
                check_cover(lift, sparse, size)
                checks += size**3
            weight = lambda mats, e: mats[0][e[0]][e[1]]+mats[1][e[0]][e[2]]+mats[2][e[1]][e[2]]
            oldJ = sum(weight(pairs,e) for e in P)-3*len(P)
            newJ = sum(weight(sparse,e) for e in splitP)-3*len(splitP)
            require(newJ == oldJ, 'split exact obstruction calibration')
            split_cases += 1
    # Repeated-label cycle: split one of the two parallel incidences.
    require(topology(4, [(0,0,1),(1,2,3)]) == 1, 'repeated-label unicycle')
    require(topology(5, [(4,0,1),(1,2,3)]) == 0, 'repeated-label split')
    barriers = []
    for b in range(4, 33):
        m = 4*b
        P = [(j,(j+1)%b,b+j) for j in range(b)] + [(2*b+2*j,2*b+2*j+1,j) for j in range(b)]
        require(topology(m, P) == 1, 'ring topology')
        degrees = Counter(j for e in P for j in e)
        require(Counter(degrees.values()) == {1:3*b, 3:b}, 'label degrees')
        L = [sum(degrees[e[s]] == 1 for e in P) for s in range(3)]
        require(L == [b]*3, 'sector leaf counts')
        h = m-len(P)
        alpha, beta, delta = F(1,h), 1-F(1,h), 1-F(2,h)
        shortfall = max(F(0), b*delta-h*min(b*alpha,beta-delta))
        require(shortfall == b-2, 'raw shortfall identity')
        require(3*shortfall-b == 2*b-6 > 0, 'donor budget obstruction')
        barriers.append({'b':b,'demand':str(3*shortfall),'capacity':b,'gap':2*b-6})
    # A damaged purported feasible budget must be rejected by the same check.
    def feasible(demand, capacity):
        require(demand <= capacity, 'insufficient donor capacity')
    try:
        feasible(F(barriers[0]['demand']), barriers[0]['capacity'])
    except ValueError:
        pass
    else:
        raise ValueError('negative control accepted')
    print(json.dumps({'status':'PASS','selective_clone_calibrations':cases,
                      'integer_team_checks':checks,'cycle_split_calibrations':split_cases,
                      'repeated_label_topology_checks':2,'unicyclic_budget_barriers':len(barriers),
                      'first_barrier':barriers[0],'negative_controls':1}))


if __name__ == '__main__':
    run()
