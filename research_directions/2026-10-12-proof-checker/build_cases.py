"""Deterministic compilation of prospectively adjudicated two-component claims."""
from pathlib import Path
import json,hashlib
from contract import aggregate_gold
BASE=Path(__file__).resolve().parent

def main():
    cases=[]
    for item in json.loads((BASE/'AUTHOR_CASES.json').read_text()):
        parts=item['components'];claim='Both statements hold: (a1) '+parts[0]['claim']+' (a2) '+parts[1]['claim']
        key=hashlib.sha256(('coop-proof-check-20261012:'+item['source_id']+':'+claim).encode()).hexdigest()[:20]
        label,proofs,relevant=aggregate_gold(parts)
        cases.append(dict(request_id=key,author_id=item['author_id'],source_id=item['source_id'],claim=claim,components=parts,passages=item['passages'],label=label,acceptable_evidence=proofs,relevant_evidence=relevant,rationale=item['rationale'],max_output_tokens=256))
    cases.sort(key=lambda c:hashlib.sha256(('order:'+c['request_id']).encode()).hexdigest())
    (BASE/'cases.json').write_text(json.dumps(cases,indent=2,sort_keys=True)+'\n')
    blind=[dict(request_id=c['request_id'],source_id=c['source_id'],claim=c['claim'],components=[{k:p[k] for k in ['id','claim']} for p in c['components']],passages=c['passages']) for c in cases]
    (BASE/'BLIND_CASES.json').write_text(json.dumps(blind,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
