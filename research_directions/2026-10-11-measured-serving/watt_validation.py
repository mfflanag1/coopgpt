#!/usr/bin/env python3
"""Frozen, within-source held-out validation of an aggregate GPU-energy model.

Both coefficients are regression proxies, not separately observed idle power or
request energy. No cross-GPU request matching or pooling simulation is performed.
"""
import argparse
import ast
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics

BASE = Path(__file__).resolve().parent
DEFAULT_DATA = BASE / 'data' / 'wattgpu' / 'llama31_8b_a100_h100_runs.csv'
GPUS = ('NVIDIA A100-SXM4-40GB', 'NVIDIA H100 NVL')
RATES = ('0.017', '0.33')
ERROR_GATE = 0.10
TTFT_GATE = 1.0
E2E_GATE = 15.0


def check(condition, message):
    if not condition:
        raise ValueError(message)


def quantile_nearest_rank(values, q):
    check(bool(values), 'Cannot summarize an empty sample')
    ordered = sorted(values)
    return ordered[max(0, math.ceil(q * len(ordered)) - 1)]


def summary(values):
    return {
        'count': len(values), 'min': min(values), 'max': max(values),
        'mean': statistics.fmean(values),
        'p50': quantile_nearest_rank(values, .50),
        'p95': quantile_nearest_rank(values, .95),
        'p99': quantile_nearest_rank(values, .99),
    }


def load(path):
    rows = []
    with path.open(newline='') as source:
        for raw in csv.DictReader(source):
            row = {
                'source_row_id': int(raw['']), 'gpu': raw['gpu_type'],
                'rate': raw['lambda_qps'],
                'duration_s': float(raw['measurement_duration']),
                'energy_j': float(raw['gpu_energy']),
                'mean_power_w': float(raw['gpu_0_power_draw_watts_mean']),
                'total_output_tokens': float(raw['generation_tokens_total']),
            }
            for short, key in [('ttft', 'time_to_first_token_seconds_events'),
                               ('e2e', 'e2e_request_latency_seconds_events'),
                               ('input', 'request_prompt_tokens'),
                               ('output', 'request_generation_tokens')]:
                row[short] = ast.literal_eval(raw[key])
                check(isinstance(row[short], list), f'{key} is not a list')
                check(all(isinstance(x, (int, float)) and math.isfinite(x) and x >= 0
                          for x in row[short]), f'Invalid {key} in row {raw[""]}')
            check(row['gpu'] in GPUS and raw['model'] == 'meta-llama/Llama-3.1-8B-Instruct',
                  'Unexpected input selection')
            check(row['rate'] in ('', *RATES), 'Unexpected rate')
            check(all(math.isfinite(row[k]) and row[k] > 0 for k in
                      ['duration_s', 'energy_j', 'mean_power_w', 'total_output_tokens']),
                  'Invalid run-level numeric quantity')
            row['request_count'] = len(row['output'])
            check(len(row['input']) == row['request_count'], 'Mismatched token arrays')
            if row['rate']:
                check(len(row['ttft']) == len(row['e2e']) == row['request_count'],
                      'Misaligned server arrays')
                check(all(t <= e for t, e in zip(row['ttft'], row['e2e'])),
                      'TTFT exceeds response duration')
            else:
                check(len(row['ttft']) == 0 and len(row['e2e']) == 1,
                      'Unexpected offline representation')
            rows.append(row)
    check(len(rows) == 30, 'Expected 30 input rows')
    check(len({r['source_row_id'] for r in rows}) == len(rows), 'Duplicate source IDs')
    return rows


def fit(rows):
    """Solve unconstrained two-column, no-intercept OLS normal equations."""
    tt = math.fsum(r['duration_s'] ** 2 for r in rows)
    tn = math.fsum(r['duration_s'] * r['request_count'] for r in rows)
    nn = math.fsum(r['request_count'] ** 2 for r in rows)
    te = math.fsum(r['duration_s'] * r['energy_j'] for r in rows)
    ne = math.fsum(r['request_count'] * r['energy_j'] for r in rows)
    determinant = tt * nn - tn * tn
    check(determinant > 1e-12 * tt * nn, 'Singular or near-singular design')
    idle = (te * nn - ne * tn) / determinant
    request = (tt * ne - tn * te) / determinant
    residuals = [r['energy_j'] - idle * r['duration_s'] - request * r['request_count']
                 for r in rows]
    # First-order OLS conditions independently verify the closed-form solution.
    for key in ['duration_s', 'request_count']:
        error = abs(math.fsum(r[key] * residual for r, residual in zip(rows, residuals)))
        scale = math.fsum(abs(r[key] * r['energy_j']) for r in rows)
        check(error <= 1e-10 * scale, 'OLS normal-equation residual too large')
    return idle, request


def latency(rows):
    ttft = [x for r in rows for x in r['ttft']]
    e2e = [x for r in rows for x in r['e2e']]
    hits = sum(t <= TTFT_GATE and e <= E2E_GATE for t, e in zip(ttft, e2e))
    return {'source_row_ids': [r['source_row_id'] for r in rows],
            'completed_requests': len(ttft), 'joint_slo_successes': hits,
            'joint_slo_fraction': hits / len(ttft),
            'ttft_s': summary(ttft), 'e2e_s': summary(e2e)}


def analyze(path):
    rows = load(path)
    models = []
    for gpu in GPUS:
        train, holdout = [], []
        by_rate = {}
        for rate in RATES:
            group = sorted((r for r in rows if r['gpu'] == gpu and r['rate'] == rate),
                           key=lambda r: r['source_row_id'])
            check(len(group) == 5, 'Expected 5 repeats per hardware and rate')
            train.extend(group[:3])
            holdout.extend(group[3:])
            by_rate[rate] = {'all_runs': latency(group), 'held_out_runs': latency(group[3:])}
        idle, per_request = fit(train)
        predictions = []
        for row in holdout:
            predicted = idle * row['duration_s'] + per_request * row['request_count']
            error = abs(predicted - row['energy_j']) / row['energy_j']
            predictions.append({'source_row_id': row['source_row_id'],
                                'arrival_rate_qps': float(row['rate']),
                                'completed_requests': row['request_count'],
                                'duration_s': row['duration_s'],
                                'observed_energy_j': row['energy_j'],
                                'predicted_energy_j': predicted,
                                'absolute_relative_error': error,
                                'passes_10_percent_gate': error <= ERROR_GATE})
        nonnegative = idle >= 0 and per_request >= 0
        models.append({'gpu': gpu,
                       'training_source_row_ids': [r['source_row_id'] for r in train],
                       'idle_power_proxy_w': idle, 'request_energy_proxy_j': per_request,
                       'coefficients_nonnegative': nonnegative,
                       'held_out_predictions': predictions,
                       'max_holdout_absolute_relative_error': max(x['absolute_relative_error'] for x in predictions),
                       'passes_energy_gate': nonnegative and all(x['passes_10_percent_gate'] for x in predictions),
                       'latency_by_arrival_rate_qps': by_rate})
    power_audit = []
    for row in rows:
        product = row['mean_power_w'] * row['duration_s']
        power_audit.append({'source_row_id': row['source_row_id'], 'gpu': row['gpu'],
                            'mode': row['rate'] or 'offline_batch',
                            'reported_energy_j': row['energy_j'],
                            'mean_power_times_duration_j': product,
                            'absolute_relative_difference': abs(product - row['energy_j']) / row['energy_j']})
    offline = []
    for gpu in GPUS:
        rs = [r for r in rows if r['gpu'] == gpu and not r['rate']]
        offline.append({'gpu': gpu, 'source_row_ids': [r['source_row_id'] for r in rs],
                        'completed_requests_per_batch': [r['request_count'] for r in rs],
                        'whole_batch_duration_s': summary([r['e2e'][0] for r in rs]),
                        'whole_run_energy_j': summary([r['energy_j'] for r in rs]),
                        'individual_slo_assessed': False})
    return {'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'frozen_method_sha256': hashlib.sha256((BASE / 'WATT_METHOD.txt').read_bytes()).hexdigest(),
            'units': {'energy': 'joules', 'power': 'watts', 'latency': 'seconds'},
            'thresholds': {'ttft_s': TTFT_GATE, 'e2e_s': E2E_GATE,
                           'holdout_absolute_relative_energy_error': ERROR_GATE},
            'models': models,
            'combined_energy_gate_passed': all(m['passes_energy_gate'] for m in models),
            'energy_power_duration_audit': power_audit,
            'max_energy_vs_mean_power_duration_relative_difference': max(x['absolute_relative_difference'] for x in power_audit),
            'offline_batch_descriptive': offline,
            'interpretation': 'Within-source aggregate held-out validation only. Regression coefficients are proxies, not measured idle/request energy. SLOs are illustrative and observations are completed requests from repeated short prompts. No cross-GPU request pairing, pooled deployment, long-prompt, peak-power, or private-cost claim.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, default=DEFAULT_DATA)
    parser.add_argument('--output', type=Path, default=BASE / 'WATT_VALIDATION.json')
    args = parser.parse_args()
    result = analyze(args.data)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    for model in result['models']:
        print(model['gpu'], 'idle_proxy_W=', model['idle_power_proxy_w'],
              'J_per_request_proxy=', model['request_energy_proxy_j'],
              'max_holdout_error=', model['max_holdout_absolute_relative_error'],
              'gate=', model['passes_energy_gate'])
        for rate, cases in model['latency_by_arrival_rate_qps'].items():
            for split, stats in cases.items():
                print(rate, split, 'SLO=', str(stats['joint_slo_successes']) + '/' + str(stats['completed_requests']),
                      'TTFT_p95=', stats['ttft_s']['p95'], 'e2e_p95=', stats['e2e_s']['p95'])
    print('max_energy_vs_mean_power_duration_relative_difference=',
          result['max_energy_vs_mean_power_duration_relative_difference'])


if __name__ == '__main__':
    main()
