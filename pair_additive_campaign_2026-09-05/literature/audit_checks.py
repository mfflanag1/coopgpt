"""Independent finite checks; no imports of the campaign verifier or solvers."""
from fractions import Fraction as Q
from itertools import product, permutations
from functools import lru_cache
import hashlib
import json
from pathlib import Path


def require(value, message):
    if not value:
        raise RuntimeError(message)


# Independent literal transcription of the full tensor from the printed matrices.
W = (((0, 1, 1), (3, 0, 1), (2, 0, 1)),
     ((3, 3, 2), (4, 0, 0), (4, 1, 1)),
     ((0, 1, 0), (4, 1, 1), (2, 0, 0)))
A = ((0, 0, 0), (2, 0, 1), (0, 1, 0))
B = ((0, 0, 1), (1, 0, 0), (0, 0, 0))
C = ((0, 1, 0), (3, 0, 0), (2, 0, 0))
require(all(W[i][j][k] == A[i][j]+B[i][k]+C[j][k]
            for i, j, k in product(range(3), repeat=3)), 'tensor transcription')
teams = [((i, j+3, k+6), W[i][j][k])
         for i, j, k in product(range(3), repeat=3)]
team_masks = [(sum(1 << u for u in team), w) for team, w in teams]


@lru_cache(None)
def worth(mask):
    if not mask:
        return 0
    first = mask & -mask
    choices = [worth(mask ^ first)]
    choices += [w + worth(mask ^ team_mask)
                for team_mask, w in team_masks
                if team_mask & first and mask & team_mask == team_mask]
    return max(choices)


match_values = [sum(W[i][p[i]][r[i]] for i in range(3))
                for p in permutations(range(3)) for r in permutations(range(3))]
require(max(match_values) == worth(511) == 8, 'integral worth')
points = {
    'x': tuple(Q(a, 6) for a in (2, 8, 5, 5, 5, 2, 14, 5, 2)),
    'z': tuple(Q(a, 2) for a in (0, 3, 2, 2, 3, 2, 3, 1, 0)),
    'y': tuple(Q(a) for a in (0, 0, 0, 3, 1, 1, 3, 0, 0)),
}
core_counts = {}
for name, p in points.items():
    slacks = [sum(p[u] for u in range(9) if mask & (1 << u))-worth(mask)
              for mask in range(512)]
    require(min(slacks) == 0 and sum(p) == 8, 'all-coalition core: '+name)
    core_counts[name] = {'coalitions': len(slacks), 'tight': slacks.count(0)}

# Entire minimax face, after the forced-coordinate reasoning in the audit:
# p(t)=(0,3/2,1,t,3/2,1,3/2,3/2-t,0).
base = tuple(Q(a, 2) for a in (0, 3, 2, 0, 3, 2, 3, 3, 0))
direction = (0, 0, 0, 1, 0, 0, 0, -1, 0)
lo, hi = None, None


def impose(c, d):
    # Impose c+d*t >= 0 with exact rational interval intersection.
    global lo, hi
    if d == 0:
        require(c >= 0, 'infeasible constant on minimax face')
    elif d > 0:
        bound = -Q(c)/d
        lo = bound if lo is None else max(lo, bound)
    else:
        bound = -Q(c)/d
        hi = bound if hi is None else min(hi, bound)


for u in range(9):
    impose(base[u], direction[u])
    impose(Q(3, 2)-base[u], -direction[u])
for team, w in teams:
    impose(sum(base[u] for u in team)-w, sum(direction[u] for u in team))
require((lo, hi) == (Q(1), Q(3, 2)), 'entire minimax interval')
require(tuple(base[u]+direction[u]*lo for u in range(9)) == points['z'],
        'left endpoint is descending selector')
require(tuple(sorted(points['x'])) == tuple(map(Q,
        ('1/3', '1/3', '1/3', '5/6', '5/6', '5/6', '5/6', '4/3', '7/3'))),
        'ascending sequence')
require(points['x'][3]/points['y'][3] == Q(5, 18), 'protection fraction')
require(sum(abs(a-b) for a, b in zip(points['x'], points['z']))/8 == Q(11, 24),
        'normalized distance')
root = Path(__file__).resolve().parents[1]
result = {
    'status': 'PASS', 'arithmetic': 'standard-library exact Fraction',
    'perfect_matchings': len(match_values), 'integral_T': 8,
    'optimal_perfect_matchings': match_values.count(8),
    'core_checks': core_counts,
    'entire_minimax_face_t_interval': [str(lo), str(hi)],
    'ratio_d': '5/18', 'rho': '11/24',
    'reviewed_sha256': {str(root/f): hashlib.sha256((root/f).read_bytes()).hexdigest()
                        for f in ('COUNTEREXAMPLE.md', 'verify_rational.py')},
    'scope': 'Finite arithmetic and interval check, supplementing conventional universal proofs',
}
print(json.dumps(result, indent=2))
