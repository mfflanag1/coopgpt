"""Frozen, offline, bounded comparison. No inference or cluster API calls."""
import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import signal
import time

from generate_cases import make_cases
from oracle import optimum
from solver import InvalidProducedPlan, greedy, solve
from verifier import strict_loads, validate_manifest, verify_plan

ROOT = Path(__file__).resolve().parent
POLICIES = ('priority_first', 'scarcity_first', 'exact')


def check_freeze():
    freeze = strict_loads((ROOT / 'FREEZE.json').read_text())
    for name, expected in freeze['sha256'].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Frozen input changed: ' + name)
    return hashlib.sha256((ROOT / 'FREEZE.json').read_bytes()).hexdigest()


def score(manifest, plan):
    checked = verify_plan(manifest, plan)
    if not checked['valid']:
        raise ValueError('Invalid produced plan: ' + str(checked['errors']))
    return checked['priority'], checked['admitted']


def properties(manifest, base, exact_plan):
    reversed_input = copy.deepcopy(manifest)
    reversed_input['nodes'].reverse()
    reversed_input['jobs'].reverse()
    for node in reversed_input['nodes']:
        node['gpus'].reverse()
    for job in reversed_input['jobs']:
        job['allowed_families'].reverse()
        job['allowed_owners'].reverse()
    relaxed = copy.deepcopy(manifest)
    for node in relaxed['nodes']:
        node['cpu_units'] += 1
        node['ram_mib'] += 1
    reduced = copy.deepcopy(manifest)
    reduced['nodes'][0]['gpus'] = []
    values = {}
    for key, altered in [('reversed', reversed_input), ('relaxed', relaxed), ('reduced', reduced)]:
        try:
            value = score(altered, solve(altered))
        except InvalidProducedPlan as error:
            error.context = key
            error.manifest = altered
            raise
        if value != optimum(altered):
            raise ValueError('Altered-instance oracle disagreement: ' + key)
        values[key] = list(value)
    if tuple(values['reversed']) != base:
        raise ValueError('Order invariance failed')
    if tuple(values['relaxed']) < base:
        raise ValueError('Resource relaxation decreased optimum')
    if tuple(values['reduced']) > base:
        raise ValueError('Resource removal increased optimum')
    corruption = None
    if len(exact_plan['placements']) >= 2:
        bad = copy.deepcopy(exact_plan)
        bad['placements'][1]['gpus'][0] = bad['placements'][0]['gpus'][0]
        corruption = verify_plan(manifest, bad)
        if corruption['valid']:
            raise ValueError('Duplicated GPU accepted')
    return {'objectives': values, 'gpu_reuse_rejection': corruption}


def summarize(rows):
    report = {}
    for cohort in ('constructed', 'generated', 'all'):
        subset = [r for r in rows if cohort == 'all' or r['kind'] == cohort]
        nonzero = [r for r in subset if r['optimum'][0] > 0]
        section = {'cases': len(subset), 'nonzero_optimum': len(nonzero),
                   'zero_optimum': len(subset) - len(nonzero),
                   'optimal_priority_total': sum(r['optimum'][0] for r in subset),
                   'corruption_checks': sum(r['properties']['gpu_reuse_rejection'] is not None for r in subset),
                   'policies': {}}
        for policy in POLICIES:
            achieved = sum(r['policies'][policy]['objective'][0] for r in subset)
            ratios = [Fraction(r['policies'][policy]['objective'][0], r['optimum'][0]) for r in nonzero]
            section['policies'][policy] = {
                'valid_plans': len(subset),
                'exact_objective_matches': sum(r['policies'][policy]['objective'] == r['optimum'] for r in subset),
                'priority_matches': sum(r['policies'][policy]['objective'][0] == r['optimum'][0] for r in subset),
                'secondary_tie_losses': sum(r['policies'][policy]['objective'][0] == r['optimum'][0] and r['policies'][policy]['objective'][1] < r['optimum'][1] for r in subset),
                'achieved_priority': achieved,
                'priority_regret': section['optimal_priority_total'] - achieved,
                'mean_priority_ratio_nonzero': str(sum(ratios, Fraction()) / len(ratios)) if ratios else None,
                'aggregate_priority_ratio': str(Fraction(achieved, section['optimal_priority_total'])) if nonzero else None,
            }
        report[cohort] = section
    return report


def capture_plan(plan):
    """Storage only: never pass this representation back into verification."""
    try:
        return json.loads(json.dumps(plan, allow_nan=False))
    except (ValueError, TypeError, OverflowError, RecursionError):
        return {'unserializable_python_type': type(plan).__name__, 'python_repr': repr(plan)}


def evaluate(case, audit=None):
    m = case['manifest']
    validate_manifest(m)
    original = copy.deepcopy(m)
    policies = {}
    if audit is not None:
        audit.update(case_id=case['case_id'], kind=case['kind'], policies=policies)
    for name in POLICIES:
        try:
            plan = solve(m) if name == 'exact' else greedy(m, name)
        except InvalidProducedPlan as error:
            policies[name] = {'plan': capture_plan(error.plan),
                              'verification': error.verification,
                              'invalid_python_repr': repr(error.plan)}
            raise
        policies[name] = {'plan': capture_plan(plan)}
        checked = verify_plan(m, plan)
        policies[name]['verification'] = checked
        if not checked['valid']:
            policies[name]['invalid_python_repr'] = repr(plan)
            raise ValueError('Invalid produced plan: ' + str(checked['errors']))
        policies[name]['objective'] = [checked['priority'], checked['admitted']]
    best = optimum(m)
    if audit is not None:
        audit['oracle_objective'] = list(best)
    if tuple(policies['exact']['objective']) != best:
        raise ValueError('Exact solver disagrees with independent optimum')
    if any(tuple(x['objective']) > best for x in policies.values()):
        raise ValueError('Candidate exceeds oracle optimum')
    checks = properties(m, best, policies['exact']['plan'])
    if m != original:
        raise ValueError('Input was mutated')
    return {'case_id': case['case_id'], 'kind': case['kind'], 'optimum': list(best),
            'policies': policies, 'properties': checks}


def run(output):
    if output.exists():
        raise ValueError('Refusing to overwrite existing run: ' + str(output))
    freeze_hash = check_freeze()
    cases = strict_loads((ROOT / 'cases.json').read_text())
    if cases != make_cases() or len(cases) != 140 or len({c['case_id'] for c in cases}) != 140:
        raise ValueError('Case suite does not match prospective generator')
    for c in cases:
        validate_manifest(c['manifest'])
    record = {'schema_version': 1, 'freeze_sha256': freeze_hash, 'status': 'running',
              'started_utc': datetime.now(timezone.utc).isoformat(), 'wall_ceiling_seconds': 180,
              'expected_cases': 140, 'rows': []}
    start = time.monotonic()

    def timeout(_signum, _frame):
        raise TimeoutError('Prospective 180-second ceiling exceeded')

    # Atomic exclusive creation closes the exists-then-write race. Hold the
    # handle so no later path replacement can overwrite an unrelated file.
    handle = output.open('x')
    old_handler = signal.signal(signal.SIGALRM, timeout)
    signal.setitimer(signal.ITIMER_REAL, 180)
    try:
        for case in cases:
            record['active_case'] = case['case_id']
            record['failed_case'] = {}
            record['rows'].append(evaluate(case, record['failed_case']))
            record.pop('failed_case')
        if check_freeze() != freeze_hash:
            raise ValueError('Freeze manifest changed during run')
        record.pop('active_case', None)
        record['status'] = 'complete'
    except Exception as error:
        record['status'] = 'failed'
        record['error'] = type(error).__name__ + ': ' + str(error)
        if isinstance(error, InvalidProducedPlan):
            record['producer_rejection'] = {
                'plan': capture_plan(error.plan), 'verification': error.verification,
                'invalid_python_repr': repr(error.plan),
                'context': getattr(error, 'context', 'original'),
                'altered_manifest': getattr(error, 'manifest', None),
            }
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)
        record['elapsed_seconds'] = time.monotonic() - start
        record['completed_utc'] = datetime.now(timezone.utc).isoformat()
        record['summary'] = summarize(record['rows'])
        record['gate_pass'] = record['status'] == 'complete' and len(record['rows']) == 140
        with handle:
            handle.write(json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + '\n')
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output)
    print(json.dumps({'status': result['status'], 'gate_pass': result['gate_pass'],
                      'cases': len(result['rows']), 'output': str(args.output)}, sort_keys=True))
    raise SystemExit(0 if result['gate_pass'] else 1)
