#!/usr/bin/env python3
"""Collect one local vLLM/NVIDIA configuration; never synthesize missing telemetry.

The model server must already be running. No model launch/download, GPU rental or
remote command is performed. Run on each hardware host with the same trace.
"""
from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def local_url(value):
    parsed = urllib.parse.urlsplit(value)
    if (parsed.scheme != 'http' or parsed.hostname not in ('localhost','127.0.0.1','::1')
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or parsed.path not in ('','/')):
        raise ValueError('Use the root HTTP URL of an existing loopback vLLM server')
    return value.rstrip('/')


def get_json(url):
    with urllib.request.urlopen(url, timeout=5) as response:
        return json.loads(response.read(2_000_001))


def load_trace(path):
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    ids = set()
    for row in rows:
        if (not isinstance(row.get('request_id'), str) or not row['request_id']
                or row['request_id'] in ids or not isinstance(row.get('prompt'), str)
                or not row['prompt']):
            raise ValueError('Trace needs unique IDs and nonempty prompts')
        offset = row.get('arrival_offset_s')
        if isinstance(offset, bool) or not isinstance(offset,(int,float)) or not math.isfinite(offset) or offset < 0:
            raise ValueError('Invalid arrival offset')
        ids.add(row['request_id'])
    if not rows:
        raise ValueError('Empty offered trace')
    return sorted(rows, key=lambda r:(r['arrival_offset_s'],r['request_id']))


def validate_config(config):
    if not config.get('config_id') or not config.get('workload_provenance'):
        raise ValueError('Configuration ID and workload provenance required')
    model, engine = config['model'], config['engine']
    for key in ('revision','tokenizer_revision'):
        if not re.fullmatch('(?:[0-9a-f]{40}|[0-9a-f]{64})',model.get(key,'')):
            raise ValueError('Pin model and tokenizer revision digests')
    if not all(isinstance(model.get(k),str) and model[k] for k in ('id','dtype','quantization')):
        raise ValueError('Model ID, dtype and quantization must be explicit')
    if engine.get('name') != 'vllm' or not engine.get('version'):
        raise ValueError('Collector currently supports an explicitly versioned vLLM server')
    if not re.fullmatch('sha256:[0-9a-f]{64}',engine.get('container_digest','')):
        raise ValueError('Pin the serving container digest')
    required = {'tensor_parallel_size','pipeline_parallel_size','enable_prefix_caching',
                'enable_chunked_prefill','cpu_offload_gb','speculative_config','max_model_len'}
    if not isinstance(engine.get('launch_config'),dict) or not required <= engine['launch_config'].keys():
        raise ValueError('Missing explicit parallelism/cache/offload/speculation launch settings')
    if engine['launch_config']['enable_prefix_caching'] is not False:
        raise ValueError('Disable prefix caching for this prospective collection contract')
    uuids = config['gpu_uuids']
    if not isinstance(uuids,list) or not uuids or len(set(uuids)) != len(uuids) or not all(
            isinstance(x,str) and x.startswith('GPU-') for x in uuids):
        raise ValueError('List each selected full-board GPU UUID exactly once')
    workers = config.get('server_gpu_worker_pids', {})
    if not isinstance(workers,dict) or set(workers) != set(uuids) or any(
            not isinstance(pids,list) or not pids or any(type(pid) is not int or pid<=0 for pid in pids)
            or len(set(pids)) != len(pids) for pids in workers.values()):
        raise ValueError('Declare the serving GPU worker PIDs on every selected board')
    decoding = config['decoding']
    if set(decoding) != {'temperature','max_tokens','seed','ignore_eos'}:
        raise ValueError('Use exactly the frozen decoding fields')
    if decoding['temperature'] != 0 or type(decoding['max_tokens']) is not int or decoding['max_tokens'] <= 0:
        raise ValueError('Use temperature zero and a positive integer generation cap')
    if type(decoding['seed']) is not int or type(decoding['ignore_eos']) is not bool:
        raise ValueError('Explicit integer seed and Boolean ignore_eos required')


def stream_request(base_url, model, decoding, request, scheduled, timeout=120):
    """Preserve observed chunks; a transport chunk is not a model token."""
    result = {'request_id':request['request_id'],
              'prompt_sha256':hashlib.sha256(request['prompt'].encode()).hexdigest(),
              'scheduled_monotonic':scheduled, 'dispatch_monotonic':time.monotonic(),
              'first_content_monotonic':None,'last_content_monotonic':None,
              'finish_monotonic':None,'chunk_events':[], 'usage':None,
              'finish_reason':None,'http_status':None,'status':'error','error':None,
              'output_sha256':None}
    output_hash = hashlib.sha256()
    payload = {'model':model,'prompt':request['prompt'],'stream':True,
               'stream_options':{'include_usage':True}, **decoding}
    body = json.dumps(payload).encode()
    done = False
    try:
        req = urllib.request.Request(base_url+'/v1/completions',data=body,
            headers={'Content-Type':'application/json','Accept':'text/event-stream',
                     'X-Request-Id':request['request_id']})
        # Do not silently truncate slow-prefill requests at a separate 10 s cap.
        # The elapsed deadline is checked between completed lines. Socket
        # timeouts bound inactivity, not total duration; this is no hard SLA.
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result['http_status'] = response.status
            if response.headers.get_content_type() != 'text/event-stream':
                raise ValueError('Expected an SSE response')
            data_lines = []
            for raw_line in response:
                if time.monotonic()-result['dispatch_monotonic'] > timeout:
                    raise TimeoutError('Absolute client request time exceeded')
                line = raw_line.decode('utf-8').rstrip('\r\n')
                if line.startswith(':'):
                    continue
                if line.startswith('data:'):
                    data_lines.append(line[5:].lstrip(' '))
                    continue
                if line or not data_lines:
                    continue
                data = '\n'.join(data_lines)
                data_lines = []
                if data == '[DONE]':
                    done = True
                    break
                event = json.loads(data)
                if event.get('error'):
                    raise ValueError('Server error event: '+str(event['error'])[:300])
                if event.get('usage') is not None:
                    result['usage'] = event['usage']
                choices = event.get('choices',[])
                if len(choices) > 1:
                    raise ValueError('Multiple completions unsupported')
                if choices:
                    choice = choices[0]
                    content = choice.get('text','')
                    if not isinstance(content,str):
                        raise ValueError('Expected text completion chunk')
                    if content:
                        now = time.monotonic()
                        output_hash.update(content.encode())
                        result['chunk_events'].append({'received_monotonic':now,'chars':len(content)})
                        if result['first_content_monotonic'] is None:
                            result['first_content_monotonic'] = now
                        result['last_content_monotonic'] = now
                    if choice.get('finish_reason') is not None:
                        result['finish_reason'] = choice['finish_reason']
            if not done:
                raise ValueError('Truncated SSE stream without [DONE]')
            if result['finish_reason'] not in ('stop','length'):
                raise ValueError('Missing or unsupported completion finish reason')
            usage = result['usage']
            if not isinstance(usage,dict) or any(type(usage.get(k)) is not int or usage[k] < 0
                    for k in ('prompt_tokens','completion_tokens')):
                raise ValueError('Missing valid server-reported token usage')
            if usage['completion_tokens'] > 0 and result['first_content_monotonic'] is None:
                raise ValueError('No visible content for positive output count')
            result['status'] = 'ok'
    except Exception as exc:
        if isinstance(exc,urllib.error.HTTPError):
            result['http_status'] = exc.code
        result['error'] = type(exc).__name__+': '+str(exc)[:500]
    finally:
        result['finish_monotonic'] = time.monotonic()
        result['output_sha256'] = output_hash.hexdigest()
    return result


def wait_until_idle(base_url, timeout):
    """Client termination is not proof of engine drain; require both gauges zero."""
    stop = time.monotonic()+timeout
    observed = []
    while time.monotonic() < stop:
        try:
            with urllib.request.urlopen(base_url+'/metrics',timeout=5) as r:
                text = r.read(10_000_001).decode()
            counts = {'running':[],'waiting':[]}
            for line in text.splitlines():
                match = re.match(r'^vllm:num_requests_(running|waiting)(?:\{[^}]*\})?\s+([0-9.eE+\-]+)(?:\s|$)',line)
                if match:
                    counts[match[1]].append(float(match[2]))
            known = all(counts[k] and all(math.isfinite(x) and x>=0 for x in counts[k])
                        for k in counts)
            idle = known and all(sum(counts[k])==0 for k in counts)
            observed.append({'monotonic':time.monotonic(),'counts':counts,'idle':bool(idle)})
            # Three consecutive observations reduce, but cannot prove absence of,
            # competing clients. Dedicated server/process attestation still matters.
            if len(observed)>=3 and all(x['idle'] for x in observed[-3:]):
                return True, observed
        except Exception as exc:
            observed.append({'monotonic':time.monotonic(),'idle':False,
                             'error':type(exc).__name__+': '+str(exc)[:300]})
        time.sleep(.2)
    return False, observed


def write_json(path, value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def write_jsonl(path, values):
    with path.open('w') as f:
        for value in values:
            f.write(json.dumps(value,allow_nan=False)+'\n')


def collect(config_path, trace_path, output, base_url, *, concurrency=1, idle_seconds=30.,
            poll_seconds=.1, request_timeout=120., drain_timeout=120., backend_factory=None):
    base_url = local_url(base_url)
    config = json.loads(config_path.read_text())
    validate_config(config)
    trace = load_trace(trace_path)
    if type(concurrency) is not int or concurrency<=0:
        raise ValueError('Positive concurrency required')
    if any(not math.isfinite(x) or x<=0 for x in (idle_seconds,poll_seconds,request_timeout,drain_timeout)):
        raise ValueError('Positive finite sampling/idle/time limits required')
    if output.exists():
        raise ValueError('Use a new run directory; never overwrite measurements')
    from telemetry import NVMLBackend, SamplingThread
    # Backend initialization fails explicitly on unsupported hosts. No mock fallback.
    backend = (backend_factory or NVMLBackend)(config['gpu_uuids'])
    simulated = backend_factory is not None
    output.mkdir(parents=True)
    shutil.copyfile(trace_path,output/'trace.jsonl')
    run = {'schema_version':1,'evidence_kind':'synthetic_fixture' if simulated else 'hardware_collection',
           'config':config,'config_sha256':canonical_hash(config),
           'trace_sha256':hashlib.sha256(trace_path.read_bytes()).hexdigest(),
           'engine_probe':{},'hardware':backend.metadata,
           'clock':{'kind':'time.monotonic','domain':'single_local_host','unit':'seconds'},
           'windows':{},'collector_errors':[],'warmup_ok':False,
           'settings':{'idle_seconds':idle_seconds,'poll_seconds':poll_seconds,
                       'max_gap_seconds':max(1.,poll_seconds*5),'max_read_seconds':.5,
                       'concurrency':concurrency,'request_timeout_s':request_timeout,
                       'drain_timeout_s':drain_timeout}}
    sampler = SamplingThread(backend.read, interval_seconds=poll_seconds,
                             close_callable=backend.close)
    records, warmups, futures = [], [], []
    sampler_started = False
    try:
        run['engine_probe']['version'] = get_json(base_url+'/version')
        run['engine_probe']['models'] = get_json(base_url+'/v1/models')
        if run['engine_probe']['version'].get('version') != config['engine']['version']:
            raise ValueError('Live vLLM version differs from operator manifest')
        model_ids = [m.get('id') for m in run['engine_probe']['models'].get('data',[])]
        if model_ids != [config['model']['id']]:
            raise ValueError('Require one dedicated served model matching the manifest')
        for phase in ('before','after_warmup'):
            if phase == 'after_warmup':
                for idx in range(3):
                    job = {**trace[0],'request_id':'warmup-'+str(idx)}
                    warmups.append(stream_request(base_url,config['model']['id'],config['decoding'],
                                                  job,time.monotonic(),request_timeout))
                run['warmup_ok'] = all(r['status']=='ok' for r in warmups)
                if not run['warmup_ok']:
                    raise ValueError('Warmup failed; preserve records but reject collection')
            idle, checks = wait_until_idle(base_url,drain_timeout)
            run['engine_probe']['quiescence_'+phase] = idle
            run['engine_probe']['quiescence_'+phase+'_observations'] = checks
            if not idle:
                raise ValueError('Unknown or nonquiescent server '+phase)
        sampler.start()
        sampler_started = True
        if not sampler.wait_for_first_sample(timeout=5):
            raise TimeoutError('Initial telemetry sample did not arrive')
        # Extra bracketing sample on each side supports interpolation at boundaries.
        time.sleep(max(.1,2*poll_seconds))
        a = time.monotonic()
        time.sleep(idle_seconds)
        b = time.monotonic()
        run['windows']['idle_before'] = [a,b]
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            for request in trace:
                scheduled = b+request['arrival_offset_s']
                time.sleep(max(0.,scheduled-time.monotonic()))
                future = pool.submit(stream_request,base_url,config['model']['id'],
                                     config['decoding'],request,scheduled,request_timeout)
                futures.append((request['request_id'],future))
            records = [f.result() for _, f in futures]
        idle, checks = wait_until_idle(base_url,drain_timeout)
        run['engine_probe']['quiescence_after_workload'] = idle
        run['engine_probe']['quiescence_after_workload_observations'] = checks
        c = time.monotonic()
        run['windows']['workload'] = [b,c]
        time.sleep(idle_seconds)
        d = time.monotonic()
        run['windows']['idle_after'] = [c,d]
        run['windows']['total'] = [a,d]
        if not idle:
            run['collector_errors'].append('Server drain not verified; complete-window accounting invalid')
        time.sleep(max(.1,2*poll_seconds))
    except Exception as exc:
        run['collector_errors'].append(type(exc).__name__+': '+str(exc)[:1000])
    finally:
        try:
            if sampler_started:
                samples = sampler.stop(timeout=max(10.,poll_seconds*3))
            else:
                backend.close()
                samples = []
        except Exception as exc:
            run['collector_errors'].append('Telemetry cleanup: '+type(exc).__name__+': '+str(exc))
            samples = sampler.records
        represented = {r['request_id'] for r in records}
        for ident, future in futures:
            if ident not in represented and future.done() and not future.cancelled():
                try:
                    records.append(future.result())
                    represented.add(ident)
                except Exception as exc:
                    run['collector_errors'].append('Request record unavailable: '+str(exc))
        submitted = {ident for ident, _ in futures}
        for request in trace:
            if request['request_id'] not in represented:
                records.append({'request_id':request['request_id'],
                                'status':'error' if request['request_id'] in submitted else 'not_dispatched',
                                'error':'Collection aborted before a terminal record was available',
                                'prompt_sha256':hashlib.sha256(request['prompt'].encode()).hexdigest(),
                                'finish_monotonic':time.monotonic()})
        write_jsonl(output/'requests.jsonl',records)
        write_jsonl(output/'warmup.jsonl',warmups)
        write_jsonl(output/'power.jsonl',samples)
        write_json(output/'run.json',run)
    return run


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config',type=Path,required=True)
    ap.add_argument('--trace',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--concurrency',type=int,default=1)
    ap.add_argument('--idle-seconds',type=float,default=30.)
    ap.add_argument('--poll-seconds',type=float,default=.1)
    ap.add_argument('--request-timeout',type=float,default=120.)
    ap.add_argument('--drain-timeout',type=float,default=120.)
    args = ap.parse_args()
    run = collect(args.config,args.trace,args.output,args.base_url,
                  concurrency=args.concurrency,idle_seconds=args.idle_seconds,
                  poll_seconds=args.poll_seconds,request_timeout=args.request_timeout,
                  drain_timeout=args.drain_timeout)
    print(json.dumps({'output':str(args.output),'errors':run['collector_errors'],
                      'evidence_kind':run['evidence_kind']}))
    if run['collector_errors']:
        raise SystemExit(1)
