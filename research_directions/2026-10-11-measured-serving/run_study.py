#!/usr/bin/env python3
"""Frozen, conditional measured-record replay; not a serving deployment."""
import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics

from replay import Job, Service, replay

BASE = Path(__file__).resolve().parent
HARDWARE = ('laptop2', 'workstation')


def training_reference(path):
    """Mean uniform-routing window joules on the frozen training cohort only."""
    energies = []
    with path.open(newline='') as source:
        for row in csv.DictReader(source):
            if row['same_prompt_tokens'] != '1' or row['same_response_text'] != '1':
                continue
            if int(row['prompt_sha256'][:8], 16) % 5 == 0:
                continue
            vals = [float(row[h + k]) for h in HARDWARE for k in
                    ('_total_duration_seconds', '_energy_gpu_kwh', '_load_fraction')]
            if not all(math.isfinite(x) for x in vals):
                continue
            if not all(vals[i] > 0 and vals[i+1] > 0 and 0 <= vals[i+2] <= .01
                       for i in (0, 3)):
                continue
            energies.append((vals[1] + vals[4]) * 3_600_000 / 2)
    if not energies:
        raise ValueError('Empty training budget reference')
    return statistics.fmean(energies), len(energies)


def make_jobs(rows, interarrival, response_deadline):
    jobs = []
    for idx, row in enumerate(sorted(rows, key=lambda r: r['request_id'])):
        arrival = idx * interarrival
        def profiles(kind):
            return {s: Service(float(row[h + '_' + kind + '_slot_s']),
                               float(row[h + '_' + kind + '_gpu_j']))
                    for s, h in enumerate(HARDWARE)}
        jobs.append(Job(row['request_id'], arrival, arrival + response_deadline,
                        profiles('pred'), profiles('actual'), 3.5))
    return jobs


def compact(result):
    return {k: v for k, v in result.items() if k not in ('records', 'rejections')}


def independently_check(result, jobs):
    """Reconcile simulator output using immutable original request measurements."""
    lookup = {j.id: j for j in jobs}
    accepted = {r['id'] for r in result['records']}
    rejected = {r['id'] for r in result['rejections']}
    if accepted & rejected or accepted | rejected != set(lookup):
        raise ValueError('Lost, repeated, or invented request')
    if len(accepted) != len(result['records']) or len(rejected) != len(result['rejections']):
        raise ValueError('Duplicated request')
    energy = [0., 0.]
    counted = {'ontime': 0, 'late': 0}
    for server in (0, 1):
        previous_end = 0.
        for r in sorted((r for r in result['records'] if r['server'] == server),
                        key=lambda r: r['start']):
            j = lookup[r['id']]
            actual, pred = j.realized[server], j.predictions[server]
            if r['start'] < max(previous_end, j.arrival):
                raise ValueError('Overlap or execution before arrival')
            response_end = r['start'] + actual.service_seconds - j.response_tail_seconds
            if not math.isclose(response_end, r['response_end'], abs_tol=1e-8):
                raise ValueError('Incorrect physical response time')
            if not math.isclose(r['slot_end'] - r['start'], actual.service_seconds,
                                rel_tol=1e-10, abs_tol=1e-8):
                raise ValueError('Incorrect physical slot')
            if r['start'] + pred.service_seconds - j.response_tail_seconds > j.deadline:
                raise ValueError('Dispatch violates prediction eligibility')
            state = 'ontime' if response_end <= j.deadline else 'late'
            if state != r['outcome']:
                raise ValueError('Incorrect realized outcome')
            counted[state] += 1
            energy[server] += actual.energy_j
            previous_end = r['slot_end']
    if any(counted[k] != result[k] for k in counted):
        raise ValueError('Incorrect terminal counts')
    if not math.isclose(sum(energy), result['total_energy_j'], rel_tol=1e-10):
        raise ValueError('Energy not charged once per actual request')
    budgets = result['initial_budgets_j']
    # Reconstruct reservations independently in chronological order. Final energy
    # balances alone would miss admitting two jobs against the same unspent quota.
    available = [sum(budgets)] if result['mode'] == 'pool' else list(budgets)
    ledger = []
    for r in result['records']:
        ledger.append((r['start'], 1, r['id'], r['server']))
        ledger.append((r['slot_end'], 0, r['id'], r['server']))
    for _, phase, ident, server in sorted(ledger):
        j = lookup[ident]
        account = 0 if result['mode'] == 'pool' else server
        predicted = j.predictions[server].energy_j
        if phase == 0:
            available[account] += predicted - j.realized[server].energy_j
        else:
            if predicted > available[account] + 1e-8:
                raise ValueError('Dispatch violates chronological energy reservation')
            available[account] -= predicted
    if result['mode'] == 'pool':
        balances = [sum(budgets) - sum(energy)]
    else:
        balances = [budgets[s] - energy[s] for s in (0, 1)]
    if any(not math.isclose(a, b, abs_tol=1e-8) for a, b in
           zip(balances, result['remaining_accounts_j'])):
        raise ValueError('Unsettled reservations or incorrect budget accounting')
    if any(not math.isclose(a, b, abs_tol=1e-8) for a, b in zip(available, balances)):
        raise ValueError('Chronological reservations fail to reconcile')


def run(cohort_path, paired_path, output):
    with cohort_path.open(newline='') as f:
        rows = list(csv.DictReader(f))
    if not rows or len({r['request_id'] for r in rows}) != len(rows):
        raise ValueError('Invalid heldout cohort')
    reference, ntrain = training_reference(paired_path)
    n = len(rows)
    cases, primary = [], None
    details = []
    for interval, deadline, factor, owner0_share in itertools.product(
            (30., 10., 3.), (30., 60., 120.), (.5, .75, 1.), (.2, .5, .8)):
        total = factor * n * reference
        budgets = [total * owner0_share, total * (1 - owner0_share)]
        jobs = make_jobs(rows, interval, deadline)
        a, p = (replay(jobs, budgets, mode) for mode in ('autarky', 'pool'))
        independently_check(a, jobs)
        independently_check(p, jobs)
        gain = p['ontime'] - a['ontime']
        case_id = f'gap{interval:g}_deadline{deadline:g}_budget{factor:g}_share{owner0_share:g}'
        case = {'case_id': case_id, 'interarrival_s': interval,
                'response_deadline_s': deadline, 'budget_factor': factor,
                'owner0_budget_share': owner0_share, 'total_window_budget_j': total,
                'autarky': compact(a), 'pool': compact(p),
                'ontime_gain_requests': gain, 'ontime_gain_fraction_offered': gain / n,
                'conditional_screen_passed': gain/n >= .05 and p['late'] == 0 and a['late'] == 0
                    and p['max_actual_budget_overrun_j'] <= 1e-8
                    and a['max_actual_budget_overrun_j'] <= 1e-8}
        # Debt invalidates either purported feasible-arm comparison.
        cases.append(case)
        details.append({'case_id': case_id, 'autarky': a, 'pool': p})
        if (interval, deadline, factor, owner0_share) == (10., 60., .75, .5):
            primary = case
    if primary is None:
        raise ValueError('Missing primary case')
    result = {'scope': 'Conditional measured-record diagnostic; not measured pooled serving.',
              'heldout_requests': n, 'training_reference_count': ntrain,
              'training_uniform_routing_reference_j': reference,
              'cohort_sha256': hashlib.sha256(cohort_path.read_bytes()).hexdigest(),
              'protocol_sha256': hashlib.sha256((BASE/'PROTOCOL.txt').read_bytes()).hexdigest(),
              'primary': primary, 'case_count': len(cases),
              'family_summary': {
                  'positive_gain': sum(c['ontime_gain_requests'] > 0 for c in cases),
                  'zero_gain': sum(c['ontime_gain_requests'] == 0 for c in cases),
                  'negative_gain': sum(c['ontime_gain_requests'] < 0 for c in cases),
                  'min_gain_requests': min(c['ontime_gain_requests'] for c in cases),
                  'max_gain_requests': max(c['ontime_gain_requests'] for c in cases),
                  'conditional_screen_passes': sum(c['conditional_screen_passed'] for c in cases),
                  'pool_late_cases': sum(c['pool']['late'] > 0 for c in cases),
                  'autarky_late_cases': sum(c['autarky']['late'] > 0 for c in cases),
                  'either_arm_actual_budget_overrun_cases': sum(
                      max(c[m]['max_actual_budget_overrun_j'] for m in ('autarky','pool')) > 1e-8
                      for c in cases)},
              'deployment_gate_passed': False,
              'missing_for_deployment': ['Pinned matching execution metadata',
                  'Measured resident-idle and full-horizon power',
                  'Independent pooled-arrival-run throughput/energy/TTFT/TPOT validation'],
              'cases': cases}
    output.mkdir(parents=True, exist_ok=True)
    (output/'REPLAY_RESULTS.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    (output/'REPLAY_SUMMARY.json').write_text(json.dumps(
        {k:v for k,v in result.items() if k != 'cases'}, indent=2, allow_nan=False)+'\n')
    # All physical records retained for audit, rather than just the primary case.
    with (output/'REPLAY_EVENTS.jsonl').open('w') as f:
        for d in details:
            f.write(json.dumps(d, separators=(',', ':'), allow_nan=False)+'\n')
    fields = ['case_id','interarrival_s','response_deadline_s','budget_factor',
              'owner0_budget_share','total_window_budget_j','ontime_gain_requests',
              'ontime_gain_fraction_offered','conditional_screen_passed']
    metrics = ['offered','started','ontime','late','rejected','total_energy_j',
               'max_actual_budget_overrun_j']
    with (output/'REPLAY_TABLE.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields+[m+'_'+k for m in ('autarky','pool') for k in metrics])
        writer.writeheader()
        for c in cases:
            writer.writerow({**{k:c[k] for k in fields},
                             **{m+'_'+k:c[m][k] for m in ('autarky','pool') for k in metrics}})
    print(json.dumps({'primary':primary, 'family_summary':result['family_summary']}, indent=2))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--cohort', type=Path, default=BASE/'COHORT.csv')
    ap.add_argument('--paired', type=Path, default=BASE/'data/melodi/PAIRED_MEASUREMENTS.csv')
    ap.add_argument('--output', type=Path, default=BASE)
    args = ap.parse_args()
    run(args.cohort, args.paired, args.output)
