"""Solver-free exact checks for the finite witness and its proof identities."""
from fractions import Fraction as F
from itertools import product
import json


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


A = ((0, 0, 0), (2, 0, 1), (0, 1, 0))
B = ((0, 0, 1), (1, 0, 0), (0, 0, 0))
C = ((0, 1, 0), (3, 0, 0), (2, 0, 0))
teams = {(u, 3+v, 6+w): A[u][v]+B[u][w]+C[v][w]
         for u, v, w in product(range(3), repeat=3)}
matching = ((0, 5, 8), (1, 3, 7), (2, 4, 6))
require(sorted(sum((list(t) for t in matching), [])) == list(range(9)),
        'matching must partition all players')
require([teams[t] for t in matching] == [1, 3, 4], 'matching weights')
T = sum(teams[t] for t in matching)
x = tuple(map(F, ('1/3', '4/3', '5/6', '5/6', '5/6', '1/3', '7/3', '5/6', '1/3')))
z = tuple(map(F, ('0', '3/2', '1', '1', '3/2', '1', '3/2', '1/2', '0')))
y = tuple(map(F, ('0', '0', '0', '3', '1', '1', '3', '0', '0')))

for name, point in (('x', x), ('z', z), ('ideal_d_witness', y)):
    require(all(v >= 0 for v in point), name + ' nonnegativity')
    require(sum(point) == T, name + ' total')
    require(all(sum(point[j] for j in team) >= weight
                for team, weight in teams.items()), name + ' triple cover')
    require(all(sum(point[j] for j in team) == teams[team]
                for team in matching), name + ' matching equalities')

# Identity underlying the second leximin level: the sum of the last two
# matching rows, less crossing row (b,f,g), equals c+d+e+h-f.
def row(team):
    return tuple(int(j in team) for j in range(9))

crossing = (1, 5, 6)
identity = tuple(a+b-c for a, b, c in
                 zip(row(matching[1]), row(matching[2]), row(crossing)))
require(identity == (0, 0, 1, 1, 1, -1, 0, 1, 0), 'budget identity')
require(teams[matching[1]]+teams[matching[2]]-teams[crossing] == 3,
        'budget right-hand side')
require(all(x[j] == F(1, 3) for j in matching[0]), 'first floor')
require(all(x[j] == F(5, 6) for j in (2, 3, 4, 7)), 'second floor')
require(F(5, 6)*4 == 3+F(1, 3), 'second floor bound attained')
require(x[1] == 3-x[3]-x[7] and x[6] == 4-x[2]-x[4],
        'remaining leximin coordinates forced')

# Exact arithmetic supporting the descending-selector proof in the note.
require(teams[crossing] == 4 and teams[(0, 4, 6)] == 3
        and teams[(0, 3, 8)] == 1, 'minimax proof weights')
require(z[1] == z[4] == z[6] == F(3, 2), 'forced top level')
require(z[0] == z[8] == 0 and z[5] == z[2] == z[3] == 1
        and z[7] == F(1, 2), 'remaining descending levels')
require(y[3] == 3 and x[3]/y[3] == F(5, 18), 'ideal ratio')
require(F(5, 18) < F(1, 3), 'strict failure')
rho = sum(abs(a-b) for a, b in zip(x, z))/T
require(rho == F(11, 24), 'selector distance')
print(json.dumps({'status': 'PASS', 'arithmetic': 'Python standard-library Fraction',
                  'team_checks': 81, 'T': T, 'ideal_d': '3',
                  'coordinate_fraction': '5/18', 'rho': str(rho),
                  'scope': 'finite witness and conventional-proof identities'}, indent=2))
