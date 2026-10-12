"""One prospective infrastructure verification qualification; no energy measurements."""
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
from contract import wire_job, score, gate, SCHEMA
from server_control import OwnedServer

BASE = Path(__file__).resolve().parent
MODEL = 'qwen3:32b'
WARM_PROMPT = 'Return {"verdict":"insufficient","evidence":[]} exactly. /no_think'
SCORE_KEYS = ('schema_valid', 'verdict_correct', 'evidence_correct', 'quality_pass', 'prediction')


def write(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')
    temporary.replace(path)


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def check_freeze():
    value = json.loads((BASE / 'FREEZE.json').read_text())
    needed = {'CONFIG.json', 'MODEL_LOCK.json', 'MODEL_MANIFEST.json', 'cases.json', 'contract.py',
              'collect.py', 'audit_runtime.py', 'transport_audit.py', 'client.py', 'server_control.py',
              'clock_bridge.py', 'PROTOCOL.txt', 'SOURCE_MANIFEST.json'}
    if not needed <= set(value['sha256']):
        raise ValueError('Freeze missing required source files')
    for name, digest in value['sha256'].items():
        if Path(name).is_absolute() or '..' in Path(name).parts:
            raise ValueError('Unsafe freeze path')
        if hashlib.sha256((BASE / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Frozen source mismatch: ' + name)
    return hashlib.sha256((BASE / 'FREEZE.json').read_bytes()).hexdigest()


def no_thinking(row):
    return all(chunk['data'].get('thinking', '') == '' for chunk in row['chunks'])


def stage(config, jobs, out, deadline):
    if time.monotonic() > deadline - 300:
        raise RuntimeError('Qualification budget stopped before stage setup')
    out.mkdir()
    result = dict(part='qualification', candidate=MODEL, planned=len(jobs), status='starting',
                  requests=[], started_utc=utc())
    write(out / 'STAGE.json', result)
    stamps = []
    try:
        with OwnedServer(out, config) as server:
            warm = dict(request_id='warm', arrival_offset_s=0, prompt=WARM_PROMPT,
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
                    raise RuntimeError('Qualification budget stopped before next request')
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
                entry = dict(request_id=job['request_id'], source_id=job['source_id'], label=job['label'],
                             api_completed=row['completed'], observed_context_margin=None, raw_file=path.name,
                             collector_duration=duration_bounds_s(raw['started_stamp'], raw['finished_stamp']),
                             phase_duration=duration_bounds_s(before, after), **dict.fromkeys(SCORE_KEYS))
                result['requests'].append(entry)
                write(out / 'STAGE.json', result)
                if not row['completed'] or not no_thinking(row):
                    raise RuntimeError('Transport or non-thinking contract failed; abort without retry')
                if raw['epoch_monotonic_ns'] != raw['started_stamp']['monotonic_after_ns'] or not (
                        0 <= row['dispatch_offset_s'] <= row['first_content_offset_s'] <=
                        row['terminal_offset_s'] <= raw['elapsed_seconds'] + 1e-6):
                    raise RuntimeError('Monotonic request ordering failed')
                margin = config['context'] - row['final']['prompt_eval_count'] - 256
                entry['observed_context_margin'] = margin
                if margin < 128:
                    raise RuntimeError('Insufficient observed prompt/output context allowance')
                if row['final']['eval_count'] > 256:
                    raise RuntimeError('Observed output exceeds fixed token cap')
                answer = ''.join(c['data'].get('response', '') for c in row['chunks'])
                scoring = score(answer, job)
                entry.update({key: scoring[key] for key in SCORE_KEYS})
                entry.update(output_tokens=row['final']['eval_count'], done_reason=row['final'].get('done_reason'),
                             completion_s=row['terminal_offset_s'] - row['arrival_offset_s'])
                write(out / 'STAGE.json', result)
                print(json.dumps(dict(stage='qualification', request=job['request_id'],
                                      quality_pass=entry['quality_pass'])), flush=True)
                time.sleep(.2)
            server.verify_loaded()
            stamps.append(paired_stamp())
            result.update(clock_stamps=stamps, clock_diagnostics=bridge_diagnostics(stamps))
            if not result['clock_diagnostics']['valid']:
                raise RuntimeError('Observed clock bridge failed')
            if re.search(r'truncat(?:e|ed|ing).*input|input.*truncat', (out / 'SERVER.log').read_text(), re.I):
                raise RuntimeError('Input truncation diagnostic')
        result.update(status='completed', quality_count=sum(x['quality_pass'] for x in result['requests']),
                      gate_passed=gate(result['requests']))
    except BaseException as error:
        result.update(status='aborted', error=type(error).__name__ + ': ' + str(error), gate_passed=False)
        raise
    finally:
        result['finished_utc'] = utc()
        write(out / 'STAGE.json', result)
    return result


def run_gate(run_stage):
    qualification = run_stage()
    if qualification['status'] != 'completed':
        raise RuntimeError('Invalid qualification stage')
    return dict(selected=MODEL, qualified=qualification['gate_passed'], stages=[qualification])


def main(out):
    freeze = check_freeze()
    config = json.loads((BASE / 'CONFIG.json').read_text())
    for name in ('model', 'options', 'context', 'lock'):
        if name not in config:
            raise ValueError('Missing required config: ' + name)
    for name, wanted in {'model': MODEL, 'budget_s': 1800, 'request_timeout_s': 90,
                         'max_output_tokens': 256, 'think': False}.items():
        if config.get(name) != wanted or type(config.get(name)) is not type(wanted):
            raise ValueError('Unsupported config: ' + name)
    jobs = json.loads((BASE / 'cases.json').read_text())
    if len(jobs) != 24 or len({j['request_id'] for j in jobs}) != 24:
        raise ValueError('Qualification requires exactly 24 unique frozen cases')
    if any(not re.fullmatch(r'[A-Za-z0-9_-]+', j['request_id']) for j in jobs):
        raise ValueError('Unsafe request identifier')
    if any(sum(j['label'] == label for j in jobs) != 8
           for label in ('supported', 'contradicted', 'insufficient')):
        raise ValueError('Qualification requires eight cases of each label')
    out.mkdir(parents=True, exist_ok=False)
    campaign = dict(started_utc=utc(), source_freeze_sha256=freeze, status='starting', qualified=False)
    write(out / 'CAMPAIGN.json', campaign)
    deadline = time.monotonic() + 1800
    try:
        campaign.update(run_gate(lambda: stage(config, jobs, out / 'qualification', deadline)))
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
