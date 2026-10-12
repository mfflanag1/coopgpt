"""Fixed cheap descriptive comparisons; no learned classification or outcome tuning."""
from pathlib import Path
import json,re
STOP=set('a an the is are to of for and or in on with our by that this it its be as can from'.split())
def tokens(text):return set(re.findall(r'[a-z0-9_]+',text.lower()))-STOP
def evaluate(cases):
    rows=[]
    for job in cases:
        q=tokens(job['claim'])
        # Jaccard similarity penalizes long catch-all blocks; ties by fixed ID.
        def rank(p):
            t=tokens(p['text']);return (-len(q&t)/max(1,len(q|t)),p['id'])
        predicted=[p['id'] for p in sorted(job['passages'],key=rank)[:3]]
        known=job['label']!='insufficient'
        coverage=any(set(proof)<=set(predicted) for proof in job['acceptable_evidence']) if known else None
        rows.append(dict(request_id=job['request_id'],gold_label=job['label'],always_insufficient_correct=not known,lexical_top3=predicted,complete_proof_covered=coverage,all_citations_relevant=set(predicted)<=set(job['relevant_evidence']) if known else None))
    return dict(always_insufficient=dict(correct=sum(r['always_insufficient_correct'] for r in rows),total=len(rows),meaning='Weak verdict-only floor, not a useful citation-aware assistant.'),lexical_top3=dict(covered=sum(r['complete_proof_covered'] is True for r in rows),decisive_cases=sum(r['complete_proof_covered'] is not None for r in rows),fully_relevant=sum(r['all_citations_relevant'] is True for r in rows),meaning='Proof-location diagnostic only; supplies no three-way verdict and is not a competitive full-task baseline.'),records=rows)
if __name__=='__main__':
    base=Path(__file__).resolve().parent
    result=evaluate(json.loads((base/'cases.json').read_text()))
    (base/'BASELINE.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='records'}))
