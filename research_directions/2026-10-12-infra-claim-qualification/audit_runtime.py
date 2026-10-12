"""Independent raw recount of the 24-case infrastructure qualification.

Only transport/controller/clock helpers are reused. The primary contract scorer
is neither imported nor executed. All offered cases remain in denominators.
"""
import argparse
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from transport_audit import (strict_json, read, require, number, same_number,
                             raw_api, clock_check, controller_check)

MODEL = 'qwen3:32b'
DIGEST = '030ee887880fc378860c2dd35101da424377520441ae4bfe7be6deff8ade7840'
LABELS = ('supported', 'contradicted', 'insufficient')
SCHEMA = {'type': 'object', 'properties': {
    'verdict': {'type': 'string', 'enum': list(LABELS)},
    'evidence': {'type': 'array', 'items': {'type': 'string'}, 'maxItems': 3, 'uniqueItems': True}},
    'required': ['verdict', 'evidence'], 'additionalProperties': False}
WARM_PROMPT = 'Return {"verdict":"insufficient","evidence":[]} exactly. /no_think'
SCORE_KEYS = ('schema_valid', 'verdict_correct', 'evidence_correct', 'quality_pass', 'prediction')


def score_output(text, job):
    result = dict(schema_valid=False, verdict_correct=False, evidence_correct=False,
                  quality_pass=False, prediction=None)
    try:
        parsed = strict_json(text)
    except (ValueError, TypeError, RecursionError):
        return result
    if (type(parsed) is not dict or set(parsed) != {'verdict', 'evidence'}
            or type(parsed['verdict']) is not str or parsed['verdict'] not in LABELS
            or type(parsed['evidence']) is not list or len(parsed['evidence']) > 3
            or any(type(x) is not str for x in parsed['evidence'])
            or len(set(parsed['evidence'])) != len(parsed['evidence'])):
        return result
    result.update(schema_valid=True, prediction=parsed,
                  verdict_correct=parsed['verdict'] == job['label'])
    evidence = set(parsed['evidence'])
    known = {p['id'] for p in job['passages']}
    if job['label'] == 'insufficient':
        correct = not evidence
    else:
        correct = (evidence <= known and evidence <= set(job['relevant_evidence'])
                   and any(set(required) <= evidence for required in job['acceptable_evidence']))
    result['evidence_correct'] = correct
    result['quality_pass'] = bool(result['verdict_correct'] and correct)
    return result


def prompt_for(job, instruction):
    return (instruction + '\nDocumentation packet:\n'
            + '\n\n'.join('[' + p['id'] + '] ' + p['text'] for p in job['passages'])
            + '\n\nClaim:\n' + job['claim'] + '\n\nJSON verdict:')


def gate_counts(jobs, records):
    by_id = {r['request_id']: r for r in records if type(r.get('request_id')) is str}
    correct = dict.fromkeys(LABELS, 0)
    schema_count = false_support = 0
    for job in jobs:
        row = by_id.get(job['request_id'], {})
        schema_count += row.get('schema_valid') is True
        ok = (row.get('api_completed') is True and row.get('schema_valid') is True
              and row.get('verdict_correct') is True and row.get('evidence_correct') is True
              and row.get('quality_pass') is True)
        correct[job['label']] += ok
        prediction = row.get('prediction')
        false_support += (type(prediction) is dict and prediction.get('verdict') == 'supported'
                          and job['label'] != 'supported')
    ids = [j['request_id'] for j in jobs]
    ids_match = (len(records) == len(jobs) == 24 and len(set(ids)) == 24
                 and Counter(r.get('request_id') for r in records) == Counter(ids)
                 and Counter(j['label'] for j in jobs) == Counter(dict.fromkeys(LABELS, 8)))
    quality = sum(correct.values())
    passed = (ids_match and schema_count == 24 and quality >= 22
              and correct['supported'] >= 7 and correct['contradicted'] >= 7
              and correct['insufficient'] == 8 and false_support == 0)
    return dict(passed=bool(passed), expected=len(jobs), observed=len(records), schema_valid=schema_count,
                quality_correct=quality, correct_by_label=correct, false_support=false_support,
                minimum_total=22, minimum_supported=7, minimum_contradicted=7, minimum_insufficient=8)


def source_check(base, campaign, faults):
    config = read(base / 'CONFIG.json', faults) or {}
    wanted = {'model': MODEL, 'digest': DIGEST, 'context': 4096, 'think': False,
              'budget_s': 1800, 'request_timeout_s': 90, 'max_output_tokens': 256}
    for key, value in wanted.items():
        require(config.get(key) == value and type(config.get(key)) is type(value),
                'unsupported config ' + key, faults)
    require(config.get('options') == dict(num_ctx=4096, num_predict=256, temperature=0, seed=0),
            'unsupported fixed options', faults)
    require(type(config.get('allow_battery_quality')) is bool, 'invalid battery flag', faults)
    lock = read(base / 'MODEL_LOCK.json', faults) or {}
    require(config.get('lock') == {k: lock.get(k) for k in ('binary_sha256', 'manifest_sha256')}
            and lock.get('manifest_sha256') == DIGEST, 'configured model lock mismatch', faults)
    manifest = read(base / 'MODEL_MANIFEST.json', faults) or {}
    try:
        require(hashlib.sha256((base / 'MODEL_MANIFEST.json').read_bytes()).hexdigest() == DIGEST,
                'saved manifest digest mismatch', faults)
    except OSError:
        faults.append('saved manifest missing')
    descriptors = [manifest.get('config')] + manifest.get('layers', [])
    checks = lock.get('blob_checks', {})
    require(len(descriptors) == 5 and all(type(d) is dict for d in descriptors),
            'manifest descriptor structure invalid', faults)
    expected_digests = set()
    for descriptor in descriptors:
        if type(descriptor) is not dict:
            continue
        digest, size = descriptor.get('digest'), descriptor.get('size')
        if type(digest) is not str:
            faults.append('invalid manifest digest'); continue
        expected_digests.add(digest)
        check = checks.get(digest, {})
        require(re.fullmatch(r'sha256:[0-9a-f]{64}', digest) and type(size) is int and size > 0
                and check.get('verified') is True and type(check.get('bytes')) is int
                and check['bytes'] == size, 'saved layer verification mismatch: ' + digest, faults)
    require(len(expected_digests) == 5 and set(checks) == expected_digests,
            'saved layer digest set mismatch', faults)
    constants = {}
    try:
        for node in ast.parse((base / 'contract.py').read_text()).body:
            if (isinstance(node, ast.Assign) and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id in ('INSTRUCTION', 'SCHEMA')):
                constants[node.targets[0].id] = ast.literal_eval(node.value)
        require(type(constants.get('INSTRUCTION')) is str and constants.get('SCHEMA') == SCHEMA,
                'source prompt/schema constants unavailable or mismatched', faults)
    except (OSError, ValueError, SyntaxError) as error:
        faults.append('source prompt constants: ' + str(error))
    jobs = read(base / 'cases.json', faults)
    if type(jobs) is not list:
        jobs = []; faults.append('case list malformed')
    ids = []
    labels = Counter()
    for job in jobs:
        if type(job) is not dict:
            faults.append('case malformed'); continue
        identifier = job.get('request_id')
        require(type(identifier) is str and re.fullmatch(r'[A-Za-z0-9_-]+', identifier),
                'unsafe/missing case ID', faults)
        ids.append(identifier)
        label = job.get('label')
        if type(label) is str:
            labels[label] += 1
        require(label in LABELS and type(job.get('source_id')) is str
                and type(job.get('claim')) is str and bool(job.get('claim')),
                'invalid case source/claim/label', faults)
        passages = job.get('passages')
        valid = type(passages) is list and bool(passages) and all(
            type(p) is dict and type(p.get('id')) is str and bool(p['id'])
            and type(p.get('text')) is str and bool(p['text']) for p in passages)
        require(valid, 'malformed passages for ' + str(identifier), faults)
        if not valid:
            continue
        known = {p['id'] for p in passages}
        require(len(known) == len(passages), 'duplicate passage IDs for ' + str(identifier), faults)
        accepted, relevant = job.get('acceptable_evidence'), job.get('relevant_evidence')
        require(type(relevant) is list and all(type(x) is str for x in relevant)
                and len(set(relevant)) == len(relevant) and set(relevant) <= known,
                'invalid relevant citations for ' + str(identifier), faults)
        if label == 'insufficient':
            require(accepted == [] and relevant == [], 'insufficient case has gold evidence', faults)
        else:
            require(type(accepted) is list and bool(accepted) and all(type(s) is list and 1 <= len(s) <= 3
                    and all(type(x) is str for x in s) and len(set(s)) == len(s)
                    and set(s) <= known and type(relevant) is list and set(s) <= set(relevant)
                    for s in accepted), 'invalid sufficient evidence sets for ' + str(identifier), faults)
    require(len(ids) == len(set(str(x) for x in ids)) == 24 and labels == Counter(dict.fromkeys(LABELS, 8)),
            '24 distinct cases/eight of each label required', faults)
    freeze = read(base / 'FREEZE.json', faults)
    if type(freeze) is dict and type(freeze.get('sha256')) is dict:
        for name, digest in freeze['sha256'].items():
            if Path(name).is_absolute() or '..' in Path(name).parts:
                faults.append('unsafe frozen source path'); continue
            try:
                require(hashlib.sha256((base / name).read_bytes()).hexdigest() == digest,
                        'source freeze mismatch: ' + name, faults)
            except OSError:
                faults.append('missing frozen source: ' + name)
        needed = {'CONFIG.json', 'MODEL_LOCK.json', 'MODEL_MANIFEST.json', 'cases.json', 'contract.py',
                  'collect.py', 'audit_runtime.py', 'transport_audit.py', 'client.py', 'server_control.py',
                  'clock_bridge.py', 'PROTOCOL.txt', 'SOURCE_MANIFEST.json'}
        require(needed <= set(freeze['sha256']), 'freeze omits required study files', faults)
        sources = read(base / 'SOURCE_MANIFEST.json', faults)
        require(type(sources) is list and bool(sources), 'source manifest malformed', faults)
        for source in sources if type(sources) is list else []:
            if type(source) is not dict:
                faults.append('source manifest entry malformed'); continue
            for file_key, digest_key in (('source_file', 'sha256'), ('license_file', 'license_sha256')):
                name, digest = source.get(file_key), source.get(digest_key)
                safe = (type(name) is str and not Path(name).is_absolute() and '..' not in Path(name).parts)
                require(safe and freeze['sha256'].get(name) == digest,
                        'source/license file missing from freeze or digest differs: ' + str(name), faults)
        require(campaign.get('source_freeze_sha256') == hashlib.sha256((base / 'FREEZE.json').read_bytes()).hexdigest(),
                'campaign source freeze differs', faults)
    else:
        faults.append('missing valid source freeze')
    return config, jobs, constants


def wire_check(row, config, prompt, cap, faults):
    require(row.get('request_model') == MODEL, 'captured request model differs', faults)
    require(row.get('request_think') is False, 'captured think is not false', faults)
    require(row.get('request_format') == SCHEMA, 'captured schema differs', faults)
    require(row.get('request_options') == dict(config.get('options', {}), num_predict=cap), 'captured options differ', faults)
    require(row.get('request_prompt') == prompt, 'captured canonical prompt differs', faults)
    require(number(row.get('arrival_offset_s')) and row['arrival_offset_s'] == 0, 'serial arrival not zero', faults)


def stage_check(path, config, jobs, constants):
    faults = []
    by_id = {job['request_id']: job for job in jobs}
    stage = read(path / 'STAGE.json', faults) or {}
    records, raw_pairs = [], {}
    for file in sorted(path.glob('*.json')):
        if file.name in ('STAGE.json', 'SERVER_CONTROL.json', 'WARMUP.json'):
            continue
        raw = read(file, faults)
        if type(raw) is not dict:
            continue
        rows = raw.get('requests')
        if type(rows) is not list:
            faults.append(file.name + ': missing request rows'); continue
        require(len(rows) == 1, file.name + ': raw cardinality differs', faults)
        for row in rows:
            if type(row) is not dict:
                faults.append(file.name + ': malformed raw row'); continue
            local = []
            identifier = row.get('request_id')
            job = by_id.get(identifier) if type(identifier) is str else None
            api, text = raw_api(raw, row, MODEL, local)
            require(api, 'request API completion not verified', local)
            require(job is not None and file.name == str(identifier) + '.json', 'unknown/misfiled ID', local)
            margin = None
            scored = dict(schema_valid=False, verdict_correct=False, evidence_correct=False,
                          quality_pass=False, prediction=None)
            if job is not None:
                wire_check(row, config, prompt_for(job, constants.get('INSTRUCTION', '')), 256, local)
                if api:
                    margin = 4096 - row['final']['prompt_eval_count'] - 256
                    require(margin >= 128, 'insufficient observed context allowance', local)
                    require(row['final']['eval_count'] <= 256, 'output exceeds token cap', local)
                    scored = score_output(text, job)
            record = dict(request_id=identifier, raw_file=file.name, dispatched=number(row.get('dispatch_offset_s')),
                          api_completed=api, observed_context_margin=margin, **scored,
                          source_id=job.get('source_id') if job else None, label=job.get('label') if job else None,
                          output_tokens=row['final'].get('eval_count') if type(row.get('final')) is dict else None,
                          done_reason=row['final'].get('done_reason') if type(row.get('final')) is dict else None,
                          faults=local)
            records.append(record)
            faults.extend(file.name + ': ' + error for error in local)
            if type(identifier) is str:
                raw_pairs[identifier] = [raw.get('started_stamp'), raw.get('finished_stamp')]
    ids = [r['request_id'] for r in records]
    require(all(type(x) is str for x in ids) and len(set(str(x) for x in ids)) == len(ids), 'duplicate/non-string raw IDs', faults)
    entries = stage.get('requests', [])
    if type(entries) is not list or any(type(e) is not dict for e in entries):
        entries = []; faults.append('stage requests malformed')
    entry_ids = [e.get('request_id') for e in entries]
    original_ids = [j['request_id'] for j in jobs]
    require(entry_ids == original_ids[:len(entry_ids)], 'stage summaries are not a frozen-order prefix', faults)
    record_by_id = {r['request_id']: r for r in records if type(r['request_id']) is str}
    for entry in entries:
        record = record_by_id.get(entry.get('request_id'))
        require(record is not None, 'summary entry lacks raw capture', faults)
        if record is None:
            continue
        for key in ('api_completed', 'source_id', 'label', 'raw_file', 'observed_context_margin',
                    'output_tokens', 'done_reason') + SCORE_KEYS:
            if (stage.get('status') != 'completed' and entry.get(key) is None
                    and key in SCORE_KEYS + ('observed_context_margin', 'output_tokens', 'done_reason')):
                continue
            require(entry.get(key) == record[key], 'summary ' + key + ' differs: ' + str(record['request_id']), faults)
    orphan = [x for x in ids if x not in entry_ids]
    if orphan:
        faults.append('raw jobs omitted from stage summary: ' + str(orphan))
    complete = stage.get('status') == 'completed'
    require(complete, 'stage not completed', faults)
    require(stage.get('part') == 'qualification' and stage.get('candidate') == MODEL
            and stage.get('planned') == len(jobs), 'stage assignment/planned count mismatch', faults)
    require(entry_ids == original_ids and Counter(ids) == Counter(original_ids), 'stage missing or extra offered jobs', faults)
    gate = gate_counts(jobs, records)
    count = sum(r['quality_pass'] for r in records)
    if complete:
        require(stage.get('quality_count') == count, 'stage quality count differs', faults)
        require(stage.get('gate_passed') is gate['passed'], 'stage gate differs', faults)
    try:
        stamps = stage.get('clock_stamps')
        diag = clock_check(stamps)
        require(diag['valid'], 'stage clock diagnostics fail', faults)
        supplied = stage.get('clock_diagnostics', {})
        require(supplied.get('valid') == diag['valid'] and all(same_number(supplied.get(k), diag[k])
                for k in ('maximum_bracket_s', 'observed_offset_span_s')), 'reported clock diagnostics differ', faults)
        require(len(stamps) == 4 * len(jobs) + 2, 'stage clock count differs', faults)
        if len(stamps) == 4 * len(jobs) + 2:
            for i, identifier in enumerate(original_ids):
                require(stamps[2+4*i:4+4*i] == raw_pairs.get(identifier), 'stage clock does not bind raw job: ' + identifier, faults)
    except (ValueError, TypeError) as error:
        faults.append(str(error))
    warm = read(path / 'WARMUP.json', faults)
    if type(warm) is dict and type(warm.get('requests')) is list and len(warm['requests']) == 1:
        row = warm['requests'][0]
        ok, _ = raw_api(warm, row, MODEL, faults)
        require(ok and row.get('request_id') == 'warm', 'warmup not completed', faults)
        wire_check(row, config, WARM_PROMPT, 32, faults)
    else:
        faults.append('warmup capture incomplete')
    controller_check(read(path / 'SERVER_CONTROL.json', faults), config, path, original_ids, faults)
    return dict(name='qualification', reported_status=stage.get('status'), planned=len(jobs), raw_offered=len(records),
                dispatched=sum(r['dispatched'] for r in records), api_completed=sum(r['api_completed'] for r in records),
                quality_correct=count, schema_valid=sum(r['schema_valid'] for r in records), summary_recorded=len(entries),
                orphan_raw_ids=orphan, missing_ids=[x for x in original_ids if x not in ids],
                valid_completed=complete and not faults, independent_quality_gate=gate['passed'], gate=gate,
                reported_stage=stage, records=records, faults=faults)


def analyze(base, capture):
    base, capture = Path(base), Path(capture)
    faults = []
    campaign = read(capture / 'CAMPAIGN.json', faults) or {}
    try:
        config, jobs, constants = source_check(base, campaign, faults)
    except (ValueError, TypeError, KeyError, AttributeError) as error:
        faults.append('malformed source: ' + str(error))
        config, jobs, constants = {}, [], {}
    stages = []
    for path in sorted(capture.iterdir()) if capture.is_dir() else []:
        if not path.is_dir():
            continue
        if path.name != 'qualification':
            faults.append('unexpected stage directory: ' + path.name); continue
        try:
            stages.append(stage_check(path, config, jobs, constants))
        except (ValueError, TypeError, KeyError, IndexError, AttributeError) as error:
            faults.append('malformed qualification stage: ' + str(error))
    require(len(stages) == 1, 'missing qualification stage', faults)
    valid = len(stages) == 1 and stages[0]['valid_completed']
    qualified = valid and stages[0]['independent_quality_gate']
    require(campaign.get('status') == 'completed' and valid, 'campaign incomplete/aborted', faults)
    require(campaign.get('selected') == MODEL, 'campaign selected model differs', faults)
    require(campaign.get('qualified') is qualified, 'campaign qualified flag differs', faults)
    require(campaign.get('stages') == [s['reported_stage'] for s in stages], 'campaign stage snapshots missing/differ', faults)
    if stages:
        data = stages[0]['reported_stage']
        chronology = [campaign.get('started_utc'), data.get('started_utc'),
                      data.get('finished_utc'), campaign.get('finished_utc')]
        require(all(type(s) is str for s in chronology) and chronology == sorted(chronology), 'campaign/stage chronology invalid', faults)
    all_faults = faults + [s['name'] + ': ' + f for s in stages for f in s['faults']]
    keys = ('planned', 'raw_offered', 'dispatched', 'api_completed', 'quality_correct', 'schema_valid', 'summary_recorded')
    return dict(schema_version=1, evidence='independent saved raw infrastructure-verification recount',
                qualified=bool(qualified and not all_faults), data_complete_valid=not all_faults,
                counts={k: sum(s[k] for s in stages) for k in keys}, stages=stages, faults=all_faults,
                limitations=['Finite authored-case engineering gate; not held-out population reliability, energy, or economic value.',
                             'Frozen labels and sufficient/relevant evidence sets are independently reviewed separately; this is a mechanical recount.',
                             'Saved layer and host metadata are checked, not live continuous attestation.',
                             'Orphan raw rows remain counted; unseen attempts cannot be reconstructed.'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('capture', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.source, args.capture)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n')
    print(json.dumps({k: result[k] for k in ('qualified', 'data_complete_valid', 'counts')}))
