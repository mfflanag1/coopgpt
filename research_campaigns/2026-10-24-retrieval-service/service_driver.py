#!/usr/bin/env python3
"""External arrivals and inclusive client latency; no real collection without a freeze."""
import argparse
from collections import deque
import hashlib
import json
import math
from pathlib import Path
import platform
import queue
import random
import statistics
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parent
DEADLINE_NS = 100_000_000
WAIT_NS = 2_000_000
MAX_BATCH = 16


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    with Path(path).open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2, allow_nan=False)
        f.write('\n')


def validate_expected_answers(value):
    """Validate the copied answer table's shape only; compute no query distances."""
    if not isinstance(value, dict) or set(value) != {str(i) for i in range(100)}:
        raise ValueError('Qualified answers must map all 100 canonical query IDs')
    for qid, top in value.items():
        if not isinstance(top, list) or len(top) != 10:
            raise ValueError(f'Qualified answer {qid}: expected ten neighbors')
        for item in top:
            if not isinstance(item, dict) or set(item) != {'id', 'distance'}:
                raise ValueError(f'Qualified answer {qid}: neighbor schema')
            if type(item['id']) is not int or not 0 <= item['id'] < 10_000:
                raise ValueError(f'Qualified answer {qid}: ID range/type')
            if type(item['distance']) is not int or not 0 <= item['distance'] <= 8_323_200:
                raise ValueError(f'Qualified answer {qid}: distance range/type')
        if len({item['id'] for item in top}) != 10:
            raise ValueError(f'Qualified answer {qid}: duplicate IDs')
        if top != sorted(top, key=lambda item: (item['distance'], item['id'])):
            raise ValueError(f'Qualified answer {qid}: noncanonical ordering')
    return value


def remaining_timeout(deadline, cap, context):
    remaining = deadline-time.monotonic()
    if remaining <= 0:
        raise TimeoutError(f'Phase watchdog before {context}')
    return min(cap, remaining)


def schedule(seed, count, rate):
    """Fixed exogenous Poisson schedule; balanced queries, independent scheduling RNG."""
    if count <= 0 or count % 100 or not math.isfinite(rate) or rate <= 0:
        raise ValueError('Count must be a positive multiple of 100; rate positive')
    timing = random.Random(seed)
    identity = random.Random(seed ^ 0x5F3759DF)
    ids = []
    for _ in range(count // 100):
        cycle = list(range(100)); identity.shuffle(cycle); ids.extend(cycle)
    elapsed = 0.0
    rows = []
    for i, qid in enumerate(ids):
        elapsed += timing.expovariate(rate)
        rows.append({'request_id': str(i), 'query_id': qid, 'offset_ns': round(elapsed * 1e9)})
    return rows


def make_plan(stage, rate=None):
    if stage not in ('calibration', 'evaluation'):
        raise ValueError('Unknown stage')
    if stage == 'evaluation' and rate not in (20, 50, 100, 200):
        raise ValueError('Evaluation needs one prespecified development rate')
    rates = (20, 50, 100, 200) if stage == 'calibration' else (rate,)
    repeats = 2 if stage == 'calibration' else 4
    windows = []
    # Evaluation seeds are fixed before calibration; only rate is selected later.
    seed_base = 241024100 if stage == 'calibration' else 241024900
    for rindex, r in enumerate(rates):
        for pair in range(repeats):
            seed = seed_base + rindex*10 + pair
            requests = schedule(seed, 200, r)
            order = ('immediate','bounded') if pair % 2 == 0 else ('bounded','immediate')
            for policy in order:
                windows.append({'window_id': f'{stage}-r{r}-p{pair}-{policy}', 'pair': pair,
                    'rate': r, 'policy': policy, 'seed': seed, 'requests': requests})
    return {'schema': 1, 'stage': stage, 'authorized': False, 'deadline_ns': DEADLINE_NS,
            'batch_wait_ns': WAIT_NS, 'max_batch': MAX_BATCH, 'batch_timeout_s': 2.0,
            'startup_timeout_s': 30.0, 'phase_timeout_s': 600.0,
            'warmup_queries': list(range(20)), 'windows': windows}


def next_batch(pending, policy, now_ns):
    """Return None while waiting; the oldest *planned* arrival sets the wait cap."""
    if policy not in ('immediate', 'bounded'):
        raise ValueError('Unknown policy')
    if not pending:
        return None
    if policy == 'bounded' and len(pending) < MAX_BATCH and now_ns < pending[0]['planned_ns'] + WAIT_NS:
        return None
    count = 1 if policy == 'immediate' else min(MAX_BATCH, len(pending))
    return [pending.popleft() for _ in range(count)]


class Backend:
    def __init__(self, command, stderr_path, startup_timeout):
        startup_start = time.monotonic_ns()
        self.stderr = Path(stderr_path).open('xb')
        self.stdout_capture = Path(str(stderr_path)+'.stdout.bin').open('xb')
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=self.stderr, bufsize=0)
        self.lines = queue.Queue()
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()
        try:
            self.ready = self.receive(startup_timeout)
            if self.ready.get('event') != 'ready':
                raise RuntimeError(f'Backend startup: {self.ready}')
            self.ready['client_startup_ns'] = time.monotonic_ns()-startup_start
        except BaseException:
            self.close(); raise

    def _read(self):
        try:
            while True:
                line = self.process.stdout.readline(1_048_577)
                if not line:
                    self.lines.put(RuntimeError('Backend EOF')); return
                self.stdout_capture.write(line); self.stdout_capture.flush()
                if len(line) > 1_048_576 or not line.endswith(b'\n'):
                    self.lines.put(RuntimeError('Oversize/truncated backend line')); return
                self.lines.put(line)
        except BaseException as exc:
            self.lines.put(exc)

    def receive(self, timeout, interrupt=None):
        deadline = time.monotonic()+timeout
        while True:
            if interrupt is not None:
                interrupt()
            remaining = deadline-time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f'No backend response within {timeout:.6g} seconds')
            try:
                value = self.lines.get(timeout=min(remaining,.05) if interrupt is not None else remaining)
                break
            except queue.Empty:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f'No backend response within {timeout:.6g} seconds') from None
        if isinstance(value, BaseException):
            raise value
        obj = json.loads(value)
        if not isinstance(obj, dict):
            raise ValueError('Backend response is not an object')
        return obj

    def solve(self, batch_id, rows, timeout, interrupt=None):
        command = {'batch_id': batch_id, 'requests': [
            {'request_id': r['request_id'], 'query_id': r['query_id']} for r in rows]}
        self.process.stdin.write(json.dumps(command, separators=(',', ':')).encode()+b'\n')
        self.process.stdin.flush()
        return self.receive(timeout, interrupt)

    def close(self):
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.process.kill(); self.process.wait(timeout=2)
        self.reader.join(timeout=1)
        self.process.stdin.close()
        self.process.stdout.close()
        self.stdout_capture.close()
        self.stderr.close()


def validate_response(response, batch_id, rows, base_count, expected=None):
    if response.get('event') != 'response' or response.get('batch_id') != batch_id:
        raise ValueError('Wrong response event/batch')
    answers = response.get('answers', [])
    if len(answers) != len(rows):
        raise ValueError('Missing/extra answers')
    for r, a in zip(rows, answers):
        if a.get('request_id') != r['request_id'] or a.get('query_id') != r['query_id']:
            raise ValueError('Wrong/reordered request identity')
        if a.get('passed') is not True or a.get('compared_distances') != base_count or a.get('mismatch_count') != 0 or a.get('invalid_dot_count') != 0:
            raise ValueError('Native exact validation failed')
        top = a.get('top10', [])
        if len(top) != 10 or len({x['id'] for x in top}) != 10:
            raise ValueError('Top-ten cardinality')
        for x in top:
            if type(x['id']) is not int or not 0 <= x['id'] < base_count or type(x['distance']) is not int or not 0 <= x['distance'] <= 8_323_200:
                raise ValueError('Neighbor type/range')
        if top != sorted(top, key=lambda x: (x['distance'], x['id'])):
            raise ValueError('Noncanonical ordering')
        digest = a.get('distance_sha256', '')
        if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('Missing distance digest')
        if expected is not None and top != expected[str(r['query_id'])]:
            raise ValueError('Mismatch with qualified canonical answer')
    return answers


def run_window(spec, backend, out, config, expected=None, phase_deadline=None):
    """Caller precreates backend; every planned request is retained even on failure."""
    out.mkdir()
    start = time.monotonic_ns() + 50_000_000
    rows = [dict(r, planned_ns=start+r['offset_ns'], status='planned', offered_ns=None,
                 submitted_ns=None, delivered_ns=None, latency_ns=None) for r in spec['requests']]
    dump(out/'PLAN.json', {'window': spec, 'start_monotonic_ns': start, 'requests': rows})
    offered = queue.Queue()
    arrival_errors = queue.Queue()
    stop = threading.Event()

    def offer():
        try:
            for r in rows:
                remaining = (r['planned_ns']-time.monotonic_ns())/1e9
                if stop.wait(max(0, remaining)):
                    return
                r['offered_ns'] = time.monotonic_ns()
                r['status'] = 'queued'
                offered.put(r)
        except BaseException as exc:
            arrival_errors.put(exc)
            stop.set()

    def check_arrivals():
        try:
            exc = arrival_errors.get_nowait()
        except queue.Empty:
            return
        raise RuntimeError(f'Arrival scheduler failed: {type(exc).__name__}: {exc}') from exc

    scheduler = threading.Thread(target=offer, name='external-arrivals', daemon=True)
    scheduler.start()
    pending = deque(); completed = 0; batch_id = 0; failure = None
    deadline = phase_deadline if phase_deadline is not None else time.monotonic() + config['phase_timeout_s']
    try:
        with (out/'RESPONSES.jsonl').open('x') as responses:
            while completed < len(rows):
                check_arrivals()
                if time.monotonic() >= deadline:
                    raise TimeoutError('Window watchdog')
                while True:
                    try: pending.append(offered.get_nowait())
                    except queue.Empty: break
                batch = next_batch(pending, spec['policy'], time.monotonic_ns())
                if batch is None:
                    time.sleep(0.0001); continue
                submitted = time.monotonic_ns()
                for r in batch: r.update(status='submitted', submitted_ns=submitted, batch_id=batch_id)
                timeout = remaining_timeout(deadline,config['batch_timeout_s'],'batch response')
                response = backend.solve(batch_id,batch,timeout,check_arrivals)
                check_arrivals()
                try:
                    validate_response(response, batch_id, batch, backend.ready['base_count'], expected)
                except BaseException:
                    responses.write(json.dumps(response, sort_keys=True)+'\n'); responses.flush()
                    raise
                # Delivery is the client receiving, decoding and validating the whole
                # answer. Native work, queueing, pipes and checking are all included.
                delivered = time.monotonic_ns()
                for r in batch:
                    r.update(status='ok', delivered_ns=delivered, latency_ns=delivered-r['planned_ns'])
                responses.write(json.dumps(response, sort_keys=True)+'\n'); responses.flush()
                completed += len(batch); batch_id += 1
    except BaseException as exc:
        failure = f'{type(exc).__name__}: {exc}'
    finally:
        stop.set(); scheduler.join(timeout=1)
        for r in rows:
            if r['status'] != 'ok':
                r['status'] = ('failed_after_submit' if r['submitted_ns'] is not None else
                               'unserved_after_offer' if r['offered_ns'] is not None else 'not_offered_after_abort')
                r['failure'] = failure or 'Window ended without response'
        result = {'synthetic': backend.ready.get('synthetic'), 'window_id': spec['window_id'], 'policy': spec['policy'], 'rate': spec['rate'],
                  'pair': spec['pair'], 'failure': failure, 'requests': rows, 'summary': summarize(rows)}
        dump(out/'RESULT.json', result)
    return result


def quantile(values, probability):
    return sorted(values)[max(0, math.ceil(probability*len(values))-1)]


def summarize(rows):
    if not rows: raise ValueError('No requests')
    successes = [r for r in rows if r['status'] == 'ok']
    # No failures are dropped from percentile denominators. Null denotes +infinity.
    latencies = [r['latency_ns'] if r['status'] == 'ok' else math.inf for r in rows]
    p95 = quantile(latencies, .95)
    jitters = [r['offered_ns']-r['planned_ns'] for r in rows if r['offered_ns'] is not None]
    jitter_valid = len(jitters) == len(rows) and quantile(jitters,.99) <= 2_000_000 and max(jitters) <= 10_000_000
    return {'planned': len(rows), 'offered': len(jitters), 'correct_delivered': len(successes),
            'deadline_success': sum(x <= DEADLINE_NS for x in latencies),
            'p95_ns': p95 if math.isfinite(p95) else None,
            'arrival_valid': jitter_valid, 'p99_offer_jitter_ns': quantile(jitters,.99) if jitters else None,
            'max_offer_jitter_ns': max(jitters) if jitters else None}


def assess(results, stage):
    groups = {}
    for result in results:
        key = (result['rate'], result['pair'])
        group = groups.setdefault(key, {})
        if result['policy'] in group: raise ValueError('Duplicate policy result')
        group[result['policy']] = result
    validity = all(len(g) == 2 for g in groups.values()) and all(
        r['failure'] is None and r['summary']['arrival_valid'] and
        r['summary']['correct_delivered'] == r['summary']['planned'] for r in results)
    if stage == 'calibration':
        eligible = []
        for rate in (20,50,100,200):
            reference = [r for r in results if r['rate']==rate and r['policy']=='immediate']
            if len(reference)==2 and all(r['summary']['arrival_valid'] and r['failure'] is None and
                r['summary']['correct_delivered']==r['summary']['planned'] and
                r['summary']['deadline_success'] >= .99*r['summary']['planned'] for r in reference):
                eligible.append(rate)
        # Never select a rate from an incomplete/invalid study or tune using batch gains.
        return {'valid': validity and len(results)==16, 'selected_rate': max(eligible) if validity and len(results)==16 and eligible else None}
    ratios = []
    for g in groups.values():
        if len(g)==2:
            a,b = g['immediate']['summary']['p95_ns'],g['bounded']['summary']['p95_ns']
            if a and b: ratios.append(b/a)
    service_gate = all(r['summary']['deadline_success'] >= .99*r['summary']['planned'] for r in results)
    complete = len(results)==8 and len(groups)==4 and len({r['rate'] for r in results})==1
    material = len(ratios)==4 and statistics.median(ratios)<=.90 and sum(r<1 for r in ratios)>=3
    return {'valid': validity and complete, 'service_gate': service_gate,
            'paired_p95_ratios': ratios, 'median_ratio': statistics.median(ratios) if ratios else None,
            'passed': validity and complete and service_gate and material}


def validate_freeze(path):
    approval = json.loads(Path(path).read_text())
    if approval.get('authorized') is not True or approval.get('stage') not in ('calibration','evaluation'):
        raise ValueError('An explicitly approved calibration/evaluation freeze is required')
    required = ['PROTOCOL.txt','service_driver.py','src/main.swift','src/QualifiedCore.swift',
                'build/retrieval-service','data/siftsmall_base.fvecs','data/siftsmall_query.fvecs','data/qualified_top10.json']
    for name in required:
        if approval.get('sha256',{}).get(name) != sha(ROOT/name):
            raise ValueError(f'Frozen file missing/changed: {name}')
    plan = approval['plan']
    wanted = make_plan(approval['stage'], approval.get('selected_rate'))
    if plan != wanted: raise ValueError('Plan differs from frozen policy/schedule generator')
    host = approval.get('host_conditions')
    if not isinstance(host, dict) or any(not isinstance(host.get(k),str) or not host[k].strip()
                                        for k in ('power_condition','desktop_activity')):
        raise ValueError('Approved freeze must state power_condition and desktop_activity')
    validate_expected_answers(json.loads((ROOT/'data/qualified_top10.json').read_text()))
    return approval, plan


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', choices=['calibration','evaluation'])
    parser.add_argument('--rate', type=int)
    parser.add_argument('--authorization', type=Path)
    parser.add_argument('--synthetic', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if sum((bool(args.prepare), bool(args.authorization), args.synthetic)) != 1:
        parser.error('Choose exactly one of --prepare, --authorization, --synthetic')
    if args.prepare:
        plan = make_plan(args.prepare, args.rate)
        validate_expected_answers(json.loads((ROOT/'data/qualified_top10.json').read_text()))
        files = ['PROTOCOL.txt','service_driver.py','src/main.swift','src/QualifiedCore.swift',
                 'build/retrieval-service','data/siftsmall_base.fvecs','data/siftsmall_query.fvecs','data/qualified_top10.json']
        dump(args.output, {'authorized':False,'stage':args.prepare,'selected_rate':args.rate,
             'sha256':{f:sha(ROOT/f) for f in files}, 'plan':plan,
             'host_conditions':{'power_condition':None,'desktop_activity':None},
             'review_note':'DRAFT: parent must approve exact freeze before changing authorized to true.'})
        return
    args.output.mkdir()
    if args.synthetic:
        plan = make_plan('evaluation',200)
        plan['windows'] = [dict(plan['windows'][0], requests=[
            {'request_id':str(i),'query_id':i%100,'offset_ns':i*500_000} for i in range(32)]),
            dict(plan['windows'][1], requests=[{'request_id':str(i),'query_id':i%100,'offset_ns':i*500_000} for i in range(32)])]
        command = [str(ROOT/'build/retrieval-service'),'--synthetic-service']; expected = None
        host_conditions = {'scope':'Synthetic test; no stable host condition claimed'}
    else:
        approval, plan = validate_freeze(args.authorization)
        command = [str(ROOT/'build/retrieval-service'),'--data',str(ROOT/'data'),'--authorization',str(args.authorization.resolve())]
        expected = validate_expected_answers(json.loads((ROOT/'data/qualified_top10.json').read_text()))
        host_conditions = approval['host_conditions']
    dump(args.output/'PLAN.json', plan)
    dump(args.output/'HOST.json', {'synthetic':args.synthetic,'platform':platform.platform(),'python':platform.python_version(),
         'python_switch_interval_seconds':sys.getswitchinterval(),'runner_changes_switch_interval':False,
         'approved_host_conditions':host_conditions})
    all_results = []; phase_start = time.monotonic(); aborted = None
    phase_deadline = phase_start+plan['phase_timeout_s']
    for spec in plan['windows']:
        if time.monotonic()-phase_start > plan['phase_timeout_s']:
            aborted = 'Phase watchdog'; break
        backend = None
        try:
            backend = Backend(command, args.output/(spec['window_id']+'-stderr.txt'),
                              remaining_timeout(phase_deadline,plan['startup_timeout_s'],'startup'))
            if bool(backend.ready.get('synthetic')) != args.synthetic: raise ValueError('Backend mode mismatch')
            dump(args.output/(spec['window_id']+'-READY.json'), backend.ready)
            for i,qid in enumerate(plan['warmup_queries']):
                r = [{'request_id':f'warmup-{i}', 'query_id':qid}]
                warmup_start = time.monotonic_ns()
                response = backend.solve(-1-i,r,remaining_timeout(phase_deadline,plan['batch_timeout_s'],'warmup'))
                dump(args.output/(spec['window_id']+f'-warmup-{i}.json'),response)
                validate_response(response,-1-i,r,backend.ready['base_count'],expected)
                dump(args.output/(spec['window_id']+f'-warmup-{i}-client.json'),
                     {'inclusive_client_ns':time.monotonic_ns()-warmup_start})
            result = run_window(spec,backend,args.output/spec['window_id'],plan,expected,phase_deadline)
            all_results.append(result)
            if result['failure']: aborted=result['failure']; break
        except BaseException as exc:
            aborted=f'{type(exc).__name__}: {exc}'; break
        finally:
            if backend is not None: backend.close()
    # The phase PLAN retains every request from windows never started. Explicit
    # not-started records prevent process/startup failure disappearing from analysis.
    completed_ids = {r['window_id'] for r in all_results}
    unrun = [s['window_id'] for s in plan['windows'] if s['window_id'] not in completed_ids]
    report = {'synthetic':args.synthetic,'aborted':aborted,'unrun_windows':unrun,
              'assessment':assess(all_results,plan['stage']) if all_results and not args.synthetic else None,
              'synthetic_checks': [{'window':r['window_id'],'planned':r['summary']['planned'],
                                    'correct_delivered':r['summary']['correct_delivered']}
                                   for r in all_results] if args.synthetic else None}
    dump(args.output/'SUMMARY.json', report)
    if aborted: raise SystemExit(1)


if __name__ == '__main__':
    main()
