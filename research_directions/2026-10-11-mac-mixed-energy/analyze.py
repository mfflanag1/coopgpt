#!/usr/bin/env python3
"""Offline validation and descriptive analysis of the 18-window mixed study."""
import argparse
from collections import Counter
from datetime import datetime
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import zlib

BASE = Path(__file__).resolve().parent
MODEL = 'llama3.2:3b'
DIGEST = 'a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72'
OPTIONS = dict(temperature=0, seed=0, num_predict=64, num_ctx=4096)
RATES, PARALLELS, CAPS, INPUTS = (.3, .6, 1.2), (1, 2, 4), (64, 192, 384), (32, 96, 192)
SLOS = {64: 8, 192: 16, 384: 30}
USAGE = ('prompt_eval_count', 'eval_count', 'total_duration', 'load_duration', 'prompt_eval_duration', 'eval_duration')
PHASES = ('loaded_idle_start', 'workload_start', 'workload_drained', 'server_quiescent', 'episode_end')


def finite(x):
    return type(x) in (float, int) and math.isfinite(x)


def integer(x):
    return type(x) is int and x >= 0


def exact(a, b):
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def timestamp(value):
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return result if result.utcoffset() is not None else None
    except (ValueError, TypeError, AttributeError):
        return None


def read_json(path, errors, hashes):
    try:
        raw = path.read_bytes()
        hashes[str(path.name)] = hashlib.sha256(raw).hexdigest()
        return json.loads(raw, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    except (OSError, ValueError, UnicodeError) as exc:
        errors.append(path.name + ': unreadable/invalid JSON (' + type(exc).__name__ + ')')
        return None


def obj(value, errors, label):
    if isinstance(value, dict):
        return value
    errors.append(label + ': expected object')
    return {}


def quality_pass(text, expected):
    """Only whitespace, a bare enclosing fence, and one final ';' are harmless."""
    if not isinstance(text, str) or not isinstance(expected, str) or not expected.strip():
        return False
    text = text.strip()
    if text.startswith('```') and text.endswith('```') and len(text) >= 6:
        text = text[3:-3]
    clean = lambda value: re.sub(r'\s+', '', value).removesuffix(';')
    return clean(text) == clean(expected)


def quantiles(values):
    ordered = sorted(values)
    return dict(n=len(values), p50=ordered[math.ceil(.5*len(values))-1] if values else None,
                p95=ordered[math.ceil(.95*len(values))-1] if values else None, method='nearest_rank')


def validate_row(record, job, elapsed):
    errors, validity = [], []
    row = obj(record, errors, 'row')
    for key in ('request_id', 'arrival_offset_s', 'dispatch_offset_s', 'first_content_offset_s',
                'terminal_offset_s', 'completed', 'error', 'chunks', 'final'):
        if key not in row:
            errors.append('missing field ' + key)
    arrival, cap = job['arrival_offset_s'], job['max_output_tokens']
    if row.get('request_id') != job['request_id'] or not finite(row.get('arrival_offset_s')) or row.get('arrival_offset_s') != arrival:
        errors.append('ID/intended arrival mismatch')
    if row.get('dispatch_offset_s') is not None or row.get('completed') is True or 'request_options' in row:
        if not exact(row.get('request_options'), dict(OPTIONS, num_predict=cap)):
            errors.append('actual request options/cap mismatch')
    completed = row.get('completed')
    if type(completed) is not bool:
        errors.append('completed is not bool')
    if completed is True and row.get('error') is not None:
        errors.append('success has error')
    if completed is False and (not isinstance(row.get('error'), str) or not row['error']):
        errors.append('failed row lacks error')
    dispatch, first, terminal = (row.get(key + '_offset_s') for key in ('dispatch', 'first_content', 'terminal'))
    if dispatch is None:
        if completed is not False:
            errors.append('success lacks dispatch')
    elif not finite(dispatch) or dispatch < arrival:
        errors.append('invalid/reversed dispatch clock')
    if not finite(terminal) or terminal < 0 or (finite(dispatch) and terminal < dispatch):
        errors.append('invalid/reversed terminal clock')
    if finite(terminal) and finite(elapsed) and terminal > elapsed:
        errors.append('terminal exceeds collection elapsed')
    lag = dispatch - arrival if finite(dispatch) else None
    chunks = row.get('chunks')
    if not isinstance(chunks, list):
        errors.append('chunks is not list')
        chunks = []
    previous, first_seen, content, dones = dispatch, None, [], []
    for index, item in enumerate(chunks):
        item = obj(item, errors, 'chunk')
        offset = item.get('offset_s')
        if not finite(offset) or offset < 0 or (finite(previous) and offset < previous) or (finite(terminal) and offset > terminal):
            errors.append('invalid/reversed chunk clock')
        if finite(offset):
            previous = offset
        data = obj(item.get('data'), errors, 'chunk data')
        if 'error' in data and completed is True:
            errors.append('success contains server error')
        if 'model' in data and data['model'] != MODEL:
            errors.append('wrong chunk model')
        if 'response' in data and not isinstance(data['response'], str):
            errors.append('response is not string')
        response = data.get('response', '')
        if isinstance(response, str) and response:
            content.append(response)
            if first_seen is None:
                first_seen = offset
        if data.get('done') is True:
            dones.append((index, data))
    if first != first_seen or (first is not None and not finite(first)):
        errors.append('first content clock inconsistent with chunks')
    if chunks and dispatch is None:
        errors.append('chunks without dispatch')
    final = row.get('final')
    if final is not None and not isinstance(final, dict):
        errors.append('invalid final type')
        final = None
    if dones:
        if len(dones) != 1 or dones[0][0] != len(chunks)-1 or not exact(final, dones[0][1]):
            errors.append('final differs from unique terminal chunk')
    elif final is not None:
        errors.append('final lacks terminal chunk')
    if completed is True:
        if not exact(row.get('http_status'), 200):
            errors.append('success lacks HTTP 200')
        if not content or not isinstance(final, dict) or final.get('done') is not True:
            errors.append('success lacks content or done=true')
        if isinstance(final, dict):
            if final.get('model') != MODEL:
                errors.append('wrong terminal model')
            if any(not integer(final.get(key)) for key in USAGE):
                errors.append('invalid terminal usage')
            if not integer(final.get('eval_count')) or not 0 < final['eval_count'] <= cap:
                errors.append('output token count outside requested cap')
    usage = {key: final[key] for key in USAGE if isinstance(final, dict) and integer(final.get(key))}
    api = completed is True and not errors
    text = ''.join(content)
    quality = api and quality_pass(text, job.get('expected'))
    ontime = api and terminal - arrival <= SLOS[cap]
    return dict(request_id=job['request_id'], record_present=isinstance(record, dict), arrival_offset_s=arrival, cap=cap,
                input_rows=job.get('input_rows'), input_class=job.get('input_class'), output_class=job.get('output_class'),
                slo_s=SLOS[cap], api_completed=api, quality_pass=quality, api_slo=ontime,
                quality_slo=quality and ontime, recorded_completed=completed if type(completed) is bool else None,
                terminal_offset_s=terminal if finite(terminal) else None,
                dispatch_offset_s=dispatch if finite(dispatch) else None, dispatch_lag_s=lag, dispatch_lag_over_100ms=lag is not None and lag > .1,
                completion_latency_s=terminal-arrival if api else None,
                first_content_latency_s=first-arrival if api else None,
                output_sha256=hashlib.sha256(text.encode()).hexdigest() if content else None,
                output_utf8_bytes=len(text.encode()), usage=usage,
                done_reason=final.get('done_reason') if isinstance(final, dict) else None,
                error=row.get('error'), validation_errors=errors, validity_errors=validity)


def collection(value, jobs, errors, label):
    value = obj(value, errors, label)
    elapsed = value.get('elapsed_seconds')
    if not finite(elapsed) or elapsed < 0 or timestamp(value.get('started_utc')) is None:
        errors.append(label + ': invalid epoch/elapsed')
    records = value.get('requests')
    if not isinstance(records, list):
        errors.append(label + ': missing request array')
        records = []
    ids = [row.get('request_id') if isinstance(row, dict) else None for row in records]
    if ids != [job['request_id'] for job in jobs]:
        errors.append(label + ': offered IDs/order differ from trace')
    counts = Counter(value for value in ids if isinstance(value, str))
    lookup = {row['request_id']: row for row in records if isinstance(row, dict)
              and isinstance(row.get('request_id'), str) and counts[row['request_id']] == 1}
    results = [validate_row(lookup.get(job['request_id']), job, elapsed) for job in jobs]
    for row in results:
        errors.extend(label + '/' + row['request_id'] + ': ' + error for error in row['validation_errors'] + row['validity_errors'])
    return results


def metrics(rows):
    n = len(rows)
    successes = [row for row in rows if row['api_completed']]
    result = dict(planned_count=n, api_completed_count=len(successes),
                  api_failure_or_unverified_count=n-len(successes),
                  recorded_failure_count=sum(row['recorded_completed'] is False for row in rows),
                  unverified_outcome_count=sum(row['recorded_completed'] is not False and not row['api_completed'] for row in rows),
                  dispatched_count=sum(row['dispatch_offset_s'] is not None for row in rows),
                  recorded_terminal_count=sum(row['terminal_offset_s'] is not None for row in rows),
                  quality_pass_count=sum(row['quality_pass'] for row in rows),
                  quality_failure_among_api_completed_count=sum(not row['quality_pass'] for row in successes),
                  api_slo_count=sum(row['api_slo'] for row in rows),
                  quality_slo_count=sum(row['quality_slo'] for row in rows),
                  completion_latency_s=quantiles([row['completion_latency_s'] for row in successes]),
                  first_content_latency_s=quantiles([row['first_content_latency_s'] for row in successes]),
                  generation_length_stop_count=sum(row['done_reason'] == 'length' for row in successes),
                  reported_output_tokens=sum(row['usage'].get('eval_count', 0) for row in rows),
                  reported_prompt_eval_tokens=sum(row['usage'].get('prompt_eval_count', 0) for row in rows),
                  output_token_reporting_count=sum('eval_count' in row['usage'] for row in rows),
                  actual_output_token_counts=[row['usage'].get('eval_count') for row in rows])
    for key in ('api_completed', 'quality_pass', 'api_slo', 'quality_slo'):
        result[key + '_fraction'] = result[key + '_count']/n if n else None
    result['quality_slo_goodput_per_second'] = result['quality_slo_count']/90
    return result


def thermal_ok(value):
    if not isinstance(value, str):
        return False
    cleaned = re.sub(r'(?im)^\s*(?:Note:\s*)?No (?:thermal warning level|performance warning level|CPU power status) has been recorded\s*$', '', value)
    return ('No thermal warning level has been recorded' in value and 'No performance warning level has been recorded' in value
            and not re.search(r'(?i)warning|thermal|CPU_Speed_Limit|Scheduler_Limit', cleaned))


def metadata(meta, plan, log, errors):
    for key, expected in dict(plan, model=MODEL, options=OPTIONS, status='completed').items():
        if not exact(meta.get(key), expected):
            errors.append('RUN mismatch: ' + key)
    if re.search(r'(?i)truncat(?:ing|ed).*prompt|prompt.*truncat', log):
        errors.append('server log reports prompt truncation')
    observed = sorted({int(n) for pattern in (r'n_seq_max\s*=\s*(\d+)', r'\bParallel[=:]\s*(\d+)', r'--parallel\s+(\d+)') for n in re.findall(pattern, log)})
    if observed != [plan['parallel']] or not exact(meta.get('runtime_parallel_values'), [plan['parallel']]):
        errors.append('actual parallelism unverified from runtime logs/metadata')
    if not isinstance(meta.get('version'), dict) or meta['version'].get('version') != '0.20.0':
        errors.append('server version mismatch')
    tag = meta.get('model_tag')
    if not isinstance(tag, dict) or tag.get('digest') != DIGEST or tag.get('name') != MODEL:
        errors.append('model tag/digest mismatch')
    settings = meta.get('server_settings', {})
    required_settings = {'OLLAMA_NUM_PARALLEL': str(plan['parallel']), 'OLLAMA_CONTEXT_LENGTH': '4096',
                         'OLLAMA_FLASH_ATTENTION': '0', 'OLLAMA_KV_CACHE_TYPE': 'f16', 'OLLAMA_MAX_LOADED_MODELS': '1'}
    if not isinstance(settings, dict) or any(settings.get(key) != expected for key, expected in required_settings.items()):
        errors.append('server settings mismatch')
    for boundary in ('before', 'after'):
        state = obj(meta.get(boundary), errors, boundary)
        if timestamp(state.get('utc')) is None or not isinstance(state.get('power'), str) or not re.search(r"Now drawing from ['\"]AC Power['\"]", state['power']):
            errors.append(boundary + ': UTC/AC snapshot invalid')
        if not thermal_ok(state.get('thermal')):
            errors.append(boundary + ': thermal warning or unrecognized snapshot')
        load = state.get('load_average')
        if not isinstance(load, list) or len(load) != 3 or not all(finite(x) and x >= 0 for x in load):
            errors.append(boundary + ': load snapshot invalid')
        if meta.get('original_endpoint_idle_' + boundary) is not True:
            errors.append(boundary + ': original endpoint not idle')
        loaded = obj(meta.get('loaded_' + boundary), errors, 'loaded_' + boundary).get('models')
        if not isinstance(loaded, list) or len(loaded) != 1 or not isinstance(loaded[0], dict):
            errors.append(boundary + ': loaded model unavailable')
        elif loaded[0].get('digest') != DIGEST or not exact(loaded[0].get('context_length'), 4096) or not finite(loaded[0].get('size_vram')) or loaded[0]['size_vram'] <= 0:
            errors.append(boundary + ': loaded digest/context/GPU mismatch')
    if not isinstance(meta.get('loaded_after_unload'), dict) or meta['loaded_after_unload'].get('models') != [] or meta.get('cleanup_error'):
        errors.append('owned-model unload/cleanup unverified')
    if not integer(meta.get('dedicated_server_pid')) or not meta.get('dedicated_server_pid') or type(meta.get('dedicated_server_returncode')) is not int:
        errors.append('owned process start/termination missing')
    phases = meta.get('phases')
    phases = phases if isinstance(phases, list) else []
    names = [phase.get('name') if isinstance(phase, dict) else None for phase in phases]
    phase_map = {phase['name']: phase.get('utc') for phase in phases if isinstance(phase, dict) and isinstance(phase.get('name'), str)}
    times = [timestamp(phase_map.get(name)) for name in PHASES]
    if any(names.count(name) != 1 for name in PHASES) or any(t is None for t in times) or any(b < a for a, b in zip(times, times[1:]) if a and b):
        errors.append('required phase clocks missing/duplicated/out of order')
    return observed, phase_map


def energy_diagnostics(parsed, phases):
    result = dict(scope='gross CPU/GPU/ANE domain estimates; no process attribution or baseline subtraction',
                  parse_errors=parsed['errors'], intervals={})
    for name, start, end in (('loaded_idle_baseline', 'loaded_idle_start', 'workload_start'),
                              ('workload_and_drain', 'workload_start', 'workload_drained'),
                              ('unload', 'workload_drained', 'server_quiescent'),
                              ('post_idle', 'server_quiescent', 'episode_end'),
                              ('full_episode', 'loaded_idle_start', 'episode_end')):
        if parsed['errors'] or not parsed['samples'] or not timestamp(phases.get(start)) or not timestamp(phases.get(end)):
            result['intervals'][name] = dict(valid=False, errors=['missing/invalid power capture or phase clocks'], lower_j=None, upper_j=None)
        else:
            import energy
            result['intervals'][name] = energy.energy_bounds(parsed['samples'], phases[start], phases[end])
    return result


def analyze_window(data_dir, plan, trace, parsed, global_errors, config):
    path = data_dir / f"window-{plan['index']:02d}"
    errors, hashes = [], {}
    meta = obj(read_json(path/'RUN.json', errors, hashes), errors, 'RUN')
    requests = read_json(path/'REQUESTS.json', errors, hashes)
    warmup = read_json(path/'WARMUP.json', errors, hashes)
    try:
        raw = (path/'SERVER.log').read_bytes()
        log = raw.decode()
        hashes['SERVER.log'] = hashlib.sha256(raw).hexdigest()
    except (OSError, UnicodeError):
        log = ''
        errors.append('SERVER.log missing/unreadable')
    observed, phases = metadata(meta, plan, log, errors)
    warm_jobs = [dict(job, max_output_tokens=64, slo_s=8) for job in config.get('warmups', [])]
    warms = collection(warmup, warm_jobs, errors, 'warmup')
    if len(warms) != 4 or not all(row['api_completed'] for row in warms):
        errors.append('four warmups did not all succeed')
    rows = collection(requests, trace, errors, 'requests')
    if isinstance(requests, dict) and isinstance(warmup, dict):
        start, warm_start = timestamp(requests.get('started_utc')), timestamp(warmup.get('started_utc'))
        if start and warm_start and finite(warmup.get('elapsed_seconds')) and (start-warm_start).total_seconds() < warmup['elapsed_seconds'] + 2:
            errors.append('two-second post-warmup wait unverified')
        phase_times = {name: timestamp(value) for name, value in phases.items()}
        if start and phase_times.get('workload_start') != start:
            errors.append('workload phase differs from client epoch')
        for early, late, minimum in (('loaded_idle_start', 'workload_start', config.get('pre_idle_s')),
                                     ('server_quiescent', 'episode_end', config.get('post_idle_s'))):
            a, b = phase_times.get(early), phase_times.get(late)
            if not finite(minimum) or (a and b and (b-a).total_seconds() < minimum):
                errors.append('fixed idle interval unverified: ' + early)
        drained = phase_times.get('workload_drained')
        elapsed = requests.get('elapsed_seconds')
        if start and drained and finite(elapsed) and (drained-start).total_seconds()+.001 < max(90, elapsed):
            errors.append('drain phase precedes offered interval/client drain')
        idle_start = phase_times.get('loaded_idle_start')
        if idle_start and warm_start and finite(warmup.get('elapsed_seconds')) and (idle_start-warm_start).total_seconds()+.001 < warmup['elapsed_seconds']:
            errors.append('loaded idle precedes warmup drain')
        before = timestamp(meta.get('before', {}).get('utc')) if isinstance(meta.get('before'), dict) else None
        after = timestamp(meta.get('after', {}).get('utc')) if isinstance(meta.get('after'), dict) else None
        episode_end = phase_times.get('episode_end')
        if (before and warm_start and before > warm_start) or (after and episode_end and after < episode_end):
            errors.append('snapshot clocks do not bracket the episode')
    result = dict(plan, valid=not errors and not global_errors, validation_errors=errors,
                  global_validation_errors=global_errors, raw_sha256=hashes, metrics=metrics(rows),
                  by_output_cap={str(cap): metrics([row for row in rows if row['cap'] == cap]) for cap in CAPS},
                  by_input_rows={str(size): metrics([row for row in rows if row['input_rows'] == size]) for size in INPUTS},
                  by_cross_class={f'{size}x{cap}': metrics([row for row in rows if row['input_rows'] == size and row['cap'] == cap]) for size in INPUTS for cap in CAPS},
                  offered_cohorts={name: metrics([row for row in rows if low <= row['arrival_offset_s'] < high]) for name, low, high in (('early_third', 0, 30), ('middle_third', 30, 60), ('late_third', 60, 90))},
                  backlog_includes_unverified_records=any(not row['record_present'] for row in rows),
                  known_dispatched_unfinished_count={str(t): sum(row['dispatch_offset_s'] is not None and row['dispatch_offset_s'] <= t and (row['terminal_offset_s'] is None or row['terminal_offset_s'] > t) for row in rows) for t in (30, 60, 90, 120, 135)},
                  unfinished_offered_count={str(t): sum(row['arrival_offset_s'] <= t and (row['terminal_offset_s'] is None or row['terminal_offset_s'] > t) for row in rows) for t in (30, 60, 90, 120, 135)},
                  api_completions_by_terminal_interval={f'{low}-{high}': sum(row['api_completed'] and low <= row['terminal_offset_s'] and (row['terminal_offset_s'] < high or (high == 135 and row['terminal_offset_s'] == high)) for row in rows) for low, high in ((0, 30), (30, 60), (60, 90), (90, 120), (120, 135))},
                  last_recorded_terminal_s=max((row['terminal_offset_s'] for row in rows if row['terminal_offset_s'] is not None), default=None),
                  maximum_dispatch_lag_s=max((row['dispatch_lag_s'] for row in rows if row['dispatch_lag_s'] is not None), default=None),
                  dedicated_server_pid=meta.get('dedicated_server_pid'),
                  warmup_completed_count=sum(row['api_completed'] for row in warms), actual_parallel_values=observed,
                  phases=phases, snapshots={key: meta.get(key) for key in ('before', 'after')},
                  loaded_model_observations={key: meta.get(key) for key in ('loaded_before', 'loaded_after', 'loaded_after_unload')},
                  memory_log_observations=[line for line in log.splitlines() if re.search(r'(?i)\bKV\b|memory|buffer size', line)],
                  energy=energy_diagnostics(parsed, phases), requests=rows)
    elapsed = requests.get('elapsed_seconds') if isinstance(requests, dict) else None
    result['intended_arrivals_elapsed_count'] = sum(row['arrival_offset_s'] <= elapsed for row in rows) if finite(elapsed) else None
    result['planned_not_yet_arrived_count'] = len(rows)-result['intended_arrivals_elapsed_count'] if finite(elapsed) else None
    conditions = dict(valid_window=result['valid'], no_api_errors=result['metrics']['api_failure_or_unverified_count'] == 0,
                      overall_quality_slo_at_least_90_percent=result['metrics']['quality_slo_fraction'] is not None and result['metrics']['quality_slo_fraction'] >= .9,
                      every_cap_quality_slo_at_least_80_percent=all(group['quality_slo_fraction'] is not None and group['quality_slo_fraction'] >= .8 for group in result['by_output_cap'].values()),
                      backlog_at_90_within_limit=result['unfinished_offered_count']['90'] <= math.ceil(.1*len(trace)))
    result['finite_window_screen'] = dict(passed=all(conditions.values()), conditions=conditions)
    return result


def load_design(source_dir, errors, hashes):
    config = obj(read_json(source_dir/'CONFIG.json', errors, hashes), errors, 'CONFIG')
    for key, expected in dict(model=MODEL, digest=DIGEST, options=OPTIONS, offered_seconds=90,
                              rates=list(RATES), parallels=list(PARALLELS), input_rows=list(INPUTS),
                              output_caps=list(CAPS), planned_offered=1134, repetitions=2,
                              slo_by_cap={str(k): v for k, v in SLOS.items()}).items():
        if not exact(config.get(key), expected):
            errors.append('CONFIG mismatch: ' + key)
    plan = read_json(source_dir/'PLAN.json', errors, hashes)
    if not isinstance(plan, list) or len(plan) != 18 or any(not isinstance(p, dict) for p in plan):
        raise ValueError('Cannot reconstruct the 18 planned windows without a valid PLAN.json')
    combinations = []
    traces = {}
    for index, p in enumerate(plan, 1):
        if (not exact(p.get('index'), index) or not finite(p.get('rate')) or p['rate'] not in RATES
                or type(p.get('rep')) is not int or p['rep'] not in (1, 2)
                or type(p.get('parallel')) is not int or p['parallel'] not in PARALLELS):
            raise ValueError('Invalid planned window dimensions at index ' + str(index))
        combinations.append((p['rate'], p['rep'], p['parallel']))
        name = p.get('trace_file')
        if not isinstance(name, str) or Path(name).is_absolute() or '..' in Path(name).parts:
            raise ValueError('Invalid planned trace path at index ' + str(index))
        if name in traces:
            continue
        trace = read_json(source_dir/name, errors, hashes)
        n = round(90*p['rate'])
        if not isinstance(trace, list) or len(trace) != n or any(not isinstance(job, dict) for job in trace):
            raise ValueError('Cannot reconstruct planned offers from ' + name)
        ids = [job.get('request_id') for job in trace]
        if any(not isinstance(value, str) or not value for value in ids) or len(set(ids)) != n:
            raise ValueError('Invalid planned request IDs in ' + name)
        for i, job in enumerate(trace):
            cap, size = job.get('max_output_tokens'), job.get('input_rows')
            if type(cap) is not int or cap not in CAPS or type(size) is not int or size not in INPUTS:
                raise ValueError('Invalid planned workload classes in ' + name)
            if not finite(job.get('arrival_offset_s')) or job['arrival_offset_s'] != i/p['rate']:
                errors.append(name + ': scheduled arrival differs from k/rate')
            if not exact(job.get('slo_s'), SLOS[cap]):
                errors.append(name + ': class deadline mismatch')
            if job.get('input_class') != dict(zip(INPUTS, ('short', 'medium', 'long')))[size] or job.get('output_class') != dict(zip(CAPS, ('small', 'medium', 'large')))[cap]:
                errors.append(name + ': class label mismatch')
            prompt = job.get('prompt')
            table = re.findall(r'^R(\d{4}) value=(\d{3}) flag=(KEEP|DROP)$', prompt, re.M) if isinstance(prompt, str) else []
            gold = ';'.join(f'R{record}={value}' for record, value, flag in table if flag == 'KEEP')
            if (len(table) != size or [int(record) for record, _, _ in table] != list(range(1, size+1))
                    or sum(flag == 'KEEP' for _, _, flag in table) != {64: 4, 192: 12, 384: 24}[cap]
                    or job.get('expected') != gold):
                errors.append(name + ': input table/gold extraction mismatch for ' + job['request_id'])
        counts = Counter((job['input_rows'], job['max_output_tokens']) for job in trace)
        if counts != Counter({(size, cap): n//9 for size in INPUTS for cap in CAPS}):
            errors.append(name + ': nine cross classes are not balanced')
        traces[name] = trace
    if Counter(combinations) != Counter((rate, rep, parallel) for rate in RATES for rep in (1, 2) for parallel in PARALLELS):
        errors.append('PLAN does not contain exactly 18 rate/rep/parallel combinations')
    for rate in RATES:
        for rep in (1, 2):
            group = [traces[p['trace_file']] for p in plan if p['rate'] == rate and p['rep'] == rep]
            if len(group) != 3 or any(not exact(group[0], trace) for trace in group[1:]):
                errors.append('matched configurations do not receive identical traces')
    freeze = obj(read_json(source_dir/'FREEZE.json', errors, hashes), errors, 'FREEZE')
    frozen = freeze.get('sha256')
    if not isinstance(frozen, dict):
        errors.append('FREEZE lacks sha256 mapping')
        frozen = {}
    required = {'CONFIG.json', 'PLAN.json', 'MODEL_LOCK.json', 'client.py', 'runstudy.py', 'power_capture.py', 'energy.py', 'analyze.py'} | set(traces)
    if not required.issubset(frozen):
        errors.append('FREEZE lacks required design/collector/trace files')
    for name, expected in sorted(frozen.items()):
        if Path(name).is_absolute() or '..' in Path(name).parts:
            errors.append('FREEZE contains unsafe relative path')
            continue
        try:
            got = hashlib.sha256((source_dir/name).read_bytes()).hexdigest()
            hashes[name] = got
            if got != expected:
                errors.append('FREEZE mismatch: ' + name)
        except OSError:
            errors.append('FREEZE missing file: ' + name)
    return config, plan, traces


def comparisons(windows):
    matched, cells = [], []
    for rate in RATES:
        for parallel in PARALLELS:
            group = [w for w in windows if w['rate'] == rate and w['parallel'] == parallel]
            cells.append(dict(rate=rate, parallel=parallel, windows=[w['index'] for w in group],
                              both_repetitions_valid=len(group) == 2 and all(w['valid'] for w in group),
                              finite_window_acceptable=len(group) == 2 and all(w['finite_window_screen']['passed'] for w in group)))
        for rep in (1, 2):
            group = {w['parallel']: w for w in windows if w['rate'] == rate and w['rep'] == rep}
            for parallel in (2, 4):
                baseline, treatment = group.get(1), group.get(parallel)
                if baseline is None or treatment is None:
                    matched.append(dict(rate=rate, rep=rep, contrast=f'P{parallel}-P1', valid=False, error='missing planned matched window'))
                    continue
                b_ids = {r['request_id']: r for r in baseline['requests']}
                equality = []
                for row in treatment['requests']:
                    other = b_ids.get(row['request_id'])
                    both = other is not None and other['output_sha256'] is not None and row['output_sha256'] is not None
                    equality.append(dict(request_id=row['request_id'], both_api_completed=bool(other and other['api_completed'] and row['api_completed']),
                                         output_equal=(other['output_sha256'] == row['output_sha256']) if both else None,
                                         baseline_output_sha256=other['output_sha256'] if other else None,
                                         treatment_output_sha256=row['output_sha256'],
                                         baseline_eval_count=other['usage'].get('eval_count') if other else None,
                                         treatment_eval_count=row['usage'].get('eval_count')))
                difference = {key: treatment['metrics'][key]-baseline['metrics'][key] for key in
                              ('quality_slo_count', 'quality_slo_fraction', 'api_slo_count', 'api_slo_fraction', 'quality_pass_count', 'api_completed_count')}
                matched.append(dict(rate=rate, rep=rep, contrast=f'P{parallel}-P1',
                                    baseline_window=baseline['index'], treatment_window=treatment['index'],
                                    valid=baseline['valid'] and treatment['valid'], difference=difference,
                                    equal_output_count=sum(row['output_equal'] is True for row in equality), output_identity_by_id=equality))
    return cells, matched


def analyze(data_dir, source_dir=BASE):
    data_dir, source_dir = Path(data_dir), Path(source_dir)
    errors, hashes = [], {}
    config, plan, traces = load_design(source_dir, errors, hashes)
    for name, expected in (('CONFIG.json', config), ('PLAN.json', plan)):
        captured = read_json(data_dir/name, errors, {})
        if not exact(captured, expected):
            errors.append('captured ' + name + ' differs from frozen source')
    parsed = dict(samples=[], errors=[])
    power_path = data_dir/'POWER.txt.gz'
    try:
        raw = power_path.read_bytes()
        hashes['POWER.txt.gz'] = hashlib.sha256(raw).hexdigest()
        import energy
        parsed = energy.parse_text(gzip.decompress(raw).decode())
    except (OSError, EOFError, zlib.error, UnicodeError, ValueError, ImportError, AttributeError) as exc:
        parsed['errors'].append('power capture unavailable/unreadable: ' + type(exc).__name__)
    stop_errors=[]
    stop=read_json(data_dir/'POWER_STOP.json',stop_errors,{})
    if not isinstance(stop,dict) or stop.get('stop_confirmed') is not True or stop.get('returncode') != 0:
        parsed['errors'].append('power sampler normal termination unverified')
    parsed['errors'].extend(stop_errors)
    windows = [analyze_window(data_dir, p, traces[p['trace_file']], parsed, list(errors), config) for p in plan]
    # Check every recorded setting, including queue size, against the frozen CONFIG.
    for window in windows:
        meta = read_json(data_dir/f"window-{window['index']:02d}"/'RUN.json', [], {})
        required_settings = dict(config.get('server_settings_common', {}), OLLAMA_NUM_PARALLEL=str(window['parallel']))
        if not isinstance(meta, dict) or not exact(meta.get('server_settings'), required_settings):
            window['validation_errors'].append('server settings differ from frozen CONFIG')
            window['valid'] = False
            window['finite_window_screen']['conditions']['valid_window'] = False
            window['finite_window_screen']['passed'] = False
    for window in windows:
        denominator=window['metrics']['quality_slo_count']
        for interval in window['energy']['intervals'].values():
            interval['quality_slo_denominator']=denominator
            interval['combined_j_per_quality_slo_success'] = ({key: interval[key+'_j']['combined']/denominator for key in ('lower','upper')} if interval['valid'] and denominator>0 else None)
    cells, matched = comparisons(windows)
    return dict(schema_version=1, analysis_kind='descriptive finite 90-second mixed-workload windows',
                planned_offered_count=1134, planned_per_parallel=378, window_count=18,
                analyzed_planned_count=sum(w['metrics']['planned_count'] for w in windows),
                valid=not errors and all(w['valid'] for w in windows), validation_errors=errors,
                input_sha256=hashes, windows=windows, rate_parallel_cells=cells, matched_comparisons=matched,
                energy_capture=dict(sample_count=len(parsed['samples']), parse_errors=parsed['errors']),
                limitations=['Two matched repetitions per rate; requests are not independent replications.',
                             'Finite-window acceptance does not establish steady-state capacity, a production SLA, or a causal effect.',
                             'API completion and task-quality completion are reported separately.',
                             'All planned offers remain denominators; missing captures are unverified, not invented server failures.',
                             'Client unfinished-count proxy includes service and is not server queue length; unverified records give an upper proxy, separately flagged from known dispatched unfinished jobs.',
                             'Quantiles condition on validated API completion; first content is not instrumented TTFT.',
                             'Energy bounds use uncertain sample edges without fixed-power interpolation, baseline subtraction, or per-request allocation.',
                             'Energy is gross CPU/GPU/ANE domain telemetry, not process-attributed or whole-machine energy.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data_dir', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    summary = analyze(args.data_dir)
    output = args.output or args.data_dir/'SUMMARY.json'
    output.write_text(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + '\n')
    print(json.dumps(dict(valid=summary['valid'], output=str(output)), sort_keys=True))


if __name__ == '__main__':
    main()
