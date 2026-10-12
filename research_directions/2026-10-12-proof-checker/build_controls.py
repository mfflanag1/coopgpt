"""Freeze24 offline control proposals on12 distinct prospectively selected claims."""
from pathlib import Path
import hashlib,json
from contract import score
BASE=Path(__file__).resolve().parent

def main():
    cases=json.loads((BASE/'cases.json').read_text());controls=[]
    for label in ['supported','contradicted','insufficient']:
        chosen=[c for c in cases if c['label']==label][:4]
        for index,c in enumerate(chosen):
            good={'verdict':label,'evidence':[] if label=='insufficient' else c['acceptable_evidence'][0]}
            if label=='insufficient':
                group='unsupported_decisive';truth=next(p for p in c['components'] if p['support']);bad={'verdict':'supported' if index<2 else 'contradicted','evidence':truth['support'][0]}
            elif index<2:group='false_insufficient';bad={'verdict':'insufficient','evidence':[]}
            else:
                group='citation';truth=next(p for p in c['components'] if p['support']);bad={'verdict':label,'evidence':truth['support'][0]}
                if score(json.dumps(bad),c)['quality_pass']:
                    bad['evidence']=next(([p['id']] for p in c['passages'] if not score(json.dumps({'verdict':label,'evidence':[p['id']]}),c)['quality_pass']),[])
            for accept,obj in [(True,good),(False,bad)]:
                pair='pair_'+c['request_id'];key='c_'+hashlib.sha256(('coop-proof-control:'+pair+':'+str(accept)).encode()).hexdigest()[:20]
                controls.append(dict(request_id=key,pair_id=pair,case_id=c['request_id'],error_group=group,expected_accept=accept,candidate=obj))
    controls.sort(key=lambda r:hashlib.sha256(('control-order:'+r['request_id']).encode()).hexdigest())
    (BASE/'controls.json').write_text(json.dumps(controls,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
