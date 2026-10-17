"""Independent exact audit, using subset-incidence aggregation, not LP output.

The certificate is input data. All threshold coefficient rows are independently
reconstructed from low/high min-three game values for every subset of 16 owners.
"""
from fractions import Fraction
from math import comb
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parent.parent
CERT = CAMPAIGN / 'unrestricted/POSITIVE_MARGINAL_FINITE_CERT_N16_S4_FACTOR5.json'
raw = CERT.read_bytes()
data = json.loads(raw)
N = data['N']
S = data['s']

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

require((N, S) == (16, 4), 'Unexpected certificate dimensions')

def binom(n, k):
    return comb(n, k) if n >= 0 and 0 <= k <= n else 0

def claimed_row(q, k, t):
    z = N - q - k
    return [Fraction(sum(comb(k, j) *
                         (binom(z, h-j) - (q-1)*binom(z, h-j-1))
                         for j in range(t+1, k+1)), comb(N-1, h))
            for h in range(N)]

def subset_incidence_row(q, k, t):
    # Resources are integer-scaled by k. The q protected owners occupy slots
    # 0..q-1, the centers q..q+k-1, and every remaining owner is a genuine null.
    # For any game increment delta and h-subset predecessor R, summing the
    # protected owners' marginal increments equals
    #   sum_{|A|=h+1} |A intersect S| delta(A)
    # - sum_{|A|=h} (q-|A intersect S|) delta(A).
    # This independently sums by final coalition A, not by focal marginal.
    numerator = [0]*N
    keeper_mask = (1 << q)-2
    center_mask = ((1 << k)-1) << q
    protected_mask = (1 << q)-1
    changed_subsets = 0
    for mask in range(1 << N):
        size = mask.bit_count()
        protected = (mask & protected_mask).bit_count()
        center_sum = (mask & center_mask).bit_count()
        leaf_low = k*(mask & keeper_mask).bit_count() + t*(mask & 1)
        leaf_high = leaf_low + (mask & 1)
        low = min(center_sum, center_sum, leaf_low)
        high = min(center_sum, center_sum, leaf_high)
        delta = high-low
        require(delta in (0, 1), 'Unexpected raw min-three increment')
        changed_subsets += delta
        if size:
            numerator[size-1] += protected*delta
        if size < N:
            numerator[size] -= (q-protected)*delta
    # Numerators measure increment/epsilon, epsilon=1/k, as in the certificate.
    return [Fraction(numerator[h], comb(N-1, h)) for h in range(N)], changed_subsets

def pure_coverage_row():
    numerator = [0]*N
    # v(A)=1 exactly when all three pure-resource owners occur in A. Same
    # incidence identity, now applied to v itself and protected owners {0,1,2}.
    for mask in range(1 << N):
        size = mask.bit_count()
        present = (mask & 7).bit_count()
        worth = int(present == 3)
        if size:
            numerator[size-1] += present*worth
        if size < N:
            numerator[size] -= (3-present)*worth
    return [Fraction(numerator[h], comb(N-1, h)) for h in range(N)]

coverage = pure_coverage_row()
require(coverage == [Fraction(3*h*(h-1), (N-1)*(N-2))
                     for h in range(N)], 'Pure-three coverage mismatch')
beta = Fraction(data['coverage_weight'])
require(beta == 5, 'Unexpected stated bound')
coefficients = [beta*c for c in coverage]
rows = []
for record in data['transition_weights']:
    q, k, t = (record[name] for name in ('q', 'k', 't'))
    weight = Fraction(record['weight'])
    require(2 <= q <= S and 1 <= k <= N-q and 0 <= t < k,
            'Invalid fixed-owner transition')
    require(weight >= 0, 'Negative dual multiplier')
    exact, changed = subset_incidence_row(q, k, t)
    require(exact == claimed_row(q, k, t), 'Threshold formula mismatch')
    coefficients = [v + weight*d for v, d in zip(coefficients, exact)]
    rows.append({'q': q, 'k': k, 't': t, 'weight': str(weight),
                 'changed_raw_subsets': changed,
                 'exact_normalized_transition': list(map(str, exact))})

require(len(rows) == 14, 'Unexpected transition count')
require(coefficients == list(map(Fraction, data['verification_coefficients'])),
        'Published coefficient vector mismatch')
slacks = [1-v for v in coefficients]
require(all(s >= 0 for s in slacks), 'Invalid dual inequality')
out = {
    'status': 'PASS',
    'certificate_sha256': hashlib.sha256(raw).hexdigest(),
    'finite_fixed_owners': N,
    'maximum_protected_coalition': S,
    'certified_funding_lower': str(beta),
    'transition_rows': len(rows),
    'raw_transition_subset_profiles': len(rows)*(1 << N),
    'raw_coverage_subset_profiles': 1 << N,
    'rational_dual_components': N,
    'dual_coefficients': list(map(str, coefficients)),
    'dual_slacks': list(map(str, slacks)),
    'minimum_dual_slack': str(min(slacks)),
    'rows': rows,
    'scope': 'Fixed nonnegative report-independent whole-owner marginal weights. '
             'Analytical label symmetrization is separately audited. '
             'Not a lower against arbitrary mechanisms.'
}
(HERE/'independent_replay.json').write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps({key: value for key, value in out.items() if key != 'rows'}, indent=2))
