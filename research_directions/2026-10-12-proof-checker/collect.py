"""One bounded blind-inventory-plus-primary collection; decisions stay offline."""
import argparse
from collections import Counter
import datetime
import hashlib
import json
from pathlib import Path
import re
import threading
import time
from client import run_trace
from clock_bridge import paired_stamp, bridge_diagnostics, duration_bounds_s
from contract import validate_inputs, primary_job, inventory_job, SCHEMA, INVENTORY_SCHEMA
from server_control import OwnedServer

BASE = Path(__file__).resolve().parent
MODEL = 'qwen3:32b'
DIGEST = '030ee887880fc378860c2dd35101da424377520441ae4bfe7be6deff8ade7840'
WARM_PROMPT = 'Return {"verdict":"insufficient","evidence":[]} exactly. /no_think'
PLANNED_REQUESTS = 48


def write(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')
    temporary.replace(path)


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def check_freeze():
    value = json.loads((BASE / 'FREEZE.json').read_text())
    needed = {'CONFIG.json', 'MODEL_LOCK.json', 'MODEL_MANIFEST.json', 'cases.json', 'controls.json',
              'contract.py', 'collect.py', 'audit_runtime.py', 'transport_audit.py', 'client.py',
              'server_control.py', 'clock_bridge.py', 'PROTOCOL.txt', 'SOURCE_MANIFEST.json', 'PRIOR_CLAIMS.json'}
    if not needed <= set(value['sha256']):
        raise ValueError('Freeze missing required source files')
    for name, digest in value['sha256'].items():
        if Path(name).is_absolute() or '..' in Path(name).parts:
            raise ValueError('Unsafe freeze path')
        if hashlib.sha256((BASE / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Frozen source mismatch: ' + name)
    sources = json.loads((BASE / 'SOURCE_MANIFEST.json').read_text())
    for source in sources:
        for filekey, hashkey in (('source_file', 'sha256'), ('license_file', 'license_sha256')):
            if value['sha256'].get(source[filekey]) != source[hashkey]:
                raise ValueError('Source/license missing from freeze or hash differs')
    return hashlib.sha256((BASE / 'FREEZE.json').read_bytes()).hexdigest()


def no_thinking(row):
    return all(chunk['data'].get('thinking', '') == '' for chunk in row['chunks'])


def checked_wire(job, identifier, cap, schema):
    if (job.get('request_id') != identifier or not re.fullmatch(r'[A-Za-z0-9_-]+', identifier)
            or type(job.get('max_output_tokens')) is not int or job['max_output_tokens'] != cap
            or job.get('think') is not False or job.get('arrival_offset_s') != 0
            or type(job.get('prompt')) is not str or type(job.get('format')) is not dict
            or job['format'] != schema):
        raise ValueError('Wire job does not match assigned request/cap/schema/non-thinking contract')
    return job


def planned_jobs(cases):
    """Freeze every job before inference; no response or control enters a prompt."""
    identifiers = [case['request_id'] for case in cases]
    if (len(cases) != 24 or len(set(identifiers)) != 24
            or any(type(identifier) is not str or not re.fullmatch(r'[A-Za-z0-9_-]+', identifier)
                   for identifier in identifiers)):
        raise ValueError('Expected 24 distinct cases with safe identifiers')
    ordered = sorted(cases, key=lambda case: hashlib.sha256(('order:' + case['request_id']).encode()).hexdigest())
    jobs = []
    for phase, prefix, factory, cap, schema in (
            ('inventory', 'i_', inventory_job, 384, INVENTORY_SCHEMA),
            ('primary', 'p_', primary_job, 256, SCHEMA)):
        for case in ordered:
            case_id = case['request_id']
            jobs.append((checked_wire(factory(case), prefix + case_id, cap, schema), phase, case_id))
    if len(jobs) != PLANNED_REQUESTS or len({job['request_id'] for job, _, _ in jobs}) != PLANNED_REQUESTS:
        raise ValueError('Expected exactly 48 distinct scored requests')
    return jobs


def stage(config, cases, controls, out, deadline):
    if time.monotonic() > deadline - 300:
        raise RuntimeError('Collection budget stopped before stage setup')
    # Controls are validated offline by the contract and never offered to inference.
    jobs = planned_jobs(cases)
    out.mkdir()
    result = dict(part='collection', candidate=MODEL, planned=PLANNED_REQUESTS, status='starting',
                  requests=[], started_utc=utc())
    write(out / 'STAGE.json', result)
    stamps = []
    try:
        with OwnedServer(out, config) as server:
            warm = checked_wire(dict(request_id='warm', arrival_offset_s=0, prompt=WARM_PROMPT,
                                     max_output_tokens=32, format=SCHEMA, think=False), 'warm', 32, SCHEMA)
            wr = run_trace('http://127.0.0.1:11562', [warm], config['model'], config['options'],
                           timeout_s=60, hard_timeout_s=65,
                           checkpoint=lambda x: write(out / 'WARMUP.json', x))
            write(out / 'WARMUP.json', wr)
            warm_row = wr['requests'][0]
            if not warm_row['completed'] or not no_thinking(warm_row):
                raise RuntimeError('Warmup transport or non-thinking contract failed')
            if (warm_row['final']['eval_count'] > 32
                    or config['context'] - warm_row['final']['prompt_eval_count'] - 32 < 128):
                raise RuntimeError('Warmup output/context cap contract failed')
            server.verify_loaded()
            stamps.append(paired_stamp())

            def offer(job, phase, case_id):
                if time.monotonic() > deadline - 300:
                    raise RuntimeError('Collection budget stopped before next request')
                identifier, cap = job['request_id'], job['max_output_tokens']
                server.check_host('before_' + identifier)
                before = paired_stamp()
                triggered = threading.Event()
                def stop():
                    triggered.set()
                    server.stop_owned()
                timer = threading.Timer(100, stop)
                timer.daemon = True
                timer.start()
                path = out / (identifier + '.json')
                try:
                    raw = run_trace('http://127.0.0.1:11562', [job], config['model'], config['options'],
                                    timeout_s=90, hard_timeout_s=95,
                                    checkpoint=lambda x: write(path, x))
                    write(path, raw)
                finally:
                    timer.cancel()
                    timer.join()
                after = paired_stamp()
                server.check_host('after_' + identifier)
                if triggered.is_set():
                    raise RuntimeError('Owned-server watchdog fired')
                stamps.extend([before, raw['started_stamp'], raw['finished_stamp'], after])
                row = raw['requests'][0]
                entry = dict(request_id=identifier, phase=phase, case_id=case_id,
                             api_completed=row['completed'], observed_context_margin=None,
                             raw_file=path.name, output_tokens=None, done_reason=None, completion_s=None,
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
                margin = config['context'] - row['final']['prompt_eval_count'] - cap
                entry['observed_context_margin'] = margin
                if margin < 128:
                    raise RuntimeError('Insufficient observed prompt/output context allowance')
                if row['final']['eval_count'] > cap:
                    raise RuntimeError('Observed output exceeds request token cap')
                entry.update(output_tokens=row['final']['eval_count'], done_reason=row['final'].get('done_reason'),
                             completion_s=row['terminal_offset_s'] - row['arrival_offset_s'])
                write(out / 'STAGE.json', result)
                print(json.dumps(dict(stage='collection', phase=phase, request=identifier,
                                      api_completed=entry['api_completed'])), flush=True)
                time.sleep(.2)

            for job, phase, case_id in jobs:
                offer(job, phase, case_id)
            if [entry['request_id'] for entry in result['requests']] != [job['request_id'] for job, _, _ in jobs]:
                raise RuntimeError('Completed collection differs from assigned 48-request chronology')
            server.verify_loaded()
            stamps.append(paired_stamp())
            result.update(clock_stamps=stamps, clock_diagnostics=bridge_diagnostics(stamps))
            if not result['clock_diagnostics']['valid']:
                raise RuntimeError('Observed clock bridge failed')
            if re.search(r'truncat(?:e|ed|ing).*?(?:input|prompt)|(?:input|prompt).*?truncat',
                         (out / 'SERVER.log').read_text(), re.I):
                raise RuntimeError('Input truncation diagnostic')
        result.update(status='completed', completed_requests=PLANNED_REQUESTS)
    except BaseException as error:
        result.update(status='aborted', error=type(error).__name__ + ': ' + str(error))
        raise
    finally:
        result['finished_utc'] = utc()
        write(out / 'STAGE.json', result)
    return result


def main(out):
    freeze = check_freeze()
    config = json.loads((BASE / 'CONFIG.json').read_text())
    for name, wanted in {'model': MODEL, 'digest': DIGEST, 'context': 4096, 'budget_s': 1800,
                         'request_timeout_s': 90, 'max_output_tokens': 256, 'think': False}.items():
        if config.get(name) != wanted or type(config.get(name)) is not type(wanted):
            raise ValueError('Unsupported config: ' + name)
    if config.get('options') != dict(num_ctx=4096, num_predict=256, temperature=0, seed=0):
        raise ValueError('Unsupported request options')
    cases, controls = validate_inputs(BASE)
    case_ids = [case['request_id'] for case in cases]
    control_ids = [control['request_id'] for control in controls]
    if len(cases) != 24 or len(set(case_ids)) != 24 or len(controls) != 24 or len(set(control_ids)) != 24:
        raise ValueError('Expected 24 distinct cases and 24 distinct control requests')
    if (any(type(identifier) is not str or not re.fullmatch(r'[A-Za-z0-9_-]+', identifier) for identifier in case_ids)
            or any(type(identifier) is not str or not re.fullmatch(r'c_[A-Za-z0-9_-]+', identifier) for identifier in control_ids)
            or any(control['case_id'] not in case_ids for control in controls)):
        raise ValueError('Unsafe or mismatched case/control identifiers')
    pairs = Counter(control['pair_id'] for control in controls)
    if len(pairs) != 12 or set(pairs.values()) != {2}:
        raise ValueError('Expected 12 offline control pairs of two candidates')
    out.mkdir(parents=True, exist_ok=False)
    campaign = dict(started_utc=utc(), source_freeze_sha256=freeze, status='starting', planned_requests=PLANNED_REQUESTS)
    write(out / 'CAMPAIGN.json', campaign)
    deadline = time.monotonic() + 1800
    try:
        collection = stage(config, cases, controls, out / 'collection', deadline)
        campaign.update(status='completed', scored_requests=PLANNED_REQUESTS, stages=[collection])
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
