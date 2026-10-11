#!/usr/bin/env python3
"""Independently validate stored pilot captures and write a deterministic summary.

This module never imports the collector or contacts a model/server. Planned offers
remain the denominator even when captures are missing, duplicated, or malformed.
"""
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
MODEL = 'llama3.2:3b'
DIGEST = 'a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72'
TRACE_SHA256 = '2acb38d57cc71e2d5bf7bbe905fe41645d6c5be7e98f90da4d13dd313cfa10c0'
ORDER = [1, 2, 2, 1, 1, 2, 2, 1]
EXPECTED = [(f'r{i+1:02d}', i / 2) for i in range(16)]
OPTIONS = dict(temperature=0, seed=0, num_predict=64, num_ctx=2048)
USAGE = ('prompt_eval_count', 'eval_count', 'total_duration', 'load_duration',
         'prompt_eval_duration', 'eval_duration')
REQUIRED_FREEZE = {'PROTOCOL.txt', 'TRACE.json', 'MODEL_LOCK.json', 'pilot.py',
                   'client.py'}


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def uint(value):
    return type(value) is int and value >= 0


def exact(a, b):
    """Reject bool-for-int substitutions that Python equality otherwise accepts."""
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def nearest_rank(values, percentile):
    if not values:
        return None
    return sorted(values)[math.ceil(percentile * len(values)) - 1]


def quantiles(values):
    return dict(n=len(values), p50=nearest_rank(values, .5),
                p95=nearest_rank(values, .95), method='nearest_rank')


def utc(value):
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return parsed if parsed.utcoffset() is not None else None
    except (AttributeError, TypeError, ValueError):
        return None


def read_json(path, errors, label, hashes=None):
    try:
        raw = path.read_bytes()
        if hashes is not None:
            hashes[label] = sha(raw)
        # Nonfinite numbers are not valid recorded clocks, even outside rows.
        return json.loads(raw, parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError('nonfinite JSON number: ' + value)))
    except (OSError, ValueError, UnicodeError) as error:
        errors.append(label + ': unreadable or invalid JSON (' + type(error).__name__ + ')')
        return None


def read_text(path, errors, label, hashes):
    try:
        raw = path.read_bytes()
        hashes[label] = sha(raw)
        return raw.decode('utf-8')
    except (OSError, UnicodeError) as error:
        errors.append(label + ': unreadable text (' + type(error).__name__ + ')')
        return ''


def object_or_error(value, errors, label):
    if not isinstance(value, dict):
        errors.append(label + ': expected object')
        return {}
    return value


def parallel_values(log):
    values = []
    for pattern in (r'n_seq_max\s*=\s*(\d+)', r'\bParallel[=:]\s*(\d+)',
                    r'--parallel\s+(\d+)'):
        values.extend(int(x) for x in re.findall(pattern, log))
    return sorted(set(values))


def inspect_request(row, request_id, arrival, elapsed):
    """Revalidate one recorded outcome; never trust its completed flag alone."""
    errors, validity_errors = [], []
    row = object_or_error(row, errors, 'row')
    for field in ('request_id', 'arrival_offset_s', 'dispatch_offset_s',
                  'first_content_offset_s', 'terminal_offset_s', 'completed',
                  'error', 'chunks', 'final'):
        if field not in row:
            errors.append('missing required field: ' + field)
    if row.get('request_id') != request_id:
        errors.append('request ID mismatch')
    if not finite(row.get('arrival_offset_s')) or row.get('arrival_offset_s') != arrival:
        errors.append('intended arrival mismatch')
    declared = row.get('completed')
    if type(declared) is not bool:
        errors.append('completed is not bool')
    error = row.get('error')
    if declared is True and error is not None:
        errors.append('completed row has error')
    if declared is False and (not isinstance(error, str) or not error):
        errors.append('failed row lacks error')
    dispatch = row.get('dispatch_offset_s')
    terminal = row.get('terminal_offset_s')
    first = row.get('first_content_offset_s')
    if dispatch is None:
        if declared is not False:
            errors.append('successful row lacks dispatch')
    elif not finite(dispatch) or dispatch < arrival:
        errors.append('dispatch precedes intended arrival or is invalid')
    if not finite(terminal) or terminal < 0:
        errors.append('invalid terminal clock')
    elif finite(dispatch) and terminal < dispatch:
        errors.append('terminal precedes dispatch')
    if finite(terminal) and finite(elapsed) and terminal > elapsed:
        errors.append('terminal exceeds collection elapsed time')
    lag = dispatch - arrival if finite(dispatch) else None
    if lag is not None and lag > .1:
        validity_errors.append('dispatch lag exceeds 0.1s')
    chunks = row.get('chunks')
    if not isinstance(chunks, list):
        errors.append('chunks is not list')
        chunks = []
    contents, first_seen, done_chunks = [], None, []
    previous = dispatch
    for index, chunk in enumerate(chunks):
        chunk = object_or_error(chunk, errors, f'chunk {index}')
        offset, data = chunk.get('offset_s'), chunk.get('data')
        if not finite(offset) or offset < 0:
            errors.append(f'chunk {index}: invalid clock')
        elif ((finite(previous) and offset < previous) or
              (finite(terminal) and offset > terminal)):
            errors.append(f'chunk {index}: clock out of order')
        if finite(offset):
            previous = offset
        data = object_or_error(data, errors, f'chunk {index} data')
        if 'error' in data:
            if declared is True:
                errors.append('completed stream contains server error')
        if 'model' in data and data['model'] != MODEL:
            errors.append(f'chunk {index}: wrong model')
        if 'response' in data and not isinstance(data['response'], str):
            errors.append(f'chunk {index}: nonstring response')
        content = data.get('response', '')
        if isinstance(content, str) and content:
            if first_seen is None:
                first_seen = offset
            contents.append(content)
        if data.get('done') is True:
            done_chunks.append((index, data))
    if first != first_seen or (first is not None and not finite(first)):
        errors.append('first-content clock does not match first nonempty response chunk')
    if chunks and dispatch is None:
        errors.append('received chunks without dispatch')
    final = row.get('final')
    if final is not None and not isinstance(final, dict):
        errors.append('final is not object or null')
        final = None
    if done_chunks:
        if len(done_chunks) != 1 or done_chunks[-1][0] != len(chunks) - 1:
            errors.append('done chunk is not the unique final stream chunk')
        if final != done_chunks[-1][1]:
            errors.append('final differs from captured done chunk')
    elif final is not None:
        errors.append('final lacks captured done chunk')
    if declared is True:
        if not exact(row.get('http_status'), 200):
            errors.append('completed stream lacks HTTP 200 status')
        if not contents:
            errors.append('completed stream lacks response content')
        if not isinstance(final, dict) or final.get('done') is not True:
            errors.append('completed stream lacks done=true final')
        if isinstance(final, dict):
            if final.get('model') != MODEL:
                errors.append('wrong terminal model')
            for field in USAGE:
                if not uint(final.get(field)):
                    errors.append('invalid terminal usage: ' + field)
            if not uint(final.get('eval_count')) or final['eval_count'] == 0:
                errors.append('terminal eval_count must be positive')
    observed_usage = {field: final[field] for field in USAGE
                      if isinstance(final, dict) and uint(final.get(field))}
    completed = declared is True and not errors
    text = ''.join(contents)
    return dict(request_id=request_id, arrival_offset_s=arrival,
                recorded_completed=declared if type(declared) is bool else None,
                completed=completed, on_time=completed and terminal - arrival <= 5,
                dispatch_lag_s=lag,
                completion_latency_s=terminal - arrival if completed else None,
                first_content_latency_s=first - arrival if completed else None,
                terminal_offset_s=terminal if finite(terminal) else None,
                first_content_offset_s=first if finite(first) else None,
                output_sha256=sha(text.encode('utf-8')) if contents else None,
                output_utf8_bytes=len(text.encode('utf-8')), usage=observed_usage,
                error=error, validation_errors=errors, validity_errors=validity_errors)


def inspect_collection(value, expected, errors, label):
    value = object_or_error(value, errors, label)
    elapsed = value.get('elapsed_seconds')
    if not finite(elapsed) or elapsed < 0:
        errors.append(label + ': invalid elapsed_seconds')
    if utc(value.get('started_utc')) is None:
        errors.append(label + ': invalid timezone-aware started_utc')
    records = value.get('requests')
    if not isinstance(records, list):
        errors.append(label + ': requests is not list')
        records = []
    ids = [row.get('request_id') if isinstance(row, dict) else None for row in records]
    if ids != [request_id for request_id, _ in expected]:
        errors.append(label + ': offered ID list/order does not match protocol')
    counts = Counter(x for x in ids if isinstance(x, str))
    by_id = {row['request_id']: row for row in records
             if isinstance(row, dict) and isinstance(row.get('request_id'), str)
             and counts[row['request_id']] == 1}
    results = []
    for request_id, arrival in expected:
        result = inspect_request(by_id.get(request_id), request_id, arrival, elapsed)
        if counts[request_id] != 1:
            result['validation_errors'].insert(0, 'expected exactly one offered row; observed ' + str(counts[request_id]))
        for error in result['validation_errors'] + result['validity_errors']:
            errors.append(label + '/' + request_id + ': ' + error)
        results.append(result)
    return results


def snapshot(value, errors, label):
    value = object_or_error(value, errors, label)
    if utc(value.get('utc')) is None:
        errors.append(label + ': invalid timezone-aware UTC')
    power = value.get('power')
    if not isinstance(power, str) or not re.search(r"Now drawing from ['\"]AC Power['\"]", power):
        errors.append(label + ': AC source not reported')
    thermal = value.get('thermal')
    # pmset reports these explicit negative statements on this Mac. Unknown
    # formats are invalid evidence, not silently interpreted as no warning.
    if not isinstance(thermal, str):
        errors.append(label + ': thermal snapshot absent')
    else:
        safe = re.sub(r'(?im)^\s*(?:Note:\s*)?No (?:thermal warning level|performance warning level|CPU power status) has been recorded\s*$', '', thermal)
        if ('No thermal warning level has been recorded' not in thermal or
                'No performance warning level has been recorded' not in thermal or
                re.search(r'(?i)(?:warning|thermal|CPU_Speed_Limit|Scheduler_Limit)', safe)):
            errors.append(label + ': reported or unrecognized thermal/performance warning')
    load = value.get('load_average')
    if not isinstance(load, list) or len(load) != 3 or not all(finite(x) and x >= 0 for x in load):
        errors.append(label + ': invalid load-average snapshot')


def inspect_loaded(value, errors, label):
    value = object_or_error(value, errors, label)
    models = value.get('models')
    if not isinstance(models, list) or len(models) != 1 or not isinstance(models[0], dict):
        errors.append(label + ': expected exactly one loaded model')
        return
    model = models[0]
    if model.get('digest') != DIGEST:
        errors.append(label + ': model digest mismatch')
    if not exact(model.get('context_length'), 2048):
        errors.append(label + ': per-sequence context is not 2048')
    if not finite(model.get('size_vram')) or model['size_vram'] <= 0:
        errors.append(label + ': GPU residency not reported')


def inspect_window(data_dir, index, parallel, hashes):
    name = f'window-{index:02d}-p{parallel}'
    path = data_dir / name
    errors = []
    meta = object_or_error(read_json(path / 'RUN.json', errors, name + '/RUN.json', hashes), errors, 'RUN')
    warm = read_json(path / 'WARMUP.json', errors, name + '/WARMUP.json', hashes)
    collection = read_json(path / 'REQUESTS.json', errors, name + '/REQUESTS.json', hashes)
    log = read_text(path / 'SERVER.log', errors, name + '/SERVER.log', hashes)
    for key, expected in dict(index=index, pair=(index + 1) // 2, parallel=parallel,
                              model=MODEL, options=OPTIONS, status='completed').items():
        if not exact(meta.get(key), expected):
            errors.append('RUN: mismatch in ' + key)
    settings = {'OLLAMA_HOST': 'http://127.0.0.1:11561', 'OLLAMA_NUM_PARALLEL': str(parallel),
                'OLLAMA_MAX_LOADED_MODELS': '1', 'OLLAMA_MAX_QUEUE': '64',
                'OLLAMA_CONTEXT_LENGTH': '2048', 'OLLAMA_FLASH_ATTENTION': '0',
                'OLLAMA_KV_CACHE_TYPE': 'f16', 'OLLAMA_MULTIUSER_CACHE': '0',
                'OLLAMA_NO_CLOUD': '1', 'OLLAMA_NOPRUNE': '1', 'OLLAMA_NOHISTORY': '1',
                'OLLAMA_KEEP_ALIVE': '120s', 'OLLAMA_DEBUG': '1'}
    if not exact(meta.get('server_settings'), settings):
        errors.append('RUN: server settings mismatch')
    if not isinstance(meta.get('version'), dict) or meta['version'].get('version') != '0.20.0':
        errors.append('RUN: wrong/missing server version')
    tag = meta.get('model_tag')
    if not isinstance(tag, dict) or tag.get('digest') != DIGEST or tag.get('name') != MODEL:
        errors.append('RUN: model tag/digest mismatch')
    actual = parallel_values(log)
    if actual != [parallel] or not exact(meta.get('runtime_parallel_values'), [parallel]):
        errors.append('RUN: actual parallelism not established from logs and metadata')
    for boundary in ('before', 'after'):
        inspect_loaded(meta.get('loaded_' + boundary), errors, 'loaded_' + boundary)
        snapshot(meta.get(boundary), errors, boundary)
        if meta.get('original_endpoint_idle_' + boundary) is not True:
            errors.append('RUN: original endpoint not verified idle ' + boundary)
    unloaded = meta.get('loaded_after_unload')
    if not isinstance(unloaded, dict) or unloaded.get('models') != []:
        errors.append('RUN: owned model unload not verified')
    if meta.get('cleanup_error'):
        errors.append('RUN: cleanup error recorded')
    if not uint(meta.get('dedicated_server_pid')) or meta.get('dedicated_server_pid') == 0:
        errors.append('RUN: dedicated server PID not recorded')
    if type(meta.get('dedicated_server_returncode')) is not int:
        errors.append('RUN: dedicated server termination not recorded')
    warm_rows = inspect_collection(warm, [('warm1', 0), ('warm2', 0)], errors, 'warmup')
    if not all(row['completed'] for row in warm_rows):
        errors.append('RUN: not all warmups succeeded')
    requests = inspect_collection(collection, EXPECTED, errors, 'requests')
    if isinstance(warm, dict) and isinstance(collection, dict):
        warm_start, work_start = utc(warm.get('started_utc')), utc(collection.get('started_utc'))
        before, after = meta.get('before'), meta.get('after')
        before_time = utc(before.get('utc')) if isinstance(before, dict) else None
        after_time = utc(after.get('utc')) if isinstance(after, dict) else None
        if warm_start and work_start and finite(warm.get('elapsed_seconds')):
            if (work_start - warm_start).total_seconds() < warm['elapsed_seconds'] + 2:
                errors.append('RUN: two-second post-warmup wait not established')
        if before_time and warm_start and before_time > warm_start:
            errors.append('RUN: warmup begins before initial snapshot')
        if after_time and work_start and finite(collection.get('elapsed_seconds')):
            if (after_time - work_start).total_seconds() < collection['elapsed_seconds'] + 2:
                errors.append('RUN: two-second post-drain wait not established')
    completed = [row for row in requests if row['completed']]
    ontime = sum(row['on_time'] for row in requests)
    terminals = [row['terminal_offset_s'] for row in requests if row['terminal_offset_s'] is not None]
    lags = [row['dispatch_lag_s'] for row in requests if row['dispatch_lag_s'] is not None]
    return dict(index=index, pair=(index + 1) // 2, parallel=parallel, directory=name,
                valid=not errors, validation_errors=errors, offered_count=16,
                captured_row_count=len(collection.get('requests', [])) if isinstance(collection, dict) and isinstance(collection.get('requests'), list) else 0,
                completed_count=len(completed), failure_count=16-len(completed),
                recorded_completed_count=sum(row['recorded_completed'] is True for row in requests),
                recorded_failure_count=sum(row['recorded_completed'] is False for row in requests),
                unverified_outcome_count=sum(row['recorded_completed'] is not False and not row['completed'] for row in requests),
                on_time_count=ontime, on_time_fraction=ontime/16,
                late_completed_count=len(completed)-ontime,
                completion_latency_s=quantiles([row['completion_latency_s'] for row in completed]),
                first_content_latency_s=quantiles([row['first_content_latency_s'] for row in completed]),
                last_terminal_from_first_offer_s=max(terminals) if terminals else None,
                terminal_count=len(terminals), maximum_dispatch_lag_s=max(lags) if lags else None,
                reported_output_tokens=sum(row['usage'].get('eval_count', 0) for row in requests),
                output_token_reporting_count=sum('eval_count' in row['usage'] for row in requests),
                completed_output_tokens=sum(row['usage']['eval_count'] for row in completed),
                reported_prompt_tokens=sum(row['usage'].get('prompt_eval_count', 0) for row in requests),
                actual_parallel_values=actual, warmup_completed_count=sum(row['completed'] for row in warm_rows),
                snapshots={key: meta.get(key) for key in ('before', 'after')},
                loaded_model_observations={key: meta.get(key) for key in ('loaded_before', 'loaded_after', 'loaded_after_unload')},
                memory_log_observations=[line for line in log.splitlines() if re.search(r'(?i)\bKV\b|memory|buffer size', line)],
                dedicated_server_pid=meta.get('dedicated_server_pid'), requests=requests)


def analyze(data_dir, source_dir=BASE):
    data_dir, source_dir = Path(data_dir), Path(source_dir)
    errors, hashes = [], {}
    freeze = object_or_error(read_json(source_dir / 'PROTOCOL_FREEZE.json', errors, 'source/PROTOCOL_FREEZE.json', hashes), errors, 'freeze')
    frozen = freeze.get('sha256')
    if not isinstance(frozen, dict):
        errors.append('freeze: sha256 mapping absent')
        frozen = {}
    if not REQUIRED_FREEZE.issubset(frozen):
        errors.append('freeze: required protocol/source files absent')
    for name, expected in sorted(frozen.items()):
        if not isinstance(name, str) or Path(name).name != name:
            errors.append('freeze: invalid relative filename')
            continue
        try:
            digest = sha((source_dir / name).read_bytes())
            hashes['source/' + name] = digest
            if digest != expected:
                errors.append('freeze: changed ' + name)
        except OSError:
            errors.append('freeze: missing ' + name)
    trace = read_json(source_dir / 'TRACE.json', errors, 'source/TRACE.json', hashes)
    if hashes.get('source/TRACE.json') != TRACE_SHA256:
        errors.append('trace: does not match prespecified immutable trace hash')
    offered = read_json(data_dir / 'OFFERED_TRACE.json', errors, 'OFFERED_TRACE.json', hashes)
    if offered != trace or not isinstance(trace, list) or len(trace) != 16:
        errors.append('trace: offered trace differs from frozen 16-prompt trace')
    campaign = object_or_error(read_json(data_dir / 'CAMPAIGN.json', errors, 'CAMPAIGN.json', hashes), errors, 'campaign')
    for key, expected in dict(status='completed', planned_order=ORDER, planned_offered=128).items():
        if not exact(campaign.get(key), expected):
            errors.append('campaign: mismatch in ' + key)
    campaign_windows = campaign.get('windows')
    if not isinstance(campaign_windows, list) or len(campaign_windows) != 8:
        errors.append('campaign: expected exactly eight window records')
        campaign_windows = []
    expected_dirs = [f'window-{i:02d}-p{p}' for i, p in enumerate(ORDER, 1)]
    actual_dirs = sorted(path.name for path in data_dir.glob('window-*'))
    if actual_dirs != sorted(expected_dirs):
        errors.append('campaign: window directories differ from prescribed order/set')
    windows = [inspect_window(data_dir, i, p, hashes) for i, p in enumerate(ORDER, 1)]
    for pos, saved in enumerate(campaign_windows):
        if not isinstance(saved, dict) or not exact(saved.get('index'), pos + 1) or not exact(saved.get('parallel'), ORDER[pos]):
            errors.append('campaign: window record order mismatch at ' + str(pos + 1))
        run = read_json(data_dir / expected_dirs[pos] / 'RUN.json', [], 'RUN')
        if not exact(saved, run):
            errors.append('campaign: window record disagrees with RUN at ' + str(pos + 1))
    pids = [window['dedicated_server_pid'] for window in windows]
    valid_pids = [pid for pid in pids if type(pid) is int and pid > 0]
    if len(set(valid_pids)) != len(valid_pids):
        errors.append('campaign: repeated dedicated server PID; fresh server not established')
    if errors:
        for window in windows:
            window['valid'] = False
    pairs = []
    for index in range(4):
        group = windows[2*index:2*index+2]
        p1 = next(window for window in group if window['parallel'] == 1)
        p2 = next(window for window in group if window['parallel'] == 2)
        difference = p2['on_time_count'] - p1['on_time_count']
        equality = []
        for a, b in zip(p1['requests'], p2['requests']):
            observed_both = a['output_sha256'] is not None and b['output_sha256'] is not None
            equality.append(dict(request_id=a['request_id'], both_completed=a['completed'] and b['completed'],
                                 both_have_received_content=observed_both,
                                 output_equal=(a['output_sha256'] == b['output_sha256']) if observed_both else None,
                                 p1_output_sha256=a['output_sha256'], p2_output_sha256=b['output_sha256'],
                                 p1_eval_count=a['usage'].get('eval_count'), p2_eval_count=b['usage'].get('eval_count')))
        pairs.append(dict(pair=index+1, p1_window=p1['index'], p2_window=p2['index'],
                          valid=p1['valid'] and p2['valid'], on_time_count_difference_p2_minus_p1=difference,
                          on_time_fraction_difference_p2_minus_p1=difference/16,
                          equal_output_count=sum(row['output_equal'] is True for row in equality),
                          both_complete_equal_output_count=sum(row['both_completed'] and row['output_equal'] is True for row in equality),
                          output_equality_by_request=equality))
    mean_count = sum(pair['on_time_count_difference_p2_minus_p1'] for pair in pairs) / 4
    nonnegative = sum(pair['on_time_count_difference_p2_minus_p1'] >= 0 for pair in pairs)
    all_valid = not errors and all(window['valid'] for window in windows)
    no_failures = all(window['failure_count'] == 0 and window['warmup_completed_count'] == 2 for window in windows)
    conditions = dict(mean_at_least_two_extra_on_time=mean_count >= 2,
                      at_least_three_nonnegative_pairs=nonnegative >= 3,
                      no_transport_or_terminal_validation_failures=no_failures,
                      all_eight_windows_valid=all_valid)
    return dict(schema_version=1, analysis_kind='stored-data descriptive four-pair local pilot',
                replication_unit='paired windows', planned_order=ORDER, offered_count=128,
                offered_per_arm=64, offered_per_window=16, response_deadline_s=5,
                deadline_origin='intended arrival', validation_errors=errors, valid=all_valid,
                input_sha256=hashes, windows=windows, pairs=pairs,
                mean_on_time_count_difference_p2_minus_p1=mean_count,
                mean_on_time_fraction_difference_p2_minus_p1=mean_count/16,
                nonnegative_pair_count=nonnegative,
                gate=dict(passed=all(conditions.values()), conditions=conditions,
                          label='engineering follow-up screen; not an empirical promotion gate'),
                limitations=['Fixed counterbalanced order, not randomized.',
                             'Four paired windows on one active Mac; requests are not independent replications.',
                             'First-content latency is a client observation, not instrumented TTFT.',
                             'Completion quantiles condition on independently validated successful completion.',
                             'Missing/invalid records remain failures in the planned offered denominator.',
                             'No energy, welfare, pricing, output-quality, or owner-pooling effect is inferred.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data_dir', type=Path)
    parser.add_argument('--output', type=Path, help='Defaults to DATA_DIR/SUMMARY.json')
    args = parser.parse_args()
    result = analyze(args.data_dir)
    output = args.output or args.data_dir / 'SUMMARY.json'
    output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n')
    print(json.dumps(dict(valid=result['valid'], gate_passed=result['gate']['passed'], output=str(output)), sort_keys=True))


if __name__ == '__main__':
    main()
