"""One prospective grounded-QA candidate; serial accuracy only, no energy claim."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import threading
import time
from client import run_trace
from clock_bridge import paired_stamp, bridge_diagnostics, duration_bounds_s
from design import wire_job, score, gate, SCHEMA
from server_control import OwnedServer
BASE = Path(__file__).resolve().parent
MODEL = 'qwen3:32b'


def write(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')
    temporary.replace(path)


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def check_freeze():
    value = json.loads((BASE / 'FREEZE.json').read_text())
    for name, digest in value['sha256'].items():
        if hashlib.sha256((BASE / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Frozen source mismatch: ' + name)
    return hashlib.sha256((BASE / 'FREEZE.json').read_bytes()).hexdigest()


def no_thinking(row):
    return all(chunk['data'].get('thinking', '') == '' for chunk in row['chunks'])


def stage(config, jobs, part, out, deadline):
    if time.monotonic() > deadline - 300:
        raise RuntimeError('Calibration budget stopped before stage setup')
    out.mkdir()
    result = dict(part=part, candidate=MODEL, planned=len(jobs), status='starting',
                  requests=[], started_utc=utc())
    write(out / 'STAGE.json', result)
    stamps = []
    try:
        with OwnedServer(out, config) as server:
            warm = dict(request_id='warm', arrival_offset_s=0,
                        prompt='Return one JSON object with answer set to the word ready. /no_think',
                        max_output_tokens=32, format=SCHEMA, think=False)
            wr = run_trace('http://127.0.0.1:11562', [warm], config['model'], config['options'],
                           timeout_s=60, hard_timeout_s=65,
                           checkpoint=lambda x: write(out / 'WARMUP.json', x))
            write(out / 'WARMUP.json', wr)
            if not wr['requests'][0]['completed'] or not no_thinking(wr['requests'][0]):
                raise RuntimeError('Warmup transport or non-thinking contract failed')
            server.verify_loaded()
            stamps.append(paired_stamp())
            for job in jobs:
                if time.monotonic() > deadline - 300:
                    raise RuntimeError('Calibration budget stopped before next request')
                server.check_host('before_' + job['request_id'])
                before = paired_stamp()
                triggered = threading.Event()
                def stop():
                    triggered.set()
                    server.stop_owned()
                timer = threading.Timer(100, stop)
                timer.daemon = True
                timer.start()
                path = out / (job['request_id'] + '.json')
                try:
                    raw = run_trace('http://127.0.0.1:11562', [wire_job(job)], config['model'],
                                    config['options'], timeout_s=90, hard_timeout_s=95,
                                    checkpoint=lambda x: write(path, x))
                    write(path, raw)
                finally:
                    timer.cancel()
                    timer.join()
                after = paired_stamp()
                server.check_host('after_' + job['request_id'])
                if triggered.is_set():
                    raise RuntimeError('Owned-server watchdog fired')
                stamps.extend([before, raw['started_stamp'], raw['finished_stamp'], after])
                row = raw['requests'][0]
                entry = dict(request_id=job['request_id'], title=job['title'],
                             is_impossible=job['is_impossible'], length_band=job['length_band'],
                             passage_chars=len(job['passage']), api_completed=row['completed'],
                             schema_valid=None, exact_match=None, f1=None, abstained=None,
                             observed_context_margin=None, raw_file=path.name,
                             collector_duration=duration_bounds_s(raw['started_stamp'], raw['finished_stamp']),
                             phase_duration=duration_bounds_s(before, after))
                result['requests'].append(entry)
                write(out / 'STAGE.json', result)
                if not row['completed'] or not no_thinking(row):
                    raise RuntimeError('Transport or non-thinking contract failed; abort without retry')
                if raw['epoch_monotonic_ns'] != raw['started_stamp']['monotonic_after_ns'] or not (
                        0 <= row['dispatch_offset_s'] <= row['first_content_offset_s'] <=
                        row['terminal_offset_s'] <= raw['elapsed_seconds'] + 1e-6):
                    raise RuntimeError('Monotonic request ordering failed')
                margin = config['context'] - row['final']['prompt_eval_count'] - job['max_output_tokens']
                entry['observed_context_margin'] = margin
                if margin < 128:
                    raise RuntimeError('Insufficient observed prompt/output context allowance')
                answer = ''.join(c['data'].get('response', '') for c in row['chunks'])
                scoring = score(answer, job)
                entry.update({key: scoring[key] for key in ('schema_valid','exact_match','f1','abstained')})
                entry.update(output_tokens=row['final']['eval_count'], done_reason=row['final'].get('done_reason'),
                             completion_s=row['terminal_offset_s'] - row['arrival_offset_s'])
                write(out / 'STAGE.json', result)
                print(json.dumps(dict(stage=part, request=job['request_id'], exact_match=entry['exact_match'])), flush=True)
                time.sleep(.2)
            server.verify_loaded()
            stamps.append(paired_stamp())
            result.update(clock_stamps=stamps, clock_diagnostics=bridge_diagnostics(stamps))
            if not result['clock_diagnostics']['valid']:
                raise RuntimeError('Observed clock bridge failed')
            if re.search(r'truncat(?:e|ed|ing).*input|input.*truncat', (out / 'SERVER.log').read_text(), re.I):
                raise RuntimeError('Input truncation diagnostic')
        result.update(status='completed', quality_count=sum(x['exact_match'] for x in result['requests']),
                      gate_passed=gate(result['requests'], part))
    except BaseException as error:
        result.update(status='aborted', error=type(error).__name__ + ': ' + str(error), gate_passed=False)
        raise
    finally:
        result['finished_utc'] = utc()
        write(out / 'STAGE.json', result)
    return result


def run_gate(run_stage):
    development = run_stage('development')
    if development['status'] != 'completed':
        raise RuntimeError('Invalid development stage')
    stages = [development]
    if not development['gate_passed']:
        return dict(selected=None, qualified=False, stages=stages)
    confirmation = run_stage('confirmation')
    if confirmation['status'] != 'completed':
        raise RuntimeError('Invalid confirmation stage')
    stages.append(confirmation)
    return dict(selected=MODEL, qualified=confirmation['gate_passed'], stages=stages)


def main(out):
    freeze = check_freeze()
    config = json.loads((BASE / 'CONFIG.json').read_text())
    for name in ('model', 'options', 'context', 'lock'):
        if name not in config:
            raise ValueError('Missing required config: ' + name)
    for name, wanted in {'model':MODEL, 'budget_s':1800, 'request_timeout_s':90,
                         'max_output_tokens':256, 'think':False}.items():
        if config.get(name) != wanted or (name == 'think' and config[name] is not False):
            raise ValueError('Unsupported config: ' + name)
    out.mkdir(parents=True, exist_ok=False)
    campaign = dict(started_utc=utc(), source_freeze_sha256=freeze, status='starting', qualified=False)
    write(out / 'CAMPAIGN.json', campaign)
    deadline = time.monotonic() + 1800
    try:
        def collect(part):
            jobs = json.loads((BASE / (part + '.json')).read_text())
            return stage(config, jobs, part, out / part, deadline)
        campaign.update(run_gate(collect))
        campaign['status'] = 'completed'
    except BaseException as error:
        campaign.update(status='aborted', error=type(error).__name__ + ': ' + str(error))
        raise
    finally:
        campaign['finished_utc'] = utc()
        write(out / 'CAMPAIGN.json', campaign)
    return campaign


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    main(parser.parse_args().output.resolve())
