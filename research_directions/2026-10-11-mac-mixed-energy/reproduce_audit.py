#!/usr/bin/env python3
"""Read-only reproduction of the independent raw-energy and answer-format audit.

Usage: python3 -B reproduce_audit.py SOURCE_DIR [--capture NAME]
       [--output /tmp/audit-checks.json]

The frozen analyzer supplies reference bounds; all raw energy block parsing,
KEEP-gold reconstruction, and alternate-format diagnostics below are independent.
The diagnostics never replace the frozen exact-quality score. No hardware calls.
"""
import argparse
from collections import Counter, defaultdict
from contextlib import contextmanager
from datetime import datetime, timedelta
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


@contextmanager
def frozen_modules(source):
    modules = {}
    for name in ('energy', 'analyze', 'independent_check'):
        path = source/(name+'.py')
        spec = importlib.util.spec_from_file_location('_raw_audit_'+name, path)
        module = importlib.util.module_from_spec(spec)
        exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
        modules[name] = module
    previous = sys.modules.get('energy')
    sys.modules['energy'] = modules['energy']
    try:
        yield modules['analyze'], modules['independent_check']
    finally:
        if previous is None:
            sys.modules.pop('energy', None)
        else:
            sys.modules['energy'] = previous


def normalize(text):
    text = re.sub(r'\s+', '', text)
    if text.startswith('```') and text.endswith('```'):
        text = text[3:-3]
    return text.removesuffix(';')


def raw_samples(text):
    """First Processor section only, with no calls to the frozen energy parser."""
    chunks = text.split('*** Sampled system activity (')[1:]
    require(bool(chunks), 'no raw sample blocks')
    samples = []
    labels = (('cpu', 'CPU Power'), ('gpu', 'GPU Power'), ('ane', 'ANE Power'),
              ('combined', 'Combined Power (CPU + GPU + ANE)'))
    for index, chunk in enumerate(chunks):
        header = re.match(r'(.+?)\) \(([0-9.]+)ms elapsed\) \*\*\*', chunk)
        require(header is not None, f'malformed raw sample header {index}')
        end = datetime.strptime(header[1], '%a %b %d %H:%M:%S %Y %z')
        ms = float(header[2])
        require(ms > 0, f'nonpositive elapsed at sample {index}')
        require('**** Processor usage ****' in chunk, f'processor section absent {index}')
        section = chunk.split('**** Processor usage ****', 1)[1].split('**** GPU usage ****', 1)[0]
        joules = {}
        for component, label in labels:
            values = re.findall('^'+re.escape(label)+r': ([0-9.]+) mW$', section, re.M)
            require(len(values) == 1, f'missing/duplicate first-section {label} at sample {index}')
            joules[component] = float(values[0])*ms/1e6
        samples.append((end, ms/1000, joules))
    return samples


def audit(source_dir, capture_name):
    source = Path(source_dir).resolve(strict=True)
    data = (source/capture_name).resolve(strict=True)
    require(source in data.parents, 'capture must be a directory under source')
    hashes = {}
    for name in ('FREEZE.json', 'CONTINUATION_FREEZE.json'):
        manifest = read(source/name)
        for relative, expected in manifest['sha256'].items():
            path = Path(relative)
            require(not path.is_absolute() and '..' not in path.parts, 'unsafe manifest path')
            require(sha(source/path) == expected, f'frozen hash differs: {name}/{relative}')
        hashes[name] = sha(source/name)
    for name in ('analyze.py', 'energy.py', 'independent_check.py', 'CONFIG.json', 'PLAN.json'):
        hashes[name] = sha(source/name)
    with frozen_modules(source) as (analyzer, checker):
        reference = analyzer.analyze(data, source_dir=source)
        counts, error_kinds, categories = Counter(), Counter(), Counter()
        separator_examples, loose_extra_examples = [], []
        gold_checks, positive_controls = 0, 0
        plan = read(source/'PLAN.json')
        for planned in plan:
            trace_path = source/planned['trace_file']
            hashes[planned['trace_file']] = sha(trace_path)
            jobs = read(trace_path)
            for job in jobs:
                pairs = re.findall(r'^(R[0-9]{4}) value=([0-9]{3}) flag=KEEP$', job['prompt'], re.M)
                gold = ';'.join(f'{key}={value}' for key, value in pairs)
                require(gold == job['expected'], f'gold differs {planned["index"]}/{job["request_id"]}')
                require(analyzer.quality_pass(gold, gold) and checker.correct_answer(gold, gold), 'positive scorer control failed')
                gold_checks += 1
                positive_controls += 1
            relative = f"window-{planned['index']:02d}/REQUESTS.json"
            path = data/relative
            if not path.exists():
                continue
            hashes[capture_name+'/'+relative] = sha(path)
            rows = read(path)['requests']
            require([r['request_id'] for r in rows] == [j['request_id'] for j in jobs], f'row IDs differ {relative}')
            run_relative = f"window-{planned['index']:02d}/RUN.json"
            hashes[capture_name+'/'+run_relative] = sha(data/run_relative)
            for job, row in zip(jobs, rows):
                counts['recorded_rows'] += 1
                if row['completed'] is not True:
                    counts['recorded_failure'] += 1
                    error_kinds[row['error']] += 1
                    continue
                counts['completed'] += 1
                text = ''.join(chunk['data'].get('response', '') for chunk in row['chunks'])
                norm = normalize(text)
                gold = job['expected']
                exact = norm == gold
                require(exact == analyzer.quality_pass(text, gold) == checker.correct_answer(text, gold), 'raw exact score disagreement')
                counts['exact_quality'] += exact
                counts['length_stop'] += row['final']['done_reason'] == 'length'
                counts['no_equals'] += '=' not in text
                counts['normalized_correct_equals_pair'] += bool(re.search(r'R\d{4}=\d{3}', norm))
                counts['contains_semicolon_id_value'] += bool(re.search(r'R\d{4};\d{3}', text))
                output_pairs = re.findall(r'(R\d{4})\s*[;=]\s*(\d{3})', text)
                gold_pairs = re.findall(r'(R\d{4})=(\d{3})', gold)
                repaired = re.sub(r'(R\d{4});(\d{3})', r'\1=\2', norm)
                only_separator = repaired == gold
                loose_match = output_pairs == gold_pairs
                counts['only_ID_value_separator_repair_match'] += only_separator
                counts['loose_pair_extraction_match'] += loose_match
                counts['loose_pair_extraction_differs'] += not loose_match
                if output_pairs:
                    categories['with_extractable_pairs'] += 1
                    categories['omitted_gold_pair'] += bool(set(gold_pairs)-set(output_pairs))
                    categories['extra_or_wrong_pair'] += bool(set(output_pairs)-set(gold_pairs))
                    categories['same_pair_set_wrong_order'] += set(gold_pairs) == set(output_pairs) and gold_pairs != output_pairs
                else:
                    categories['no_extractable_pairs'] += 1
                example = dict(window=planned['index'], request_id=job['request_id'], input_rows=job['input_rows'],
                               cap=job['max_output_tokens'], expected=gold, actual=text,
                               done_reason=row['final']['done_reason'], output_tokens=row['final']['eval_count'])
                if only_separator:
                    separator_examples.append(example)
                if loose_match and not only_separator:
                    loose_extra_examples.append(example)
        require(counts['completed'] == sum(w['metrics']['api_completed_count'] for w in reference['windows']), 'raw/reference completion mismatch')
        require(counts['exact_quality'] == sum(w['metrics']['quality_pass_count'] for w in reference['windows']), 'raw/reference quality mismatch')
    campaign = read(data/'CAMPAIGN.json')
    stop = read(data/'POWER_STOP.json')
    require(stop == campaign['power_stop'], 'campaign and POWER_STOP disagree')
    require(stop.get('stop_confirmed') is True and type(stop.get('returncode')) is int and stop['returncode'] == 0, 'sampler not normally stopped')
    require((data/'POWER_exit_status.txt').read_text().strip() == '0', 'raw sampler exit status not zero')
    for name in ('CAMPAIGN.json', 'POWER_STOP.json', 'POWER_exit_status.txt', 'POWER_supervisor_log.txt', 'POWER.txt.gz'):
        hashes[capture_name+'/'+name] = sha(data/name)
    samples = raw_samples(gzip.decompress((data/'POWER.txt.gz').read_bytes()).decode())
    require(len(samples) == reference['energy_capture']['sample_count'], 'raw/reference sample count differs')
    bounds_checked, max_difference, intervals = 0, 0.0, []
    totals = {name: {edge: defaultdict(float) for edge in ('lower', 'upper')} for name in reference['windows'][0]['energy']['intervals']}
    for window in reference['windows']:
        if not (data/f"window-{window['index']:02d}").is_dir():
            continue
        for name, interval in window['energy']['intervals'].items():
            require(interval['valid'], f'reference interval invalid: {window["index"]}/{name}')
            start = datetime.fromisoformat(interval['window']['start_utc'])
            end = datetime.fromisoformat(interval['window']['end_utc'])
            sums = {edge: defaultdict(float) for edge in ('lower', 'upper')}
            for stamp, elapsed, joules in samples:
                inside = stamp-timedelta(seconds=1+elapsed) >= start and stamp+timedelta(seconds=1) <= end
                overlap = stamp+timedelta(seconds=1) > start and stamp-timedelta(seconds=1+elapsed) < end
                for edge, include in (('lower', inside), ('upper', overlap)):
                    if include:
                        for component, value in joules.items():
                            sums[edge][component] += value
            for edge in ('lower', 'upper'):
                for component in ('cpu', 'gpu', 'ane', 'combined'):
                    difference = abs(sums[edge][component]-interval[edge+'_j'][component])
                    require(difference == 0, f'energy bound mismatch: {window["index"]}/{name}/{edge}/{component}')
                    bounds_checked += 1
                    max_difference = max(max_difference, difference)
                    totals[name][edge][component] += sums[edge][component]
            intervals.append(dict(window=window['index'], phase=name, lower_j=dict(sums['lower']), upper_j=dict(sums['upper'])))
    endpoints = [x[0].timestamp() for x in samples]
    cumulative, residuals = 0.0, [0.0]
    for index in range(1, len(samples)):
        cumulative += samples[index][1]
        residuals.append(endpoints[index]-endpoints[0]-cumulative)
    return dict(source_dir=str(source), capture=capture_name, input_sha256=hashes,
                assertion_method='Explicit ValueError guards, active with or without python -O',
                source_gold_equal_checks=gold_checks, expected_answer_positive_controls=positive_controls,
                outcome_counts=dict(counts), recorded_failure_kinds=dict(error_kinds),
                loose_pair_categories=dict(categories), delimiter_only_examples=separator_examples,
                loose_match_with_extra_material_examples=loose_extra_examples,
                power_stop=stop, raw_sample_blocks=len(samples), energy_bound_component_checks=bounds_checked,
                energy_max_abs_difference_j=max_difference, phase_intervals=intervals,
                summed_phase_component_bounds=totals,
                continuity=dict(header_span_s=endpoints[-1]-endpoints[0], internal_elapsed_s=cumulative,
                                residual_min_s=min(residuals), residual_max_s=max(residuals),
                                residual_range_s=max(residuals)-min(residuals)),
                limitations=['Alternate-format diagnostics never replace predeclared exact quality.',
                             'Loose extracted pairs can discard extra material; only delimiter-only repair is a narrow formatting diagnostic.',
                             'Energy sums assume complete continuous capture and +/-1-second endpoint alignment; no calibration-error guarantee.',
                             'Gross component energy includes other processes; no baseline subtraction or causal efficiency claim.',
                             'Adjacent phase edge bounds can overlap; do not sum them as an exact full-episode decomposition.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_dir', type=Path)
    parser.add_argument('--capture', default='capture-ac-confirmed')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit(args.source_dir, args.capture)
    text = json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n'
    if args.output:
        output = args.output.resolve()
        source = args.source_dir.resolve()
        require(source != output and source not in output.parents, 'output must be outside canonical source/capture')
        args.output.write_text(text)
        print(json.dumps(dict(output=str(output), source_gold_checks=result['source_gold_equal_checks'],
                              energy_checks=result['energy_bound_component_checks'], energy_difference=result['energy_max_abs_difference_j'],
                              counts=result['outcome_counts']), sort_keys=True))
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
