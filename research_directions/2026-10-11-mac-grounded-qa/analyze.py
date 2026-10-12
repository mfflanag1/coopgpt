"""Independent offline Qwen SQuAD calibration recount; no model/scorer imports.

Qualification is a finite engineering gate, not a population reliability,
performance, energy, or economic-value claim. Raw orphan rows remain visible.
"""
import argparse
import ast
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import string

MODEL = 'qwen3:32b'
DIGEST = '030ee887880fc378860c2dd35101da424377520441ae4bfe7be6deff8ade7840'
SOURCE_SHA256 = '80a5225e94905956a6446d296ca1093975c4d3b3260f1d6c8f68bc2ab77182d8'
SCHEMA = {'type':'object','properties':{'answer':{'type':['string','null']}},
          'required':['answer'],'additionalProperties':False}
USAGE = ('prompt_eval_count','eval_count','total_duration','load_duration','prompt_eval_duration','eval_duration')
BANDS = ('short','medium','long')
LABELS = ('answerable','unanswerable')
WARM_PROMPT = 'Return one JSON object with answer set to the word ready. /no_think'

def pairs(items):
    out = {}
    for key, value in items:
        if key in out:
            raise ValueError('duplicate JSON key: ' + key)
        out[key] = value
    return out


def strict_json(text):
    def invalid(value):
        raise ValueError('nonfinite JSON constant: ' + value)
    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid)


def read(path, faults):
    try:
        return strict_json(path.read_text())
    except (OSError, ValueError, UnicodeError) as error:
        faults.append(str(path.name) + ': ' + str(error))
        return None


def require(value, message, faults):
    if not value:
        faults.append(message)
    return bool(value)


def number(x):
    return type(x) in (int, float) and math.isfinite(x)


def same_number(a, b):
    return number(a) and number(b) and abs(a - b) <= 1e-6


def stamp_parts(stamp):
    if type(stamp) is not dict:
        raise ValueError('missing paired stamp')
    b, w, a = (stamp.get(k) for k in ('monotonic_before_ns', 'wall_ns', 'monotonic_after_ns'))
    if any(type(x) is not int for x in (b, w, a)) or not 0 <= b <= a:
        raise ValueError('invalid paired-stamp integer bracket')
    return b, w, a


def clock_check(stamps):
    if type(stamps) is not list or len(stamps) < 2:
        raise ValueError('at least two paired stamps required')
    parts = [stamp_parts(x) for x in stamps]
    if any(y[0] < x[2] for x, y in zip(parts, parts[1:])):
        raise ValueError('paired stamps overlap or run backwards')
    width = max(a-b for b, w, a in parts) / 10**9
    span = (max(w-b for b, w, a in parts) - min(w-a for b, w, a in parts)) / 10**9
    return dict(valid=width <= .01 and span <= .05,
                maximum_bracket_s=width, observed_offset_span_s=span)


def raw_api(raw, row, model, faults):
    """Recount transport success separately from quality and provenance validity."""
    if type(row) is not dict:
        faults.append('missing raw request row')
        return False, ''
    chunks, final = row.get('chunks'), row.get('final')
    content = []
    offsets = []
    content_offsets = []
    structure = type(chunks) is list
    if structure:
        for chunk in chunks:
            if type(chunk) is not dict or type(chunk.get('data')) is not dict or not number(chunk.get('offset_s')):
                structure = False
                continue
            data = chunk['data']
            offsets.append(chunk['offset_s'])
            if 'response' in data and type(data['response']) is not str:
                structure = False
            if type(data.get('response')) is str and data['response']:
                content.append(data['response'])
                content_offsets.append(chunk['offset_s'])
            if 'error' in data:
                structure = False
            if data.get('model') != model or data.get('thinking', '') != '':
                structure = False
                faults.append('chunk model mismatch or unexpected thinking content')
    text = ''.join(content)
    api = (row.get('completed') is True and row.get('error') is None and row.get('http_status') == 200
           and row.get('deadline_exceeded') is False
           and structure and bool(text) and type(final) is dict and final.get('done') is True
           and final.get('model') == model
           and all(type(final.get(k)) is int and final[k] >= 0 for k in USAGE)
           and final.get('eval_count', 0) > 0)
    if api:
        require(chunks[-1]['data'] == final and all(c['data'].get('done') is not True for c in chunks[:-1]),
                'terminal chunk does not uniquely match final', faults)
        require(offsets == sorted(offsets), 'chunk offsets out of order', faults)
        d, f, t, e = (row.get('dispatch_offset_s'), row.get('first_content_offset_s'),
                      row.get('terminal_offset_s'), raw.get('elapsed_seconds'))
        require(all(number(v) for v in (d, f, t, e)) and 0 <= d <= f <= t <= e+1e-6,
                'request offsets invalid or outside collector interval', faults)
        require(all(number(d) and number(t) and d <= offset <= t for offset in offsets),
                'chunk outside dispatch/terminal bounds', faults)
        require(bool(content_offsets) and same_number(f, content_offsets[0]) and same_number(t, offsets[-1]),
                'recorded content/terminal time disagrees with chunks', faults)
    elif row.get('completed') is True:
        faults.append('reported API completion not supported by raw response')
    try:
        diagnostics = clock_check([raw.get('started_stamp'), raw.get('finished_stamp')])
        require(diagnostics['valid'], 'raw clock tolerances failed', faults)
        b, w, a = stamp_parts(raw['started_stamp'])
        eb, ew, ea = stamp_parts(raw['finished_stamp'])
        require(raw.get('epoch_monotonic_ns') == a, 'raw epoch differs from paired stamp', faults)
        require(same_number(raw.get('elapsed_seconds'), (eb-a)/10**9), 'raw elapsed duration inconsistent', faults)
    except (ValueError, KeyError) as error:
        faults.append(str(error))
    if raw.get('collection_incomplete') is True:
        faults.append('raw collector checkpoint is incomplete')
    return bool(api), text


def host_ok(state, allow_battery):
    if type(state) is not dict:
        return False
    sources = re.findall(r"(?m)^Now drawing from '(AC Power|Battery Power)'$", str(state.get('power', '')))
    percents = re.findall(r'(?m)^\s*-InternalBattery-\d+\b[^\n]*?[ \t](\d{1,3})%;', str(state.get('power', '')))
    if len(sources) != 1 or len(percents) != 1:
        return False
    source, percent = sources[0], int(percents[0])
    if state.get('power_source') != source or state.get('battery_percent') != percent:
        return False
    power = ((source == 'AC Power' and state.get('external_power_connected') is True)
             or (allow_battery is True and source == 'Battery Power'
                 and state.get('external_power_connected') is False and 60 <= percent <= 100))
    thermal = str(state.get('thermal', ''))
    cleaned = re.sub(r'(?im)^\s*(?:Note:\s*)?No (?:thermal warning level|performance warning level|CPU power status) has been recorded\s*$', '', thermal)
    return power and 'No thermal warning level has been recorded' in thermal and 'No performance warning level has been recorded' in thermal and not re.search(r'(?i)warning|thermal|CPU_Speed_Limit|Scheduler_Limit', cleaned)


def controller_check(meta, config, stage_dir, ids, faults):
    if type(meta) is not dict:
        faults.append('missing controller metadata')
        return
    require(meta.get('status') == 'completed' and meta.get('errors') == []
            and meta.get('clean_unload_verified') is True and meta.get('forced_stop', False) is False
            and meta.get('loaded_after_unload') == {'models': []}
            and type(meta.get('dedicated_server_returncode')) is int,
            'controller completion/clean unload not verified', faults)
    require(meta.get('model') == config.get('model') and meta.get('context') == config.get('context')
            and meta.get('parallel') == 1 and meta.get('runtime_parallel_values') == [1],
            'controller model/context/parallel mismatch', faults)
    require(meta.get('version', {}).get('version') == config.get('version', '0.20.0'), 'server version mismatch', faults)
    tag = meta.get('model_tag', {})
    require(tag.get('name') == config.get('model') and tag.get('digest') == config.get('digest'), 'tag/digest mismatch', faults)
    require(meta.get('options') == config.get('options') and meta.get('server_settings') == dict(config.get('server_settings_common', {}), OLLAMA_NUM_PARALLEL='1'), 'server/request settings mismatch', faults)
    require(meta.get('allow_battery_quality') == config.get('allow_battery_quality', False), 'power policy mismatch', faults)
    lock = config.get('lock', {})
    require(meta.get('lock_verification') == {k: lock.get(k) for k in ('binary_sha256', 'manifest_sha256')}, 'binary/manifest lock evidence mismatch', faults)
    pid = meta.get('dedicated_server_pid')
    require(type(pid) is int and pid > 0 and meta.get('dedicated_process_group') == pid, 'owned process-group evidence missing', faults)
    loaded = meta.get('loaded_checks', [])
    require(type(loaded) is list and len(loaded) >= 3, 'missing loaded-model checks', faults)
    for item in loaded if type(loaded) is list else []:
        models = item.get('response', {}).get('models', [])
        ok = type(models) is list and len(models) == 1 and type(models[0]) is dict
        if ok:
            m = models[0]
            ok = (m.get('name') == config.get('model') and m.get('digest') == config.get('digest')
                  and type(m.get('context_length')) is int and m['context_length'] == config.get('context')
                  and number(m.get('size_vram')) and m['size_vram'] > 0)
        require(ok, 'loaded model/context/GPU evidence mismatch', faults)
    for phase in ('before', 'after'):
        require(meta.get('original_endpoint_idle_'+phase) is True and host_ok(meta.get(phase), config.get('allow_battery_quality')),
                'controller host gate failed: '+phase, faults)
    checks = meta.get('host_checks', [])
    expected = [prefix+request_id for request_id in ids for prefix in ('before_', 'after_')]
    require(type(checks) is list and [x.get('phase') for x in checks] == expected, 'per-job host gates missing/duplicated/reordered', faults)
    for item in checks if type(checks) is list else []:
        require(item.get('passed') is True and item.get('original_endpoint_idle') is True
                and host_ok(item.get('state'), config.get('allow_battery_quality')), 'per-job host condition failed', faults)
    try:
        log = (stage_dir/'SERVER.log').read_text()
        parallel = sorted({int(n) for pattern in (r'n_seq_max\s*=\s*(\d+)', r'\bParallel[=:]\s*(\d+)', r'--parallel\s+(\d+)') for n in re.findall(pattern, log)})
        require(parallel == [1], 'runtime parallelism unsupported by log', faults)
        require(not re.search(r'(?i)truncat(?:e|ed|ing).*?(?:input|prompt)|(?:input|prompt).*?truncat', log), 'input/prompt truncation diagnostic', faults)
    except (OSError, UnicodeError) as error:
        faults.append('server log unavailable: '+str(error))

def normalize(text):
    text = ''.join(char for char in text.lower() if char not in string.punctuation)
    return ' '.join(re.sub(r'\b(a|an|the)\b', ' ', text, flags=re.UNICODE).split())


def f1(gold, prediction):
    g, p = normalize(gold).split(), normalize(prediction).split()
    if not g or not p:
        return float(g == p)
    common = sum((Counter(g) & Counter(p)).values())
    return 2.0 * common / (len(g) + len(p))


def score_output(text, job):
    result = dict(schema_valid=False, exact_match=False, f1=0.0, abstained=False,
                  official_exact_match=0, prediction=None)
    try:
        parsed = strict_json(text)
    except (ValueError, TypeError, RecursionError):
        return result
    if (type(parsed) is not dict or set(parsed) != {'answer'}
            or parsed['answer'] is not None and type(parsed['answer']) is not str):
        return result
    answer = parsed['answer']
    prediction = '' if answer is None else answer
    answers = [a['text'] for a in job['answers'] if normalize(a['text'])]
    if job['is_impossible']:
        answers = ['']
    if not answers:
        return result  # Invalid answerable source; source_check also records it.
    em = max(int(normalize(gold) == normalize(prediction)) for gold in answers)
    return dict(schema_valid=True, exact_match=(answer is None if job['is_impossible'] else answer is not None and bool(em)),
                f1=max(f1(gold, prediction) for gold in answers), abstained=answer is None,
                official_exact_match=em, prediction=answer)


def length_band(passage):
    n = len(passage)
    return 'short' if n < 600 else 'medium' if n < 1200 else 'long' if n <= 2400 else None


def prompt_for(job, instruction):
    return instruction + 'Passage:\n' + job['passage'] + '\nQuestion:\n' + job['question'] + '\nJSON answer:'


def gate_counts(jobs, records, part):
    """All assigned jobs remain denominators; no F1 substitution for strict EM."""
    per_cell = 2 if part == 'development' else 6
    total_min, label_min, band_min = (11, 5, 3) if part == 'development' else (33, 16, 10)
    by_id = {r['request_id']: r for r in records if type(r.get('request_id')) is str}
    ids = [j['request_id'] for j in jobs]
    correct_label = dict.fromkeys(LABELS, 0)
    correct_band = dict.fromkeys(BANDS, 0)
    correct_cell = {band+':'+label:0 for band in BANDS for label in LABELS}
    schema_count = correct = 0
    for job in jobs:
        row = by_id.get(job['request_id'], {})
        schema_count += row.get('schema_valid') is True
        ok = row.get('schema_valid') is True and row.get('exact_match') is True and row.get('api_completed') is True
        correct += ok
        label = 'unanswerable' if job['is_impossible'] else 'answerable'
        correct_label[label] += ok
        correct_band[job['length_band']] += ok
        correct_cell[job['length_band']+':'+label] += ok
    ids_match = (len(records) == len(jobs) == 6 * per_cell and len(set(ids)) == len(ids)
                 and Counter(r.get('request_id') for r in records) == Counter(ids))
    passed = (ids_match and schema_count == len(jobs) and correct >= total_min
              and all(x >= label_min for x in correct_label.values())
              and all(x >= band_min for x in correct_band.values())
              and all(x >= per_cell-1 for x in correct_cell.values()))
    return dict(passed=bool(passed), expected=len(jobs), observed=len(records), schema_valid=schema_count,
                exact_correct=correct, correct_by_label=correct_label, correct_by_length=correct_band,
                correct_by_cell=correct_cell, minimum_per_cell=per_cell-1,
                minimum_total=total_min, minimum_per_label=label_min, minimum_per_length=band_min)


def source_check(base, campaign, faults):
    config = read(base/'CONFIG.json', faults) or {}
    for key, wanted in [('model', MODEL), ('digest', DIGEST), ('context', 4096), ('think', False)]:
        require(config.get(key) == wanted and type(config.get(key)) is type(wanted), 'unsupported config '+key, faults)
    require(config.get('options') == dict(num_ctx=4096, num_predict=256, temperature=0, seed=0), 'unsupported fixed options', faults)
    require(type(config.get('allow_battery_quality', False)) is bool, 'invalid battery permission flag', faults)
    lock = read(base/'MODEL_LOCK.json', faults)
    lock = lock if type(lock) is dict else {}
    required_hashes = {key:lock.get(key) for key in ('binary_sha256', 'manifest_sha256')}
    require(config.get('lock') == required_hashes and lock.get('manifest_sha256') == DIGEST,
            'configured model lock differs from MODEL_LOCK/pinned digest', faults)
    manifest = read(base/'MODEL_MANIFEST.json', faults)
    try:
        require(hashlib.sha256((base/'MODEL_MANIFEST.json').read_bytes()).hexdigest() == DIGEST,
                'saved model manifest hash differs from pinned digest', faults)
    except OSError:
        faults.append('saved model manifest unavailable')
    descriptors = []
    if type(manifest) is dict and type(manifest.get('layers')) is list:
        descriptors = [manifest.get('config')] + manifest['layers']
    valid_descriptors = (len(descriptors) == 5 and all(type(item) is dict
        and type(item.get('digest')) is str and re.fullmatch(r'sha256:[0-9a-f]{64}', item['digest'])
        and type(item.get('size')) is int and item['size'] > 0 for item in descriptors))
    require(valid_descriptors, 'expected five manifest config/layer descriptors', faults)
    if valid_descriptors:
        expected_blobs = {item['digest']:item['size'] for item in descriptors}
        checks = lock.get('blob_checks')
        require(len(expected_blobs) == 5 and type(checks) is dict and set(checks) == set(expected_blobs),
                'saved blob verification digest set differs from manifest', faults)
        for digest, size in expected_blobs.items():
            check = checks.get(digest) if type(checks) is dict else None
            require(type(check) is dict and check.get('verified') is True
                    and type(check.get('bytes')) is int and check['bytes'] == size,
                    'saved blob hash/size verification missing or failed: '+digest, faults)
    constants = {}
    try:
        for node in ast.parse((base/'design.py').read_text()).body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in ('INSTRUCTION', 'SCHEMA'):
                constants[node.targets[0].id] = ast.literal_eval(node.value)
        require(type(constants.get('INSTRUCTION')) is str and constants.get('SCHEMA') == SCHEMA, 'prompt/schema constants unavailable or mismatched', faults)
    except (OSError, ValueError, SyntaxError) as error:
        faults.append('source prompt constants: '+str(error))
    official = read(base/'sources/dev-v2.0.json', faults) or {}
    source_jobs = {}
    try:
        require(hashlib.sha256((base/'sources/dev-v2.0.json').read_bytes()).hexdigest() == SOURCE_SHA256,
                'official source hash mismatch', faults)
        for article in official['data']:
            for paragraph in article['paragraphs']:
                for qa in paragraph['qas']:
                    if qa['id'] in source_jobs:
                        faults.append('duplicate official source ID')
                    source_jobs[qa['id']] = dict(title=article['title'], passage=paragraph['context'],
                        question=qa['question'], answers=qa['answers'], is_impossible=qa['is_impossible'])
    except (OSError, KeyError, TypeError) as error:
        faults.append('official source structure: '+str(error))
    tasks = {}
    for part, quota in [('development', 2), ('confirmation', 6)]:
        jobs = read(base/(part+'.json'), faults)
        if type(jobs) is not list or any(type(j) is not dict for j in jobs):
            jobs = [];faults.append('source tasks missing/malformed: '+part)
        tasks[part] = jobs
        counts = Counter((j.get('length_band'), j.get('is_impossible')) for j in jobs)
        require(counts == Counter({(band, impossible):quota for band in BANDS for impossible in (False, True)}),
                'source cell composition mismatch: '+part, faults)
        ids = [j.get('request_id') for j in jobs]
        require(all(type(x) is str and x for x in ids) and len(set(str(x) for x in ids)) == len(ids), 'duplicate/non-string source IDs: '+part, faults)
        passages = []
        for job in jobs:
            identifier = job.get('request_id')
            original = source_jobs.get(identifier)
            require(original is not None and all(job.get(k) == v for k, v in original.items()),
                    'job differs from official source: '+str(identifier), faults)
            passage = job.get('passage', '')
            if type(passage) is not str:
                faults.append('non-string source passage');continue
            passages.append(passage)
            require(job.get('qid') == identifier and job.get('max_output_tokens') == 256
                    and job.get('passage_chars') == len(passage) and job.get('length_band') == length_band(passage)
                    and job.get('context_sha256') == hashlib.sha256(passage.encode()).hexdigest()
                    and type(job.get('is_impossible')) is bool,
                    'source task metadata/cap mismatch: '+str(identifier), faults)
            answers = job.get('answers')
            if type(answers) is not list:
                faults.append('source answers malformed: '+str(identifier));continue
            for answer in answers:
                valid = (type(answer) is dict and type(answer.get('text')) is str and bool(answer['text'])
                         and type(answer.get('answer_start')) is int and answer['answer_start'] >= 0)
                require(valid and passage[answer['answer_start']:answer['answer_start']+len(answer['text'])] == answer['text'],
                        'source answer offset/text mismatch: '+str(identifier), faults)
            require((job.get('is_impossible') is True and not answers)
                    or (job.get('is_impossible') is False and any(type(a) is dict and type(a.get('text')) is str and normalize(a['text']) for a in answers)),
                    'answerability/gold metadata inconsistent: '+str(identifier), faults)
        require(len(passages) == len(set(passages)), 'source passage repeated within '+part, faults)
    for key in ('request_id', 'title', 'passage'):
        require(not ({j.get(key) for j in tasks['development']} & {j.get(key) for j in tasks['confirmation']}),
                'development/confirmation '+key+' overlap', faults)
    freeze = read(base/'FREEZE.json', faults)
    if type(freeze) is dict and type(freeze.get('sha256')) is dict:
        for name, digest in freeze['sha256'].items():
            if Path(name).is_absolute() or '..' in Path(name).parts:
                faults.append('unsafe frozen source path');continue
            try:
                require(hashlib.sha256((base/name).read_bytes()).hexdigest() == digest, 'source freeze mismatch: '+name, faults)
            except OSError:
                faults.append('missing frozen source: '+name)
        needed = {'CONFIG.json','MODEL_LOCK.json','MODEL_MANIFEST.json','development.json','confirmation.json','design.py','client.py',
                  'calibrate.py','server_control.py','clock_bridge.py','PROTOCOL.txt','sources/dev-v2.0.json'}
        require(needed <= set(freeze['sha256']), 'freeze omits required study files', faults)
        require(campaign.get('source_freeze_sha256') == hashlib.sha256((base/'FREEZE.json').read_bytes()).hexdigest(),
                'campaign source freeze differs', faults)
    else:
        faults.append('missing valid source freeze')
    return config, tasks, constants


def wire_check(row, config, prompt, cap, faults):
    require(row.get('request_model') == MODEL, 'captured request model differs', faults)
    require(row.get('request_think') is False, 'captured think is not false', faults)
    require(row.get('request_format') == SCHEMA, 'captured public schema differs', faults)
    require(row.get('request_options') == dict(config.get('options', {}), num_predict=cap), 'captured options/cap differ', faults)
    require(row.get('request_prompt') == prompt, 'captured canonical prompt differs', faults)
    require(type(row.get('arrival_offset_s')) in (int, float) and row.get('arrival_offset_s') == 0, 'serial arrival offset not zero', faults)


def stage_check(path, config, tasks, constants):
    faults = []
    part = path.name
    jobs = tasks[part]
    by_id = {job['request_id']:job for job in jobs}
    stage = read(path/'STAGE.json', faults) or {}
    records, raw_pairs = [], {}
    for file in sorted(path.glob('*.json')):
        if file.name in ('STAGE.json', 'SERVER_CONTROL.json', 'WARMUP.json'):
            continue
        raw = read(file, faults)
        if type(raw) is not dict:
            continue
        rows = raw.get('requests')
        if type(rows) is not list:
            faults.append(file.name+': missing request rows');continue
        require(len(rows) == 1, file.name+': raw request cardinality differs', faults)
        for row in rows:
            if type(row) is not dict:
                faults.append(file.name+': malformed raw row');continue
            local = []
            identifier = row.get('request_id')
            job = by_id.get(identifier) if type(identifier) is str else None
            api, text = raw_api(raw, row, MODEL, local)
            require(api, 'request API completion not verified', local)
            require(job is not None and file.name == str(identifier)+'.json', 'unknown/misfiled request ID', local)
            margin = None
            score = dict(schema_valid=False, exact_match=False, f1=0.0, abstained=False, official_exact_match=0, prediction=None)
            if job is not None:
                wire_check(row, config, prompt_for(job, constants.get('INSTRUCTION', '')), 256, local)
                if api:
                    margin = 4096-row['final']['prompt_eval_count']-256
                    require(margin >= 128, 'insufficient observed context allowance', local)
                    require(row['final']['eval_count'] <= 256, 'output exceeds token cap', local)
                    score = score_output(text, job)
            record = dict(request_id=identifier, raw_file=file.name, dispatched=number(row.get('dispatch_offset_s')),
                          api_completed=api, observed_context_margin=margin, **score,
                          title=job.get('title') if job else None, is_impossible=job.get('is_impossible') if job else None,
                          length_band=job.get('length_band') if job else None, passage_chars=job.get('passage_chars') if job else None,
                          output_tokens=row['final'].get('eval_count') if type(row.get('final')) is dict else None,
                          done_reason=row['final'].get('done_reason') if type(row.get('final')) is dict else None, faults=local)
            records.append(record)
            faults.extend(file.name+': '+error for error in local)
            if type(identifier) is str:
                raw_pairs[identifier] = [raw.get('started_stamp'), raw.get('finished_stamp')]
    ids = [r['request_id'] for r in records]
    require(all(type(x) is str for x in ids) and len(set(str(x) for x in ids)) == len(ids), 'duplicate/non-string raw IDs', faults)
    entries = stage.get('requests', [])
    if type(entries) is not list or any(type(e) is not dict for e in entries):
        entries = [];faults.append('stage requests malformed')
    entry_ids = [e.get('request_id') for e in entries]
    original_ids = [j['request_id'] for j in jobs]
    require(entry_ids == original_ids[:len(entry_ids)], 'stage summaries are not a frozen-order prefix', faults)
    record_by_id = {r['request_id']:r for r in records if type(r['request_id']) is str}
    for entry in entries:
        record = record_by_id.get(entry.get('request_id'))
        require(record is not None, 'summary entry lacks raw capture', faults)
        if record is None:
            continue
        keys = ('api_completed', 'schema_valid', 'exact_match', 'f1', 'abstained', 'observed_context_margin',
                'title', 'is_impossible', 'length_band', 'passage_chars', 'raw_file', 'output_tokens', 'done_reason')
        for key in keys:
            if stage.get('status') != 'completed' and entry.get(key) is None and key in ('schema_valid', 'exact_match', 'f1', 'abstained', 'observed_context_margin', 'output_tokens', 'done_reason'):
                continue
            equal = same_number(entry.get(key), record[key]) if key == 'f1' else entry.get(key) == record[key]
            require(equal, 'summary '+key+' differs: '+str(record['request_id']), faults)
    orphan = [x for x in ids if x not in entry_ids]
    if orphan:
        faults.append('raw jobs omitted from stage summary: '+str(orphan))
    complete = stage.get('status') == 'completed'
    require(complete, 'stage not completed', faults)
    require(stage.get('part') == part and stage.get('candidate') == MODEL and stage.get('planned') == len(jobs), 'stage assignment/planned count mismatch', faults)
    require(entry_ids == original_ids and Counter(ids) == Counter(original_ids), 'stage missing or extra offered jobs', faults)
    gate = gate_counts(jobs, records, part)
    count = sum(r['exact_match'] for r in records)
    if complete:
        require(stage.get('quality_count') == count, 'stage quality count differs', faults)
        require(stage.get('gate_passed') is gate['passed'], 'stage gate differs', faults)
    try:
        stamps = stage.get('clock_stamps')
        diag = clock_check(stamps)
        require(diag['valid'], 'stage clock diagnostics fail', faults)
        supplied = stage.get('clock_diagnostics', {})
        require(supplied.get('valid') == diag['valid'] and all(same_number(supplied.get(k), diag[k]) for k in ('maximum_bracket_s', 'observed_offset_span_s')), 'reported clock diagnostics differ', faults)
        require(len(stamps) == 4*len(jobs)+2, 'stage clock count differs', faults)
        if len(stamps) == 4*len(jobs)+2:
            for i, identifier in enumerate(original_ids):
                require(stamps[2+4*i:4+4*i] == raw_pairs.get(identifier), 'stage clock does not bind raw job: '+identifier, faults)
    except (ValueError, TypeError) as error:
        faults.append(str(error))
    warm = read(path/'WARMUP.json', faults)
    if type(warm) is dict and type(warm.get('requests')) is list and len(warm['requests']) == 1:
        row = warm['requests'][0]
        ok, _ = raw_api(warm, row, MODEL, faults)
        require(ok and row.get('request_id') == 'warm', 'warmup not completed', faults)
        wire_check(row, config, WARM_PROMPT, 32, faults)
    else:
        faults.append('warmup capture incomplete')
    controller_check(read(path/'SERVER_CONTROL.json', faults), config, path, original_ids, faults)
    return dict(name=part, reported_status=stage.get('status'), planned=len(jobs), raw_offered=len(records),
                dispatched=sum(r['dispatched'] for r in records), api_completed=sum(r['api_completed'] for r in records),
                exact_quality=count, schema_valid=sum(r['schema_valid'] for r in records), summary_recorded=len(entries),
                orphan_raw_ids=orphan, missing_ids=[x for x in original_ids if x not in ids],
                valid_completed=complete and not faults, independent_quality_gate=gate['passed'], gate=gate,
                reported_stage=stage, records=records, faults=faults)


def analyze(base, capture):
    base, capture = Path(base), Path(capture)
    faults = []
    campaign = read(capture/'CAMPAIGN.json', faults) or {}
    config, tasks, constants = source_check(base, campaign, faults)
    stages = {}
    for path in sorted(capture.iterdir()) if capture.is_dir() else []:
        if not path.is_dir():
            continue
        if path.name not in ('development', 'confirmation'):
            faults.append('unexpected stage directory: '+path.name);continue
        try:
            stages[path.name] = stage_check(path, config, tasks, constants)
        except (ValueError, TypeError, KeyError, IndexError, AttributeError) as error:
            faults.append('malformed stage '+path.name+': '+str(error))
    expected = ['development']
    selected = None
    qualified = tree_complete = False
    dev = stages.get('development')
    if dev is not None and dev['valid_completed']:
        if dev['independent_quality_gate']:
            selected = MODEL
            expected.append('confirmation')
            confirmation = stages.get('confirmation')
            if confirmation is not None and confirmation['valid_completed']:
                tree_complete = True
                qualified = confirmation['independent_quality_gate']
        else:
            tree_complete = True
    missing = [name for name in expected if name not in stages]
    extra = sorted(set(stages)-set(expected))
    require(not missing, 'missing required stages: '+str(missing), faults)
    require(not extra, 'unexpected stages/fallback: '+str(extra), faults)
    expected_saved = [stages[name] for name in expected if name in stages]
    previous = None
    for stage in expected_saved:
        data = stage['reported_stage']
        start, end = data.get('started_utc'), data.get('finished_utc')
        require(type(start) is str and type(end) is str and start <= end and (previous is None or previous <= start), 'stage chronology invalid', faults)
        previous = end
    require(campaign.get('status') == 'completed' and tree_complete, 'campaign incomplete/aborted', faults)
    require(campaign.get('selected') == selected, 'campaign selected model differs', faults)
    require(campaign.get('qualified') is qualified, 'campaign qualified flag differs', faults)
    require(campaign.get('stages') == [s['reported_stage'] for s in expected_saved], 'campaign stage snapshots missing/differ', faults)
    all_faults = faults+[s['name']+': '+f for s in stages.values() for f in s['faults']]
    totals = {}
    for part in ('development', 'confirmation', 'all'):
        chosen = [s for name, s in stages.items() if part == 'all' or name == part]
        totals[part] = {key:sum(s[key] for s in chosen) for key in ('planned', 'raw_offered', 'dispatched', 'api_completed', 'exact_quality', 'schema_valid', 'summary_recorded')}
    return dict(schema_version=1, evidence='independent saved raw QA recount', qualified=qualified and not all_faults,
                data_complete_valid=not all_faults, selected=selected, expected_stages=expected,
                missing_stages=missing, extra_stages=extra, counts=totals,
                source_planned={part:len(jobs) for part, jobs in tasks.items()},
                required_planned=sum(len(tasks[part]) for part in expected),
                stages=[stages[name] for name in ('development', 'confirmation') if name in stages], faults=all_faults,
                limitations=['Finite benchmark engineering gate; not a population reliability, speed, energy, or economic-value claim.',
                             'Official normalized F1 is diagnostic and never substitutes for strict unanswerable null or exact-match gates.',
                             'Model blob evidence is checked against the pinned saved manifest; live model blobs are not reread.',
                             'Saved metadata/clock checks are not live attestation or continuous host/clock monitoring.',
                             'Retained raw request rows, including orphans, are counted; unseen attempts cannot be reconstructed.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('capture', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.source, args.capture)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ('qualified', 'data_complete_valid', 'selected', 'counts')}))


if __name__ == '__main__':
    main()
