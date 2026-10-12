"""Frozen, offline SQuAD 2.0 grounded-QA selection and calibration scoring.

Source answers never enter the wire payload. This benchmark is a service proxy,
not a representative support workload or a proof of economic value. The scorer
uses the official SQuAD normalization; this study additionally requires literal
JSON null for unanswerable questions and valid one-field JSON for every response.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import string

SOURCE_SHA256 = '80a5225e94905956a6446d296ca1093975c4d3b3260f1d6c8f68bc2ab77182d8'
ARTICLE_SEED = 'coop-qa-20261012:'
PHASE_SEEDS = {p:'coop-qa-20261012:'+p+':' for p in ('development','confirmation')}
LENGTH_BINS = ('short','medium','long')
LABELS = ('answerable','unanswerable')
CELLS = tuple((length,label) for length in LENGTH_BINS for label in LABELS)
PER_CELL = {'development':2,'confirmation':6}
MAX_OUTPUT_TOKENS = 256
SCHEMA = {'type':'object','properties':{'answer':{'type':['string','null']}},
          'required':['answer'],'additionalProperties':False}
INSTRUCTION = (
    'Answer the question using only the passage below. If the passage supports an answer, '
    'copy the minimal exact contiguous span that answers the question. If the passage does '
    'not support an answer, return null. Do not use outside knowledge or guess. '
    'Return exactly one JSON object with one field named answer, whose value is the copied '
    'string or null. Do not add an explanation or any other field.\n/no_think\n'
)


def strict_object(items):
    result = {}
    for key,value in items:
        if key in result:
            raise ValueError('duplicate JSON key: '+key)
        result[key] = value
    return result


def strict_json(text):
    def invalid(value):
        raise ValueError('nonfinite JSON value: '+value)
    return json.loads(text,object_pairs_hook=strict_object,parse_constant=invalid)


def normalize_answer(text):
    """Official SQuAD: lowercase, ASCII punctuation, English articles, whitespace."""
    text = ''.join(ch for ch in text.lower() if ch not in string.punctuation)
    text = re.sub(r'\b(a|an|the)\b',' ',text,flags=re.UNICODE)
    return ' '.join(text.split())


def token_f1(gold,prediction):
    g,p = normalize_answer(gold).split(),normalize_answer(prediction).split()
    if not g or not p:
        return float(g == p)
    shared = sum((Counter(g)&Counter(p)).values())
    return 2*shared/(len(g)+len(p)) if shared else 0.0


def length_bin(context):
    n = len(context)
    if n < 600:
        return 'short'
    if n < 1200:
        return 'medium'
    if n <= 2400:
        return 'long'
    return None


def validate_qa(context,qa):
    if type(context) is not str or not context:
        raise ValueError('missing passage')
    if type(qa) is not dict or type(qa.get('id')) is not str or not qa['id']:
        raise ValueError('invalid QA ID')
    if type(qa.get('question')) is not str or not qa['question'].strip():
        raise ValueError('empty question: '+qa['id'])
    if type(qa.get('is_impossible')) is not bool or type(qa.get('answers')) is not list:
        raise ValueError('invalid answerability metadata: '+qa['id'])
    if qa['is_impossible'] and qa['answers']:
        raise ValueError('unanswerable QA contains gold answers: '+qa['id'])
    for answer in qa['answers']:
        if type(answer) is not dict or type(answer.get('text')) is not str or type(answer.get('answer_start')) is not int:
            raise ValueError('malformed gold answer: '+qa['id'])
        text,start = answer['text'],answer['answer_start']
        if not text or start < 0 or context[start:start+len(text)] != text:
            raise ValueError('gold answer offset mismatch: '+qa['id'])
    if not qa['is_impossible'] and not any(normalize_answer(a['text']) for a in qa['answers']):
        raise ValueError('answerable QA lacks nonempty normalized gold: '+qa['id'])


def rank(seed,value):
    return hashlib.sha256((seed+value).encode('utf-8')).hexdigest()


def build_dataset(source):
    """Validate pinned source and deterministically select fresh article-split cases."""
    raw = Path(source).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError('source SHA256 mismatch')
    data = strict_json(raw)
    articles = data.get('data')
    if type(articles) is not list or len(articles) != 35:
        raise ValueError('expected 35 official development articles')
    titles = [a.get('title') for a in articles]
    if not all(type(t) is str and t for t in titles) or len(set(titles)) != 35:
        raise ValueError('invalid or duplicate article titles')
    ordered = sorted(titles,key=lambda t:(rank(ARTICLE_SEED,t),t))
    phase_titles = {'development':ordered[:12],'confirmation':ordered[12:]}
    title_phase = {t:p for p,group in phase_titles.items() for t in group}
    pools = {p:[] for p in phase_titles}
    seen_ids = set()
    source_counts = Counter()
    for article in articles:
        title = article['title'];phase = title_phase[title]
        for paragraph in article['paragraphs']:
            context = paragraph['context'];length = length_bin(context)
            for qa in paragraph['qas']:
                validate_qa(context,qa)  # Bad source data fails; never silently repaired.
                if qa['id'] in seen_ids:
                    raise ValueError('duplicate source QA ID: '+qa['id'])
                seen_ids.add(qa['id'])
                if length is None:
                    continue  # Prospective passage-length eligibility only.
                label = 'unanswerable' if qa['is_impossible'] else 'answerable'
                source_counts[(phase,length,label)] += 1
                pools[phase].append(dict(request_id=qa['id'],qid=qa['id'],title=title,
                    passage=context,context_sha256=hashlib.sha256(context.encode()).hexdigest(),
                    question=qa['question'],answers=qa['answers'],is_impossible=qa['is_impossible'],
                    label=label,length_band=length,passage_chars=len(context),max_output_tokens=MAX_OUTPUT_TOKENS))
    selected = {}
    for phase,pool in pools.items():
        # A single global ranking implements each cell's same hash ranking while
        # giving cross-cell duplicate contexts a deterministic first-ranked owner.
        ranked = sorted(pool,key=lambda job:(rank(PHASE_SEEDS[phase],job['qid']),job['qid']))
        counts = Counter();used_contexts = set();jobs = []
        for job in ranked:
            cell = (job['length_band'],job['label'])
            if counts[cell] >= PER_CELL[phase] or job['context_sha256'] in used_contexts:
                continue
            counts[cell] += 1;used_contexts.add(job['context_sha256']);jobs.append(job)
            if len(jobs) == 6*PER_CELL[phase]:
                break
        if counts != Counter({cell:PER_CELL[phase] for cell in CELLS}):
            raise ValueError('insufficient distinct eligible paragraphs: '+phase)
        selected[phase] = jobs
    dev,confirm = selected['development'],selected['confirmation']
    if ({j['context_sha256'] for j in dev}&{j['context_sha256'] for j in confirm}
            or {j['qid'] for j in dev}&{j['qid'] for j in confirm}):
        raise ValueError('cross-phase context/ID overlap')
    return dict(schema_version=1,source_sha256=SOURCE_SHA256,article_seed=ARTICLE_SEED,
        phase_seeds=PHASE_SEEDS,article_partition=phase_titles,selection_rule=
        'Global ascending SHA256(phase_seed + QA_ID); accept only unfilled cells and never-used paragraph text; quotas fixed before responses.',
        cells=[dict(length_band=n,label=l) for n,l in CELLS],per_cell=PER_CELL,
        eligible_qa_counts=[dict(phase=p,length_band=n,label=l,count=source_counts[(p,n,l)]) for p in PER_CELL for n,l in CELLS],
        development=dev,confirmation=confirm)


def wire_job(job):
    """Construct the only model payload; no source gold/label enters this object."""
    return dict(request_id=job['request_id'],arrival_offset_s=0,
        prompt=INSTRUCTION+'Passage:\n'+job['passage']+'\nQuestion:\n'+job['question']+'\nJSON answer:',
        max_output_tokens=MAX_OUTPUT_TOKENS,format=SCHEMA,think=False)


def score(text,job):
    """Strict study EM plus separately labeled official normalized EM/F1 diagnostics."""
    validate_qa(job['passage'],dict(id=job['request_id'],question=job['question'],
                                  is_impossible=job['is_impossible'],answers=job['answers']))
    invalid = dict(schema_valid=False,exact_match=False,official_exact_match=0,
                   f1=0.0,official_f1=0.0,abstained=False,prediction=None,literal_span=False)
    try:
        result = strict_json(text)
    except (ValueError,TypeError,UnicodeError,RecursionError):
        return invalid
    if type(result) is not dict or set(result) != {'answer'} or (result['answer'] is not None and type(result['answer']) is not str):
        return invalid
    value = result['answer'];prediction = '' if value is None else value
    golds = [a['text'] for a in job['answers'] if normalize_answer(a['text'])] or ['']
    em = max(int(normalize_answer(answer) == normalize_answer(prediction)) for answer in golds)
    primary = value is None if job['is_impossible'] else value is not None and bool(em)
    return dict(schema_valid=True,exact_match=bool(primary),official_exact_match=em,
                f1=max(token_f1(answer,prediction) for answer in golds),
                official_f1=max(token_f1(answer,prediction) for answer in golds),
                abstained=value is None,prediction=value,
                literal_span=type(value) is str and bool(value) and value in job['passage'])


def always_null_baseline(jobs):
    """Weak balanced-label floor only; not a competitive QA economic alternative."""
    values = [dict(request_id=j['request_id'],**score('{"answer":null}',j)) for j in jobs]
    return dict(name='always-null',interpretation='Weak abstention floor, not a competitive non-LLM service baseline.',
                offered=len(jobs),exact_correct=sum(v['exact_match'] for v in values),
                exact_accuracy=sum(v['exact_match'] for v in values)/len(jobs) if jobs else None,
                records=values)


def gate_details(entries,part):
    """Pure complete-cohort gate; identities are additionally bound by the collector.

    Each entry includes request_id, is_impossible, length_band, schema_valid and
    exact_match. Missing/duplicate/extra rows or malformed flags close the gate.
    Transport/host/context validity remains a separate mandatory collector gate.
    """
    if part not in PER_CELL:
        raise ValueError('unknown phase')
    expected = 6*PER_CELL[part]
    errors=[]
    if type(entries) is not list:
        entries=[];errors.append('entries is not a list')
    ids=[e.get('request_id') if type(e) is dict else None for e in entries]
    if (len(entries) != expected or not all(type(i) is str and i for i in ids)
            or len(set(str(i) for i in ids)) != len(ids)):
        errors.append('missing, duplicate, extra or malformed request IDs')
    safe=[]
    for entry in entries:
        if (type(entry) is not dict or type(entry.get('is_impossible')) is not bool
                or entry.get('length_band') not in LENGTH_BINS
                or type(entry.get('schema_valid')) is not bool
                or type(entry.get('exact_match')) is not bool
                or (entry['exact_match'] and not entry['schema_valid'])):
            errors.append('malformed/inconsistent scoring or cell metadata')
        else:
            safe.append(entry)
    cells=Counter((e['length_band'],'unanswerable' if e['is_impossible'] else 'answerable') for e in safe)
    if cells != Counter({cell:PER_CELL[part] for cell in CELLS}):
        errors.append('cohort cell composition differs')
    correct=sum(e['exact_match'] and e['schema_valid'] for e in safe)
    schemas=sum(e['schema_valid'] for e in safe)
    label_counts={label:sum(e['exact_match'] and e['schema_valid'] for e in safe
                           if e['is_impossible'] == (label=='unanswerable')) for label in LABELS}
    length_counts={length:sum(e['exact_match'] and e['schema_valid'] for e in safe
                             if e['length_band']==length) for length in LENGTH_BINS}
    total_min,label_min,length_min,cell_min=(11,5,3,1) if part=='development' else (33,16,10,5)
    cell_correct={(length,label):sum(e['exact_match'] and e['schema_valid'] for e in safe
                     if e['length_band']==length and e['is_impossible']==(label=='unanswerable'))
                  for length,label in CELLS}
    if schemas != expected:errors.append('not every response is schema-valid')
    if correct < total_min:errors.append('total exact-match threshold failed')
    if any(label_counts[label] < label_min for label in LABELS):errors.append('answerability subgroup threshold failed')
    if any(length_counts[length] < length_min for length in LENGTH_BINS):errors.append('length subgroup threshold failed')
    if any(cell_correct[cell] < cell_min for cell in CELLS):errors.append('crossed length/answerability cell threshold failed')
    return dict(phase=part,passed=not errors,expected=expected,observed=len(entries),schema_valid=schemas,
                exact_correct=correct,correct_by_label=label_counts,correct_by_length=length_counts,
                correct_by_cell=[dict(length_band=n,label=l,correct=cell_correct[(n,l)]) for n,l in CELLS],
                minimum_total=total_min,minimum_per_label=label_min,minimum_per_length=length_min,minimum_per_cell=cell_min,errors=errors,
                scope='Finite benchmark engineering gate; not a population 90% reliability claim.')


def gate(entries,part):
    return gate_details(entries,part)['passed']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();data=build_dataset(args.source)
    args.out.mkdir(parents=True,exist_ok=False)
    for phase in PER_CELL:
        (args.out/(phase+'.json')).write_text(json.dumps(data[phase],indent=2,sort_keys=True,allow_nan=False)+'\n')
    metadata={k:v for k,v in data.items() if k not in PER_CELL}
    (args.out/'SELECTION.json').write_text(json.dumps(metadata,indent=2,sort_keys=True)+'\n')
    baselines={p:always_null_baseline(data[p]) for p in PER_CELL}
    (args.out/'BASELINE.json').write_text(json.dumps(baselines,indent=2,sort_keys=True)+'\n')
    print(json.dumps({p:len(data[p]) for p in PER_CELL}))

if __name__=='__main__':main()
