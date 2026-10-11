#!/usr/bin/env python3
"""Small real Ollama serving preflight, not a representative performance study."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import time
import urllib.request

MODEL='llama3.2:3b'
BASE='http://127.0.0.1:11434'
PROMPTS=[
    'Explain in at most sixty words why inference servers batch requests.',
    'Explain in at most sixty words how a queue can increase response latency.',
    'Explain in at most sixty words the difference between power and energy.',
]
OPTIONS={'temperature':0,'seed':0,'num_predict':64,'num_ctx':2048}


def api(path,body=None):
    request=urllib.request.Request(BASE+path,data=None if body is None else json.dumps(body).encode(),
                                   headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=120) as response:
        return json.load(response)


def probe(prompt):
    body=dict(model=MODEL,prompt=prompt,stream=True,options=OPTIONS,keep_alive='60s')
    started=time.monotonic()
    result=dict(prompt=prompt,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                chunks=[],first_content_seconds=None,completed=False,error=None)
    try:
        request=urllib.request.Request(BASE+'/api/generate',data=json.dumps(body).encode(),
                                       headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(request,timeout=120) as response:
            for line in response:
                if not line.strip():continue
                item=json.loads(line)
                elapsed=time.monotonic()-started
                result['chunks'].append(dict(elapsed_seconds=elapsed,data=item))
                if item.get('response') and result['first_content_seconds'] is None:
                    result['first_content_seconds']=elapsed
                if item.get('error'):raise ValueError(item['error'])
                if item.get('done'):
                    for name in ('eval_count','prompt_eval_count','eval_duration','total_duration','load_duration'):
                        if not isinstance(item.get(name),int) or item[name]<0:
                            raise ValueError('Missing/invalid final usage: '+name)
                    if item['eval_count']<=0 or result['first_content_seconds'] is None:
                        raise ValueError('No generated content')
                    result['final']=item
                    result['completed']=True
                    break
                if elapsed>120:raise TimeoutError('Elapsed budget exceeded between received lines')
        if not result['completed']:raise ValueError('No terminal done message')
    except Exception as error:
        result['error']=type(error).__name__+': '+str(error)
    result['client_duration_seconds']=time.monotonic()-started
    return result


def main(output):
    output.mkdir(parents=True,exist_ok=False)
    policy=dict(kind='LOCAL_HARDWARE_SERVING_SMOKE_ONLY',model=MODEL,options=OPTIONS,
                prompts=PROMPTS,warmup_prompt='Write one sentence about computer memory.',
                energy_collected=False,two_hardware_gate=False,representative_workload=False,
                notes='Shared active Mac; native default Ollama server, serial requests. No causal or configuration comparison. Socket timeout is not a hard real-time deadline.')
    raw=(json.dumps(policy,indent=2,sort_keys=True)+'\n').encode()
    (output/'PROTOCOL.json').write_bytes(raw)
    (output/'PROTOCOL_FREEZE.json').write_text(json.dumps(dict(
        frozen_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        sha256=hashlib.sha256(raw).hexdigest()),indent=2)+'\n')
    loaded=api('/api/ps')
    if loaded.get('models'):raise RuntimeError('Existing loaded model: leave active serving unchanged')
    tag=next((m for m in api('/api/tags')['models'] if m['name']==MODEL),None)
    if tag is None or not tag.get('digest'):raise RuntimeError('Required local model unavailable')
    metadata=dict(version=api('/api/version'),local_model=tag,loaded_before=loaded)
    (output/'ENVIRONMENT.json').write_text(json.dumps(metadata,indent=2)+'\n')
    warmup=probe(policy['warmup_prompt'])
    (output/'WARMUP.json').write_text(json.dumps(warmup,indent=2)+'\n')
    rows=[]
    with (output/'REQUESTS.jsonl').open('w') as f:
        for i,prompt in enumerate(PROMPTS):
            row=dict(request_id='smoke-'+str(i+1),**probe(prompt))
            rows.append(row);f.write(json.dumps(row,sort_keys=True)+'\n');f.flush()
    metadata['loaded_after']=api('/api/ps')
    after=next(m for m in api('/api/tags')['models'] if m['name']==MODEL)
    metadata['model_digest_stable']=after['digest']==tag['digest']
    (output/'ENVIRONMENT.json').write_text(json.dumps(metadata,indent=2)+'\n')
    summary=dict(offered=len(rows),completed=sum(r['completed'] for r in rows),
                 failed=sum(not r['completed'] for r in rows),
                 client_duration_seconds=[r['client_duration_seconds'] for r in rows],
                 first_content_seconds=[r['first_content_seconds'] for r in rows],
                 generated_tokens=[r.get('final',{}).get('eval_count') for r in rows],
                 model_digest_stable=metadata['model_digest_stable'],
                 warmup_completed=warmup['completed'],energy_collected=False,
                 two_hardware_gate=False,study_promotion_gate=False)
    (output/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    main(parser.parse_args().output)
