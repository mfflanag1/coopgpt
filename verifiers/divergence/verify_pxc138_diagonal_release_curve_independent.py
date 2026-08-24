#!/usr/bin/env python3
"""Standalone exact replay of the PXC138 sharp release curve.

This audit imports no project game, LP, selector, or PXC136--138 code.  It
checks the two primal certificates against the six-row core description and
the parametric upper dual against the lower-envelope coalition values used
by its support.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


N, T = 6, F(4)
X = (F(4, 3), F(1, 3), F(1, 3), F(1, 3), F(4, 3), F(1, 3))
Z = (F(1), F(1), F(0), F(0), F(1), F(1))
ROWS = {14: F(1), 19: F(3), 20: F(1), 35: F(2), 44: F(1), 49: F(3)}
# Values on every coalition used by the independent dual certificate.  Each
# is also obtained by minimizing over the displayed six-row core polytope.
DUAL_VALUES = {3: F(1), 9: F(0), 14: F(1), 19: F(3), 20: F(1),
               33: F(1), 35: F(2), 44: F(1), 49: F(3), 61: F(3)}


def row_sum(row, mask):
    return sum(row[i] for i in range(N) if mask >> i & 1)


def solve_square(matrix, rhs):
    aug = [list(map(F, row)) + [F(value)] for row, value in zip(matrix, rhs)]
    for col in range(N):
        pivot = next((row for row in range(col, N) if aug[row][col]), None)
        if pivot is None:
            return None
        aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = aug[col][col]
        aug[col] = [value / scale for value in aug[col]]
        for row in range(N):
            if row == col or not aug[row][col]:
                continue
            scale = aug[row][col]
            aug[row] = [a - scale * b for a, b in zip(aug[row], aug[col])]
    return tuple(aug[row][-1] for row in range(N))


def lower_envelope():
    inequalities = []
    for i in range(N):
        inequalities.append((tuple(F(int(i == j)) for j in range(N)), F(0)))
    for mask, bound in ROWS.items():
        inequalities.append((tuple(F(int(mask >> j & 1)) for j in range(N)), bound))
    total_row = tuple(F(1) for _ in range(N))
    vertices = set()
    for active in itertools.combinations(range(len(inequalities)), N - 1):
        matrix = [total_row] + [inequalities[index][0] for index in active]
        rhs = [T] + [inequalities[index][1] for index in active]
        point = solve_square(matrix, rhs)
        if point is None:
            continue
        if all(sum(a * b for a, b in zip(normal, point)) >= bound
               for normal, bound in inequalities):
            vertices.add(point)
    if not vertices:
        raise AssertionError("empty sharp core polytope")
    values = tuple(min(row_sum(point, mask) for point in vertices) for mask in range(1 << N))
    if any(values[1 << i] != 0 for i in range(N)):
        raise AssertionError("sharp game lost singleton normalization")
    if any(values[mask] != value for mask, value in DUAL_VALUES.items()):
        raise AssertionError("independent lower envelope changed")
    return vertices, values


def certificates():
    pi0 = tuple(map(F, (F(23, 68), F(2, 17), F(1, 12), F(5, 102), F(5, 17), F(2, 17))))
    f0 = [[F(0)] * N for _ in range(N)]
    for (r, i), value in {
        (0, 1): F(23, 272), (0, 4): F(23, 136), (0, 5): F(23, 272),
        (1, 0): F(1, 17), (1, 2): F(1, 102), (1, 3): F(1, 51), (1, 4): F(1, 34),
        (2, 1): F(1, 48), (2, 4): F(1, 24), (2, 5): F(1, 48),
        (3, 1): F(5, 408), (3, 4): F(5, 204), (3, 5): F(5, 408),
        (4, 0): F(15, 68), (4, 2): F(5, 68),
        (5, 0): F(1, 17), (5, 3): F(1, 34), (5, 4): F(1, 34),
    }.items(): f0[r][i] = value
    ux0 = tuple(map(F, (F(4, 3), F(1, 3), F(1, 3), F(10, 51), F(20, 17), F(1, 3))))
    uz0 = tuple(map(F, (F(1), F(8, 17), 0, 0, F(1), F(8, 17))))

    pi1 = tuple(map(F, (F(1, 3), F(13, 108), F(1, 12), F(5, 108), F(8, 27), F(13, 108))))
    f1 = (
        tuple(map(F, (0, F(1, 12), 0, 0, F(1, 6), F(1, 12)))),
        tuple(map(F, (F(19, 324), F(1, 1296), F(1, 81), F(11, 648), F(5, 162), F(1, 1296)))),
        tuple(map(F, (0, F(1, 48), 0, 0, F(1, 24), F(1, 48)))),
        tuple(map(F, (0, F(5, 432), 0, 0, F(5, 216), F(5, 432)))),
        tuple(map(F, (F(35, 162), F(1, 324), F(23, 324), 0, F(1, 324), F(1, 324)))),
        tuple(map(F, (F(19, 324), F(1, 1296), 0, F(19, 648), F(5, 162), F(1, 1296)))),
    )
    ux1 = tuple(map(F, (F(4, 3), F(1, 3), F(1, 3), F(5, 27), F(32, 27), F(1, 3))))
    uz1 = tuple(map(F, (F(1), F(13, 27), 0, 0, F(1), F(13, 27))))
    return (pi0, tuple(map(tuple, f0)), ux0, uz0), (pi1, f1, ux1, uz1)


def replay_primal(cert, t, values):
    pi, flow, ux, uz = cert
    diag = tuple(X[i] * Z[i] / T**2 for i in range(N))
    assert sum(pi) == 1
    for r in range(N):
        assert sum(flow[r]) == pi[r] and min(flow[r]) >= 0
        assert flow[r][r] <= t * diag[r]
        for mask in range(1, (1 << N) - 1):
            assert T * row_sum(flow[r], mask) >= pi[r] * values[mask]
    for i in range(N):
        assert sum(flow[r][i] for r in range(N)) == pi[i]
        assert 0 <= ux[i] <= min(X[i], T*pi[i])
        assert 0 <= uz[i] <= min(Z[i], T*pi[i])
    return sum(ux) + sum(uz) - T


def replay_dual():
    theta=F(45,17)
    alpha=tuple(map(F,(1,1,0,0,0,1))); beta=tuple(map(F,(1,0,1,1,1,0)))
    p=tuple(map(F,(0,0,1,1,1,0))); q=tuple(map(F,(0,1,0,0,0,1)))
    A=tuple(F(k,17) for k in (28,40,72,18,50,40)); B=tuple(F(k,17) for k in (50,0,-18,-18,10,0))
    lam={(0,19):F(7,17),(0,33):F(9,34),(0,61):F(5,34),
         (1,14):F(11,34),(1,19):F(25,34),(1,35):F(10,17),
         (2,14):F(11,34),(2,19):F(25,34),(2,33):F(10,17),(2,61):F(8,17),
         (3,3):F(2,17),(3,9):F(8,17),(3,19):F(5,34),(3,49):F(9,34),
         (4,19):F(25,34),(4,20):F(8,17),(4,49):F(25,34),
         (5,35):F(10,17),(5,44):F(11,34),(5,49):F(25,34)}
    defects=[]
    for i in range(N):
        assert alpha[i]+p[i]>=1 and beta[i]+q[i]>=1
        root=theta-A[i]-B[i]+sum(lam.get((i,s),0)*DUAL_VALUES[s] for r,s in lam if r==i)-T*(p[i]+q[i])
        assert root>=0
    for r in range(N):
        loads=[]
        for i in range(N):
            load=T*sum(w for (rr,s),w in lam.items() if rr==r and (s>>i)&1)
            loads.append(load)
            if i!=r: assert A[r]+B[i]>=load
        defects.append(loads[r]-A[r]-B[r])
    D=theta+sum(alpha[i]*X[i]+beta[i]*Z[i] for i in range(N))
    diag=tuple(X[i]*Z[i]/T**2 for i in range(N))
    E=sum(diag[i]*max(F(0),defects[i]) for i in range(N))
    return D,tuple(defects),E


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path); args=parser.parse_args()
    vertices,values=lower_envelope()
    c0,c1=certificates(); v0=replay_primal(c0,F(0),values); v1=replay_primal(c1,F(1,27),values)
    D,defects,E=replay_dual(); overlap=sum(min(a,b) for a,b in zip(X,Z))
    assert v0==F(45,17) and v1==overlap==F(8,3)
    assert D-T==v0 and E==F(9,17) and E/F(27)==overlap-v0
    assert D < T+overlap and D+E/F(27) == T+overlap
    payload={"claim":"standalone exact PXC138 sharp-curve replay","zero_value":str(v0),
             "breakpoint_value":str(v1),"breakpoint":"1/27","dual_objective":str(D),
             "dual_exposure":str(E),"dual_defects":list(map(str,defects)),
             "independent_core_vertices":len(vertices),"all_64_values_reconstructed":True,
             "omitting_diagonal_penalty_breaks_upper_bound":True,
             "exact_curve":"45/17+min(9t/17,1/51)",
             "scope":"independent rational certificate replay; general theorem still uses standard parametric LP duality"}
    rendered=json.dumps(payload,indent=2)+"\n"
    if args.output: args.output.write_text(rendered)
    print(rendered,end="")


if __name__=="__main__": main()
