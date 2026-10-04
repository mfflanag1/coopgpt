"""Exact stress checks and independent rational LP-dual certificate validation.
The analytic theorem is in SHAPLEY_THEOREM.txt; grids alone are not its proof.
"""
from collections import defaultdict
from fractions import Fraction as F
from itertools import permutations, product
from pathlib import Path
import hashlib
import json
import random

ROOT = Path(__file__).resolve().parent
ORDERS = tuple(permutations(range(4)))


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def worth(c, mask):
    left = sum(c[i] for i in (0, 1) if mask >> i & 1)
    right = sum(c[i] for i in (2, 3) if mask >> i & 1)
    return min(left, right)


def shapley(c):
    values = [worth(c, mask) for mask in range(16)]
    sums = [F(0)] * 4
    for order in ORDERS:
        mask = 0
        for i in order:
            after = mask | (1 << i)
            sums[i] += values[after] - values[mask]
            mask = after
    return tuple(x / 24 for x in sums)


def first_coordinate_formula(c):
    a, b, c, d = c
    total = min(a + b, c + d)
    bracket = (min(a, c) + min(a, d) + min(a+b, c) - min(b, c)
               + min(a+b, d) - min(b, d) + min(a, c+d))
    return bracket / 12 + (total - min(b, c+d)) / 4


def check_profile(c, phi):
    total = worth(c, 15)
    require(sum(phi) == total and min(phi) >= 0, 'Shapley efficiency/nonnegativity')
    y = tuple(F(6, 5) * x for x in phi)
    require(sum(y) == F(6, 5)*total, 'budget')
    for mask in range(1, 16):
        v = worth(c, mask)
        phis = sum(phi[i] for i in range(4) if mask >> i & 1)
        require(6*phis >= 5*v, 'coalition factor')
        require(sum(y[i] for i in range(4) if mask >> i & 1) >= v, 'coalition payment')
    transforms = [(0,1,2,3), (1,0,2,3), (2,3,0,1), (3,2,0,1)]
    for i, order in enumerate(transforms):
        require(phi[i] == first_coordinate_formula(tuple(c[j] for j in order)), 'formula identity')
        marginal = total - worth(c, 15 ^ (1 << i))
        require(phi[i] >= marginal/2, 'removal marginal bound')
        require(y[i] >= F(3,5)*marginal, 'stronger fairness bound')
    if not total:
        require(y == (0,0,0,0), 'zero-flow boundary')


def verify_dual(report):
    """Construct >= rows from public game definitions, without a solver/matrix."""
    coef = defaultdict(F)
    rhs = F(0)
    profiles = set()
    for row in report['dual_support']:
        weight = F(row['multiplier'])
        require(weight >= 0, 'negative dual multiplier')
        c = tuple(map(F, row['profile']))
        require(len(c) == 4 and min(c) >= 0, 'invalid profile')
        profiles.add(c)
        kind = row['kind']
        if kind == 'budget':
            total = worth(c,15)
            coef['beta'] += weight*total
            rhs -= weight*total
            for i in range(4):
                coef[(c,i)] -= weight
        elif kind == 'cover':
            mask = row['coalition']
            require(isinstance(mask,int) and 1 <= mask <= 15, 'invalid coalition')
            rhs += weight*worth(c,mask)
            for i in range(4):
                if mask >> i & 1:
                    coef[(c,i)] += weight
        elif kind == 'monotone':
            low = tuple(map(F,row['low_profile']))
            i = row['owner']
            require(len(low)==4 and min(low)>=0 and isinstance(i,int) and 0<=i<4,
                    'invalid monotonicity row')
            require(low[i] < c[i] and all(low[j]==c[j] for j in range(4) if j!=i),
                    'monotonicity profiles disagree')
            profiles.add(low)
            coef[(c,i)] += weight
            coef[(low,i)] -= weight
        else:
            raise RuntimeError('unknown row type')
    require(coef.pop('beta',F(0)) == 1, 'beta coefficient is not one')
    require(all(x <= 0 for x in coef.values()), 'uneliminated positive payment coefficient')
    require(rhs == F(1,8), 'expected lower bound not obtained')
    # Weighted constraints give beta + sum(nonpositive*y) >= rhs. With y>=0,
    # this proves beta>=rhs for every rule containing the listed profiles.
    return {'lower_bound':str(rhs), 'rows':len(report['dual_support']),
            'profiles_in_certificate':len(profiles)}


def main():
    grid = tuple(map(F,[0,F(1,2),1,2,5]))
    cached = {c:shapley(c) for c in product(grid,repeat=4)}
    own = 0
    for c,phi in cached.items():
        check_profile(c,phi)
        for i in range(4):
            position = grid.index(c[i])
            if position:
                low = list(c); low[i] = grid[position-1]
                require(phi[i] >= cached[tuple(low)][i], 'grid own-capacity monotonicity')
                own += 1
    rng = random.Random(20261004)
    random_profiles = 200
    zero_halvings = 0
    for _ in range(random_profiles):
        c = tuple(F(rng.randrange(41),rng.randrange(1,8)) for _ in range(4))
        phi = shapley(c)
        check_profile(c,phi)
        for i in range(4):
            if c[i] == 0:
                zero_halvings += 1
                continue
            low = list(c); low[i] /= 2
            require(phi[i] >= shapley(tuple(low))[i], 'rational own-capacity monotonicity')
            own += 1
    witness = tuple(map(F,[2,1,1,1]))
    phi = shapley(witness)
    require(phi==(F(7,12),F(1,4),F(7,12),F(7,12)), 'sharp profile')
    require(phi[1]+phi[2]==F(5,6), 'sharp coalition')
    require(F(9,8)*(phi[1]+phi[2])<1, 'insufficient scaling witness')
    certificates = {}
    for filename in ('lp-012.json','lp-01234.json'):
        report = json.loads((ROOT/filename).read_text())
        certificates[filename] = verify_dual(report)
        mutations = []
        bad = json.loads(json.dumps(report))
        bad['dual_support'][0]['multiplier'] = '-1'
        mutations.append(('negative multiplier', bad))
        bad = json.loads(json.dumps(report))
        for row in bad['dual_support']:
            row['multiplier'] = str(2*F(row['multiplier']))
        mutations.append(('wrong beta coefficient', bad))
        bad = json.loads(json.dumps(report))
        row = next(r for r in bad['dual_support'] if r['kind']=='monotone')
        row['low_profile'][(row['owner']+1)%4] += 1
        mutations.append(('invalid monotonicity pair', bad))
        bad = json.loads(json.dumps(report))
        row = next(r for r in bad['dual_support'] if r['kind']=='cover')
        row['coalition'] = 0
        mutations.append(('invalid coalition mask', bad))
        bad = json.loads(json.dumps(report))
        extra = dict(next(r for r in bad['dual_support'] if r['kind']=='cover'))
        extra['multiplier'] = str(1+sum(F(r['multiplier']) for r in bad['dual_support']))
        bad['dual_support'].append(extra)
        mutations.append(('positive payment residual', bad))
        if filename == 'lp-012.json':
            bad = json.loads(json.dumps(report))
            bad['dual_support'][0]['coalition'] = 1
            mutations.append(('insufficient right side', bad))
        for label, bad in mutations:
            try:
                verify_dual(bad)
            except RuntimeError:
                pass
            else:
                raise RuntimeError('invalid certificate accepted: '+label)
        certificates[filename]['rejected_corruptions'] = len(mutations)
    n = len(cached)+random_profiles
    print(json.dumps({'status':'passed','arithmetic':'fractions.Fraction',
        'scope':'finite stress checks plus exact finite-profile dual lower bounds; continuum proof is separate',
        'grid':list(map(str,grid)), 'grid_profiles':len(cached),
        'seeded_rational_profiles':random_profiles,'random_seed':20261004,
        'coalition_checks':15*n,
        'removal_marginal_floor_checks':4*n,'strict_own_report_comparisons':own,'zero_halvings_skipped':zero_halvings,
        'count_note':'Scaled coverage/budget/fairness identities are not counted as independent extra checks.',
        'certificates':certificates,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2))

if __name__ == '__main__':
    main()
