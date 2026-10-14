"""Collect the two frozen SIFT10K correctness profiles, retaining failures."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_freeze(binary):
    path = ROOT / 'DESIGN_FREEZE.json'
    frozen = json.loads(path.read_text())
    for name, expected in frozen['source_sha256'].items():
        if sha(ROOT / name) != expected:
            raise ValueError('Frozen source/data changed: ' + name)
    if sha(binary) != frozen['binary_sha256']:
        raise ValueError('Frozen binary changed')
    return sha(path)


def save_new(path, obj):
    with path.open('x') as handle:
        json.dump(obj, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write('\n')


def diagnostics(deadline):
    result = {}
    for kind in ('batt', 'therm'):
        command = ['/usr/bin/pmset', '-g', kind]
        remaining = min(10, deadline - time.monotonic())
        if remaining <= 0:
            result[kind] = {'command': command, 'status': 'unavailable', 'error_type': 'CampaignDeadline'}
            continue
        try:
            p = subprocess.run(command, capture_output=True, text=True, timeout=remaining, shell=False, check=False)
            result[kind] = {'command': command, 'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
        except (OSError, subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
            result[kind] = {'command': command, 'status': 'unavailable', 'error_type': type(exc).__name__}
            if isinstance(exc, KeyboardInterrupt):
                break
    return result


def interrupted(diags):
    return any(v.get('error_type') == 'KeyboardInterrupt' for v in diags.values())


def run_profile(binary, folder, profile, timeout, deadline, frozen):
    if folder.exists():
        raise FileExistsError('Native profile directory already exists')
    before = diagnostics(deadline)
    timeout = max(0, min(timeout, deadline - time.monotonic()))
    command = [str(binary), '--data', str(ROOT / 'data'), '--batch-size', str(profile['batch_size']),
               '--output-dir', str(folder)]
    meta = {k: profile[k] for k in ('index', 'profile_id', 'batch_size')}
    meta.update(command=command, started_utc=utc(), timeout_seconds=timeout, before=before,
                freeze_sha256=frozen, source_changed=False)
    tick = time.monotonic()
    try:
        if interrupted(before):
            raise KeyboardInterrupt
        if timeout <= 0:
            raise subprocess.TimeoutExpired(command, timeout)
        p = subprocess.run(command, capture_output=True, text=True, timeout=timeout, shell=False, check=False)
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
    folder.mkdir(exist_ok=True)
    for name, value in [('STDOUT.txt', stdout), ('STDERR.txt', stderr)]:
        with (folder / name).open('xb') as handle:
            handle.write(value if isinstance(value, bytes) else value.encode())
    meta['after'] = diagnostics(deadline)
    meta['diagnostic_interrupted'] = interrupted(before) or interrupted(meta['after'])
    try:
        if verify_freeze(binary) != frozen:
            meta['source_changed'] = True
    except (OSError, ValueError, KeyError):
        meta['source_changed'] = True
    raw_path = folder / 'RAW.json'
    meta.update(raw_output_present=raw_path.is_file(), raw_gate_passed=False)
    if meta['raw_output_present']:
        try:
            raw = json.loads(raw_path.read_text())
            meta['raw_gate_passed'] = isinstance(raw, dict) and raw.get('gate_passed') is True
        except (OSError, ValueError):
            meta['raw_parse_error'] = True
    save_new(folder / 'EXECUTION.json', meta)
    ok = (meta['returncode'] == 0 and meta['process_status'] == 'completed'
          and meta['raw_gate_passed'] and not meta['source_changed'] and not meta['diagnostic_interrupted'])
    return meta, ok


def collect(binary, output):
    frozen = verify_freeze(binary)
    plan = json.loads((ROOT / 'PLAN.json').read_text())
    output.mkdir(exist_ok=False)
    from capture_inventory import capture
    campaign = {'schema_version': 1, 'started_utc': utc(), 'campaign_timeout_seconds': plan['campaign_timeout_seconds'],
                'plan_sha256': sha(ROOT / 'PLAN.json'), 'freeze_sha256': frozen,
                'profiles': [], 'unrun_profile_ids': [], 'stop_reason': None, 'source_changed': False}
    tick = time.monotonic()
    deadline = tick + plan['campaign_timeout_seconds']
    try:
        inventory = capture('mac-local')
        save_new(output / 'INVENTORY.json', inventory)
        if not isinstance(inventory.get('hardware', {}).get('gpu_inventory', {}).get('devices'), list):
            raise ValueError('GPU inventory unavailable')
        for profile in plan['profiles']:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                campaign['stop_reason'] = 'campaign_time_ceiling'
                break
            if verify_freeze(binary) != frozen:
                raise ValueError('Frozen manifest changed')
            item = dict(profile, status='started', returncode=None)
            campaign['profiles'].append(item)
            meta, ok = run_profile(binary, output / profile['folder'], profile,
                                   min(plan['window_timeout_seconds'], remaining), deadline, frozen)
            item.update(status='completed' if ok else 'invalid', returncode=meta['returncode'])
            print(json.dumps({'profile': profile['profile_id'], 'status': item['status'],
                              'elapsed_seconds': meta['process_elapsed_seconds']}), flush=True)
            if not ok:
                campaign.update(stop_reason='invalid_profile:' + profile['profile_id'], source_changed=meta['source_changed'])
                break
    except (OSError, ValueError, KeyError, KeyboardInterrupt) as exc:
        campaign['stop_reason'] = 'collection_exception:' + type(exc).__name__
    recorded = {w['profile_id'] for w in campaign['profiles']}
    campaign['unrun_profile_ids'] = [p['profile_id'] for p in plan['profiles'] if p['profile_id'] not in recorded]
    campaign.update(finished_utc=utc(), monotonic_duration_seconds=time.monotonic() - tick)
    try:
        if verify_freeze(binary) != frozen:
            campaign['source_changed'] = True
    except (OSError, ValueError, KeyError):
        campaign['source_changed'] = True
    save_new(output / 'CAMPAIGN.json', campaign)
    return not campaign['unrun_profile_ids'] and not campaign['stop_reason'] and not campaign['source_changed']


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    success = collect(args.binary.resolve(), args.output.resolve())
    print(json.dumps({'collection_completed': success, 'capture_directory': str(args.output)}))
    raise SystemExit(0 if success else 1)
