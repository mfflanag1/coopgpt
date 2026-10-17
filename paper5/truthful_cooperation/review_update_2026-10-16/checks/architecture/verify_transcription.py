"""Exact parameter and structural checks for the consolidation fragment.

This checks transcription and reusable-lemma hypotheses. It is not a proof
assistant or a replacement for the full frozen construction verifiers.
"""
from fractions import Fraction as Q
from math import isqrt
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).parent
FRAGMENT = HERE / 'latex_fragment.txt'
SOURCE = HERE / 'host_labels_before.json'
counts = {}

def check(condition, name):
    if not condition:
        raise AssertionError(name)
    counts[name] = counts.get(name, 0) + 1

text = FRAGMENT.read_text()
labels = re.findall(r'\\label\{([^}]+)\}', text)
refs = re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', text)
oldlabels = set(json.loads(SOURCE.read_text()))
check(len(labels) == len(set(labels)), 'unique_labels')
check(all(label.startswith('arch:') for label in labels), 'label_namespace')
check(not set(labels) & oldlabels, 'no_existing_label_collision')
check(not set(refs) - set(labels), 'all_fragment_references_internal')
stack = []
for action, name in re.findall(r'\\(begin|end)\{([^}]+)\}', text):
    if action == 'begin':
        stack.append(name)
    else:
        check(bool(stack) and stack.pop() == name, 'matched_environment')
check(not stack, 'no_unclosed_environment')
brace_depth = 0
for i, char in enumerate(text):
    if char not in '{}':
        continue
    preceding_backslashes = 0
    j = i - 1
    while j >= 0 and text[j] == '\\':
        preceding_backslashes += 1
        j -= 1
    if preceding_backslashes % 2:
        continue
    brace_depth += 1 if char == '{' else -1
    check(brace_depth >= 0, 'nonnegative_brace_depth')
check(brace_depth == 0, 'balanced_braces')

def realize_parameters(n, coeffs):
    eps, eta = Q(1, 100*n**6), Q(1, n**3)
    t = 1+(n-1)*eps
    check(all(coeffs[l] >= coeffs[l+1] >= 0 for l in range(1,n-1)), 'a_decreases')
    v = [Q(1)] + [(n-l)*coeffs[l] for l in range(1,n)] + [Q(0)]
    check(all(v[l] >= v[l+1] for l in range(n)), 'v_decreases')
    check(all(v[l] <= Q(n-l,n)-eta for l in range(1,n)), 'realization_baseline_gap')
    errors = [Q(n-1)] + [Q(n*n*(n-l),l)+(n-l-1)*v[l] for l in range(1,n)] + [Q(0)]
    check(all(0 <= e <= 2*n**3 for e in errors), 'error_coefficient_bound')
    values = [v[l]+eps*errors[l] for l in range(n+1)]
    delta = [v[l]-v[l+1] for l in range(n)]
    for l in range(n):
        check((values[l]-values[l+1])/t >= delta[l]-eta, 'normalized_endpoint_bound')
    check(Q(n*n,(n-1)**2) > t, 'raw_price_strictly_exceeds_T')
    return values, delta

tested_n = list(range(5,65)) + [100,256]
for n in tested_n:
    m = 1
    while (m+1)*(m+8) <= 2*(n-1):
        m += 1
    a = 1-Q(2*m+1,n)
    D = n-3*m-1
    check(a > 0 and m < n, 'owner_cap_positive')
    check(Q(m*(m+1),2) <= D, 'triangular_weight_threshold')
    for k in range(1,m+1):
        coeffs = [None]+[Q(n-l,n*n) if l < k else Q(0) for l in range(1,n)]
        values, delta = realize_parameters(n, coeffs)
        eps = Q(1,100*n**6)
        t = 1+(n-1)*eps
        r = n-k+1
        threshold = (values[k-1]-values[k])/t
        check(threshold >= a, 'owner_V_threshold')
        check(r*threshold >= D, 'owner_endpoint_total')
    if n < 9:
        continue
    def S(k):
        return sum(Q(k-l,n-l) for l in range(k))
    m = 1
    while m+1 < n and S(m+1) <= 1:
        m += 1
    check(2 <= m and 2*m < n, 'compressed_T_m_range')
    for mode in ('T','V'):
        if mode == 'T':
            sm = S(m)
            delta = [Q(m-l,n-l)/sm if l < m else Q(0) for l in range(n)]
        else:
            m = isqrt(2*n)
            a = 1/(1+sum(Q(m-l,n-l) for l in range(1,m)))
            delta = [a]+[a*Q(m-l,n-l) if l < m else Q(0) for l in range(1,n)]
        check(sum(delta) == 1, 'increment_sum')
        check(all(delta[l] >= delta[l+1] for l in range(n-1)), 'increments_decrease')
        check(delta[0] >= Q(1,n)+Q(1,n*n), 'increment_baseline_parameter')
        tails = [Q(0)]*(n+1)
        for l in reversed(range(n)):
            tails[l] = tails[l+1]+delta[l]
        coeffs = [None]+[tails[l]/(n-l) for l in range(1,n)]
        realize_parameters(n,coeffs)

out = {
    'status':'pass',
    'scope':'exact parameter and transcription checks; not full proof verification',
    'fragment_sha256':hashlib.sha256(FRAGMENT.read_bytes()).hexdigest(),
    'counts':counts,
    'tested_owner_counts':tested_n,
    'latex_compiled_by_this_script':False,
    'canonical_files_edited_by_this_script':False,
}
(HERE/'TRANSCRIPTION_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
