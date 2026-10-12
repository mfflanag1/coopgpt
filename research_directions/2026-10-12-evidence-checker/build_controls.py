"""Fixed prospective paired stress cases, selected before all model responses."""
from pathlib import Path
import hashlib,json
BASE=Path(__file__).resolve().parent
CHOICES=[('K-03','missing_premise','supported',['D1']),('T-04','missing_premise','supported',['D1','D2']),('R-04','missing_premise','contradicted',['D1']),('V-04','missing_premise','contradicted',['D1']),('A-01','wrong_verdict','contradicted',['D1','D2']),('T-02','wrong_verdict','contradicted',['D1']),('K-02','wrong_verdict','supported',['D1']),('V-02','wrong_verdict','supported',['D1']),('R-01','citation','supported',['D1']),('L-01','citation','supported',['D1']),('A-03','citation','contradicted',['D3']),('L-03','citation','contradicted',['D2'])]
def main():
    by={c['author_id']:c for c in json.loads((BASE/'cases.json').read_text())};controls=[]
    for aid,group,verdict,ids in CHOICES:
        case=by[aid];pair='pair_'+case['request_id']
        good={'verdict':case['label'],'evidence':[] if case['label']=='insufficient' else case['acceptable_evidence'][0]}
        bad={'verdict':verdict,'evidence':ids}
        for accept,candidate in [(True,good),(False,bad)]:
            key=hashlib.sha256(('coop-control:'+pair+':'+str(accept)).encode()).hexdigest()[:20]
            controls.append(dict(request_id='c_'+key,case_id=case['request_id'],pair_id=pair,error_group=group,expected_accept=accept,candidate=candidate))
    controls.sort(key=lambda x:hashlib.sha256(('checker-order:'+x['request_id']).encode()).hexdigest())
    (BASE/'controls.json').write_text(json.dumps(controls,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
