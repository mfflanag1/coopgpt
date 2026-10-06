"""Exact substitutions for the two scoped divergent-cost witnesses."""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from verify_continuous import check, marginals, payments

rows = []
for k in (2, 3, 4, 8, 32, 216):
    c = ((Q(1, 3),) * 3,) * k
    y = payments(c)
    fair = tuple(max(v, m / k) for v, m in zip(y, marginals(c)))
    check(y == (Q(1, k) + Q(4, 9),) * (3 * k), 'coordinate formula')
    check(sum(y) == 3 + Q(4 * k, 3), 'linear factor')
    check(fair == y, 'floor top-up inactive')
    rows.append({'k': k, 'base_and_fair_factor': str(sum(y))})
mixtures = []
for r in (3, 4, 8, 32, 216):
    # Independent aggregate calculation from the rejected rule's coefficients.
    z0, z1 = Q(1, r), Q(1, 2)
    c0 = r * ((1 - z0) / r) + r * z0
    c1 = r * ((1 - z1) / 2) + r * z1
    total = (c0 + c1) / 2
    check(total == 1 - Q(1, 2 * r) + Q(3 * r, 8), 'mixture cost formula')
    mixtures.append({'r': r, 'rejected_mixture_factor': str(total)})
result = {'status': 'PASS', 'scope': 'Exact substitutions; the unbounded claims rely on the written identities.',
          'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'payment_source_sha256': hashlib.sha256(Path(__file__).with_name('verify_continuous.py').read_bytes()).hexdigest(),
          'many_altered': rows, 'failed_mixture': mixtures}
Path(__file__).with_name('SCOPE_CHECKS.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
