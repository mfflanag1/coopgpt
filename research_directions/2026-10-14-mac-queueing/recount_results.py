"""Small independent recount of saved timings; does not import the main analyzer."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from statistics import median


def recount(root):
    campaign=json.loads((root/'capture/CAMPAIGN.json').read_text())
    rows=[]; checks=[]; lookup={}; inputs={}
    if len(campaign['windows']) != 24 or campaign['unrun_window_ids']:
        raise ValueError('Cannot recount a complete 24-window cohort')
    for w in campaign['windows']:
        path=root/'capture'/w['folder']/'RAW.json'
        inputs[str(path.relative_to(root))]=hashlib.sha256(path.read_bytes()).hexdigest()
        raw=json.loads(path.read_text()); jobs=raw['jobs']
        if len(jobs)!=60 or [j['id'] for j in jobs]!=list(range(60)):
            raise ValueError('Job denominator mismatch')
        if not all(j['passed'] and j['command_buffer_status']==4 and j['check']['mismatch_count']==0 and j['check']['nonfinite_count']==0 for j in jobs):
            raise ValueError('Failed job')
        lat=sorted(j['validated_completion_s']-i/w['rate'] for i,j in enumerate(jobs))
        jitter=sorted(j['observed_enqueue_s']-i/w['rate'] for i,j in enumerate(jobs))
        ontime=sum(j['validated_completion_s']<=i/w['rate']+.100 for i,j in enumerate(jobs))
        occupancy=defaultdict(float); prev=0.; active=0
        for e in raw['events']:
            occupancy[active]+=e['time_s']-prev
            active=e['active_count'];prev=e['time_s']
        occupancy[active]+=raw['window_end_s']-prev
        row={'window_id':w['window_id'],'round':w['round'],'rate':w['rate'],'concurrency':w['concurrency'],
             'p95_latency_seconds':lat[56],'p95_producer_lateness_seconds':jitter[56],'on_time':ontime,
             'measured_elements':sum(j['n']**2 for j in jobs),'warmup_elements':sum(j['n']**2 for j in raw['warmups']),
             'seconds_by_active_pipelines':dict(occupancy)}
        rows.append(row);lookup[(w['round'],w['rate'],w['concurrency'])]=row
    pairs=[]
    for rate in (10,40,100):
        ratios=[]
        for rnd in range(1,5):
            a,b=[lookup[(rnd,rate,c)] for c in (1,2)]
            ratio=b['p95_latency_seconds']/a['p95_latency_seconds'];ratios.append(ratio)
            pairs.append({'round':rnd,'rate':rate,'ratio':ratio,'cap1_p95_ms':1000*a['p95_latency_seconds'],
                          'cap2_p95_ms':1000*b['p95_latency_seconds']})
        checks.append({'rate':rate,'median_paired_p95_ratio':median(ratios),'cap2_faster_pairs':sum(v<1 for v in ratios),
                       'cap1_on_time':sum(lookup[(rnd,rate,1)]['on_time'] for rnd in range(1,5)),
                       'cap2_on_time':sum(lookup[(rnd,rate,2)]['on_time'] for rnd in range(1,5))})
    main=json.loads((root/'INDEPENDENT_ANALYSIS.json').read_text())
    comparisons=0
    for row,other in zip(rows,main['windows']):
        for key,other_value in [('window_id',other['window_id']),('p95_latency_seconds',other['nominal_offer_latency_seconds']['p95']),
                                ('p95_producer_lateness_seconds',other['producer_lateness_seconds']['p95']),('on_time',other['on_time_successes'])]:
            if row[key]!=other_value:raise ValueError('Independent recount mismatch: '+row['window_id']+' '+key)
            comparisons+=1
    for pair in pairs:
        other=next(p for p in main['pairs'] if p['round']==pair['round'] and p['rate']==pair['rate'])
        if pair['ratio']!=other['p95_ratio_cap2_over_cap1']:raise ValueError('Pair ratio mismatch')
        comparisons+=1
    return {'schema_version':1,'interpretation':'Independent descriptive timing/count recount of the saved fixed cohort; promotion gate belongs to frozen analyzer.',
            'comparison_count':comparisons,'mismatches':0,'measured_jobs':len(rows)*60,'warmup_jobs':len(rows)*3,
            'measured_output_elements':sum(r['measured_elements'] for r in rows),'warmup_output_elements':sum(r['warmup_elements'] for r in rows),
            'windows':rows,'pairs':pairs,'rates':checks,'input_sha256':inputs}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=recount(Path(__file__).resolve().parent)
    with args.output.open('x') as handle:json.dump(result,handle,indent=2,sort_keys=True);handle.write('\n')
    print(json.dumps({'comparison_count':result['comparison_count'],'mismatches':result['mismatches']}))
