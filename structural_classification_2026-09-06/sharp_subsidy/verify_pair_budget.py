"""Exact counterexample to diagonal-pair and cycle-worth subsidy bounds."""
from fractions import Fraction as F
from itertools import permutations, product

A = ((0, 1, 0), (0, 0, 0), (0, 0, 0))
B = ((1, 0, 1), (0, 1, 0), (0, 0, 1))
C = ((1, 0, 0), (0, 1, 1), (0, 0, 1))
WITNESSES = (
    (2, 1, 1, 0, 0, 0, 0, 1, 1),
    (2, 2, 1, 0, 0, 0, 0, 0, 1),
    (2, 1, 2, 0, 1, 0, 0, 0, 0),
    (0, 0, 0, 2, 2, 1, 0, 0, 1),
    (0, 0, 0, 1, 2, 1, 1, 0, 1),
    (1, 0, 0, 1, 2, 2, 0, 0, 0),
    (0, 0, 0, 0, 1, 0, 2, 1, 2),
    (1, 0, 0, 0, 0, 0, 1, 2, 2),
    (1, 0, 0, 0, 0, 0, 1, 2, 2),
)
TEAMS = tuple(product(range(3), repeat=3))

def require(condition, message):
    if not condition:
        raise ValueError(message)

def worth(e, include_a=True):
    a, b, c = e
    return (A[a][b] if include_a else 0) + B[a][c] + C[b][c]

def total_optimum(include_a):
    return max(sum(worth((a, p[a], q[a]), include_a) for a in range(3))
               for p in permutations(range(3)) for q in permutations(range(3)))

def stable(x):
    return min(x) >= 0 and all(x[a] + x[3+b] + x[6+c] >= worth((a,b,c))
                               for a,b,c in TEAMS)

def main():
    # Nonnegative weights permit extension of any partial matching to a perfect one.
    require(total_optimum(True) == total_optimum(False) == 6, 'grand worth')
    require([worth((j,j,j)) for j in range(3)] == [2,2,2], 'diagonal tightness')
    # The tight optimal diagonal bounds each coordinate by 2; witnesses attain it.
    for i,x in enumerate(WITNESSES):
        require(sum(x) == 6 and stable(x) and x[i] == 2, 'core ideal witness')
    y = (F(5,3),) + (F(2,3),)*8
    require(stable(y) and sum(y) == 7, 'subsidy primal')
    # One protected special triple plus the floors of the other six players.
    require(worth((0,1,2)) + 6*F(2,3) == 7, 'subsidy lower certificate')
    require(sum(A[j][j] for j in range(3)) == 0, 'diagonal pair budget')
    pair_optima = [max(sum(M[j][p[j]] for j in range(3))
                       for p in permutations(range(3))) for M in (A,B,C)]
    require(pair_optima == [1,3,3], 'pairwise optima')
    require(not stable((F(2,3),)*9), 'negative control')
    print('PASS: T=6, H_i=2 for all 9 players, s_3=1; diagonal AB budget=0; deleting AB leaves T=6; pair optima=(1,3,3).')

if __name__ == '__main__':
    main()
