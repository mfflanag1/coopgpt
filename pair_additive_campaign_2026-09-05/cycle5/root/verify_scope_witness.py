"""Exact whole-core witnesses and the within-sector order reversal.

The reversal excludes any class requiring a fixed within-sector payoff order
on the whole core. The external theorem's hypotheses still require source review.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def main():
    raw = (ROOT/'calibration/reduced_candidate.json').read_bytes()
    source = json.loads(raw)
    A, B, C = [[[F(v) for v in row] for row in matrix]
               for matrix in source['matrices']]
    require(all(len(matrix) == 7 and all(len(row) == 7 for row in matrix)
                for matrix in (A, B, C)), 'matrix shapes')
    require(all(v >= 0 for matrix in (A, B, C) for row in matrix for v in row),
            'nonnegative pairs')

    def value(team):
        i, j, k = team
        return A[i][j]+B[i][k]+C[j][k]

    def players(team):
        i, j, k = team
        return i, 7+j, 14+k

    matching = source['matching']
    require(sorted(v for team in matching for v in players(team)) == list(range(21)),
            'perfect matching')
    T = sum(map(value, matching))
    require(T == 15, 'matching worth')
    u = list(map(F, source['floor_witness']))
    y = list(map(F, source['ideal_witness']))
    checked = 0
    for point in (u, y):
        require(len(point) == 21 and min(point) >= 0 and sum(point) == T,
                'nonnegative efficient cover')
        for team in product(range(7), repeat=3):
            require(sum(point[v] for v in players(team)) >= value(team),
                    'induced triple cover')
            checked += 1
    require(u[0] > u[3] and y[0] < y[3], 'within-sector payoff reversal')
    report = dict(status='PASS', source_sha256=hashlib.sha256(raw).hexdigest(),
                  complete_triple_checks=checked, matching_worth=str(T),
                  coordinate_pair=['a0', 'a3'],
                  first_cover_difference=str(u[0]-u[3]),
                  second_cover_difference=str(y[0]-y[3]),
                  conclusion='No fixed order of these two players holds throughout the full core; relabeling cannot remove this reversal',
                  limitation='This excludes fixed-order core classes only, not all historical core representations')
    (ROOT/'scope_witness_checks.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
