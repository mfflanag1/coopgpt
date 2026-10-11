#!/usr/bin/env python3
"""Prepare a frozen conditional MELODI calibration; no dispatch or pooling.
Derived numeric data: CC BY-SA 4.0, Husom et al. (2024).
See CALIBRATION_METHOD.txt and original MELODI PROVENANCE.json.
"""
import argparse
import csv
import hashlib
import json
import math
import re
import statistics
from collections import Counter
from pathlib import Path

HARDWARE = ('laptop2', 'workstation')
BINS = ('[0,32)', '[32,64)', '[64,128)', '[128,256)', '[256,infinity)')
SOURCE_DEFAULT = Path(__file__).resolve().parent / 'data/melodi/PAIRED_MEASUREMENTS.csv'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def number(row, key):
    try:
        return float(row[key])
    except (TypeError, ValueError, KeyError):
        return math.nan

def input_bin(tokens):
    if tokens < 0:
        raise ValueError('Negative input token count')
    for idx, upper in enumerate((32, 64, 128, 256)):
        if tokens < upper:
            return BINS[idx]
    return BINS[-1]

def nearest_rank(values, probability=0.9):
    if not values:
        raise ValueError('Empty quantile sample')
    return sorted(values)[math.ceil(probability * len(values)) - 1]

def diagnostics(actual, predicted):
    if not actual or len(actual) != len(predicted) or min(actual) <= 0:
        raise ValueError('Invalid diagnostic inputs')
    errors = [abs(p - a) / a for a, p in zip(actual, predicted)]
    return {
        'n': len(actual),
        'actual_sum': sum(actual),
        'predicted_sum': sum(predicted),
        'aggregate_absolute_relative_error': abs(sum(predicted)-sum(actual))/sum(actual),
        'mean_request_absolute_relative_error': statistics.mean(errors),
        'median_request_absolute_relative_error': statistics.median(errors),
        'p90_request_absolute_relative_error': nearest_rank(errors),
        'fraction_actual_le_forecast': sum(a <= p for a, p in zip(actual, predicted)) / len(actual),
        'aggregate_error_at_most_ten_percent': abs(sum(predicted)-sum(actual))/sum(actual) <= 0.10,
    }

def prepare(source, output):
    method = output / 'CALIBRATION_METHOD.txt'
    if not method.exists():
        raise ValueError('Frozen method file must precede preparation')
    method_hash = sha(method)
    with source.open(newline='') as f:
        rows = list(csv.DictReader(f))
    ids = [r['prompt_sha256'] for r in rows]
    counts = Counter(ids)
    duplicates = {k: v for k, v in counts.items() if v > 1}
    if duplicates:
        raise ValueError(f'Duplicate prompt IDs: {len(duplicates)}')
    if any(not re.fullmatch('[0-9a-f]{64}', ident) for ident in ids):
        raise ValueError('Invalid SHA identifier')
    reasons = Counter()
    first_reasons = Counter()
    cohort = []
    for r in rows:
        failed = []
        if r['same_prompt_tokens'] != '1':
            failed.append('different_prompt_tokens')
        if r['same_response_text'] != '1':
            failed.append('different_response_text')
        if r['same_prompt_tokens'] == '1' and r['laptop2_prompt_token_length'] != r['workstation_prompt_token_length']:
            raise ValueError('Inconsistent source prompt-token identity flag')
        if r['same_response_text'] == '1' and r['laptop2_response_sha256'] != r['workstation_response_sha256']:
            raise ValueError('Inconsistent source response identity flag')
        values = {}
        for h in HARDWARE:
            duration = number(r, h+'_total_duration_seconds')
            energy_kwh = number(r, h+'_energy_gpu_kwh')
            load = number(r, h+'_load_fraction')
            if not math.isfinite(duration) or duration <= 0:
                failed.append(h+'_nonpositive_or_nonfinite_duration')
            if not math.isfinite(energy_kwh) or energy_kwh <= 0:
                failed.append(h+'_nonpositive_or_nonfinite_energy')
            if not math.isfinite(load) or load < 0 or load > 0.01:
                failed.append(h+'_load_fraction_outside_0_to_1pct')
            values[h+'_actual_api_s'] = duration
            values[h+'_actual_gpu_j'] = energy_kwh*3600000.0
            values[h+'_actual_slot_s'] = duration+4.0
        if failed:
            reasons.update(failed)
            first_reasons[failed[0]] += 1
            continue
        tokens = int(r['laptop2_prompt_token_length'])
        ident = r['prompt_sha256']
        cohort.append({'request_id': ident, 'prompt_tokens': tokens, 'input_bin': input_bin(tokens), **values})
    training = [r for r in cohort if int(r['request_id'][:8], 16) % 5 != 0]
    heldout = sorted((r for r in cohort if int(r['request_id'][:8], 16) % 5 == 0), key=lambda r:r['request_id'])
    if not training or not heldout:
        raise ValueError('Empty split')
    if set(r['request_id'] for r in training) & set(r['request_id'] for r in heldout):
        raise ValueError('Prompt-group split leakage')
    models = {}
    for h in HARDWARE:
        global_p90 = {metric: nearest_rank([r[h+'_actual_'+metric] for r in training]) for metric in ('api_s', 'gpu_j')}
        models[h] = {'global_training_n': len(training), 'global_p90': global_p90, 'bins': {}}
        for bin_name in BINS:
            group = [r for r in training if r['input_bin'] == bin_name]
            use_bin = len(group) >= 10
            chosen = group if use_bin else training
            model = {'bin_training_n': len(group), 'forecast_source': 'bin' if use_bin else 'global',
                     'pred_api_s': nearest_rank([r[h+'_actual_api_s'] for r in chosen]),
                     'pred_gpu_j': nearest_rank([r[h+'_actual_gpu_j'] for r in chosen])}
            model['pred_slot_s'] = model['pred_api_s']+4.0
            models[h]['bins'][bin_name] = model
        for r in heldout:
            model = models[h]['bins'][r['input_bin']]
            r[h+'_pred_api_s'] = model['pred_api_s']
            r[h+'_pred_gpu_j'] = model['pred_gpu_j']
            r[h+'_pred_slot_s'] = model['pred_slot_s']
            r[h+'_forecast_source'] = model['forecast_source']
            r[h+'_bin_training_n'] = model['bin_training_n']
    fields = ['request_id','prompt_tokens','input_bin']
    for h in HARDWARE:
        fields.extend(h+'_'+k for k in ('actual_api_s','pred_api_s','actual_slot_s','pred_slot_s','actual_gpu_j','pred_gpu_j','forecast_source','bin_training_n'))
    output.mkdir(parents=True, exist_ok=True)
    with (output/'COHORT.csv').open('w',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=fields)
        writer.writeheader(); writer.writerows(heldout)
    report = {
        'method_file_sha256': method_hash,
        'source_file': source.name, 'source_sha256': sha(source),
        'output_csv_sha256': sha(output/'COHORT.csv'),
        'source_rows': len(rows), 'source_unique_prompt_ids': len(counts), 'duplicate_prompt_ids': len(duplicates),
        'eligible_cohort': len(cohort), 'training_count': len(training), 'heldout_count': len(heldout),
        'excluded_rows': len(rows)-len(cohort),
        'exclusion_reasons_nonexclusive': dict(reasons), 'first_exclusion_reasons_exclusive': dict(first_reasons),
        'training_input_bins': dict(Counter(r['input_bin'] for r in training)),
        'heldout_input_bins': dict(Counter(r['input_bin'] for r in heldout)),
        'models': models,
        'heldout_prediction_diagnostics': {h: {
            metric: diagnostics([r[h+'_actual_'+metric] for r in heldout], [r[h+'_pred_'+metric] for r in heldout])
            for metric in ('api_s','slot_s','gpu_j')} for h in HARDWARE},
        'scope': {
            'retrospective_identical_response_selection': True,
            'realized_output_hidden_from_predictor': True,
            'cohort_membership_not_a_prospective_admission_filter': True,
            'no_fitted_or_replayed_pooling_outcomes': True,
            'measured_heldout_records_are_independent_of_training_prompt_groups': True,
            'not_heldout_live_serving_arrival_windows': True,
            'physical_compatibility_gate_passed': False,
            'idle_energy_between_requests_included': False,
            'request_window_energy_may_include_one_second_padding': True,
            'missing_metadata': ['checkpoint digest','quantization','Ollama version','decoding policy','CPU/GPU offload','power limits','raw power traces','idle power baseline','exact collection code revision'],
            'unverified_CPU_runner_accounting_not_used': True,
            'no_core_or_truthfulness_guarantees_transferred': True,
        },
    }
    if sha(method) != method_hash:
        raise ValueError('Method file changed during fitting')
    (output/'MELODI_CALIBRATION.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:report[k] for k in ('eligible_cohort','training_count','heldout_count','training_input_bins','heldout_input_bins','heldout_prediction_diagnostics')},indent=2))

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=SOURCE_DEFAULT);p.add_argument('--output',type=Path,default=Path(__file__).resolve().parent)
    a=p.parse_args(); prepare(a.source,a.output)
if __name__ == '__main__':main()
