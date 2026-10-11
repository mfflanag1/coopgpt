#!/usr/bin/env python3
"""Validate retained single-host measurement evidence, never deployment readiness."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
from telemetry import integrate_energy

SHA = re.compile(r'[0-9a-f]{64}')
PIN = re.compile(r'[0-9a-f]{40}|[0-9a-f]{64}')
COLLECTION_SETTINGS = ('concurrency','idle_seconds','poll_seconds','max_gap_seconds','max_read_seconds','request_timeout_s','drain_timeout_s')
CONSISTENCY_ABSOLUTE_J = 1.0
CONSISTENCY_RELATIVE = 0.20
PLACEHOLDERS = {'unknown', 'todo', 'tbd', 'change_me', 'changeme', 'placeholder', 'latest', 'main', 'master', 'your_value', 'unavailable'}

def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)

def nonnegative_integer(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0

def concrete(value):
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().lower() not in PLACEHOLDERS and not any(x in value for x in ('<', '>', 'CHANGE_ME', 'YOUR_'))
    if isinstance(value, dict):
        return all(concrete(v) for v in value.values())
    if isinstance(value, list):
        return all(concrete(v) for v in value)
    return value is None or isinstance(value, (bool, int, float)) and (not isinstance(value, float) or math.isfinite(value))

def read_jsonl(path):
    rows=[]
    with path.open() as f:
        for line_no, line in enumerate(f,1):
            if line.strip():
                row=json.loads(line)
                if not isinstance(row,dict):
                    raise ValueError(f'{path.name}:{line_no}: expected object')
                rows.append(row)
    return rows

def summary(values):
    values=sorted(values)
    if not values:return {'n':0,'mean':None,'p50':None,'p95':None,'maximum':None}
    return {'n':len(values),'mean':sum(values)/len(values),'p50':values[math.ceil(.5*len(values))-1],
            'p95':values[math.ceil(.95*len(values))-1],'maximum':values[-1]}

def _hardware(metadata):
    if isinstance(metadata,dict):
        boards=metadata.get('boards',[])
        driver=metadata.get('driver_version')
    elif isinstance(metadata,list):
        boards=metadata
        driver=[b.get('driver_version') for b in boards if isinstance(b,dict)]
    else:
        return [],None
    return boards,driver

def validate_bundle(directory):
    directory=Path(directory)
    failures=[]
    report={'bundle':str(directory),'data_quality_pass':False,'measured_data_ready':False,
            'deployment_gate':False,'forecast_calibration_gate':False,'failures':failures,
            'attestation_limits':['Checkpoint, tokenizer, quantization, launch arguments and container are operator attestations; endpoint labels do not verify loaded artifacts.',
             'This validator checks recorded evidence and cannot authenticate the physical origin of a bundle.',
             'No per-request GPU energy or server token-generation timestamps are inferred.',
             'Observed compute PID residency is matched to operator-declared worker PIDs; serving roles and loaded checkpoint identity remain attestations.']}
    def check(condition,message):
        if not condition:failures.append(message)
        return bool(condition)
    try:
        run=json.loads((directory/'run.json').read_text())
        trace_raw=(directory/'trace.jsonl').read_bytes()
        trace=read_jsonl(directory/'trace.jsonl')
        requests=read_jsonl(directory/'requests.jsonl')
        power=read_jsonl(directory/'power.jsonl')
        if not isinstance(run,dict):raise ValueError('run.json must be an object')
    except (OSError,ValueError,TypeError) as exc:
        failures.append(f'Bundle parse failure: {exc}')
        return report
    check(run.get('schema_version')==1,'Unsupported/missing schema_version')
    kind=run.get('evidence_kind')
    check(kind in ('hardware_collection','synthetic_fixture'),'Unknown evidence_kind')
    report['evidence_kind']=kind
    config=run.get('config',{})
    if not isinstance(config,dict):config={};check(False,'config must be an object')
    check(run.get('config_sha256')==canonical_sha(config),'config_sha256 mismatch')
    trace_hash=hashlib.sha256(trace_raw).hexdigest()
    check(run.get('trace_sha256')==trace_hash,'trace_sha256 mismatch')
    report['trace_sha256']=trace_hash
    for key in ('config_id','workload_provenance'):
        check(key in config and concrete(config[key]) and config[key] not in (None,{},[]),f'Missing/template config.{key}')
    check(concrete(config),'Unknown/template value in config')
    model=config.get('model',{})
    if not isinstance(model,dict):model={}
    for key in ('id','revision','tokenizer_revision','dtype','quantization'):
        check(key in model,f'Missing model.{key}')
    check(isinstance(model.get('id'),str) and concrete(model.get('id')),'Invalid model.id')
    for key in ('revision','tokenizer_revision'):
        check(isinstance(model.get(key),str) and bool(PIN.fullmatch(model[key])),f'model.{key} must be immutable 40/64-hex revision')
    check(isinstance(model.get('dtype'),str) and concrete(model.get('dtype')),'Missing/invalid model.dtype')
    check(isinstance(model.get('quantization'),str) and concrete(model['quantization']),'Quantization must be a concrete string; use none for disabled')
    engine=config.get('engine',{})
    if not isinstance(engine,dict):engine={}
    check(engine.get('name')=='vllm','Engine must be vllm')
    check(isinstance(engine.get('version'),str) and concrete(engine['version']),'Missing engine.version')
    digest=engine.get('container_digest','')
    check(isinstance(digest,str) and bool(re.fullmatch(r'(?:[^\s]+@)?sha256:[0-9a-f]{64}',digest)),'Missing/invalid immutable container digest')
    launch=engine.get('launch_config',{})
    if not isinstance(launch,dict):launch={}
    for key in ('tensor_parallel_size','pipeline_parallel_size','enable_prefix_caching','cpu_offload_gb','speculative_config','enable_chunked_prefill','max_model_len'):
        check(key in launch,f'Missing engine.launch_config.{key}')
    for key in ('tensor_parallel_size','pipeline_parallel_size'):
        check(nonnegative_integer(launch.get(key)) and launch.get(key,0)>0,f'Invalid launch {key}')
    check(launch.get('enable_prefix_caching') is False,'Prefix caching must be disabled for the initial prospective contract')
    check(isinstance(launch.get('enable_chunked_prefill'),bool),'Chunked-prefill policy must be explicit boolean')
    check(nonnegative_integer(launch.get('max_model_len')) and launch.get('max_model_len',0)>0,'Invalid max_model_len')
    check(finite(launch.get('cpu_offload_gb')) and launch.get('cpu_offload_gb',-1)>=0,'CPU offload must be explicit nonnegative GB')
    uuids=config.get('gpu_uuids',[])
    valid_uuids=isinstance(uuids,list) and bool(uuids) and all(isinstance(x,str) and x.startswith('GPU-') for x in uuids) and len(set(uuids))==len(uuids)
    check(valid_uuids,'GPU list must contain unique explicit full-board GPU- UUIDs')
    if not valid_uuids:uuids=[]
    workers=config.get('server_gpu_worker_pids')
    valid_workers=isinstance(workers,dict) and set(workers)==set(uuids) and bool(uuids)
    if isinstance(workers,dict):
        for gpu,pids in workers.items():
            good=isinstance(pids,list) and bool(pids) and all(nonnegative_integer(pid) and pid>0 for pid in pids)
            good=good and len(set(pids))==len(pids)
            check(good,f'Invalid operator worker PID list for {gpu}')
            valid_workers=valid_workers and good
    check(valid_workers,'server_gpu_worker_pids must map every selected GPU to a nonempty unique positive PID list')
    decoding=config.get('decoding',{})
    if not isinstance(decoding,dict):decoding={}
    check(finite(decoding.get('temperature')) and decoding['temperature']==0,'Temperature must be explicitly zero')
    check(nonnegative_integer(decoding.get('max_tokens')) and decoding.get('max_tokens',0)>0,'Invalid max_tokens')
    check(isinstance(decoding.get('seed'),int) and not isinstance(decoding.get('seed'),bool),'Missing integer decoding seed')
    check(isinstance(decoding.get('ignore_eos'),bool),'Missing boolean ignore_eos')
    probe=run.get('engine_probe',{})
    if not isinstance(probe,dict):probe={}
    version=probe.get('version',{})
    live_version=version.get('version') if isinstance(version,dict) else None
    check(isinstance(live_version,str) and live_version.lstrip('v')==str(engine.get('version','')).lstrip('v'),'Live /version mismatch or missing')
    models=probe.get('models',{})
    listed=models.get('data',[]) if isinstance(models,dict) else []
    if not isinstance(listed,list):listed=[]
    check(len(listed)==1 and isinstance(listed[0],dict) and listed[0].get('id')==model.get('id'),'Live /v1/models must contain exactly the one declared model')
    for key in ('quiescence_before','quiescence_after_warmup','quiescence_after_workload'):
        check(probe.get(key) is True,f'Missing/failed {key}')
    check(run.get('warmup_ok') is True,'Warmup unsuccessful or unconfirmed')
    check(run.get('collector_errors')==[],'Collector errors or missing collector_errors list')
    check(run.get('clock')=={'kind':'time.monotonic','domain':'single_local_host','unit':'seconds'},'Clock must be one local monotonic seconds domain')
    boards,driver=_hardware(run.get('hardware'))
    check(isinstance(boards,list) and bool(boards),'Missing NVML hardware evidence')
    if not isinstance(boards,list):boards=[]
    observed_uuids=[b.get('gpu_uuid') for b in boards if isinstance(b,dict)]
    check(all(isinstance(x,str) for x in observed_uuids) and len(observed_uuids)==len(boards)==len(uuids) and set(observed_uuids)==set(uuids),'Hardware UUID inventory mismatch')
    check(concrete(driver) and bool(driver) and (isinstance(driver,str) or isinstance(driver,list) and all(isinstance(x,str) and x for x in driver)),'Missing concrete driver version')
    for board in boards:
        if not isinstance(board,dict):check(False,'Malformed hardware board');continue
        check(isinstance(board.get('name'),str) and concrete(board['name']),'Missing GPU model name')
        check(nonnegative_integer(board.get('memory_total_bytes')) and board.get('memory_total_bytes',0)>0,'Missing positive GPU memory')
        check(finite(board.get('power_limit_w')) and board.get('power_limit_w',0)>0,'Missing observed power limit')
    report['hardware_observed']=boards
    settings=run.get('settings',{})
    if not isinstance(settings,dict):settings={}
    for key in ('idle_seconds','poll_seconds','max_gap_seconds','max_read_seconds','request_timeout_s','drain_timeout_s'):
        check(finite(settings.get(key)) and settings.get(key,0)>0,f'Invalid settings.{key}')
    check(nonnegative_integer(settings.get('concurrency')) and settings.get('concurrency',0)>0,'Invalid concurrency')
    report['operator_collection_settings']={key:settings.get(key) for key in COLLECTION_SETTINGS}
    report['telemetry_threshold_scope']='Polling, gap/read and timeout settings are operator-selected acceptance limits, not objective sensor accuracy, latency or measurement-completeness guarantees.'
    windows=run.get('windows',{})
    valid_windows=isinstance(windows,dict)
    parsed={}
    for key in ('idle_before','workload','idle_after','total'):
        w=windows.get(key) if isinstance(windows,dict) else None
        good=isinstance(w,list) and len(w)==2 and all(finite(t) for t in w) and w[1]>w[0]
        check(good,f'Invalid window {key}')
        valid_windows=valid_windows and good
        if good:parsed[key]=w
    if valid_windows:
        a,b=parsed['idle_before'];b2,c=parsed['workload'];c2,d=parsed['idle_after'];a2,d2=parsed['total']
        check(all(math.isclose(x,y,rel_tol=0,abs_tol=1e-8) for x,y in ((a,a2),(b,b2),(c,c2),(d,d2))),'Windows must be contiguous and total exactly bracket phases')
        if finite(settings.get('idle_seconds')):
            check(b-a+1e-6>=settings['idle_seconds'] and d-c+1e-6>=settings['idle_seconds'],'Resident idle interval shorter than declared')
    else:b=c=None
    trace_by_id={}
    for idx,item in enumerate(trace):
        ident=item.get('request_id')
        good=isinstance(ident,str) and bool(ident)
        check(good,f'Trace row {idx} missing ID')
        if not good:continue
        check(ident not in trace_by_id,f'Duplicate trace ID {ident}')
        trace_by_id[ident]=item
        check(isinstance(item.get('prompt'),str),f'Trace {ident} missing prompt string')
        check(finite(item.get('arrival_offset_s')) and item.get('arrival_offset_s',-1)>=0,f'Invalid arrival offset for {ident}')
    check(bool(trace_by_id),'Empty offered trace')
    req_ids=[r.get('request_id') for r in requests]
    check(all(isinstance(x,str) and x for x in req_ids),'Request records require IDs')
    check(len(set(x for x in req_ids if isinstance(x,str)))==len(req_ids),'Duplicate/malformed request IDs')
    check(set(x for x in req_ids if isinstance(x,str))==set(trace_by_id) and len(requests)==len(trace),'Request IDs must match every offered trace ID exactly once')
    latencies=[];first_content=[];chunk_gaps=[];tpot=[];succeeded=0;failed=0;unsent=0;slo_success=0
    per_request=[]
    slo=config.get('slo')
    slo_keys=('response_seconds','first_content_seconds','client_tpot_seconds')
    if slo is not None:
        check(isinstance(slo,dict) and bool(slo),'slo must be a nonempty object')
        if not isinstance(slo,dict):slo=None
        else:
            check(set(slo)<=set(slo_keys),'Unknown SLO field')
            for key,value in slo.items():check(finite(value) and value>0,f'Invalid SLO threshold {key}')
    for r in requests:
        ident=r.get('request_id');source=trace_by_id.get(ident) if isinstance(ident,str) else None
        status=r.get('status')
        check(status in ('ok','error','not_dispatched'),f'{ident}: unknown status')
        failed+=status=='error';unsent+=status=='not_dispatched'
        scheduled=r.get('scheduled_monotonic');dispatch=r.get('dispatch_monotonic');finish=r.get('finish_monotonic')
        check(finite(scheduled),f'{ident}: invalid scheduled timestamp')
        if source and isinstance(source.get('prompt'),str):
            check(r.get('prompt_sha256')==hashlib.sha256(source['prompt'].encode()).hexdigest(),f'{ident}: prompt hash mismatch')
            if b is not None and finite(source.get('arrival_offset_s')) and finite(scheduled):
                check(math.isclose(scheduled,b+source['arrival_offset_s'],rel_tol=0,abs_tol=1e-6),f'{ident}: scheduled arrival mismatch')
        if status=='not_dispatched':
            check(dispatch is None,f'{ident}: not_dispatched has dispatch timestamp')
        else:
            check(finite(dispatch) and finite(scheduled) and dispatch>=scheduled-1e-6,f'{ident}: invalid dispatch order')
        check(finite(finish),f'{ident}: missing terminal outcome timestamp')
        if finite(dispatch) and finite(finish):check(finish>=dispatch,f'{ident}: finish precedes dispatch')
        if b is not None:
            if finite(dispatch):check(b-1e-6<=dispatch<=c+1e-6,f'{ident}: dispatch outside workload/drain interval')
            if finite(finish):check(b-1e-6<=finish<=c+1e-6,f'{ident}: terminal outcome outside workload/drain interval')
        events=r.get('chunk_events')
        check(isinstance(events,list),f'{ident}: missing chunk list')
        times=[]
        if isinstance(events,list):
            for event in events:
                if not isinstance(event,dict):check(False,f'{ident}: malformed chunk');continue
                t=event.get('received_monotonic');chars=event.get('chars')
                check(finite(t),f'{ident}: invalid chunk time')
                check(nonnegative_integer(chars) and chars>0,f'{ident}: chunks must contain positive observed characters')
                if finite(t):times.append(t)
            check(all(x<=y for x,y in zip(times,times[1:])),f'{ident}: nonmonotone chunk order')
            if times and finite(dispatch) and finite(finish):check(dispatch<=times[0]<=times[-1]<=finish,f'{ident}: chunks outside request interval')
        first=r.get('first_content_monotonic');last=r.get('last_content_monotonic')
        if times:
            check(finite(first) and finite(last) and first==times[0] and last==times[-1],f'{ident}: first/last content mismatch')
        else:check(first is None and last is None,f'{ident}: content time without chunk evidence')
        usage=r.get('usage')
        valid_usage=isinstance(usage,dict) and all(nonnegative_integer(usage.get(k)) for k in ('prompt_tokens','completion_tokens'))
        if usage is not None:check(valid_usage,f'{ident}: invalid server usage counts')
        if status=='ok':
            succeeded+=1
            check(r.get('http_status')==200,f'{ident}: successful request lacks HTTP 200')
            check(isinstance(r.get('finish_reason'),str) and bool(r['finish_reason']),f'{ident}: successful stream lacks finish reason')
            check(valid_usage,f'{ident}: successful request missing server usage')
            check(isinstance(r.get('output_sha256'),str) and bool(SHA.fullmatch(r['output_sha256'])),f'{ident}: successful output hash missing')
            check(r.get('error') in (None,''),f'{ident}: successful request contains error')
        else:check(bool(r.get('error')),f'{ident}: failed/unsent request lacks explanation')
        e2e=finish-scheduled if finite(finish) and finite(scheduled) and status!='not_dispatched' else None
        fc=first-scheduled if finite(first) and finite(scheduled) else None
        avg=(last-first)/(usage['completion_tokens']-1) if valid_usage and usage['completion_tokens']>1 and finite(first) and finite(last) else None
        if status=='ok':
            if e2e is not None:latencies.append(e2e)
            if fc is not None:first_content.append(fc)
            if avg is not None:tpot.append(avg)
            chunk_gaps.extend(y-x for x,y in zip(times,times[1:]))
        metrics={'response_seconds':e2e,'first_content_seconds':fc,'client_tpot_seconds':avg}
        meets=None
        if isinstance(slo,dict) and slo:
            meets=status=='ok' and all(finite(limit) and metrics.get(key) is not None and metrics[key]<=limit for key,limit in slo.items())
            slo_success+=bool(meets)
        per_request.append({'request_id':ident,'status':status,**metrics,'meets_configured_slo':meets})
    offered=len(trace)
    report['metrics']={'offered_requests':offered,'successful_requests':succeeded,'failed_requests':failed,'not_dispatched_requests':unsent,
        'successful_fraction_of_offered':succeeded/offered if offered else None,
        'slo_evaluated':bool(slo),'slo_successful_requests':slo_success if slo else None,
        'slo_success_fraction_of_offered':slo_success/offered if slo and offered else None,
        'successful_client_response_seconds':summary(latencies),'successful_client_first_content_seconds':summary(first_content),
        'successful_inter_content_chunk_gap_seconds':summary(chunk_gaps),'successful_client_average_output_token_proxy_seconds':summary(tpot),
        'token_proxy_warning':'(last content receipt - first content receipt)/(server completion_tokens - 1), not measured individual token times; stream chunks can contain multiple tokens.',
        'per_request':per_request}
    energy={}
    if valid_windows and uuids and all(finite(settings.get(k)) and settings[k]>0 for k in ('max_gap_seconds','max_read_seconds')):
        for phase,window in parsed.items():
            try:energy[phase]=integrate_energy(power,*window,uuids,max_gap_seconds=settings['max_gap_seconds'],max_read_seconds=settings['max_read_seconds'])
            except (ValueError,TypeError,KeyError) as exc:check(False,f'{phase} energy invalid: {exc}')
        if len(energy)==4:
            summed=sum(energy[k]['aggregate_board_energy_j'] for k in ('idle_before','workload','idle_after'))
            total=energy['total']['aggregate_board_energy_j']
            check(math.isclose(summed,total,rel_tol=1e-9,abs_tol=1e-6),'Phase energy does not reconcile to total')
            energy['resident_idle_average_w']={k:energy[k]['aggregate_board_energy_j']/energy[k]['duration_seconds'] for k in ('idle_before','idle_after')}
            energy['phase_accounting_note']='Phase/idle estimates are diagnostics, not separately validated by the TOTAL consistency screen; counter update granularity can shift energy across phase boundaries.'
    consistency={'scope':'Full TOTAL window only, per selected GPU, for this resident-compute collection contract.',
        'absolute_floor_j':CONSISTENCY_ABSOLUTE_J,'relative_fraction_of_power_integral':CONSISTENCY_RELATIVE,
        'rule':'Positive selected energy and power integral; when available, positive counter energy with absolute counter-power difference <= max(1 J, 20% of power integral).',
        'interpretation':'Fixed conservative data-quality screen; not a calibration, sensor-error bound or statistical confidence guarantee.',
        'per_gpu':{}}
    if 'total' in energy:
        for gpu,measurement in energy['total']['per_gpu'].items():
            selected_energy=measurement['energy_j']
            power_integral=measurement['power_integral_j']
            counter_energy=measurement['counter_energy_j']
            check(selected_energy>0,f'{gpu}: TOTAL selected energy must be positive for resident-compute collection')
            check(power_integral>0,f'{gpu}: TOTAL reported-power integral must be positive')
            threshold=max(CONSISTENCY_ABSOLUTE_J,CONSISTENCY_RELATIVE*power_integral)
            delta=None if counter_energy is None else abs(counter_energy-power_integral)
            if counter_energy is not None:
                check(counter_energy>0,f'{gpu}: TOTAL cumulative counter is nonpositive or stuck')
                check(delta<=threshold,f'{gpu}: TOTAL counter-power inconsistency exceeds fixed conservative screening threshold')
            consistency['per_gpu'][gpu]={'selected_energy_j':selected_energy,'power_integral_j':power_integral,
                'counter_energy_j':counter_energy,'absolute_difference_j':delta,'allowed_difference_j':threshold,
                'counter_comparison_applied':counter_energy is not None}
    report['total_energy_consistency_screen']=consistency
    process_samples=0
    if valid_windows and uuids:
        total_start,total_end=parsed['total']
        selected_process_samples=[sample for sample in power if finite(sample.get('sample_monotonic')) and total_start<=sample['sample_monotonic']<=total_end]
        process_samples=len(selected_process_samples)
        check(process_samples>0,'No observed total-window sample establishes declared GPU worker residency')
        for sample in selected_process_samples:
            rows=sample.get('readings')
            if not isinstance(rows,list):
                check(False,'Total-window sample lacks compute-process readings');continue
            board_rows={}
            for reading in rows:
                if isinstance(reading,dict) and isinstance(reading.get('gpu_uuid'),str):
                    board_rows.setdefault(reading['gpu_uuid'],[]).append(reading)
            check(set(board_rows)==set(uuids) and all(len(v)==1 for v in board_rows.values()),'Total-window compute-process board inventory mismatch')
            for gpu in uuids:
                matching=board_rows.get(gpu,[])
                if len(matching)!=1:continue
                reading=matching[0]
                check(reading.get('compute_process_status')=='ok',f'{gpu}: compute-process inspection missing, unsupported or failed')
                pids=reading.get('compute_process_ids')
                valid_observed=isinstance(pids,list) and all(nonnegative_integer(pid) and pid>0 for pid in pids)
                valid_observed=valid_observed and len(set(pids))==len(pids)
                check(valid_observed,f'{gpu}: invalid observed compute PID list')
                if valid_observed and valid_workers:
                    check(set(pids)==set(workers[gpu]),f'{gpu}: observed compute PIDs differ from declared server workers')
    report['gpu_worker_residency']={'total_window_samples_checked':process_samples,'operator_declared_pid_mapping':workers,
        'scope':'Exact observed compute PID sets across the TOTAL window, including both idle phases and workload/completion/drain; process-to-serving-role and checkpoint associations remain operator attestations.'}
    report['energy']=energy
    report['data_quality_pass']=not failures
    report['measured_data_ready']=not failures and kind=='hardware_collection'
    report['readiness_reason']='Recorded hardware collection passes quality checks; compatibility claims still include operator attestations.' if report['measured_data_ready'] else ('Synthetic fixtures cannot establish measured-data readiness.' if kind=='synthetic_fixture' else 'Missing/invalid evidence prevents measured-data readiness.')
    return report

def compare_bundles(first,second):
    left=validate_bundle(first);right=validate_bundle(second)
    reasons=[]
    try:
        a=json.loads((Path(first)/'run.json').read_text());b=json.loads((Path(second)/'run.json').read_text())
        ca=a['config'];cb=b['config']
        if not isinstance(ca,dict) or not isinstance(cb,dict):raise ValueError('Pair configs must be objects')
        for key in ('model','engine','decoding'):
            if ca.get(key)!=cb.get(key):reasons.append(f'Paired {key} mismatch')
        if a.get('trace_sha256')!=b.get('trace_sha256'):reasons.append('Paired complete trace mismatch')
        if ca.get('slo')!=cb.get('slo'):reasons.append('Paired SLO settings mismatch')
        sa=a.get('settings',{});sb=b.get('settings',{})
        if not isinstance(sa,dict) or not isinstance(sb,dict):
            raise ValueError('Pair settings must be objects')
        for setting in COLLECTION_SETTINGS:
            if sa.get(setting)!=sb.get(setting):
                reasons.append(f'Paired collector {setting} mismatch')
        if ca.get('config_id')==cb.get('config_id'):reasons.append('Configuration IDs must differ')
        def fingerprint(run):
            boards,_=_hardware(run.get('hardware'))
            if not isinstance(boards,list) or any(not isinstance(x,dict) for x in boards):raise ValueError('Malformed pair hardware')
            return sorted((x.get('name'),x.get('memory_total_bytes'),x.get('power_limit_w')) for x in boards)
        if fingerprint(a)==fingerprint(b):reasons.append('No observed hardware model/memory/power configuration difference')
    except (OSError,ValueError,TypeError,KeyError) as exc:reasons.append(f'Pair parse failure: {exc}')
    quality=left['data_quality_pass'] and right['data_quality_pass'] and not reasons
    return {'left':left,'right':right,'pair_data_quality_pass':quality,
            'paired_measured_data_ready':quality and left['measured_data_ready'] and right['measured_data_ready'],
            'verified_running_artifact_identity':False,'deployment_gate':False,'forecast_calibration_gate':False,
            'pair_failures':reasons,'scope':'Matched recorded model/engine/decoding attestations and observed configuration differences; no independent proof of loaded model/container identity, forecast calibration, or pooling gains.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path);p.add_argument('--compare',type=Path);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();report=compare_bundles(args.run,args.compare) if args.compare else validate_bundle(args.run)
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:report[k] for k in ('pair_data_quality_pass','paired_measured_data_ready','data_quality_pass','measured_data_ready','deployment_gate') if k in report}))
    return 0 if report.get('pair_data_quality_pass',report.get('data_quality_pass')) else 1
if __name__=='__main__':raise SystemExit(main())
