#!/usr/bin/env python3
"""Verify archived files and reproduce the stored-data summary without hardware."""
import hashlib
import json
from pathlib import Path
import analyze

BASE=Path(__file__).resolve().parent

def require(condition,message):
    if not condition:raise ValueError(message)

def main():
    manifest=json.loads((BASE/'FILE_SHA256.json').read_text())
    for name,digest in manifest.items():
        require(hashlib.sha256((BASE/name).read_bytes()).hexdigest()==digest,'Changed file: '+name)
    for frozen_name in ['PROTOCOL_FREEZE.json','AMENDMENT_01_FREEZE.json']:
        frozen=json.loads((BASE/frozen_name).read_text())
        for name,digest in frozen['sha256'].items():
            require(hashlib.sha256((BASE/name).read_bytes()).hexdigest()==digest,'Frozen source changed: '+name)
    prior=json.loads((BASE/'capture/preflight_abort/CAMPAIGN.json').read_text())
    current=json.loads((BASE/'capture/CAMPAIGN.json').read_text())
    aborted_dir=BASE/'capture/preflight_abort/window-02-p2'
    aborted=json.loads((aborted_dir/'RUN.json').read_text())
    require(prior['status']=='aborted' and len(prior['windows'])==1,'Prior abort not preserved')
    require(prior['windows'][0]==current['windows'][0],'First completed window changed')
    require(current.get('amendment')=='AMENDMENT_01' and current.get('prior_abort')=='preflight_abort/CAMPAIGN.json','Continuation provenance missing')
    require(aborted['status']=='aborted' and 'Address already in use' in aborted.get('error',''),'Wrong retained setup failure')
    require(sorted(x.name for x in aborted_dir.iterdir())==['RUN.json'],'Aborted setup has unaccounted offers or process output')
    result=analyze.analyze(BASE/'capture',BASE)
    encoded=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n'
    require(encoded==(BASE/'capture/SUMMARY.json').read_text(),'Summary is not byte-reproducible')
    counts=[];word_counts=[];reasons=set();tokens=set()
    for index,p in enumerate([1,2,2,1,1,2,2,1],1):
        data=json.loads((BASE/f'capture/window-{index:02d}-p{p}/REQUESTS.json').read_text())
        rows=data['requests']
        require([r['request_id'] for r in rows]==[f'r{i:02d}' for i in range(1,17)],'Missing offered row')
        # Independent direct endpoint recount; stream consistency is separately validated by analyze.
        count=sum(r['completed'] is True and r['terminal_offset_s']-r['arrival_offset_s']<=5 for r in rows)
        require(count==result['windows'][index-1]['on_time_count'],'Raw endpoint recount disagrees')
        counts.append(count)
        for row in rows:
            require(row['terminal_offset_s']==row['chunks'][-1]['offset_s'],'Terminal timestamp differs from final chunk')
            reasons.add(row['final'].get('done_reason'));tokens.add(row['final']['eval_count'])
            content=''.join(c['data'].get('response','') for c in row['chunks'])
            word_counts.append(len(content.split()))
    require(reasons=={'length'} and tokens=={64},'Capped-generation claim changed')
    require([min(word_counts),max(word_counts)]==[54,60],'Observed word-count range changed')
    require(not (BASE/'capture/preflight_abort/window-02-p2/REQUESTS.json').exists(),'Unreported replacement workload')
    print(json.dumps(dict(artifact_checks='passed',offered=128,on_time_by_window=counts,
                         output_word_range=[min(word_counts),max(word_counts)],terminal_reasons=sorted(reasons),
                         scientific_validity_screen=result['valid'],engineering_gate=result['gate']['passed']),sort_keys=True))

if __name__=='__main__':main()
