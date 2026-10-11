#!/usr/bin/env python3
"""Continue the fixed pilot after its preserved pre-window-2 socket-probe abort."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import time
import urllib.request
from client import run_trace

BASE=Path(__file__).resolve().parent
MODEL='llama3.2:3b'
DIGEST='a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72'
PORT=11561
URL='http://127.0.0.1:'+str(PORT)
ORIGINAL='http://127.0.0.1:11434'
OPTIONS=dict(temperature=0,seed=0,num_predict=64,num_ctx=2048)
ORDER=(1,2,2,1,1,2,2,1)
WARMUPS=[dict(request_id='warm1',prompt='Describe a blue triangle and a red circle in a detailed paragraph.',arrival_offset_s=0),
         dict(request_id='warm2',prompt='Explain why a wooden chair can have four legs in a detailed paragraph.',arrival_offset_s=0)]

def write(path,obj):path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')

def api(url,path,body=None,timeout=5):
    r=urllib.request.Request(url+path,data=None if body is None else json.dumps(body).encode(),
                             headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(r,timeout=timeout) as response:return json.load(response)

def state():
    power=subprocess.run(['/usr/bin/pmset','-g','batt'],capture_output=True,text=True).stdout
    thermal=subprocess.run(['/usr/bin/pmset','-g','therm'],capture_output=True,text=True).stdout
    return dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                power=re.sub(r'\(id=\d+\)','(id=REDACTED)',power).strip(),
                thermal=thermal.strip(),load_average=list(os.getloadavg()))

def check_lock():
    freeze=json.loads((BASE/'PROTOCOL_FREEZE.json').read_text())
    for name,digest in freeze['sha256'].items():
        if hashlib.sha256((BASE/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('Frozen input changed: '+name)
    manifest=Path.home()/'.ollama/models/manifests/registry.ollama.ai/library/llama3.2/3b'
    if hashlib.sha256(manifest.read_bytes()).hexdigest()!=DIGEST:raise ValueError('Model manifest changed')
    lock=json.loads((BASE/'MODEL_LOCK.json').read_text())
    if hashlib.sha256(Path('/opt/homebrew/bin/ollama').resolve().read_bytes()).hexdigest()!=lock['binary_sha256']:
        raise ValueError('Ollama binary changed')

def actual_parallel(log):
    # Old llama.cpp and Ollama load-request diagnostics give independent runtime evidence.
    values=[int(x) for x in re.findall(r'n_seq_max\s*=\s*(\d+)',log)]
    values += [int(x) for x in re.findall(r'\bParallel[=:]\s*(\d+)',log)]
    values += [int(x) for x in re.findall(r'--parallel\s+(\d+)',log)]
    return sorted(set(values))

def original_idle():
    try:return not api(ORIGINAL,'/api/ps')['models']
    except Exception:return None

def window(index,parallel,trace,out):
    path=out/f'window-{index:02d}-p{parallel}';path.mkdir()
    meta=dict(index=index,pair=(index+1)//2,parallel=parallel,model=MODEL,options=OPTIONS,
              status='starting',before=state(),original_endpoint_idle_before=original_idle())
    write(path/'RUN.json',meta)
    env={k:v for k,v in os.environ.items() if k in ('PATH','HOME','TMPDIR','LANG','LC_ALL')}
    settings={'OLLAMA_HOST':URL,'OLLAMA_NUM_PARALLEL':str(parallel),
              'OLLAMA_MAX_LOADED_MODELS':'1','OLLAMA_MAX_QUEUE':'64',
              'OLLAMA_CONTEXT_LENGTH':'2048','OLLAMA_FLASH_ATTENTION':'0',
              'OLLAMA_KV_CACHE_TYPE':'f16','OLLAMA_MULTIUSER_CACHE':'0',
              'OLLAMA_NO_CLOUD':'1','OLLAMA_NOPRUNE':'1','OLLAMA_NOHISTORY':'1',
              'OLLAMA_KEEP_ALIVE':'120s','OLLAMA_DEBUG':'1'}
    env.update(settings);meta['server_settings']=settings
    log_path=path/'SERVER.log'
    proc=None
    try:
        if meta['original_endpoint_idle_before'] is not True:
            raise RuntimeError('Cannot establish idle original serving endpoint')
        # Refuse to take over any pre-existing listener.
        with socket.socket() as probe:
            probe.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            probe.bind(('127.0.0.1',PORT))
        with log_path.open('w') as log:
            proc=subprocess.Popen(['/opt/homebrew/bin/ollama','serve'],env=env,stdout=log,
                                   stderr=subprocess.STDOUT,start_new_session=True)
            meta['dedicated_server_pid']=proc.pid
        deadline=time.monotonic()+30
        while True:
            if proc.poll() is not None:raise RuntimeError('Dedicated server exited before readiness')
            try:
                version=api(URL,'/api/version');break
            except Exception:
                if time.monotonic()>deadline:raise RuntimeError('Server readiness timeout')
                time.sleep(.1)
        if version['version']!='0.20.0':raise ValueError('Wrong server version')
        tag=next(x for x in api(URL,'/api/tags')['models'] if x['name']==MODEL)
        if tag['digest']!=DIGEST:raise ValueError('Wrong cached model')
        warm=run_trace(URL,WARMUPS,MODEL,OPTIONS,timeout_s=60)
        write(path/'WARMUP.json',warm)
        if not all(r['completed'] for r in warm['requests']):raise RuntimeError('Warmup failure')
        meta['version']=version;meta['model_tag']=tag
        meta['loaded_before']=api(URL,'/api/ps')
        models=meta['loaded_before']['models']
        if len(models)!=1 or models[0]['digest']!=DIGEST or models[0].get('context_length')!=2048:
            raise ValueError('Loaded model/context mismatch')
        if models[0].get('size_vram',0)<=0:raise ValueError('No reported GPU residency')
        observed=actual_parallel(log_path.read_text())
        meta['runtime_parallel_values']=observed
        if observed!=[parallel]:raise ValueError('Actual runner parallelism unverified: '+str(observed))
        time.sleep(2)
        result=run_trace(URL,trace,MODEL,OPTIONS,timeout_s=60)
        write(path/'REQUESTS.json',result)
        time.sleep(2)
        meta['loaded_after']=api(URL,'/api/ps')
        meta['after']=state();meta['original_endpoint_idle_after']=original_idle()
        meta['status']='completed'
    except Exception as error:
        meta['status']='aborted';meta['error']=type(error).__name__+': '+str(error)
        raise
    finally:
        # Scope cleanup to the exact process group created above; user's server untouched.
        if proc is not None:
            try:
                api(URL,'/api/generate',dict(model=MODEL,keep_alive=0),timeout=10)
                unload_deadline=time.monotonic()+10
                while True:
                    meta['loaded_after_unload']=api(URL,'/api/ps')
                    if not meta['loaded_after_unload']['models']:break
                    if time.monotonic()>=unload_deadline:raise RuntimeError('Unloading did not quiesce within10s')
                    time.sleep(.1)
            except Exception as error:
                meta['cleanup_error']=type(error).__name__+': '+str(error)
            if proc.poll() is None:
                os.killpg(proc.pid,signal.SIGTERM)
                try:proc.wait(timeout=10)
                except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=5)
            meta['dedicated_server_returncode']=proc.returncode
        if log_path.exists():
            clean=log_path.read_text().replace(str(Path.home()),'USER_HOME')
            log_path.write_text(clean)
        write(path/'RUN.json',meta)
    return meta

def main(out):
    check_lock()
    amendment=json.loads((BASE/'AMENDMENT_01_FREEZE.json').read_text())
    for name,digest in amendment['sha256'].items():
        if hashlib.sha256((BASE/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('Amendment input changed: '+name)
    previous=json.loads((out/'CAMPAIGN.json').read_text())
    if previous.get('status')!='aborted' or len(previous.get('windows',[]))!=1:
        raise ValueError('Continuation requires exact recorded one-window abort')
    first=json.loads((out/'window-01-p1'/'RUN.json').read_text())
    if previous['windows']!=[first] or first['status']!='completed':
        raise ValueError('First completed window does not reconcile')
    failed=out/'window-02-p2'
    if (failed/'REQUESTS.json').exists() or (failed/'WARMUP.json').exists():
        raise ValueError('Second attempt already has offers; cannot replace')
    archive=out/'preflight_abort';archive.mkdir()
    (out/'CAMPAIGN.json').rename(archive/'CAMPAIGN.json')
    failed.rename(archive/'window-02-p2')
    trace=json.loads((BASE/'TRACE.json').read_text())
    if json.loads((out/'OFFERED_TRACE.json').read_text())!=trace:
        raise ValueError('Trace changed')
    campaign=dict(status='running',planned_order=list(ORDER),planned_offered=128,
                  amendment='AMENDMENT_01',prior_abort='preflight_abort/CAMPAIGN.json',windows=[first])
    try:
        for index,parallel in enumerate(ORDER[1:],2):
            print(json.dumps(dict(window=index,parallel=parallel,status='starting')),flush=True)
            result=window(index,parallel,trace,out);campaign['windows'].append(result)
            print(json.dumps(dict(window=index,parallel=parallel,status=result['status'])),flush=True)
        campaign['status']='completed'
    except Exception as error:
        campaign['status']='aborted';campaign['error']=type(error).__name__+': '+str(error)
        raise
    finally:write(out/'CAMPAIGN.json',campaign)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    main(parser.parse_args().output)
