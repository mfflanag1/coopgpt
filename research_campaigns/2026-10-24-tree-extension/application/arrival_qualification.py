#!/usr/bin/env python3
"""Preparation defaults only. Timing requires a reviewed, explicitly approved freeze."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import platform
import random
import sys
import threading
import time

ROOT = Path(__file__).resolve().parent
P99_LIMIT = 2_000_000
MAX_LIMIT = 10_000_000
PHASE_SECONDS = 80


def save(path, value):
    with Path(path).open('x') as f:
        json.dump(value,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def offsets(seed, rate, count=50):
    rng=random.Random(seed);elapsed=0;out=[]
    for i in range(count):
        elapsed+=rng.expovariate(rate)
        out.append({'request_id':i,'offset_ns':round(elapsed*1e9)})
    return out


def plan():
    cases=[]
    for rep in range(3):
        groups=[(rate,load) for rate in (20,50,100,200) for load in ('idle','python_cpu')]
        random.Random(2410244000+rep).shuffle(groups)
        for rate,load in groups:
            ri=(20,50,100,200).index(rate)
            seed=2410242000+rep*10+ri
            modes=['thread','process']
            if (rep+ri+(load=='python_cpu'))%2: modes.reverse()
            for mode in modes:
                cases.append({'case_id':f'r{rep}-rate{rate}-{load}-{mode}','rep':rep,'rate':rate,
                    'load':load,'mode':mode,'seed':seed,'requests':offsets(seed,rate)})
    total=sum(c['requests'][-1]['offset_ns']+50_000_000 for c in cases)
    if total>=70_000_000_000: raise ValueError('Predetermined arrival horizon exceeds design allowance')
    return {'schema':1,'stage':'arrival-driver-qualification','phase_seconds':PHASE_SECONDS,
            'startup_seconds':2,'case_drain_seconds':1,'lead_ns':50_000_000,
            'p99_limit_ns':P99_LIMIT,'maximum_limit_ns':MAX_LIMIT,
            'planned_offer_horizons_plus_leads_ns':total,'cases':cases}


def nearest(values, percent):
    if not values: raise ValueError('Empty percentile')
    return sorted(values)[(len(values)*percent+99)//100-1]


def summarize(rows):
    # Missing admissions are infinite, never removed from the denominator.
    admission=[r['admitted_ns']-r['planned_ns'] if r.get('admitted_ns') is not None else math.inf for r in rows]
    wakes=[r['wake_ns']-r['planned_ns'] if r.get('wake_ns') is not None else math.inf for r in rows]
    emitted=[r['emitted_ns']-r['planned_ns'] if r.get('emitted_ns') is not None else math.inf for r in rows]
    receipt=[r['received_ns']-r['planned_ns'] if r.get('received_ns') is not None else math.inf for r in rows]
    def metrics(v):
        return {key:(value if math.isfinite(value) else None) for key,value in
                [('p99_ns',nearest(v,99)),('maximum_ns',max(v))]}
    admitted=sum(r.get('admitted_ns') is not None for r in rows)
    complete=admitted==len(rows) and all(r.get('received_ns') is not None for r in rows)
    return {'planned':len(rows),'admitted':admitted,'received':sum(r.get('received_ns') is not None for r in rows),
        'wake_jitter':metrics(wakes),'emission_jitter':metrics(emitted),'admission_jitter':metrics(admission),'receipt_delay':metrics(receipt),
        'qualification_pass':complete and min(admission)>=0 and nearest(admission,99)<=P99_LIMIT and max(admission)<=MAX_LIMIT}


def produce(schedule, stop, clock, send):
    """Injected clock/transport permit deterministic tests without physical timing."""
    rows=[dict(r,wake_ns=None,emitted_ns=None,admitted_ns=None) for r in schedule]
    failure=None
    try:
        for r in rows:
            while True:
                if stop.wait(max(0,(r['planned_ns']-clock())/1e9)):
                    failure='Producer stopped before all offers';break
                woke=clock()
                if woke>=r['planned_ns']:
                    r['wake_ns']=woke;break
                # Conservative early-return guard; the original absolute
                # deadline stays fixed and cancellation is checked each wait.
            if failure is not None:break
            r['emitted_ns']=clock()
            send({'kind':'offer','request_id':r['request_id'],'planned_ns':r['planned_ns'],
                  'wake_ns':r['wake_ns'],'emitted_ns':r['emitted_ns']})
            r['admitted_ns']=clock()
    except BaseException as exc:
        failure=f'{type(exc).__name__}: {exc}'
    return {'kind':'done','rows':rows,'failure':failure}


def scheduler(control, transport, stop):
    # Both placements use the original threading.Event wait implementation.
    # The shared multiprocessing event is cancellation only, not the timer.
    timed_stop=threading.Event()
    def relay_stop():
        stop.wait();timed_stop.set()
    threading.Thread(target=relay_stop,daemon=True).start()
    try:
        control.send({'kind':'ready','pid':os.getpid(),'switch_interval_seconds':sys.getswitchinterval()})
        while not control.poll(.05):
            if stop.is_set():return
        config=control.recv()
        def send(value):transport.send_bytes(json.dumps(value,separators=(',',':')).encode())
        done=produce(config['requests'],timed_stop,time.monotonic_ns,send)
        send(done)
    except BaseException as exc:
        try:control.send({'kind':'fatal','error':f'{type(exc).__name__}: {exc}'})
        except BaseException:pass
    finally:
        timed_stop.set()
        control.close();transport.close()


def cpu_load(stop, started, state):
    # One continuously runnable Python-integer thread in the consumer process.
    # No sleep, C numeric extension, MPS or switch-interval adjustment.
    value=1;iterations=0;started.set()
    while not stop.is_set():
        for _ in range(2048):value=(value*1664525+1013904223)&0xffffffff
        iterations+=2048
    state.update(iterations=iterations,checksum=value)


def final_cpu_accounting(state, worker_exists, worker_alive):
    if not worker_exists:
        return {'status':'not_started','iterations':None},'CPU load worker not started'
    if worker_alive:
        return {'status':'cleanup_incomplete','iterations':None},'CPU load cleanup incomplete; final accounting unavailable'
    result=dict(state,status='complete')
    return result,('CPU load completed with zero recorded iterations' if result['iterations']==0 else None)


def reconcile(planned, offers, done):
    expected={r['request_id']:r for r in planned}
    if len(expected)!=len(planned):raise ValueError('Duplicate planned ID')
    observed={}
    for offer in offers:
        rid=offer['request_id']
        if rid not in expected or rid in observed:raise ValueError('Unknown/duplicate offered ID')
        if offer['planned_ns']!=expected[rid]['planned_ns']:raise ValueError('Planned timestamp changed')
        observed[rid]=offer
    if list(observed)!=list(expected)[:len(observed)]:raise ValueError('Offers reordered')
    completed={}
    if done is not None:
        if len(done['rows'])!=len(planned):raise ValueError('Final producer denominator changed')
        for row in done['rows']:
            rid=row['request_id']
            if rid in completed or rid not in expected or row['planned_ns']!=expected[rid]['planned_ns']:
                raise ValueError('Final producer ID/timestamp changed')
            completed[rid]=row
    out=[]
    for p in planned:
        rid=p['request_id'];a=observed.get(rid,{});b=completed.get(rid,{})
        if a and b and (a['emitted_ns']!=b['emitted_ns'] or a['wake_ns']!=b['wake_ns']):raise ValueError('Wake/emission timestamp changed')
        row=dict(p,wake_ns=a.get('wake_ns',b.get('wake_ns')),emitted_ns=a.get('emitted_ns',b.get('emitted_ns')),
                 admitted_ns=b.get('admitted_ns'),received_ns=a.get('received_ns'))
        e,ad,rc=row['emitted_ns'],row['admitted_ns'],row['received_ns']
        if row['wake_ns'] is not None and (row['wake_ns']<p['planned_ns'] or e is None or e<row['wake_ns']):raise ValueError('Wake ordering')
        if e is not None and e<p['planned_ns']:raise ValueError('Early offer')
        if ad is not None and (e is None or ad<e or rc is None):raise ValueError('Admission without coherent offer/receipt')
        # Receiver may read while sender reacquires its GIL after write; rc<ad is
        # legal. Both are after emission. Post-write ad is a conservative upper
        # bound on kernel acceptance time, not a claimed kernel timestamp.
        if rc is not None and (e is None or rc<e):raise ValueError('Receipt precedes emission')
        row['status']='complete' if ad is not None and rc is not None else 'incomplete'
        out.append(row)
    return out


def run_case(spec, root, shared_deadline, p):
    directory=root/spec['case_id'];directory.mkdir()
    ctx=mp.get_context('spawn');parent,child=ctx.Pipe();receiver,sender=ctx.Pipe(duplex=False)
    stop=ctx.Event();load_stop=threading.Event();load_started=threading.Event();load_state={'iterations':0}
    load_worker=None;load_join_incomplete=False;worker=None;offers=[];done=None;failure=None;planned=[];ready=None
    try:
        worker=(ctx.Process(target=scheduler,args=(child,sender,stop),daemon=True) if spec['mode']=='process'
                else threading.Thread(target=scheduler,args=(child,sender,stop),daemon=True))
        worker.start()
        if spec['mode']=='process':
            # The spawned child owns transferred endpoints. Parent-held duplicate
            # writers would otherwise conceal EOF when that child exits early.
            child.close();sender.close()
        startup_deadline=min(shared_deadline,time.monotonic()+p['startup_seconds'])
        while not parent.poll(.01):
            if time.monotonic()>=startup_deadline:raise TimeoutError('Scheduler readiness timeout')
        ready=parent.recv()
        if ready.get('kind')!='ready':raise RuntimeError(f'Scheduler startup: {ready}')
        if spec['load']=='python_cpu':
            load_worker=threading.Thread(target=cpu_load,args=(load_stop,load_started,load_state),daemon=True)
            load_worker.start()
            if not load_started.wait(max(0,shared_deadline-time.monotonic())):raise TimeoutError('Load startup')
        start=time.monotonic_ns()+p['lead_ns']
        planned=[dict(r,planned_ns=start+r['offset_ns']) for r in spec['requests']]
        save(directory/'PLAN.json',{'spec':spec,'case_start_monotonic_ns':start,'requests':planned,'ready':ready})
        parent.send({'requests':planned})
        case_deadline=min(shared_deadline,(planned[-1]['planned_ns']/1e9)+p['case_drain_seconds'])
        with (directory/'RAW.jsonl').open('x') as raw:
            while done is None:
                if time.monotonic()>=case_deadline:raise TimeoutError('Case or shared phase deadline')
                if receiver.poll(min(.01,max(0,case_deadline-time.monotonic()))):
                    body=receiver.recv_bytes();received=time.monotonic_ns()
                    msg=json.loads(body)
                    raw.write(json.dumps({'received_ns':received,'message':msg},sort_keys=True)+'\n')
                    if msg.get('kind')=='offer':offers.append(dict(msg,received_ns=received))
                    elif msg.get('kind')=='done':done=msg
                    else:raise ValueError('Unknown producer message')
                elif parent.poll():raise RuntimeError(f'Scheduler error: {parent.recv()}')
            if done['failure']:raise RuntimeError(done['failure'])
    except BaseException as exc:failure=f'{type(exc).__name__}: {exc}'
    finally:
        stop.set();load_stop.set()
        receiver.close();parent.close()
        if worker is not None:
            worker.join(timeout=.5)
            if worker.is_alive() and spec['mode']=='process':worker.terminate();worker.join(timeout=.5)
            if worker.is_alive():failure=(failure or '')+' Worker cleanup incomplete'
        if load_worker is not None:
            load_worker.join(timeout=.5)
            load_join_incomplete=load_worker.is_alive()
        # Thread worker owns these connections too; close only after bounded join.
        child.close();sender.close()
    if not planned:
        planned=[dict(r,planned_ns=None) for r in spec['requests']]
        rows=[dict(r,wake_ns=None,emitted_ns=None,admitted_ns=None,received_ns=None,status='not_started') for r in planned]
        stats=None
    else:
        try:rows=reconcile(planned,offers,done);stats=summarize(rows)
        except BaseException as exc:
            failure=(failure or '')+f' Reconciliation: {exc}'
            rows=[dict(r,wake_ns=None,emitted_ns=None,admitted_ns=None,received_ns=None,status='unverified') for r in planned];stats=None
    if spec['load']=='python_cpu':
        load_state,accounting_error=final_cpu_accounting(load_state,load_worker is not None,load_join_incomplete)
        if accounting_error:failure=(failure or '')+' '+accounting_error
    result={'case_id':spec['case_id'],'spec':spec,'failure':failure,'requests':rows,'summary':stats,
            'producer_ready':ready,'consumer_load':load_state,'raw_offers_received':len(offers)}
    save(directory/'RESULT.json',result);return result


def frozen_files():return ['arrival_qualification.py','PROTOCOL.txt','DIAGNOSIS.txt','test_arrival_qualification.py']


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--authorization',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if bool(args.prepare)==bool(args.authorization):parser.error('Choose --prepare OR --authorization')
    p=plan();hashes={name:digest(ROOT/name) for name in frozen_files()}
    if args.prepare:
        save(args.output,{'authorized':False,'plan':p,'sha256':hashes,
             'host_conditions':None,'review_note':'Timing forbidden until root reviews exact freeze and sends go.'});return
    approval=json.loads(args.authorization.read_text())
    if approval.get('authorized') is not True or approval.get('plan')!=p or approval.get('sha256')!=hashes:
        raise ValueError('Explicit reviewed authorization and exact current freeze required')
    if not isinstance(approval.get('host_conditions'),str) or not approval['host_conditions'].strip():
        raise ValueError('Host condition declaration required')
    args.output.mkdir()
    save(args.output/'PLAN.json',p)
    epoch={'phase_start_monotonic_ns':time.monotonic_ns(),'wall_epoch_ns':time.time_ns(),
           'utc':datetime.now(timezone.utc).isoformat(),'platform':platform.platform(),'python':platform.python_version(),
           'consumer_pid':os.getpid(),'switch_interval_seconds':sys.getswitchinterval(),'runner_adjusted_switch_interval':False,
           'host_conditions':approval['host_conditions']}
    save(args.output/'EPOCH.json',epoch)
    deadline=epoch['phase_start_monotonic_ns']/1e9+PHASE_SECONDS
    results=[];aborted=None
    for spec in p['cases']:
        if time.monotonic()>=deadline:aborted='Shared phase deadline';break
        result=run_case(spec,args.output,deadline,p);results.append(result)
        if result['failure']:aborted=result['failure'];break
    done_ids={r['case_id'] for r in results}
    groups=[]
    for mode in ('thread','process'):
        for load in ('idle','python_cpu'):
            rs=[r for r in results if r['spec']['mode']==mode and r['spec']['load']==load]
            groups.append({'mode':mode,'load':load,'complete_cases':len(rs),'expected_cases':12,
                'qualification_pass':aborted is None and len(results)==48 and len(rs)==12 and all(r['failure'] is None and r['summary'] and r['summary']['qualification_pass'] for r in rs)})
    save(args.output/'SUMMARY.json',{'aborted':aborted,'phase_end_monotonic_ns':time.monotonic_ns(),
         'unrun_cases':[c['case_id'] for c in p['cases'] if c['case_id'] not in done_ids],
         'planned_requests':sum(len(c['requests']) for c in p['cases']),'completed_cases':len(results),'groups':groups,
         'interpretation':'Synthetic arrival-driver qualification only; no serving/energy/pooling or pure-GIL-causality claim.'})
    if aborted:raise SystemExit(1)


if __name__=='__main__':main()
