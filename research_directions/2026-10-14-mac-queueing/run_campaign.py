"""Execute the frozen local queueing comparison, preserving incomplete windows."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time

from analyze_results import audit_window, expected_hash

ROOT = Path(__file__).resolve().parent


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_freeze(binary):
    frozen_bytes = (ROOT / 'DESIGN_FREEZE.json').read_bytes()
    frozen = json.loads(frozen_bytes)
    for name, expected in frozen['source_sha256'].items():
        if digest(ROOT / name) != expected:
            raise ValueError('Frozen source changed: ' + name)
    if digest(binary) != frozen['binary_sha256']:
        raise ValueError('Binary differs from frozen executable')
    return hashlib.sha256(frozen_bytes).hexdigest()


def diagnostic(kind, deadline=None):
    command = ['/usr/bin/pmset', '-g', kind]
    remaining = 10 if deadline is None else min(10, deadline - time.monotonic())
    if remaining <= 0:
        return {'command': command, 'status': 'unavailable', 'error_type': 'CampaignDeadline'}
    try:
        p = subprocess.run(command, capture_output=True, text=True, timeout=remaining,
                           shell=False, check=False)
        return {'command': command, 'returncode': p.returncode,
                'stdout': p.stdout, 'stderr': p.stderr}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'command': command, 'status': 'unavailable', 'error_type': type(exc).__name__}


def diagnostics(deadline):
    result = {}
    for kind in ('batt', 'therm'):
        try:
            result[kind] = diagnostic(kind, deadline)
        except KeyboardInterrupt:
            result[kind] = {'status': 'unavailable', 'error_type': 'KeyboardInterrupt'}
            break
    return result


def interrupted(diagnostics_result):
    return any(item.get('error_type') == 'KeyboardInterrupt'
               for item in diagnostics_result.values())


def save_new(path, obj):
    with path.open('x') as handle:
        json.dump(obj, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write('\n')


def run_window(binary, folder, window, timeout, frozen, deadline=None, audit_context=None):
    folder.mkdir(exist_ok=False)
    before = diagnostics(deadline)
    if deadline is not None:
        timeout = max(0, min(timeout, deadline - time.monotonic()))
    command = [str(binary), '--concurrency', str(window['concurrency']),
               '--rate', str(window['rate']), '--output', str(folder / 'RAW.json')]
    meta = {k: window[k] for k in ('window_id', 'index', 'round', 'rate', 'concurrency')}
    meta.update(command=command, started_utc=utc(), timeout_seconds=timeout,
                before=before, freeze_sha256=frozen, source_changed=False)
    tick = time.monotonic()
    try:
        if interrupted(before):
            raise KeyboardInterrupt
        if timeout <= 0:
            raise subprocess.TimeoutExpired(command, timeout)
        p = subprocess.run(command, capture_output=True, text=True,
                           timeout=timeout, shell=False, check=False)
        meta.update(returncode=p.returncode, process_status='completed')
        stdout, stderr = p.stdout, p.stderr
    except subprocess.TimeoutExpired as exc:
        meta.update(returncode=None, process_status='timed_out')
        stdout, stderr = exc.stdout or b'', exc.stderr or b''
    except KeyboardInterrupt:
        meta.update(returncode=None, process_status='interrupted')
        stdout, stderr = '', ''
    except OSError as exc:
        meta.update(returncode=None, process_status='launch_failed', error_type=type(exc).__name__)
        stdout, stderr = '', ''
    meta.update(finished_utc=utc(), process_elapsed_seconds=time.monotonic() - tick)
    for name, value in [('STDOUT.txt', stdout), ('STDERR.txt', stderr)]:
        (folder / name).write_bytes(value if isinstance(value, bytes) else value.encode())
    meta['after'] = diagnostics(deadline)
    meta['diagnostic_interrupted'] = interrupted(before) or interrupted(meta['after'])
    try:
        if verify_freeze(binary) != frozen:
            meta['source_changed'] = True
    except (OSError, ValueError, KeyError):
        meta['source_changed'] = True
    raw_path = folder / 'RAW.json'
    meta['raw_output_present'] = raw_path.is_file()
    meta['raw_gate_passed'] = False
    meta['independent_window_checks_passed'] = False
    meta['independent_window_errors'] = ['Raw output or independent audit context unavailable']
    if meta['raw_output_present']:
        try:
            raw = json.loads(raw_path.read_text())
            meta['raw_gate_passed'] = isinstance(raw, dict) and raw.get('gate_passed') is True
            if isinstance(raw, dict) and audit_context is not None:
                audit = audit_window(raw, window, *audit_context)
                meta['independent_window_checks_passed'] = audit['checks_passed'] is True
                meta['independent_window_errors'] = audit['errors']
        except (OSError, ValueError, TypeError, KeyError, AttributeError):
            meta['raw_parse_error'] = True
    save_new(folder / 'EXECUTION.json', meta)
    ok = (meta['returncode'] == 0 and meta['process_status'] == 'completed'
          and meta['raw_gate_passed'] and meta['independent_window_checks_passed']
          and not meta['diagnostic_interrupted'] and not meta['source_changed'])
    return meta, ok


def collect(binary, output):
    frozen = verify_freeze(binary)
    plan = json.loads((ROOT / 'PLAN.json').read_text())
    output.mkdir(exist_ok=False)
    from capture_inventory import capture
    campaign = {'schema_version': 1, 'started_utc': utc(),
                'campaign_timeout_seconds': plan['campaign_timeout_seconds'],
                'plan_sha256': digest(ROOT / 'PLAN.json'), 'freeze_sha256': frozen,
                'windows': [], 'unrun_window_ids': [], 'stop_reason': None,
                'source_changed': False}
    tick = time.monotonic()
    deadline = tick + plan['campaign_timeout_seconds']
    try:
        inventory = capture('mac-local')
        save_new(output / 'INVENTORY.json', inventory)
        devices = inventory.get('hardware', {}).get('gpu_inventory', {}).get('devices', [])
        if not isinstance(devices, list):
            raise ValueError('GPU device inventory unavailable')
        device_names = {d.get('model') for d in devices if isinstance(d, dict)}
        audit_context = (plan, {n: expected_hash(n) for n in plan['warmup_dimensions']}, device_names)
        for window in plan['windows']:
            if campaign['windows']:
                time.sleep(max(0, min(plan['inter_window_idle_seconds'], deadline - time.monotonic())))
            remaining = plan['campaign_timeout_seconds'] - (time.monotonic() - tick)
            if remaining <= 0:
                campaign['stop_reason'] = 'campaign_time_ceiling'
                break
            try:
                if verify_freeze(binary) != frozen:
                    raise ValueError('Design freeze changed')
            except (OSError, ValueError, KeyError) as exc:
                campaign.update(stop_reason='source_integrity_failure', source_changed=True)
                break
            folder_name = f"w{window['index']:02d}_{window['window_id']}"
            timeout = min(plan['window_timeout_seconds'], remaining)
            item = {k: window[k] for k in ('window_id', 'index', 'round', 'rate', 'concurrency')}
            item.update(folder=folder_name, status='started', returncode=None)
            campaign['windows'].append(item)
            meta, ok = run_window(binary, output / folder_name, window, timeout, frozen, deadline, audit_context)
            item.update(status='completed' if ok else 'invalid', returncode=meta['returncode'])
            print(json.dumps({'window': window['window_id'], 'status': item['status'],
                              'elapsed_seconds': meta['process_elapsed_seconds']}), flush=True)
            if not ok:
                campaign['stop_reason'] = 'invalid_window:' + window['window_id']
                campaign['source_changed'] = meta['source_changed']
                break
    except (OSError, ValueError, KeyError, KeyboardInterrupt) as exc:
        campaign['stop_reason'] = 'collection_exception:' + type(exc).__name__
    recorded = {w['window_id'] for w in campaign['windows']}
    campaign['unrun_window_ids'] = [w['window_id'] for w in plan['windows']
                                    if w['window_id'] not in recorded]
    campaign.update(finished_utc=utc(), monotonic_duration_seconds=time.monotonic() - tick)
    try:
        if verify_freeze(binary) != frozen:
            campaign['source_changed'] = True
    except (OSError, ValueError, KeyError):
        campaign['source_changed'] = True
    save_new(output / 'CAMPAIGN.json', campaign)
    return not campaign['unrun_window_ids'] and not campaign['stop_reason'] and not campaign['source_changed']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='New capture directory')
    args = parser.parse_args()
    passed = collect(args.binary.resolve(), args.output.resolve())
    print(json.dumps({'capture_directory': str(args.output), 'collection_completed': passed}))
    raise SystemExit(0 if passed else 1)
