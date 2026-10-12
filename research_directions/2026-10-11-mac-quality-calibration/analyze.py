"""Independent, offline recount of the bounded Mac answer-quality calibration.

No collector/scorer modules are imported, and no hardware or network is queried.
Passing means the saved finite calibration meets its contract; it is not a
population reliability estimate, performance comparison, or energy measurement.
"""
import argparse
import ast
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re

SCHEMA = {'type': 'object', 'properties': {'records': {'type': 'array', 'items': {
    'type': 'object', 'properties': {'id': {'type': 'string', 'pattern': '^R[0-9]{4}$'},
    'value': {'type': 'string', 'pattern': '^[0-9]{3}$'}}, 'required': ['id', 'value'],
    'additionalProperties': False}}}, 'required': ['records'], 'additionalProperties': False}
CAPS = {4: 192, 12: 512, 24: 1024}
USAGE = ('prompt_eval_count', 'eval_count', 'total_duration', 'load_duration', 'prompt_eval_duration', 'eval_duration')


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


def prompt_rows(prompt):
    """Parse actual input section, excluding the candidate-B demonstration."""
    if not isinstance(prompt, str) or prompt.count('\nInput records:\n') != 1:
        raise ValueError('missing/ambiguous input section in captured prompt')
    body = prompt.split('\nInput records:\n')[1]
    if not body.endswith('\nJSON answer:'):
        raise ValueError('missing exact answer delimiter')
    lines = body[:-len('\nJSON answer:')].splitlines()
    rows = []
    for line in lines:
        match = re.fullmatch(r'(R[0-9]{4}) value=([0-9]{3}) flag=(KEEP|DROP)', line)
        if not match:
            raise ValueError('malformed input record')
        rows.append(dict(zip(('id', 'value', 'flag'), match.groups())))
    ids = [r['id'] for r in rows]
    if not rows or len(set(ids)) != len(ids) or ids != sorted(ids):
        raise ValueError('empty, duplicate, or unordered input IDs')
    return rows


def gold(rows):
    return {'records': [{'id': row['id'], 'value': row['value']} for row in rows if row['flag'] == 'KEEP']}


def score_output(text, expected):
    try:
        answer = strict_json(text)
    except (ValueError, TypeError):
        return False
    if type(answer) is not dict or set(answer) != {'records'} or type(answer['records']) is not list:
        return False
    for item in answer['records']:
        if (type(item) is not dict or set(item) != {'id', 'value'}
                or type(item['id']) is not str or type(item['value']) is not str
                or not re.fullmatch(r'R[0-9]{4}', item['id'])
                or not re.fullmatch(r'[0-9]{3}', item['value'])):
            return False
    return answer == expected


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
    text = ''.join(content)
    api = (row.get('completed') is True and row.get('error') is None and row.get('http_status') == 200
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


def source_check(base, campaign, faults):
    config = read(base/'CONFIG.json', faults) or {}
    tasks = {}
    for part, repeats in (('development', 1), ('confirmation', 3)):
        jobs = read(base/(part+'.json'), faults)
        if type(jobs) is not list:
            faults.append('source tasks missing: '+part)
            jobs = []
        tasks[part] = jobs
        counts = Counter((j.get('input_rows'), j.get('keep_count')) for j in jobs)
        require(counts == Counter({(n,k):repeats for n in (32,96,192) for k in CAPS}), 'source cell composition mismatch: '+part, faults)
        ids = [j.get('request_id') for j in jobs]
        require(all(type(x) is str for x in ids) and len(set(ids)) == len(ids), 'source duplicate/non-string IDs: '+part, faults)
        for job in jobs:
            rows = job.get('rows', [])
            require(len(rows) == job.get('input_rows') and sum(r.get('flag') == 'KEEP' for r in rows) == job.get('keep_count')
                    and job.get('max_output_tokens') == CAPS.get(job.get('keep_count')),
                    'source job cell/cap mismatch: '+str(job.get('request_id')), faults)
            require(job.get('expected') == gold(rows), 'source expected answer differs from source rows', faults)
    require(not ({j['request_id'] for j in tasks['development']} & {j['request_id'] for j in tasks['confirmation']}), 'development/confirmation IDs overlap', faults)
    require(not ({json.dumps(j['rows'],sort_keys=True) for j in tasks['development']} & {json.dumps(j['rows'],sort_keys=True) for j in tasks['confirmation']}), 'development/confirmation input rows overlap', faults)
    constants = {}
    try:
        tree = ast.parse((base/'design.py').read_text())
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in ('INSTRUCTION','EXAMPLE'):
                constants[node.targets[0].id] = ast.literal_eval(node.value)
        require(all(type(constants.get(k)) is str for k in ('INSTRUCTION','EXAMPLE')), 'source prompt constants unavailable', faults)
    except (OSError, ValueError, SyntaxError) as error:
        faults.append('source prompt constants: '+str(error))
    freeze = read(base/'FREEZE.json', faults)
    if type(freeze) is dict and type(freeze.get('sha256')) is dict:
        for name, digest in freeze['sha256'].items():
            path = base/name
            if Path(name).is_absolute() or '..' in Path(name).parts:
                faults.append('unsafe frozen source path')
                continue
            try:
                require(hashlib.sha256(path.read_bytes()).hexdigest() == digest, 'source freeze mismatch: '+name, faults)
            except OSError:
                faults.append('missing frozen source: '+name)
        require({'CONFIG.json','development.json','confirmation.json','design.py','client.py','calibrate.py','server_control.py','clock_bridge.py','PROTOCOL.txt'} <= set(freeze['sha256']), 'source freeze omits required study files', faults)
        require(campaign.get('source_freeze_sha256') == hashlib.sha256((base/'FREEZE.json').read_bytes()).hexdigest(), 'campaign source freeze differs', faults)
    else:
        faults.append('missing valid source freeze')
    return config, tasks, constants


def stage_check(path, config, tasks, constants):
    faults = []
    part, candidate = path.name.split('-')
    jobs = tasks[part]
    by_id = {job['request_id']: job for job in jobs}
    stage = read(path/'STAGE.json', faults) or {}
    records, raw_pairs = [], {}
    for file in sorted(path.glob('*.json')):
        if file.name in ('STAGE.json','SERVER_CONTROL.json','WARMUP.json'):
            continue
        raw = read(file, faults)
        if type(raw) is not dict:
            continue
        rows = raw.get('requests')
        if type(rows) is not list or len(rows) != 1:
            faults.append(file.name+': raw request cardinality is not one')
            rows = rows if type(rows) is list else []
        for row in rows:
            local = []
            if type(row) is not dict:
                faults.append(file.name+': absent request row')
                continue
            request_id = row.get('request_id')
            job = by_id.get(request_id) if type(request_id) is str else None
            api, text = raw_api(raw, row, config.get('model'), local)
            expected = None
            try:
                parsed = prompt_rows(row.get('request_prompt'))
                expected = gold(parsed)
                require(job is not None and parsed == job['rows'], 'captured prompt rows differ from assigned source task', local)
                if job is not None:
                    prompt = constants.get('INSTRUCTION','') + (constants.get('EXAMPLE','') if candidate == 'B' else '') + 'Output schema: '+json.dumps(SCHEMA,separators=(',',':'))+'\nInput records:\n'+'\n'.join(f"{r['id']} value={r['value']} flag={r['flag']}" for r in job['rows'])+'\nJSON answer:'
                    require(row.get('request_prompt') == prompt, 'captured candidate prompt mismatch', local)
            except ValueError as error:
                local.append(str(error))
            require(job is not None and file.name == str(request_id)+'.json', 'unknown/misfiled request ID', local)
            require(row.get('request_model') == config.get('model'), 'captured request model absent/mismatched', local)
            require(row.get('request_format') == SCHEMA, 'captured structured schema differs', local)
            require(row.get('arrival_offset_s') == 0, 'serial job arrival offset not zero', local)
            margin = None
            if job is not None:
                require(row.get('request_options') == dict(config.get('options',{}),num_predict=job['max_output_tokens']), 'captured request options/cap differ', local)
                if api:
                    margin = config['context'] - row['final']['prompt_eval_count'] - job['max_output_tokens']
                    require(margin >= 128, 'insufficient observed context allowance', local)
                    require(row['final']['eval_count'] <= job['max_output_tokens'], 'output count exceeds configured cap', local)
            quality = api and expected is not None and score_output(text, expected)
            records.append(dict(request_id=request_id,raw_file=file.name,dispatched=number(row.get('dispatch_offset_s')),
                                api_completed=api,quality_pass=quality,observed_context_margin=margin,
                                output_tokens=row.get('final',{}).get('eval_count') if type(row.get('final')) is dict else None,
                                faults=local))
            faults.extend(file.name+': '+error for error in local)
            if type(request_id) is str:
                raw_pairs[request_id] = [raw.get('started_stamp'),raw.get('finished_stamp')]
    ids = [r['request_id'] for r in records]
    require(all(type(x) is str for x in ids) and len(set(str(x) for x in ids)) == len(ids), 'duplicate/non-string raw IDs', faults)
    entries = stage.get('requests', [])
    if type(entries) is not list:
        entries=[];faults.append('stage requests is not a list')
    entry_ids = [e.get('request_id') for e in entries]
    require(len(set(str(x) for x in entry_ids)) == len(entry_ids), 'duplicate stage-summary IDs', faults)
    original_ids = [j['request_id'] for j in jobs]
    require(entry_ids == original_ids[:len(entry_ids)], 'stage summaries do not follow frozen request order', faults)
    record_by_id = {r['request_id']:r for r in records if type(r['request_id']) is str}
    for entry in entries:
        record = record_by_id.get(entry.get('request_id'))
        require(record is not None, 'summary entry lacks raw capture', faults)
        if record is None:
            continue
        for key in ('api_completed','quality_pass','observed_context_margin','raw_file'):
            if key == 'quality_pass' and entry.get(key) is None and stage.get('status') != 'completed':
                continue  # Saved but not scored before an infrastructure abort.
            require(entry.get(key) == record[key], 'summary '+key+' differs from independent recount: '+record['request_id'], faults)
        if record['api_completed']:
            require(entry.get('output_tokens') == record['output_tokens'], 'summary output token count differs', faults)
    orphan = [r['request_id'] for r in records if r['request_id'] not in entry_ids]
    if orphan:
        faults.append('raw jobs omitted from stage summary: '+str(orphan))
    complete = stage.get('status') == 'completed'
    require(complete, 'stage not completed', faults)
    require(stage.get('candidate') == candidate and stage.get('planned') == len(jobs), 'stage assignment/planned count mismatch', faults)
    require(entry_ids == original_ids and all(type(x) is str for x in ids) and set(str(x) for x in ids) == set(original_ids), 'stage missing or extra offered jobs', faults)
    count = sum(r['quality_pass'] for r in records)
    passed = len(records) == len(jobs) and count == len(jobs)
    require(stage.get('quality_count') == count, 'stage reported quality count differs', faults)
    require(stage.get('gate_passed') is passed, 'stage reported gate differs', faults)
    try:
        stamps = stage.get('clock_stamps')
        diag = clock_check(stamps)
        require(diag['valid'], 'stage clock diagnostics fail', faults)
        supplied = stage.get('clock_diagnostics',{})
        require(supplied.get('valid') == diag['valid'] and all(same_number(supplied.get(k),diag[k]) for k in ('maximum_bracket_s','observed_offset_span_s')), 'reported clock diagnostics differ', faults)
        require(len(stamps) == 4*len(jobs)+2, 'stage clock stamp count differs', faults)
        if len(stamps) == 4*len(jobs)+2:
            for i, request_id in enumerate(original_ids):
                require(stamps[2+4*i:4+4*i] == raw_pairs.get(request_id), 'stage clock does not bind raw job: '+request_id, faults)
    except (ValueError, TypeError) as error:
        faults.append(str(error))
    warm = read(path/'WARMUP.json',faults)
    if type(warm) is dict and type(warm.get('requests')) is list and len(warm['requests']) == 1:
        ok, _ = raw_api(warm,warm['requests'][0],config.get('model'),faults)
        require(ok and warm['requests'][0].get('request_id') == 'warm', 'warmup not completed', faults)
    else:
        faults.append('warmup capture incomplete')
    controller_check(read(path/'SERVER_CONTROL.json',faults),config,path,original_ids,faults)
    return dict(name=path.name,reported_status=stage.get('status'),planned=len(jobs),raw_offered=len(records),
                dispatched=sum(r['dispatched'] for r in records),api_completed=sum(r['api_completed'] for r in records),
                exact_quality=count,summary_recorded=len(entries),summary_unscored_ids=[e.get('request_id') for e in entries if e.get('quality_pass') is None],orphan_raw_ids=orphan,
                missing_ids=[x for x in original_ids if x not in ids],valid_completed=complete and not faults,
                independent_quality_gate=passed,reported_stage=stage,records=records,faults=faults)


def analyze(base,capture):
    base,capture=Path(base),Path(capture)
    faults=[]
    campaign=read(capture/'CAMPAIGN.json',faults) or {}
    config,tasks,constants=source_check(base,campaign,faults)
    stages={}
    for path in sorted(capture.iterdir()):
        if not path.is_dir():
            continue
        if path.name not in ('development-A','development-B','confirmation-A','confirmation-B'):
            faults.append('unexpected stage directory: '+path.name);continue
        try:
            stages[path.name]=stage_check(path,config,tasks,constants)
        except (ValueError,TypeError,KeyError,IndexError,AttributeError) as error:
            faults.append('malformed stage '+path.name+': '+str(error))
    expected=[];selected=None;qualified=False;tree_complete=False
    for candidate in ('A','B'):
        name='development-'+candidate;expected.append(name);stage=stages.get(name)
        if stage is None or not stage['valid_completed']:
            break
        if stage['independent_quality_gate']:
            selected=candidate;name='confirmation-'+candidate;expected.append(name);confirmation=stages.get(name)
            if confirmation is not None and confirmation['valid_completed']:
                qualified=confirmation['independent_quality_gate'];tree_complete=True
            break
        if candidate == 'B':
            tree_complete=True
    missing=[name for name in expected if name not in stages]
    extra=sorted(set(stages)-set(expected))
    require(not missing,'missing required stages: '+str(missing),faults)
    require(not extra,'unexpected stages/fallback: '+str(extra),faults)
    valid_stages=[stages[name] for name in expected if name in stages]
    previous=None
    for stage in valid_stages:
        data=stage['reported_stage'];start,end=data.get('started_utc'),data.get('finished_utc')
        require(type(start) is str and type(end) is str and start<=end and (previous is None or previous<=start),'stage chronology invalid',faults)
        previous=end
    require(campaign.get('status') == 'completed' and tree_complete,'campaign incomplete/aborted',faults)
    require(campaign.get('selected') == selected,'campaign selected candidate differs',faults)
    require(campaign.get('qualified') is qualified,'campaign qualified flag differs',faults)
    require(campaign.get('stages') == [s['reported_stage'] for s in valid_stages], 'campaign stage snapshots missing/differ',faults)
    all_faults=faults+[stage['name']+': '+f for stage in stages.values() for f in stage['faults']]
    totals={}
    for part in ('development','confirmation','all'):
        chosen=[stage for name,stage in stages.items() if part=='all' or name.startswith(part+'-')]
        totals[part]={key:sum(stage[key] for stage in chosen) for key in ('planned','raw_offered','dispatched','api_completed','exact_quality','summary_recorded')}
    return dict(schema_version=1,evidence='offline independent raw calibration recount',qualified=qualified and not all_faults,
                data_complete_valid=not all_faults,selected=selected,expected_stages=expected,missing_stages=missing,extra_stages=extra,
                counts=totals,stages=[stages[name] for name in stages],faults=all_faults,
                limitations=['Finite synthetic quality gate only; no population reliability, latency, scheduling or energy claim.',
                             'Metadata, logs and captured payloads are saved evidence, not fresh hardware attestation.',
                             'Sampled clock checks cannot exclude unobserved jumps.',
                             'Raw offered counts count retained request rows; unseen attempts cannot be reconstructed.'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path);parser.add_argument('capture',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=analyze(args.source,args.capture)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ('qualified','data_complete_valid','selected','counts')}))

if __name__=='__main__':
    main()
