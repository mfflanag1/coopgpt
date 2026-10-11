#!/usr/bin/env python3
"""Independent offline mixed-study recount; imports neither analysis module.

Usage: independent_check.py SOURCE_DIR DATA_DIR [--output FILE]
       independent_check.py --self-test

This checks request outcomes and reconstructs gold from prompt KEEP records.
It does not establish metadata validity, experiment acceptability, or energy.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re

CAP_SLO = {64: 8, 192: 16, 384: 30}
CAP_RECORDS = {64: 4, 192: 12, 384: 24}
INPUT_SIZES = (32, 96, 192)
USAGE_FIELDS = ('prompt_eval_count', 'eval_count', 'total_duration', 'load_duration',
                'prompt_eval_duration', 'eval_duration')


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def nonnegative_integer(value):
    return type(value) is int and value >= 0


def same_json(a, b):
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def gold_from_prompt(job):
    """Derive the requested ordered answer without trusting job['expected']."""
    prompt = job.get('prompt')
    if not isinstance(prompt, str):
        raise ValueError('prompt must be a string')
    table = re.findall(r'^R([0-9]{4}) value=([0-9]{3}) flag=(KEEP|DROP)$', prompt, re.MULTILINE)
    size, cap = job.get('input_rows'), job.get('max_output_tokens')
    if type(size) is not int or size not in INPUT_SIZES or type(cap) is not int or cap not in CAP_SLO:
        raise ValueError('unsupported input/output class')
    if len(table) != size or [int(row[0]) for row in table] != list(range(1, size+1)):
        raise ValueError('table IDs/count do not match declared input rows')
    keep = [(record, value) for record, value, flag in table if flag == 'KEEP']
    if len(keep) != CAP_RECORDS[cap]:
        raise ValueError('KEEP count differs from fixed output class')
    return ';'.join('R' + record + '=' + value for record, value in keep)


def correct_answer(output, gold):
    if not isinstance(output, str) or not gold:
        return False
    value = output.strip()
    if value[:3] == '```' and value[-3:] == '```' and len(value) >= 6:
        value = value[3:-3]
    value = ''.join(value.split())
    target = ''.join(gold.split())
    if value.endswith(';'):
        value = value[:-1]
    if target.endswith(';'):
        target = target[:-1]
    return value == target


def recount_row(row, job, config, elapsed, gold):
    """Fail closed on malformed successes, retaining one outcome per planned ID."""
    errors = []
    arrival, cap = job['arrival_offset_s'], job['max_output_tokens']
    item = dict(request_id=job['request_id'], arrival_offset_s=arrival,
                input_rows=job['input_rows'], cap=cap, slo_s=CAP_SLO[cap],
                api_completed=False, quality_pass=False, api_slo=False, quality_slo=False,
                completion_latency_s=None, first_content_latency_s=None,
                output_sha256=None, output_tokens=None, recorded_failure=False,
                unverified=False, dispatched=False, errors=errors)
    if not isinstance(row, dict):
        errors.append('missing or duplicate row')
        item['unverified'] = True
        return item
    item['dispatched'] = number(row.get('dispatch_offset_s'))
    item['recorded_failure'] = row.get('completed') is False
    # A failed request cannot enter any successful-completion or quality count.
    if row.get('completed') is not True:
        if row.get('completed') is not False:
            errors.append('completed is not bool')
            item['unverified'] = True
        return item
    required = ('request_id', 'arrival_offset_s', 'dispatch_offset_s', 'first_content_offset_s',
                'terminal_offset_s', 'error', 'http_status', 'request_options', 'chunks', 'final')
    if any(key not in row for key in required):
        errors.append('required success fields missing')
    if row.get('request_id') != job['request_id'] or not number(row.get('arrival_offset_s')) or row['arrival_offset_s'] != arrival:
        errors.append('ID or intended arrival mismatch')
    if row.get('error') is not None or not same_json(row.get('http_status'), 200):
        errors.append('success has error or lacks HTTP 200')
    options = dict(config['options'], num_predict=cap)
    if not same_json(row.get('request_options'), options):
        errors.append('sent request options/cap mismatch')
    dispatch, terminal, first = (row.get(name) for name in ('dispatch_offset_s', 'terminal_offset_s', 'first_content_offset_s'))
    if not number(dispatch) or dispatch < arrival or not number(terminal) or terminal < arrival:
        errors.append('invalid dispatch/terminal clocks')
    elif terminal < dispatch or not number(elapsed) or terminal > elapsed:
        errors.append('terminal clock outside collection')
    chunks = row.get('chunks')
    if not isinstance(chunks, list):
        chunks = []
        errors.append('invalid chunks')
    previous, first_seen, text_parts, terminals = dispatch, None, [], []
    for position, wrapped in enumerate(chunks):
        if not isinstance(wrapped, dict) or not isinstance(wrapped.get('data'), dict):
            errors.append('invalid wrapped stream object')
            continue
        time, data = wrapped.get('offset_s'), wrapped['data']
        if not number(time) or time < 0 or (number(previous) and time < previous) or (number(terminal) and time > terminal):
            errors.append('nonmonotonic stream clock')
        previous = time
        if 'error' in data or ('model' in data and data['model'] != config['model']):
            errors.append('stream error/wrong model')
        response = data.get('response', '')
        if not isinstance(response, str):
            errors.append('nonstring response content')
        elif response:
            text_parts.append(response)
            if first_seen is None:
                first_seen = time
        if data.get('done') is True:
            terminals.append((position, data))
    if not text_parts or not number(first) or first != first_seen:
        errors.append('missing content or inconsistent first-content clock')
    final = row.get('final')
    if not isinstance(final, dict):
        errors.append('missing final object')
    else:
        if final.get('done') is not True or final.get('model') != config['model']:
            errors.append('invalid terminal model/done')
        if any(not nonnegative_integer(final.get(field)) for field in USAGE_FIELDS):
            errors.append('invalid usage')
        if not nonnegative_integer(final.get('eval_count')) or not 0 < final['eval_count'] <= cap:
            errors.append('output count outside cap')
        if nonnegative_integer(final.get('eval_count')):
            item['output_tokens'] = final['eval_count']
    if len(terminals) != 1 or terminals[0][0] != len(chunks)-1 or not same_json(terminals[0][1], final):
        errors.append('final does not match unique terminal chunk')
    text = ''.join(text_parts)
    if text:
        item['output_sha256'] = hashlib.sha256(text.encode('utf-8')).hexdigest()
    if errors:
        item['unverified'] = True
        return item
    item.update(api_completed=True, quality_pass=correct_answer(text, gold),
                api_slo=terminal-arrival <= CAP_SLO[cap],
                completion_latency_s=terminal-arrival, first_content_latency_s=first-arrival)
    item['quality_slo'] = item['quality_pass'] and item['api_slo']
    return item


def nearest_ranks(values):
    values = sorted(values)
    n = len(values)
    return dict(n=n, p50=values[(50*n+99)//100-1] if n else None,
                p95=values[(95*n+99)//100-1] if n else None, method='nearest_rank')


def counts(rows):
    n = len(rows)
    successful = [row for row in rows if row['api_completed']]
    output = dict(planned_count=n, observed_dispatch_count=sum(row['dispatched'] for row in rows), recorded_failure_count=sum(row['recorded_failure'] for row in rows),
                  unverified_count=sum(row['unverified'] for row in rows),
                  completion_latency_s=nearest_ranks([row['completion_latency_s'] for row in successful]),
                  first_content_latency_s=nearest_ranks([row['first_content_latency_s'] for row in successful]))
    for field in ('api_completed', 'quality_pass', 'api_slo', 'quality_slo'):
        total = sum(row[field] for row in rows)
        output[field + '_count'] = total
        output[field + '_fraction'] = total/n if n else None
    output['api_failure_or_unverified_count'] = n-len(successful)
    return output


def strata(rows):
    return dict(overall=counts(rows),
                by_cap={str(cap): counts([r for r in rows if r['cap'] == cap]) for cap in CAP_SLO},
                by_input_rows={str(size): counts([r for r in rows if r['input_rows'] == size]) for size in INPUT_SIZES},
                by_cross_class={f'{size}x{cap}': counts([r for r in rows if r['input_rows'] == size and r['cap'] == cap])
                                for size in INPUT_SIZES for cap in CAP_SLO})


def load(path, key, hashes):
    raw = path.read_bytes()
    hashes[key] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def independent_check(source_dir, data_dir):
    source_dir, data_dir = Path(source_dir), Path(data_dir)
    source_hashes, capture_hashes, design_errors = {}, {}, []
    config = load(source_dir/'CONFIG.json', 'CONFIG.json', source_hashes)
    plan = load(source_dir/'PLAN.json', 'PLAN.json', source_hashes)
    if not isinstance(config, dict) or not isinstance(config.get('options'), dict) or not isinstance(config.get('model'), str):
        raise ValueError('invalid CONFIG')
    if not isinstance(plan, list) or len(plan) != 18:
        raise ValueError('expected 18 planned windows')
    windows, traces = [], {}
    combinations = []
    for ordinal, planned in enumerate(plan, 1):
        if not isinstance(planned, dict) or type(planned.get('index')) is not int or planned['index'] != ordinal:
            raise ValueError('invalid planned index/order')
        rate, parallel, rep = planned.get('rate'), planned.get('parallel'), planned.get('rep')
        if not number(rate) or rate not in (.3, .6, 1.2) or type(parallel) is not int or parallel not in (1, 2, 4) or type(rep) is not int or rep not in (1, 2):
            raise ValueError('invalid planned dimensions')
        combinations.append((rate, parallel, rep))
        name = planned.get('trace_file')
        if not isinstance(name, str) or Path(name).is_absolute() or '..' in Path(name).parts:
            raise ValueError('unsafe trace filename')
        if name not in traces:
            traces[name] = load(source_dir/name, name, source_hashes)
        trace = traces[name]
        if not isinstance(trace, list) or len(trace) != round(90*rate):
            raise ValueError('planned trace count differs from fixed 90-second design')
        ids = [job.get('request_id') if isinstance(job, dict) else None for job in trace]
        if any(not isinstance(value, str) or not value for value in ids) or len(set(ids)) != len(ids):
            raise ValueError('invalid/duplicate planned IDs')
        gold = {}
        for i, job in enumerate(trace):
            if not number(job.get('arrival_offset_s')) or job['arrival_offset_s'] != i/rate:
                raise ValueError('planned arrival differs from k/rate')
            gold[job['request_id']] = gold_from_prompt(job)
            if job.get('expected') != gold[job['request_id']]:
                design_errors.append(name + '/' + job['request_id'] + ': supplied expected answer disagrees with reconstructed gold')
            if not same_json(job.get('slo_s'), CAP_SLO[job['max_output_tokens']]):
                design_errors.append(name + '/' + job['request_id'] + ': supplied SLO differs from fixed cap rule')
        capture_errors = []
        relative = f'window-{ordinal:02d}/REQUESTS.json'
        try:
            stored = load(data_dir/relative, relative, capture_hashes)
        except (OSError, ValueError, UnicodeError) as error:
            stored = {}
            capture_errors.append('missing/unreadable REQUESTS: ' + type(error).__name__)
        if not isinstance(stored, dict):
            stored = {}
            capture_errors.append('REQUESTS is not object')
        captured = stored.get('requests')
        if not isinstance(captured, list):
            captured = []
            capture_errors.append('request array missing')
        actual_ids = [row.get('request_id') if isinstance(row, dict) else None for row in captured]
        if actual_ids != ids:
            capture_errors.append('captured ID sequence differs from planned sequence')
        frequency = Counter(value for value in actual_ids if isinstance(value, str))
        unique = {row['request_id']: row for row in captured if isinstance(row, dict)
                  and isinstance(row.get('request_id'), str) and frequency[row['request_id']] == 1}
        outcomes = [recount_row(unique.get(job['request_id']), job, config, stored.get('elapsed_seconds'), gold[job['request_id']]) for job in trace]
        windows.append(dict(planned, captured_row_count=len(captured), capture_errors=capture_errors,
                            metrics=strata(outcomes), requests=outcomes))
    required = Counter((rate, p, rep) for rate in (.3, .6, 1.2) for p in (1, 2, 4) for rep in (1, 2))
    if Counter(combinations) != required:
        raise ValueError('PLAN lacks the exact rate/parallel/repetition cells')
    cells, matched = [], []
    for rate in (.3, .6, 1.2):
        for p in (1, 2, 4):
            selected = [w for w in windows if w['rate'] == rate and w['parallel'] == p]
            rows = [r for w in selected for r in w['requests']]
            cells.append(dict(rate=rate, parallel=p, windows=[w['index'] for w in selected], metrics=strata(rows)))
        for rep in (1, 2):
            group = {w['parallel']: w for w in windows if w['rate'] == rate and w['rep'] == rep}
            base = group[1]
            for p in (2, 4):
                treatment = group[p]
                if not same_json(traces[base['trace_file']], traces[treatment['trace_file']]):
                    design_errors.append(f'rate={rate}, rep={rep}: matched traces differ')
                difference = {field: treatment['metrics']['overall'][field]-base['metrics']['overall'][field]
                              for field in ('quality_slo_count', 'quality_slo_fraction', 'api_slo_count', 'api_slo_fraction', 'quality_pass_count', 'api_completed_count')}
                matched.append(dict(rate=rate, rep=rep, contrast=f'P{p}-P1', baseline_window=base['index'],
                                    treatment_window=treatment['index'], difference=difference,
                                    cap_quality_slo_count_difference={str(cap): treatment['metrics']['by_cap'][str(cap)]['quality_slo_count']-base['metrics']['by_cap'][str(cap)]['quality_slo_count'] for cap in CAP_SLO}))
    all_rows = [row for window in windows for row in window['requests']]
    return dict(schema_version=1, method='independent raw-data recount with prompt-derived gold',
                metadata_and_energy_validity_assessed=False, planned_offered_count=1134,
                recounted_planned_count=len(all_rows), recorded_request_rows=sum(w['captured_row_count'] for w in windows),
                recorded_request_file_count=len(capture_hashes), source_sha256=source_hashes, capture_sha256=capture_hashes,
                design_errors=sorted(set(design_errors)), windows=windows, rate_parallel_cells=cells,
                matched_comparisons=matched, aggregate_mixed_class_totals=strata(all_rows),
                notes=['All planned offers remain in denominators.',
                       'Quantiles are nearest-rank arrival-to-event latencies among validated API completions.',
                       'Cell quantiles pool two repetitions descriptively; no independence or population CI is asserted.',
                       'Missing REQUESTS files alone do not distinguish unoffered work from lost captures; inspect collector abort metadata for that distinction.',
                       'This recount does not replace metadata/provenance validity checks or the finite-window screen.'])


def self_test():
    """Synthetic memory fixtures only: does not open source or capture files."""
    config = dict(model='fixture', options=dict(temperature=0, seed=0, num_ctx=4096, num_predict=64))
    def job_for(cap=64, arrival=0):
        records = CAP_RECORDS[cap]
        table = '\n'.join(f'R{i:04d} value=123 flag={"KEEP" if i <= records else "DROP"}' for i in range(1, 33))
        return dict(request_id='r0001', arrival_offset_s=arrival, input_rows=32, max_output_tokens=cap, prompt=table)
    def row_for(job, latency=1):
        arrival = job['arrival_offset_s']
        final = dict(model='fixture', done=True, response='', prompt_eval_count=20, eval_count=10,
                     total_duration=100, load_duration=1, prompt_eval_duration=20, eval_duration=79)
        return dict(request_id='r0001', arrival_offset_s=arrival, dispatch_offset_s=arrival+.09,
                    terminal_offset_s=arrival+latency, first_content_offset_s=arrival+.1,
                    completed=True, error=None, http_status=200,
                    request_options=dict(config['options'], num_predict=job['max_output_tokens']),
                    chunks=[dict(offset_s=arrival+.1, data={'response': gold_from_prompt(job), 'done': False}),
                            dict(offset_s=arrival+latency-.001, data=final)], final=final.copy())
    checks = 0
    for cap, deadline in CAP_SLO.items():
        job = job_for(cap, 2)
        row = row_for(job, deadline)
        assert recount_row(row, job, config, 100, gold_from_prompt(job))['quality_slo']
        row['terminal_offset_s'] += .04
        row['chunks'][-1]['offset_s'] += .04
        late = recount_row(row, job, config, 100, gold_from_prompt(job))
        assert late['api_completed'] and not late['api_slo']
        checks += 2
    job = job_for()
    gold = gold_from_prompt(job)
    assert correct_answer('```\n' + gold.replace(';', '; \n') + ';\n```', gold)
    for wrong in ('Answer: '+gold, gold+';;', gold+';R0032=123', '```text\n'+gold+'```', ';'.join(reversed(gold.split(';')))):
        assert not correct_answer(wrong, gold)
    checks += 6
    edits = [lambda r: r.update(completed=False), lambda r: r.update(completed=1),
             lambda r: r.update(http_status=500), lambda r: r['final'].update(eval_count=True),
             lambda r: r['chunks'][0]['data'].update(response='wrong'),
             lambda r: r.update(first_content_offset_s=.2),
             lambda r: r.update(request_options=dict(config['options'], num_predict=192))]
    for edit in edits:
        row = row_for(job)
        edit(row)
        assert not recount_row(row, job, config, 100, gold)['quality_slo']
        checks += 1
    missing = recount_row(None, job, config, None, gold)
    successful = recount_row(row_for(job), job, config, 100, gold)
    result = counts([missing, successful])
    assert result['planned_count'] == 2 and result['quality_slo_fraction'] == .5
    assert nearest_ranks(list(range(1, 17))) == dict(n=16, p50=8, p95=16, method='nearest_rank')
    assert nearest_ranks([])['p95'] is None
    assert counts([])['quality_slo_fraction'] is None
    checks += 4
    # End-to-end fixtures live in an automatically removed temporary directory.
    # None of these paths are the real study's source or capture directory.
    import tempfile
    with tempfile.TemporaryDirectory(prefix='independent-check-fixture-') as directory:
        source, data = Path(directory)/'source', Path(directory)/'capture'
        source.mkdir()
        data.mkdir()
        def save(path, value):
            path.write_text(json.dumps(value, sort_keys=True))
        save(source/'CONFIG.json', config)
        plan = []
        for rate in (.3, .6, 1.2):
            for rep in (1, 2):
                trace = []
                for i in range(round(90*rate)):
                    cap = tuple(CAP_SLO)[i % 3]
                    size = INPUT_SIZES[(i//3) % 3]
                    job = job_for(cap, i/rate)
                    job.update(request_id=f'r{i+1:04d}', input_rows=size,
                               prompt='\n'.join(f'R{k:04d} value=123 flag={"KEEP" if k <= CAP_RECORDS[cap] else "DROP"}' for k in range(1, size+1)),
                               slo_s=CAP_SLO[cap])
                    job['expected'] = gold_from_prompt(job)
                    trace.append(job)
                trace_file = f'trace-{rate}-{rep}.json'
                save(source/trace_file, trace)
                for parallel in (1, 2, 4):
                    index = len(plan)+1
                    plan.append(dict(index=index, rate=rate, rep=rep, parallel=parallel, trace_file=trace_file))
                    window = data/f'window-{index:02d}'
                    window.mkdir()
                    rows = []
                    for i, job in enumerate(trace):
                        latency = CAP_SLO[job['max_output_tokens']]+1 if parallel == 2 and i == 0 else 1
                        row = row_for(job, latency)
                        row['request_id'] = job['request_id']
                        if parallel == 4 and i == 0:
                            row['chunks'][0]['data']['response'] = 'wrong'
                        rows.append(row)
                    save(window/'REQUESTS.json', dict(elapsed_seconds=max(r['terminal_offset_s'] for r in rows)+.1, requests=rows))
        save(source/'PLAN.json', plan)
        audit = independent_check(source, data)
        totals = audit['aggregate_mixed_class_totals']['overall']
        assert audit['recounted_planned_count'] == 1134 and not audit['design_errors']
        assert totals['api_completed_count'] == 1134 and totals['quality_pass_count'] == 1128
        assert totals['api_slo_count'] == 1128 and totals['quality_slo_count'] == 1122
        assert len(audit['rate_parallel_cells']) == 9 and len(audit['matched_comparisons']) == 12
        assert all(m['difference']['quality_slo_count'] == -1 for m in audit['matched_comparisons'])
        first_cell = audit['rate_parallel_cells'][0]
        expected_latencies = sorted([((i/.3)+1)-(i/.3) for i in range(27)]*2)
        assert first_cell['metrics']['overall']['completion_latency_s'] == dict(n=54, p50=expected_latencies[26], p95=expected_latencies[51], method='nearest_rank')
        assert first_cell['metrics']['by_cross_class']['32x64']['planned_count'] == 6
        (data/'window-01'/'REQUESTS.json').unlink()
        missing_audit = independent_check(source, data)
        assert missing_audit['recounted_planned_count'] == 1134
        assert missing_audit['windows'][0]['metrics']['overall']['unverified_count'] == 27
        assert missing_audit['aggregate_mixed_class_totals']['overall']['api_completed_count'] == 1107
        checks += 10
    return dict(synthetic_only=True, passed=True, assertion_groups=checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_dir', nargs='?', type=Path)
    parser.add_argument('data_dir', nargs='?', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        result = self_test()
    else:
        if args.source_dir is None or args.data_dir is None:
            parser.error('SOURCE_DIR and DATA_DIR are required unless --self-test is used')
        result = independent_check(args.source_dir, args.data_dir)
    encoded = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n'
    if args.output:
        args.output.write_text(encoded)
        print(json.dumps(dict(output=str(args.output), written=True), sort_keys=True))
    else:
        print(encoded, end='')


if __name__ == '__main__':
    main()
