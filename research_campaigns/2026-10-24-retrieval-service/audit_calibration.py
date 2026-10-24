#!/usr/bin/env python3
"""Read-only recount of retained calibration evidence; never imports/runs service."""
import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(test, message):
    if not test:
        raise ValueError(message)


def percentile(values, numerator, denominator=100):
    """Exact nearest-rank percentile, using integer rank arithmetic."""
    require(bool(values) and 0 < numerator <= denominator, 'Bad percentile input')
    return sorted(values)[(len(values)*numerator+denominator-1)//denominator-1]


class Reader:
    def __init__(self):
        self.hashes = {}

    def raw(self, path):
        path = Path(path)
        body = path.read_bytes()
        try: name = str(path.relative_to(ROOT))
        except ValueError: name = str(path)
        self.hashes[name] = hashlib.sha256(body).hexdigest()
        return body

    def json(self, path):
        return json.loads(self.raw(path))

    def lines(self, path):
        return [json.loads(line) for line in self.raw(path).splitlines()]


def audit():
    r = Reader(); native = ROOT/'calibration_native_run'; initial = ROOT/'calibration_run'
    freeze = r.json(ROOT/'APPROVED_CALIBRATION_NATIVE.json')
    first_freeze = r.json(ROOT/'APPROVED_CALIBRATION.json')
    require(freeze['authorized'] is True and freeze['stage']=='calibration', 'Missing native authorization')
    require(freeze['plan']==first_freeze['plan'] and freeze['sha256']==first_freeze['sha256'], 'Amendment changed design/files')
    for filename,digest in freeze['sha256'].items():
        require(hashlib.sha256(r.raw(ROOT/filename)).hexdigest()==digest, f'Frozen file changed: {filename}')
    r.raw(ROOT/freeze['execution_amendment'])
    plan = r.json(native/'PLAN.json')
    require(plan==freeze['plan']==r.json(initial/'PLAN.json'), 'Plan differs across attempts or freeze')
    require(plan['deadline_ns']==100_000_000 and plan['batch_wait_ns']==2_000_000 and
            plan['max_batch']==16 and plan['phase_timeout_s']==600, 'Unexpected protocol constants')
    require(len(plan['windows'])==16 and plan['warmup_queries']==list(range(20)), 'Phase size/warmup plan')
    host = r.json(native/'HOST.json')
    require(host['synthetic'] is False and host['approved_host_conditions']==freeze['host_conditions'], 'Host/freeze mismatch')
    require(host['runner_changes_switch_interval'] is False, 'Switch interval unexpectedly changed')

    # Reuse prior already-qualified answers and distance digests; no new distance
    # calculations, GPU calls, subprocesses, or timing experiments are performed.
    expected = r.json(ROOT/'data/qualified_top10.json')
    provenance = r.json(ROOT/'PROVENANCE.json')
    prior_path = Path(provenance['existing_answers_source'])
    prior_body = r.raw(prior_path)
    require(hashlib.sha256(prior_body).hexdigest()==provenance['existing_answers_source_sha256'], 'Prior qualified RAW changed')
    prior = json.loads(prior_body)
    gold = {str(q['query_id']):q for q in prior['queries']}
    require(set(expected)==set(gold)=={str(i) for i in range(100)}, 'Qualified answer coverage')
    for qid in gold:
        require(expected[qid]==gold[qid]['cpu_top10']==gold[qid]['top10'], 'Prior top-ten mismatch')
        require(gold[qid]['cpu_distance_sha256']==gold[qid]['gpu_distance_sha256'], 'Prior distance digest mismatch')

    def answer(a, qid, rid):
        require(a['query_id']==qid and a['request_id']==rid, 'Response identity mismatch')
        require(a['passed'] is True and a['compared_distances']==10_000 and
                a['mismatch_count']==0 and a['invalid_dot_count']==0, 'Native exact check failed')
        require(a['top10']==expected[str(qid)], 'Returned top ten differs from qualified answer')
        require(a['distance_sha256']==gold[str(qid)]['cpu_distance_sha256'], 'Full distance digest differs from qualified output')

    windows=[]; phase_latencies=[]; phase_jitters=[]; response_total=0; warmup_total=0
    warmup_latencies=[]; earliest_native=None; latest_delivery=0; previous_last=None
    plans={}; startups=[]; native_batch_total=0
    for spec in plan['windows']:
        wid=spec['window_id']; wdir=native/wid
        require(wid not in plans, 'Duplicate window ID'); plans[wid]=spec
        frozen_rows=spec['requests']; count=len(frozen_rows)
        require(count==200 and [x['request_id'] for x in frozen_rows]==[str(i) for i in range(count)], 'Planned ID coverage/order')
        require(Counter(x['query_id'] for x in frozen_rows)==Counter({q:2 for q in range(100)}), 'Query balance')
        offsets=[x['offset_ns'] for x in frozen_rows]
        require(offsets==sorted(offsets) and offsets[0]>=0, 'Nonmonotone planned schedule')
        wp=r.json(wdir/'PLAN.json'); result=r.json(wdir/'RESULT.json')
        require(wp['window']==spec and len(wp['requests'])==count, 'Window/phase plan differs')
        require(result['window_id']==wid and result['rate']==spec['rate'] and
                result['pair']==spec['pair'] and result['policy']==spec['policy'], 'Result header differs')
        require(result['synthetic'] is False and result['failure'] is None and len(result['requests'])==count, 'Result incomplete/failed')
        ready=r.json(native/(wid+'-READY.json'))
        require(ready['event']=='ready' and ready['synthetic'] is False and ready['base_count']==10_000 and
                ready['query_count']==100 and ready['dimensions']==128 and ready['device']=='Apple M3 Max', 'Readiness mismatch')
        require(ready['base_sha256']==freeze['sha256']['data/siftsmall_base.fvecs'] and
                ready['query_sha256']==freeze['sha256']['data/siftsmall_query.fvecs'], 'Native input digests differ')
        require(0<=ready['client_startup_ns']<=30_000_000_000, 'Startup watchdog exceeded')
        startups.append(ready['client_startup_ns'])
        require(r.raw(native/(wid+'-stderr.txt'))==b'', 'Native stderr not empty')
        raw_stdout=r.lines(native/(wid+'-stderr.txt.stdout.bin'))
        native_ready=dict(ready);del native_ready['client_startup_ns']
        require(raw_stdout[0]==native_ready, 'Saved readiness/raw stdout differ')
        warmup_responses=[]
        for j,qid in enumerate(plan['warmup_queries']):
            w=r.json(native/(wid+f'-warmup-{j}.json'))
            c=r.json(native/(wid+f'-warmup-{j}-client.json'))
            require(w['event']=='response' and w['batch_id']==-1-j and len(w['answers'])==1, 'Warmup response shape')
            answer(w['answers'][0],qid,f'warmup-{j}')
            require(w['native_start_ns']<=w['native_checked_ns']<=wp['start_monotonic_ns'], 'Warmup overlaps planned measured start')
            require(0<=c['inclusive_client_ns']<=2_000_000_000, 'Warmup client duration')
            require(c['inclusive_client_ns']>=w['native_checked_ns']-w['native_start_ns'], 'Warmup client/native clock consistency')
            if previous_last is not None: require(w['native_start_ns']>=previous_last, 'Warmup/window order')
            previous_last=w['native_checked_ns']
            earliest_native=w['native_start_ns'] if earliest_native is None else min(earliest_native,w['native_start_ns'])
            warmup_responses.append(w);warmup_latencies.append(c['inclusive_client_ns']);warmup_total+=1
        responses=r.lines(wdir/'RESPONSES.jsonl')
        require(raw_stdout==[native_ready]+warmup_responses+responses, 'Raw stdout does not reconcile to complete warmup/measured output')
        require([x['batch_id'] for x in responses]==list(range(len(responses))), 'Batch identity/sequence')
        by_id={}; sizes=[]
        for response in responses:
            require(response['event']=='response', 'Nonresponse in measured stream')
            size=len(response['answers']);sizes.append(size)
            require(1<=size<=16 and (spec['policy']!='immediate' or size==1), 'Batch size violates policy')
            for a in response['answers']:
                rid=a['request_id'];require(rid not in by_id, 'Duplicate measured answer')
                by_id[rid]=(a,response)
        require(list(by_id)==[x['request_id'] for x in frozen_rows], 'Missing/extra/reordered measured answers')
        latencies=[];jitters=[];delivery_times=[]
        for frozen,prepared,actual in zip(frozen_rows,wp['requests'],result['requests']):
            rid=frozen['request_id'];qid=frozen['query_id']
            for key in ('request_id','query_id','offset_ns'):
                require(frozen[key]==prepared[key]==actual[key], 'Request identity/offset changed')
            planned=wp['start_monotonic_ns']+frozen['offset_ns']
            require(planned==prepared['planned_ns']==actual['planned_ns'], 'Planned timestamp changed')
            require(prepared['status']=='planned' and all(prepared[k] is None for k in
                    ('offered_ns','submitted_ns','delivered_ns','latency_ns')), 'Plan contains later outcomes')
            a,response=by_id[rid];answer(a,qid,rid)
            require(actual['status']=='ok' and actual['batch_id']==response['batch_id'], 'Status/batch mismatch')
            times=[planned,actual['offered_ns'],actual['submitted_ns'],response['native_start_ns'],
                   response['native_checked_ns'],actual['delivered_ns']]
            require(all(type(t) is int for t in times) and times==sorted(times), 'Client/native timestamp order')
            latency=actual['delivered_ns']-planned;jitter=actual['offered_ns']-planned
            require(latency==actual['latency_ns'], 'Stored latency differs from planned-to-delivery')
            require(actual['delivered_ns']-actual['submitted_ns']<=2_000_000_000, 'Dispatched request duration exceeds batch cap')
            latencies.append(latency);jitters.append(jitter);delivery_times.append(actual['delivered_ns'])
        for response in responses:
            related=[x for x in result['requests'] if x['batch_id']==response['batch_id']]
            require(len({x['submitted_ns'] for x in related})==1 and len({x['delivered_ns'] for x in related})==1, 'Batch not jointly submitted/delivered')
        computed={'planned':count,'offered':count,'correct_delivered':count,
                  'deadline_success':sum(x<=100_000_000 for x in latencies),
                  'p95_ns':percentile(latencies,95),'arrival_valid':percentile(jitters,99)<=2_000_000 and max(jitters)<=10_000_000,
                  'p99_offer_jitter_ns':percentile(jitters,99),'max_offer_jitter_ns':max(jitters)}
        require(computed==result['summary'], 'Stored summary differs from independent raw recount')
        windows.append({'window_id':wid,'rate':spec['rate'],'pair':spec['pair'],'policy':spec['policy'],
                        **computed,'deadline_misses':count-computed['deadline_success'],
                        'deadline_99_percent_pass':computed['deadline_success']>=198,
                        'p50_latency_ns':percentile(latencies,50),'max_latency_ns':max(latencies),
                        'p50_offer_jitter_ns':percentile(jitters,50),'batches':len(responses),'max_batch_size':max(sizes),
                        'warmups':20,'startup_ns':ready['client_startup_ns']})
        phase_latencies.extend(latencies);phase_jitters.extend(jitters);response_total+=count;native_batch_total+=len(responses)
        previous_last=max(delivery_times);latest_delivery=max(latest_delivery,previous_last)

    for a,b in zip(plan['windows'][::2],plan['windows'][1::2]):
        require(a['requests']==b['requests'] and a['rate']==b['rate'] and a['pair']==b['pair'] and
                {a['policy'],b['policy']}=={'immediate','bounded'}, 'Paired schedules differ')
    eligible=[]
    for rate in (20,50,100,200):
        refs=[w for w in windows if w['rate']==rate and w['policy']=='immediate']
        require(len(refs)==2,'Reference window coverage')
        if all(w['arrival_valid'] and w['deadline_99_percent_pass'] for w in refs):eligible.append(rate)
    phase_valid=all(w['arrival_valid'] for w in windows)
    selected=max(eligible) if phase_valid and eligible else None
    summary=r.json(native/'SUMMARY.json')
    require(summary['aborted'] is None and summary['unrun_windows']==[] and summary['synthetic'] is False and
            summary['assessment']=={'valid':phase_valid,'selected_rate':selected}, 'Phase assessment mismatch')

    aborted=r.json(initial/'SUMMARY.json');initial_host=r.json(initial/'HOST.json')
    require(initial_host==host,'Attempts have different recorded host declarations')
    require(aborted['assessment'] is None and aborted['unrun_windows']==[w['window_id'] for w in plan['windows']], 'Initial aborted denominator lost')
    require(not list(initial.glob('*warmup*')) and not list(initial.glob('*/RESULT.json')), 'Initial run contains unexpected outcomes')
    first_stdout=r.lines(initial/(plan['windows'][0]['window_id']+'-stderr.txt.stdout.bin'))
    require(len(first_stdout)==1 and first_stdout[0]['event']=='fatal' and 'Unified-memory' in first_stdout[0]['error'], 'Initial failure evidence')
    r.raw(initial/(plan['windows'][0]['window_id']+'-stderr.txt'))
    power={name:r.raw(ROOT/name).decode() for name in
           ('calibration_pre_power.txt','calibration_post_power.txt','calibration_native_post_power.txt')}
    report={'audit_version':1,'independent_of_service_driver_import':True,'no_new_distance_or_service_execution':True,
        'frozen_file_hashes_match':True,'native_amendment_preserves_plan_and_hashes':True,
        'windows':windows,'totals':{'windows':16,'planned_measured':response_total,'correct_measured':response_total,
        'measured_batches':native_batch_total,'measured_native_distance_comparisons':response_total*10_000,
        'deadline_success':sum(x<=100_000_000 for x in phase_latencies),
        'deadline_misses':sum(x>100_000_000 for x in phase_latencies),
        'arrival_invalid_windows':sum(not w['arrival_valid'] for w in windows),
        'deadline_99_percent_failing_windows':sum(not w['deadline_99_percent_pass'] for w in windows),
        'warmup_correct':warmup_total,'warmup_native_distance_comparisons':warmup_total*10_000,
        'warmup_max_client_ns':max(warmup_latencies),'startup_max_ns':max(startups)},
        'assessment':{'valid':phase_valid,'selected_rate':selected,'evaluation_authorized_by_this_audit':False},
        'initial_attempt':{'aborted':aborted['aborted'],'planned_requests_retained':3200,'unrun_windows':16,'measured_responses':0,'warmup_responses':0},
        'phase_clock_scope':{'observed_first_native_warmup_to_last_delivery_ns':latest_delivery-earliest_native,
           'phase_start_epoch_not_retained':True,'exact_full_process_wall_time_not_certified':True,
           'note':'All windows complete, per-startup/batch clocks within caps and shared600-second watchdog source is frozen. Recorded span excludes initial startup and final bookkeeping; no exact global start timestamp was persisted.'},
        'host':host,'power_observations':power,
        'interpretation':['Calibration invalid under frozen arrival criterion; no rate selection or evaluation follows.',
          'Correctness matches retained qualified top-ten answers AND full-distance digests, without recomputing distances.',
          'Roughly5ms jitter and recorded5ms Python switch interval are observationally compatible; GIL causation unconfirmed.',
          'AC-labelled but discharging battery observations do not establish stable wall power, energy consumption or causal treatment effects.',
          'Warmup320 requests are distinct from measured3200; initial startup-only failure remains a separate preserved attempt.'],
        'input_sha256':r.hashes}
    columns=['window_id','rate','pair','policy','planned','correct_delivered','deadline_success','deadline_misses',
             'deadline_99_percent_pass','p95_ns','p99_offer_jitter_ns','max_offer_jitter_ns','arrival_valid','batches','max_batch_size']
    csv_text=io.StringIO();writer=csv.DictWriter(csv_text,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(windows)
    return report,csv_text.getvalue()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--verify-only',action='store_true');args=parser.parse_args()
    require(percentile(list(range(1,201)),95)==190 and percentile(list(range(1,201)),99)==198,'Percentile selfcheck')
    report,table=audit()
    encoded=json.dumps(report,sort_keys=True,indent=2)+'\n'
    if args.verify_only:
        require(json.loads((ROOT/'CALIBRATION_AUDIT.json').read_text())==report,'Saved audit differs')
        require((ROOT/'CALIBRATION_TABLE.csv').read_text()==table.replace('\r\n','\n'),'Saved table differs')
    else:
        with (ROOT/'CALIBRATION_AUDIT.json').open('x') as f:f.write(encoded)
        with (ROOT/'CALIBRATION_TABLE.csv').open('x',newline='') as f:f.write(table)
    print(json.dumps({'audit':'PASS','totals':report['totals'],'assessment':report['assessment'],
                      'phase_clock_scope':report['phase_clock_scope']},sort_keys=True,indent=2))


if __name__=='__main__':main()
