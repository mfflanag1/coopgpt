"""Integer certificates; no optimization library is required."""
import json
from itertools import product
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def market(q):
    m = 2*q+1
    pairs = [[[int(i == j) for j in range(m)] for i in range(m)] for _ in range(3)]
    triples = [(s, q+s, s-1 if s else 2*q) for s in range(q)]
    for a, b, c in triples:
        pairs[0][a][b], pairs[1][a][c], pairs[2][b][c] = 2, 1, 2
    return m, pairs, triples


def rooted_colors(m, triples, root, sector):
    colors = {root: sector}
    pending = list(triples)
    while pending:
        progressed = False
        for edge in list(pending):
            seen = [v for v in edge if v in colors]
            if not seen:
                continue
            require(len(seen) == 1, 'incidence graph is not a tree')
            for k, v in enumerate(edge):
                if v not in colors:
                    colors[v] = k
            pending.remove(edge)
            progressed = True
        require(progressed, 'disconnected incidence graph')
    require(len(colors) == m, 'missing label')
    return colors


def check_cover(pay, pairs, m):
    require(len(pay) == 3*m and min(pay) >= 0, 'invalid payoff')
    for a, b, c in product(range(m), repeat=3):
        value = pairs[0][a][b]+pairs[1][a][c]+pairs[2][b][c]
        require(pay[a]+pay[m+b]+pay[2*m+c] >= value, 'uncovered triple')


def run():
    cases = []
    count = 0
    for q in range(1, 13):
        m, pairs, triples = market(q)
        T = 3*m
        witnesses = []
        for k, root in product(range(3), range(m)):
            colors = rooted_colors(m, triples, root, k)
            require(all(sum(colors[v] == j for j, v in enumerate(e)) >= 2 for e in triples), 'bad coloring')
            pay = [int(j == k)+2*int(colors[v] == j) for j in range(3) for v in range(m)]
            require(sum(pay) == T and pay[k*m+root] == 3, 'ideal witness failed')
            check_cover(pay, pairs, m)
            count += m**3
            witnesses.append(pay)
        y = [1]*(3*m)
        for a, b, c in triples:
            y[a] += 2
        check_cover(y, pairs, m)
        count += m**3
        require(sum(y) == T+2*q and min(y) >= 1, 'subsidy upper bound failed')
        used = [k*m+e[k] for e in triples for k in range(3)]
        require(len(set(used)) == 3*q, 'partial matching overlap')
        require(sum(pairs[0][a][b]+pairs[1][a][c]+pairs[2][b][c] for a,b,c in triples) == 5*q, 'partial matching worth')
        require(5*q+(3*m-3*q)-T == 2*q, 'dual bound failed')
        # A deliberately damaged subsidy witness must fail the same verifier.
        bad = y.copy()
        bad[triples[0][0]] -= 1
        try:
            check_cover(bad, pairs, m)
        except ValueError:
            pass
        else:
            raise ValueError('negative control accepted')
        cases.append({'q': q, 'm': m, 'T': T, 's': 2*q, 'H': [3]*(3*m), 'matching': triples, 'core_witnesses': witnesses, 'allocation': y})
    output = {'status': 'PASS', 'arithmetic': 'integer', 'q_range': [1,12], 'full_triple_checks': count, 'negative_controls': 12, 'cases': cases}
    Path(__file__).with_name('TREE_CERTIFICATES.json').write_text(json.dumps(output, indent=2)+'\n')
    print(json.dumps({k: v for k,v in output.items() if k != 'cases'}))


if __name__ == '__main__':
    run()
