#!/usr/bin/env python3
"""Independent stdlib audit of the fixed Mac queueing campaign; no GPU execution."""
import argparse
from collections import deque
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import statistics
import struct

CAP = 64 * 1024 * 1024
REQUIRED = {'PROTOCOL.txt', 'PLAN.json', 'queue_benchmark.swift', 'run_campaign.py',
            'capture_inventory.py', 'analyze_results.py', 'test_analyze_results.py'}


def load(path):
    def unique(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    def reject(value):
        raise ValueError('Nonfinite JSON constant: ' + value)
    return json.loads(Path(path).read_text(), object_pairs_hook=unique, parse_constant=reject)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def integer(x, minimum=0):
    return type(x) is int and x >= minimum


def finite(x, minimum=0):
    return type(x) in (int, float) and math.isfinite(x) and x >= minimum


def quantile95(values):
    return sorted(values)[math.ceil(.95 * len(values)) - 1] if values else None


def summary(values):
    return {'count': len(values), 'mean': statistics.mean(values) if values else None,
            'median': statistics.median(values) if values else None,
            'p95': quantile95(values), 'maximum': max(values) if values else None}


def expected_hash(n):
    if n not in (4, 256, 512, 1024):
        raise ValueError('Unexpected fixed workload dimension')
    matrix = [[sum((((i + 3*k) % 7)-3) * (((5*k+j) % 11)-5) for k in range(n))
               for j in range(11)] for i in range(7)]
    rows = [b''.join(struct.pack('<f', matrix[i][j % 11]) for j in range(n)) for i in range(7)]
    h = hashlib.sha256()
    for i in range(n):
        h.update(rows[i % 7])
    return h.hexdigest()


def check_plan(plan):
    windows = []
    for rnd, rates in enumerate(([10,40,100], [100,40,10], [40,10,100], [100,10,40]), 1):
        for rate in rates:
            for cap in ([1,2] if rnd % 2 else [2,1]):
                windows.append({'index': len(windows)+1, 'round': rnd, 'rate': rate, 'concurrency': cap,
                                'jobs': 60, 'window_id': f'r{rnd}_rate{rate}_c{cap}'})
    expected = {'schema_version': 1, 'dimensions': [256,512,1024]*20,
                'warmup_dimensions': [256,512,1024], 'windows': windows,
                'deadline_seconds': .1, 'time_consistency_tolerance_seconds': 1e-6,
                'producer_p95_lateness_limit_seconds': .01, 'primary_rate': 100, 'low_rate': 10,
                'primary_median_ratio_limit': .90, 'primary_min_improved_pairs': 3,
                'low_median_ratio_limit': 1.10, 'campaign_timeout_seconds': 600,
                'window_timeout_seconds': 90, 'inter_window_idle_seconds': 1}
    if plan != expected:
        raise ValueError('Plan differs from reviewed fixed cohort or gate')


def power(diagnostic):
    """Only explicitly reported successful pmset AC/Battery source labels qualify."""
    if not isinstance(diagnostic, dict) or type(diagnostic.get('returncode')) is not int or diagnostic['returncode'] != 0:
        return {'source': None, 'battery_percent': None}
    raw = diagnostic.get('stdout', '')
    if not isinstance(raw, str):
        return {'source': None, 'battery_percent': None}
    sources = re.findall(r"Now drawing from '([^']+)'", raw)
    percentages = re.findall(r'\b(\d+)%', raw)
    source = sources[0] if len(sources) == 1 and sources[0] in ('AC Power', 'Battery Power') else None
    percent = int(percentages[0]) if len(percentages) == 1 and 0 <= int(percentages[0]) <= 100 else None
    return {'source': source, 'battery_percent': percent}


def interval_utc(obj, start, end):
    try:
        a, b = [datetime.fromisoformat(obj[key].replace('Z', '+00:00')) for key in (start, end)]
        return (a.utcoffset() is not None and b.utcoffset() is not None and
                a.utcoffset().total_seconds() == b.utcoffset().total_seconds() == 0 and b >= a)
    except (KeyError, TypeError, ValueError, AttributeError):
        return False


def audit_window(raw, window, plan, expected, device_names):
    errors = []
    def check(ok, message):
        if not ok:
            errors.append(message)
    tol = plan['time_consistency_tolerance_seconds']
    cap, rate = window['concurrency'], window['rate']
    check(raw.get('schema_version') == 1 and type(raw.get('schema_version')) is int, 'Wrong native schema')
    check(raw.get('protocol_id') == 'mac-mps-queueing-v1', 'Wrong native protocol')
    check(raw.get('concurrency') == cap and type(raw.get('concurrency')) is int and raw.get('rate') == rate
          and type(raw.get('rate')) is int, 'Native treatment differs')
    check(raw.get('gate_passed') is True and raw.get('cpu_self_test_passed') is True and raw.get('failure') is None,
          'Native gate/self-test/failure status')
    check(raw.get('device_name') in device_names and raw.get('has_unified_memory') is True, 'Device/inventory mismatch')
    check(raw.get('per_job_explicit_byte_cap') == CAP and raw.get('active_explicit_byte_cap') == CAP*cap,
          'Wrong explicit memory caps')
    check(integer(raw.get('max_buffer_length'), 1), 'Invalid maximum buffer length')
    check(integer(raw.get('recommended_max_working_set_size'), 1), 'Invalid advisory working set')
    check(integer(raw.get('epoch_uptime_ns'), 1) and integer(raw.get('warmup_epoch_uptime_ns'), 1)
          and raw['epoch_uptime_ns'] > raw['warmup_epoch_uptime_ns'], 'Invalid separate epochs')
    check(interval_utc(raw, 'started_at', 'completed_at'), 'Invalid native UTC interval')
    jobs, warmups = raw.get('jobs'), raw.get('warmups')
    if not isinstance(jobs, list) or not isinstance(warmups, list):
        raise ValueError('Jobs and warmups must be lists')
    check(len(jobs) == 60 and len(warmups) == 3, 'Missing/extra measured or warmup rows')
    latencies, enqueue_latencies, queue_delays, jitter, services, cleanup = [], [], [], [], [], []
    correct, on_time, released, warm_correct = 0, 0, 0, 0
    payload = {}
    by_id = {}
    for group, expected_ns in [('warmup', plan['warmup_dimensions']), ('measured', plan['dimensions'])]:
        group_rows = warmups if group == 'warmup' else jobs
        for index, n in enumerate(expected_ns):
            label = f'{group}[{index}]'
            before = len(errors)
            row = group_rows[index] if index < len(group_rows) else None
            if not isinstance(row, dict):
                check(False, label + ': missing/non-object row'); continue
            check(row.get('id') == index and type(row.get('id')) is int and row.get('n') == n
                  and type(row.get('n')) is int and row.get('kind') == group, label + ': wrong identity/order')
            check(row.get('status') == 'passed' and row.get('passed') is True and row.get('failure') is None
                  and row.get('failed_at_s') is None, label + ': failed job')
            check(row.get('command_buffer_status') == 4 and type(row.get('command_buffer_status')) is int
                  and row.get('command_buffer_error') is None, label + ': unsuccessful GPU command')
            check(row.get('gpu_output_sha256') == expected[n] and row.get('cpu_reference_sha256') == expected[n],
                  label + ': independent output hash mismatch')
            comparison = row.get('check')
            if not isinstance(comparison, dict):
                check(False, label + ': missing comparator')
            else:
                for key, value in [('compared_elements',n*n), ('mismatch_count',0), ('nonfinite_count',0)]:
                    check(type(comparison.get(key)) is int and comparison.get(key) == value, label + ': wrong ' + key)
                for key in ['max_abs_error','max_abs_finite_error']:
                    check(finite(comparison.get(key)) and comparison[key] == 0, label + ': nonzero/nonfinite ' + key)
            rb, allocated = row.get('row_bytes'), row.get('buffer_allocated_bytes')
            check(integer(rb,4*n) and rb % 4 == 0, label + ': bad stride')
            for key, value in [('buffer_payload_bytes',12*n*n), ('cpu_reference_payload_bytes',4*n*n),
                               ('cpu_hash_scratch_bytes',4*n)]:
                check(type(row.get(key)) is int and row.get(key) == value, label + ': wrong ' + key)
            length = row.get('buffer_length_bytes')
            check(integer(length,1) and integer(rb,1) and length == 3*n*rb, label + ': buffer length mismatch')
            check(integer(allocated,1) and integer(length,1) and allocated >= length, label + ': allocation mismatch')
            total = allocated + 4*n*n + 4*n if integer(allocated) else None
            check(integer(total,1) and total <= CAP, label + ': job memory cap exceeded')
            check(integer(rb,1) and integer(raw.get('max_buffer_length'),1) and n*rb <= raw['max_buffer_length'],
                  label + ': device maximum buffer exceeded')
            for key in ['device_allocated_before_buffers_sample','device_allocated_with_buffers_sample','device_allocated_after_release_sample']:
                check(integer(row.get(key)), label + ': missing/invalid global allocation sample')
            fields = ['encode_done_s','submit_s','gpu_completion_observed_s','validated_completion_s','resource_release_s']
            if group == 'measured':
                fields = ['observed_enqueue_s','admission_s'] + fields
                nominal, deadline = index/rate, index/rate + plan['deadline_seconds']
                check(finite(row.get('planned_offer_s')) and abs(row['planned_offer_s']-nominal) <= tol,
                      label + ': nominal offered schedule changed')
                check(finite(row.get('deadline_s')) and abs(row['deadline_s']-deadline) <= tol,
                      label + ': deadline changed')
                check(row.get('admission_sequence') == index and type(row.get('admission_sequence')) is int,
                      label + ': non-FIFO admission sequence')
                by_id[index] = row
                if integer(total): payload[index] = total
            else:
                check(row.get('planned_offer_s') == 0 and row.get('deadline_s') == 0, label + ': warmup timebase fields')
            times = [row.get(key) for key in fields]
            check(all(finite(x) for x in times), label + ': missing/invalid host times')
            if all(finite(x) for x in times):
                check(all(b+tol >= a for a,b in zip(times,times[1:])), label + ': reversed host timeline')
                if group == 'measured':
                    check(times[0]+tol >= nominal, label + ': enqueue before nominal offer')
                    latencies.append(row['validated_completion_s']-nominal)
                    enqueue_latencies.append(row['validated_completion_s']-row['observed_enqueue_s'])
                    queue_delays.append(row['admission_s']-row['observed_enqueue_s'])
                    jitter.append(row['observed_enqueue_s']-nominal)
                    services.append(row['validated_completion_s']-row['admission_s'])
                    cleanup.append(row['resource_release_s']-row['validated_completion_s'])
            gpu_times = [row.get(k) for k in ['gpu_start_time','gpu_end_time','gpu_interval_seconds']]
            if any(x is not None for x in gpu_times):
                check(all(finite(x) and x > 0 for x in gpu_times), label + ': partial/invalid GPU times')
                if all(finite(x) and x > 0 for x in gpu_times):
                    gs,ge,dt = gpu_times
                    check(ge > gs and math.isclose(ge-gs,dt,rel_tol=1e-9,abs_tol=1e-12), label + ': inconsistent GPU duration')
            ok = len(errors) == before
            if group == 'measured':
                correct += int(ok)
                released += int(finite(row.get('resource_release_s')))
                # Deadline uses the original planned schedule and no tolerance/rounding.
                on_time += int(ok and row['validated_completion_s'] <= deadline)
            else:
                warm_correct += int(ok)
    # Replay the chronological locked event log rather than trusting reported maxima.
    pending, active, enqueued, admitted, released_ids = deque(), set(), [], [], []
    maximum_active = 0; maximum_active_payload_bound = 0; previous_time = -math.inf
    events = raw.get('events')
    if not isinstance(events, list):
        events = []; check(False,'Missing event log')
    check(len(events) == 180, 'Missing/extra FIFO events')
    for seq,event in enumerate(events):
        if not isinstance(event,dict): check(False,'Non-object event'); continue
        jid,kind,t = event.get('job_id'),event.get('kind'),event.get('time_s')
        check(type(event.get('sequence')) is int and event['sequence'] == seq, 'Event sequence changed')
        check(integer(jid) and jid < 60 and jid in by_id, 'Unknown event job')
        check(finite(t) and t+tol >= previous_time, 'Event times out of order')
        if finite(t): previous_time = t
        if not integer(jid) or jid >= 60 or jid not in by_id: continue
        row = by_id[jid]
        if kind == 'enqueue':
            check(jid not in enqueued, 'Duplicate enqueue'); enqueued.append(jid); pending.append(jid)
            field = 'observed_enqueue_s'
        elif kind == 'admit':
            check(bool(pending) and pending[0] == jid and jid not in active, 'Non-FIFO/duplicate admission')
            if pending: pending.popleft()
            active.add(jid); admitted.append(jid); field = 'admission_s'
        elif kind == 'release':
            check(jid in active and jid not in released_ids, 'Release without admission/duplicate')
            active.discard(jid); released_ids.append(jid); field = 'resource_release_s'
        else:
            check(False,'Unknown FIFO event'); continue
        check(finite(t) and finite(row.get(field)) and abs(t-row[field]) <= tol, 'Event/job timestamp mismatch')
        check(type(event.get('active_count')) is int and event['active_count'] == len(active)
              and len(active) <= cap, 'Active count/cap mismatch')
        check(type(event.get('queue_count')) is int and event['queue_count'] == len(pending), 'Queue count mismatch')
        maximum_active = max(maximum_active,len(active))
        maximum_active_payload_bound = max(maximum_active_payload_bound,sum(payload.get(i,0) for i in active))
    check(enqueued == list(range(60)) and admitted == list(range(60)) and sorted(released_ids) == list(range(60)),
          'Missing/repeated/non-FIFO event identities')
    check(not active and not pending, 'Window was not drained')
    check(type(raw.get('max_active_observed')) is int and raw['max_active_observed'] == maximum_active,
          'Reported active maximum disagrees with replay')
    check(maximum_active_payload_bound <= CAP*cap, 'Active explicit memory bound exceeded')
    check(finite(raw.get('window_end_s')) and raw['window_end_s']+tol >= previous_time, 'Window ends before last event')
    if integer(raw.get('epoch_uptime_ns')) and integer(raw.get('warmup_epoch_uptime_ns')) and len(warmups) == 3:
        gap = (raw['epoch_uptime_ns']-raw['warmup_epoch_uptime_ns'])/1e9
        check(all(isinstance(r,dict) and finite(r.get('resource_release_s')) and r['resource_release_s'] <= gap+tol
                  for r in warmups), 'Warmup overlaps measured epoch')
    gpu_boundaries = []
    for row in jobs:
        if isinstance(row,dict) and finite(row.get('gpu_start_time')) and finite(row.get('gpu_end_time')) and row['gpu_end_time']>row['gpu_start_time']:
            gpu_boundaries.extend([(row['gpu_start_time'],1),(row['gpu_end_time'],-1)])
    gpu_active = gpu_max = 0
    for _, delta in sorted(gpu_boundaries):
        gpu_active += delta; gpu_max = max(gpu_max,gpu_active)
    # These are raw command-buffer intervals on the device's own clock. Overlap
    # is not proof of simultaneous kernels and is never mixed with host offsets.
    return {'window_id':window['window_id'],'round':window['round'],'rate':rate,'concurrency':cap,
            'planned_jobs':60,'reported_jobs':len(jobs),'released_jobs':released,'independently_correct_jobs':correct,
            'on_time_successes':on_time,'on_time_fraction':on_time/60,'planned_warmups':3,
            'independently_correct_warmups':warm_correct,'checks_passed':not errors,'errors':errors,
            'nominal_offer_latency_seconds':summary(latencies), 'actual_enqueue_latency_seconds':summary(enqueue_latencies),
            'queue_delay_seconds':summary(queue_delays),'producer_lateness_seconds':summary(jitter),
            'active_service_seconds':summary(services),'cleanup_seconds':summary(cleanup),
            'max_active_from_events':maximum_active,'max_active_explicit_payload_bound_bytes':maximum_active_payload_bound,
            'jobs_with_gpu_timestamps':len(gpu_boundaries)//2,
            'max_overlapping_gpu_command_intervals':gpu_max if gpu_boundaries else None,
            'latency_complete':len(latencies)==60}


def paired_gates(windows, plan, validity):
    lookup = {(w['round'],w['rate'],w['concurrency']):w for w in windows}
    pairs = []
    for rnd in range(1,5):
        for rate in (10,40,100):
            a,b = [lookup.get((rnd,rate,c)) for c in (1,2)]
            qa,qb = [(w.get('nominal_offer_latency_seconds',{}).get('p95') if w and w.get('latency_complete') else None) for w in (a,b)]
            ratio = qb/qa if finite(qa) and qa>0 and finite(qb) and qb>0 else None
            powers = [p.get('source') for w in (a,b) if w for p in w.get('power',[])]
            comparable = len(powers)==4 and all(p is not None for p in powers) and len(set(powers))==1
            pairs.append({'round':rnd,'rate':rate,'p95_cap1_seconds':qa,'p95_cap2_seconds':qb,
                          'p95_ratio_cap2_over_cap1':ratio,'cap2_strictly_faster':ratio is not None and ratio<1,
                          'on_time_cap1':a.get('on_time_successes',0) if a else 0,
                          'on_time_cap2':b.get('on_time_successes',0) if b else 0,
                          'power_sources':powers,'power_comparable':comparable})
    primary = [p for p in pairs if p['rate']==plan['primary_rate']]
    low = [p for p in pairs if p['rate']==plan['low_rate']]
    def median_ratio(rows):
        values = [p['p95_ratio_cap2_over_cap1'] for p in rows]
        return statistics.median(values) if len(values)==4 and all(finite(x) for x in values) else None
    pm,lm = median_ratio(primary),median_ratio(low)
    jitter_ok = len(windows)==24 and all(w.get('producer_lateness_seconds',{}).get('count')==60
               and finite(w['producer_lateness_seconds'].get('p95'),-1e-6)
               and w['producer_lateness_seconds']['p95']<=plan['producer_p95_lateness_limit_seconds'] for w in windows)
    all_power = all(p['power_comparable'] for p in pairs)
    valid = validity and all_power and jitter_ok
    conditions = {'validity':valid,'primary_median_improves_10_percent':pm is not None and pm<=plan['primary_median_ratio_limit'],
                  'primary_at_least_three_favorable_pairs':sum(p['cap2_strictly_faster'] for p in primary)>=plan['primary_min_improved_pairs'],
                  'primary_no_total_on_time_loss':sum(p['on_time_cap2'] for p in primary)>=sum(p['on_time_cap1'] for p in primary),
                  'low_rate_no_more_than_10_percent_regression':lm is not None and lm<=plan['low_median_ratio_limit']}
    return {'pairs':pairs,'all_power_pairs_comparable':all_power,'all_producer_jitter_gates_pass':jitter_ok,
            'primary_median_p95_ratio':pm,'low_rate_median_p95_ratio':lm,'conditions':conditions,
            'validity_passed':valid,'promotion_gate_passed':all(conditions.values()),
            'outcome':'invalid_or_incomplete' if not valid else ('engineering_gate_passes' if all(conditions.values()) else 'fails_material_improvement_gate')}


def analyze(root, capture, binary=None):
    root,capture = Path(root),Path(capture)
    errors,windows = [],[]
    def check(ok,message):
        if not ok: errors.append(message)
    output = {'schema_version':1,'errors':errors,'windows':windows,'validity_passed':False,'promotion_gate_passed':False,
              'planned_windows':24,'planned_measured_jobs':1440,'planned_warmup_jobs':72,
              'binary_bytes_reverified':False,'analyzer_sha256':sha(Path(__file__)),
              'interpretation':'Fixed artificial Mac cohort. Digest oracle checks content under SHA256 collision assumptions; no hardware attestation, energy, production or pooling claim.'}
    try:
        plan = load(root/'PLAN.json'); check_plan(plan)
        freeze = load(root/'DESIGN_FREEZE.json'); frozen_sha = sha(root/'DESIGN_FREEZE.json')
        sources = freeze['source_sha256']; check(REQUIRED<=set(sources),'Freeze omits required reviewed sources/tests')
        for name,expected in sources.items():
            rel = PurePosixPath(name)
            if rel.is_absolute() or '..' in rel.parts or name!=rel.as_posix(): raise ValueError('Unsafe frozen path')
            check(sha(root/name)==expected,'Frozen source mismatch: '+name)
        if binary is not None:
            check(sha(binary)==freeze['binary_sha256'],'Frozen binary mismatch')
            output['binary_bytes_reverified'] = sha(binary)==freeze['binary_sha256']
        campaign,inventory = load(capture/'CAMPAIGN.json'),load(capture/'INVENTORY.json')
        output['input_sha256'] = {'CAMPAIGN.json':sha(capture/'CAMPAIGN.json'),'INVENTORY.json':sha(capture/'INVENTORY.json')}
        output['freeze_sha256'] = frozen_sha
        check(campaign.get('plan_sha256')==sha(root/'PLAN.json') and campaign.get('freeze_sha256')==frozen_sha,'Campaign plan/freeze mismatch')
        check(campaign.get('source_changed') is False,'Campaign source changed')
        check(campaign.get('stop_reason') is None,'Campaign stopped early: '+str(campaign.get('stop_reason')))
        check(interval_utc(campaign,'started_utc','finished_utc'),'Campaign UTC interval invalid')
        check(campaign.get('campaign_timeout_seconds')==plan['campaign_timeout_seconds'],'Campaign budget mismatch')
        check(finite(campaign.get('monotonic_duration_seconds')),'Missing campaign duration')
        hardware = inventory['hardware']; gpu = hardware.get('gpu_inventory',{})
        device_names = {d.get('model') for d in gpu.get('devices',[]) if isinstance(d,dict)}
        check(hardware.get('platform')=='Darwin' and gpu.get('status')=='observed' and bool(device_names),'Mac GPU inventory unavailable')
        ram = hardware.get('physical_ram_bytes',{})
        check(ram.get('status')=='observed' and integer(ram.get('value'),1),'Physical RAM unavailable')
        check(inventory.get('capacity_kind')=='hardware_totals' and inventory.get('placement_ready') is False,'Inventory capacity interpretation changed')
        recorded = campaign.get('windows')
        if not isinstance(recorded,list): raise ValueError('Campaign windows must be list')
        planned_ids = [w['window_id'] for w in plan['windows']]
        recorded_ids = [w.get('window_id') for w in recorded]
        check(recorded_ids==planned_ids[:len(recorded_ids)],'Campaign order/duplicate/extra windows')
        unrun = [name for name in planned_ids if name not in recorded_ids]
        check(campaign.get('unrun_window_ids')==unrun,'Unrun denominator identities mismatch')
        check(not unrun and len(recorded)==24,'Campaign incomplete')
        output['unrun_window_ids'] = unrun
        expected = {n:expected_hash(n) for n in (256,512,1024)}
        output['expected_output_sha256'] = {str(n):h for n,h in expected.items()}
        metadata_by_id = {m.get('window_id'):m for m in recorded}
        previous_execution_finish = None
        for w in plan['windows']:
            entry = metadata_by_id.get(w['window_id'])
            if entry is None:
                windows.append(dict(w,planned_jobs=60,reported_jobs=0,released_jobs=0,independently_correct_jobs=0,
                                    on_time_successes=0,on_time_fraction=0,planned_warmups=3,independently_correct_warmups=0,
                                    checks_passed=False,latency_complete=False,errors=['Window unrun'],power=[])); continue
            errs = []
            folder_name = f"w{w['index']:02d}_{w['window_id']}"
            for key in ('window_id','index','round','rate','concurrency'):
                if entry.get(key)!=w[key]: errs.append('Campaign metadata differs: '+key)
            if entry.get('folder')!=folder_name: errs.append('Wrong window folder')
            folder = capture/folder_name
            try:
                execution,raw = load(folder/'EXECUTION.json'),load(folder/'RAW.json')
                result = audit_window(raw,w,plan,expected,device_names)
                for key in ('window_id','round','rate','concurrency'):
                    if execution.get(key)!=w[key]: errs.append('Execution metadata differs: '+key)
                if execution.get('freeze_sha256')!=frozen_sha or execution.get('source_changed') is not False: errs.append('Execution source/freeze mismatch')
                if execution.get('returncode')!=0 or type(execution.get('returncode')) is not int or execution.get('process_status')!='completed': errs.append('Execution failed/incomplete')
                if execution.get('raw_output_present') is not True or execution.get('raw_gate_passed') is not True: errs.append('Execution does not confirm valid raw output')
                if execution.get('independent_window_checks_passed') is not True or execution.get('independent_window_errors')!=[]: errs.append('Execution window-check record disagrees with success')
                if execution.get('diagnostic_interrupted') is not False: errs.append('Diagnostic interruption or missing status')
                if entry.get('status')!='completed' or entry.get('returncode')!=0: errs.append('Campaign entry not successful')
                if not interval_utc(execution,'started_utc','finished_utc'):
                    errs.append('Execution UTC interval invalid')
                else:
                    start_utc=datetime.fromisoformat(execution['started_utc'].replace('Z','+00:00'))
                    finish_utc=datetime.fromisoformat(execution['finished_utc'].replace('Z','+00:00'))
                    if previous_execution_finish is not None and (start_utc-previous_execution_finish).total_seconds()+plan['time_consistency_tolerance_seconds']<plan['inter_window_idle_seconds']:
                        errs.append('Inter-window process gap shorter than prescribed idle')
                    previous_execution_finish=finish_utc
                if not finite(execution.get('process_elapsed_seconds')): errs.append('Execution duration invalid')
                if not finite(execution.get('timeout_seconds')) or not 0<execution['timeout_seconds']<=plan['window_timeout_seconds']: errs.append('Execution timeout invalid')
                command = execution.get('command',[])
                if (not isinstance(command,list) or len(command)!=7 or command[1:5]!=['--concurrency',str(w['concurrency']),'--rate',str(w['rate'])]
                    or command[5]!='--output' or Path(command[6]).name!='RAW.json'): errs.append('Native command differs')
                result['power'] = [power(execution.get(when,{}).get('batt')) for when in ('before','after')]
                result['input_sha256'] = {'RAW.json':sha(folder/'RAW.json'),'EXECUTION.json':sha(folder/'EXECUTION.json')}
                result['errors'].extend(errs); result['checks_passed'] = not result['errors']
            except (OSError,ValueError,TypeError,KeyError,AttributeError) as exc:
                result = dict(w,planned_jobs=60,reported_jobs=0,released_jobs=0,independently_correct_jobs=0,
                              on_time_successes=0,on_time_fraction=0,planned_warmups=3,independently_correct_warmups=0,
                              checks_passed=False,latency_complete=False,errors=errs+[type(exc).__name__+': '+str(exc)],power=[])
            windows.append(result)
        output.update(paired_gates(windows,plan,not errors and all(w['checks_passed'] for w in windows)))
        output['reported_measured_jobs'] = sum(w['reported_jobs'] for w in windows)
        output['released_measured_jobs'] = sum(w['released_jobs'] for w in windows)
        output['independently_correct_measured_jobs'] = sum(w['independently_correct_jobs'] for w in windows)
        output['on_time_successes_out_of_1440'] = sum(w['on_time_successes'] for w in windows)
        output['independently_correct_warmups'] = sum(w['independently_correct_warmups'] for w in windows)
    except (OSError,ValueError,TypeError,KeyError,AttributeError) as exc:
        errors.append(type(exc).__name__+': '+str(exc))
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True,help='New JSON file; never overwritten')
    parser.add_argument('--binary',type=Path,help='Optional exact collected executable hash check')
    args = parser.parse_args()
    if args.output.exists(): parser.error('Output already exists')
    result = analyze(Path(__file__).resolve().parent,args.capture,args.binary)
    with args.output.open('x') as handle:
        json.dump(result,handle,indent=2,sort_keys=True,allow_nan=False); handle.write('\n')
    print(json.dumps({'validity_passed':result['validity_passed'],'promotion_gate_passed':result['promotion_gate_passed'],
                      'outcome':result.get('outcome','invalid_or_incomplete'),'output':str(args.output)}))
    return 0 if result['validity_passed'] else 1


if __name__=='__main__': raise SystemExit(main())
