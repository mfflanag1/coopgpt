"""Independent saved-data audit of the 24 primary + 48 checker experiment.

The primary contract is never imported or executed. Only its frozen public prompt
constants are read with AST literal evaluation; transport/host helpers are reused.
"""
import argparse
import ast
from collections import Counter
from datetime import datetime
import hashlib
import html
import json
from pathlib import Path
import re
from transport_audit import read, require, number, same_number, raw_api, clock_check, controller_check

MODEL = 'qwen3:32b'
DIGEST = '030ee887880fc378860c2dd35101da424377520441ae4bfe7be6deff8ade7840'
LABELS = ('supported', 'contradicted', 'insufficient')
SCHEMA = {'type': 'object', 'properties': {
    'verdict': {'type': 'string', 'enum': list(LABELS)},
    'evidence': {'type': 'array', 'items': {'type': 'string'}, 'maxItems': 3, 'uniqueItems': True}},
    'required': ['verdict', 'evidence'], 'additionalProperties': False}
CHECK_SCHEMA = {'type': 'object', 'properties': {'accept': {'type': 'boolean'}},
                'required': ['accept'], 'additionalProperties': False}
WARM_PROMPT = 'Return {"accept":false} exactly. /no_think'
NEEDED = {'CONFIG.json', 'MODEL_LOCK.json', 'MODEL_MANIFEST.json', 'cases.json', 'controls.json',
          'PRIOR_CLAIMS.json', 'contract.py', 'collect.py', 'audit_runtime.py', 'transport_audit.py',
          'client.py', 'server_control.py', 'clock_bridge.py', 'PROTOCOL.txt', 'SOURCE_MANIFEST.json'}


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate key')
            result[key] = value
        return result
    def nonfinite(value):
        raise ValueError('nonfinite constant: ' + value)
    return json.loads(text, object_pairs_hook=pairs, parse_constant=nonfinite)


def score_output(text, job):
    result = dict(schema_valid=False, verdict_correct=False, evidence_correct=False,
                  quality_pass=False, prediction=None)
    try:
        obj = strict_json(text)
    except (ValueError, TypeError, UnicodeError, RecursionError):
        return result
    if (type(obj) is not dict or set(obj) != {'verdict', 'evidence'}
            or type(obj['verdict']) is not str or obj['verdict'] not in LABELS
            or type(obj['evidence']) is not list or len(obj['evidence']) > 3
            or any(type(x) is not str for x in obj['evidence'])
            or len(set(obj['evidence'])) != len(obj['evidence'])):
        return result
    ids = set(obj['evidence'])
    evidence = (not ids if job['label'] == 'insufficient' else
                ids <= {p['id'] for p in job['passages']} and ids <= set(job['relevant_evidence'])
                and any(set(proof) <= ids for proof in job['acceptable_evidence']))
    verdict = obj['verdict'] == job['label']
    return dict(schema_valid=True, verdict_correct=verdict, evidence_correct=bool(evidence),
                quality_pass=bool(verdict and evidence), prediction=obj)


def parse_checker(text):
    try:
        obj = strict_json(text)
    except (ValueError, TypeError, UnicodeError, RecursionError):
        obj = None
    valid = type(obj) is dict and set(obj) == {'accept'} and type(obj['accept']) is bool
    return dict(schema_valid=valid, accept=obj['accept'] if valid else False)


def quality_summary(cases, controls, primary_answers, checker_answers):
    """Fixed offered denominators; schema referral is not a semantic catch."""
    natural, controlled = [], []
    expected = {'n_' + c['request_id'] for c in cases} | {c['request_id'] for c in controls}
    complete = (len(cases) == len(controls) == 24
                and set(primary_answers) == {c['request_id'] for c in cases}
                and set(checker_answers) == expected and len(expected) == 48)
    for case in cases:
        key = case['request_id']
        baseline = score_output(primary_answers.get(key, ''), case)
        checker = parse_checker(checker_answers.get('n_' + key, ''))
        automatic = baseline['schema_valid'] and checker['schema_valid'] and checker['accept']
        good = baseline['quality_pass']
        natural.append(dict(case_id=key, label=case['label'], baseline=baseline, checker=checker,
                            automatic=automatic, retained_correct=automatic and good,
                            accepted_error=automatic and not good,
                            semantic_catch=baseline['schema_valid'] and not good and
                            checker['schema_valid'] and not checker['accept'],
                            format_referral=not baseline['schema_valid'], lost_correct=good and not automatic))
    for item in controls:
        checker = parse_checker(checker_answers.get(item['request_id'], ''))
        controlled.append(dict(request_id=item['request_id'], pair_id=item['pair_id'],
                               case_id=item['case_id'], error_group=item['error_group'],
                               expected_accept=item['expected_accept'], checker=checker,
                               correct_decision=checker['schema_valid'] and
                               checker['accept'] is item['expected_accept']))
    baseline = sum(r['baseline']['quality_pass'] for r in natural)
    retained = sum(r['retained_correct'] for r in natural)
    accepted_errors = sum(r['accepted_error'] for r in natural)
    rejected_bad = sum(r['correct_decision'] for r in controlled if not r['expected_accept'])
    retained_good = sum(r['correct_decision'] for r in controlled if r['expected_accept'])
    schemas = sum(r['checker']['schema_valid'] for r in natural + controlled)
    native_gate = accepted_errors == 0 and retained >= 18 and 10 * retained >= 9 * baseline
    control_gate = rejected_bad == 12 and retained_good >= 11
    return dict(input_complete=complete, engineering_gate_passed=bool(complete and schemas == 48 and
                native_gate and control_gate), native_gate_passed=native_gate,
                control_gate_passed=control_gate, checker_schema_valid=schemas,
                baseline_correct=baseline, baseline_errors=24-baseline,
                baseline_schema_valid=sum(r['baseline']['schema_valid'] for r in natural),
                automatic_correct=retained, automatic_errors=accepted_errors,
                automatic_total=sum(r['automatic'] for r in natural),
                referrals=24-sum(r['automatic'] for r in natural), correct_referred=baseline-retained,
                format_referrals=sum(r['format_referral'] for r in natural),
                checker_accepted_malformed=sum(not r['baseline']['schema_valid'] and
                    r['checker']['schema_valid'] and r['checker']['accept'] for r in natural),
                semantic_errors_caught=sum(r['semantic_catch'] for r in natural),
                native_sensitivity_observed=any(r['baseline']['schema_valid'] and
                                               not r['baseline']['quality_pass'] for r in natural),
                constructed_invalid_rejected=rejected_bad, constructed_valid_retained=retained_good,
                correct_automatic_per_offered=retained/24, baseline_correct_per_offered=baseline/24,
                natural=natural, controlled=controlled)


def prompt_for(case, constants, proposal=None):
    instruction = constants['INSTRUCTION' if proposal is None else 'CHECK_INSTRUCTION']
    text = (instruction + '\nDocumentation packet:\n'
            + '\n\n'.join('[' + p['id'] + '] ' + p['text'] for p in case['passages'])
            + '\n\nClaim:\n' + case['claim'])
    return text + ('\n\nJSON verdict:' if proposal is None else
                   '\n\nProposed answer:\n' + proposal + '\n\nAudit JSON:')


def order_for(cases, controls):
    checker = ['n_' + c['request_id'] for c in cases] + [c['request_id'] for c in controls]
    return (['p_' + c['request_id'] for c in cases]
            + sorted(checker, key=lambda x: hashlib.sha256(('checker-order:' + x).encode()).hexdigest()))



def checker_duplicate_diagnostics(rows, proposal_contexts=None):
    """Group inputs only; never deduplicate calls or alter acceptance decisions.

    JSON-equivalent proposals ignore whitespace/object-key order, preserve array
    order, and require all remaining prompt text and payload fields to match.
    stream/keep_alive are fixed fields from the frozen collector client.
    """
    contexts = proposal_contexts or {}
    exact, equivalent = {}, {}
    unavailable, unparsed = [], []
    canonical = lambda obj: json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False)
    for row in rows:
        identifier = row.get('request_id')
        try:
            if (type(row['request_prompt']) is not str or type(row['request_model']) is not str
                    or type(row['request_options']) is not dict or type(row['request_format']) is not dict
                    or type(row['request_think']) is not bool):
                raise ValueError('captured wire fields unavailable')
            payload = dict(model=row['request_model'], prompt=row['request_prompt'],
                           options=row['request_options'], format=row['request_format'],
                           think=row['request_think'], stream=True, keep_alive='120s')
            key = canonical(payload)
            exact.setdefault(key, []).append(identifier)
        except (KeyError, ValueError, TypeError, RecursionError):
            unavailable.append(identifier)
            continue
        try:
            prefix, suffix = contexts[identifier]
            prompt = payload['prompt']
            if not prompt.startswith(prefix) or not prompt.endswith(suffix):
                raise ValueError('proposal delimiters differ')
            proposal = prompt[len(prefix):len(prompt)-len(suffix)]
            parsed = strict_json(proposal)
            # Keep the complete non-proposal prompt, schema and options in this key.
            normalized = dict(payload, prompt=dict(prefix=prefix, proposal_json=parsed, suffix=suffix))
            equivalent.setdefault(canonical(normalized), []).append(identifier)
        except (KeyError, ValueError, TypeError, UnicodeError, RecursionError):
            unparsed.append(identifier)
    def describe(groups):
        duplicates = [dict(payload_sha256=hashlib.sha256(key.encode()).hexdigest(),
                           request_ids=sorted(ids), calls=len(ids), excess_calls=len(ids)-1)
                      for key, ids in sorted(groups.items()) if len(ids) > 1]
        return dict(input_rows=sum(map(len, groups.values())), unique_inputs=len(groups),
                    duplicate_group_count=len(duplicates),
                    calls_in_duplicate_groups=sum(x['calls'] for x in duplicates),
                    excess_duplicate_calls=sum(x['excess_calls'] for x in duplicates), groups=duplicates)
    return dict(diagnostic_only=True, planned_checker_calls=48, observed_checker_rows=len(rows),
                exact_payload=describe(exact), proposal_json_equivalence=describe(equivalent),
                unavailable_wire_request_ids=unavailable, unavailable_proposal_json_request_ids=unparsed,
                definition='Exact captured prompt plus model/options/schema/think and frozen stream=true, keep_alive=120s. '
                           'Proposal JSON equivalence ignores whitespace/object-key order, preserves array order, '
                           'and includes exact remaining prompt and payload; these groups also include exact duplicates. '
                           'All calls remain in scoring denominators.')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc(text):
    value = datetime.fromisoformat(text.replace('Z', '+00:00'))
    if value.tzinfo is None:
        raise ValueError('timezone missing')
    return value


def validate_controls(cases, controls, faults):
    by_id = {c['request_id']: c for c in cases}
    require(type(controls) is list and len(controls) == 24, '24 controls required', faults)
    pairs = {}
    for c in controls:
        require(bool(re.fullmatch(r'c_[0-9a-f]{20}', c['request_id'])) and
                c['case_id'] in by_id and type(c['expected_accept']) is bool,
                'invalid control assignment', faults)
        case = by_id[c['case_id']]
        scored = score_output(json.dumps(c['candidate'], allow_nan=False), case)
        require(scored['schema_valid'] and scored['quality_pass'] is c['expected_accept'],
                'declared control validity differs from independent score', faults)
        group = c['error_group']
        require(group in ('missing_premise', 'wrong_verdict', 'citation'), 'unknown control group', faults)
        pairs.setdefault(c['pair_id'], []).append(c)
        if not c['expected_accept']:
            pred = c['candidate']['verdict']
            valid = ((group == 'missing_premise' and case['label'] == 'insufficient' and pred in LABELS[:2])
                     or (group == 'wrong_verdict' and case['label'] in LABELS[:2] and pred in LABELS[:2]
                         and not scored['verdict_correct'])
                     or (group == 'citation' and case['label'] in LABELS[:2] and
                         scored['verdict_correct'] and not scored['evidence_correct']))
            require(valid, 'control error-group mismatch', faults)
    require(len({c['request_id'] for c in controls}) == 24 and len(pairs) == 12
            and len({c['case_id'] for c in controls}) == 12, 'control distinct/pair counts differ', faults)
    for pair in pairs.values():
        require(len(pair) == 2 and {x['expected_accept'] for x in pair} == {True, False}
                and len({(x['case_id'], x['error_group']) for x in pair}) == 1,
                'unmatched control pair', faults)
    require(Counter(c['error_group'] for c in controls if not c['expected_accept']) ==
            Counter(dict.fromkeys(('missing_premise', 'wrong_verdict', 'citation'), 4)),
            'control group balance differs', faults)
    require(Counter(by_id[c['case_id']]['label'] for c in controls if c['expected_accept']) ==
            Counter(dict.fromkeys(LABELS, 4)), 'valid control label balance differs', faults)
    for group in ('missing_premise', 'wrong_verdict'):
        require(Counter(c['candidate']['verdict'] for c in controls if not c['expected_accept']
                        and c['error_group'] == group) == Counter(supported=2, contradicted=2),
                'positive/negative control balance differs', faults)


def source_check(base, campaign, faults):
    config = read(base/'CONFIG.json', faults) or {}
    for key, wanted in dict(model=MODEL, digest=DIGEST, context=4096, think=False,
                            budget_s=1800, request_timeout_s=90, max_output_tokens=256).items():
        require(type(config.get(key)) is type(wanted) and config.get(key) == wanted,
                'unsupported config ' + key, faults)
    require(config.get('options') == dict(num_ctx=4096, num_predict=256, temperature=0, seed=0)
            and type(config.get('allow_battery_quality', False)) is bool, 'unsupported options/power policy', faults)
    lock = read(base/'MODEL_LOCK.json', faults) or {}
    require(config.get('lock') == {k: lock.get(k) for k in ('binary_sha256', 'manifest_sha256')}
            and lock.get('manifest_sha256') == DIGEST, 'model lock mismatch', faults)
    manifest = read(base/'MODEL_MANIFEST.json', faults) or {}
    require(sha(base/'MODEL_MANIFEST.json') == DIGEST, 'saved manifest digest mismatch', faults)
    descriptors = [manifest.get('config')] + manifest.get('layers', [])
    checks = lock.get('blob_checks', {})
    require(len(descriptors) == 5 and len({d['digest'] for d in descriptors}) == 5
            and set(checks) == {d['digest'] for d in descriptors}, 'saved blob digest set mismatch', faults)
    for d in descriptors:
        require(re.fullmatch(r'sha256:[0-9a-f]{64}', d['digest']) and type(d['size']) is int
                and d['size'] > 0 and checks.get(d['digest']) == {'bytes': d['size'], 'verified': True},
                'saved layer hash/size verification mismatch', faults)
    constants = {}
    for node in ast.parse((base/'contract.py').read_text()).body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id in ('INSTRUCTION', 'CHECK_INSTRUCTION', 'SCHEMA', 'CHECK_SCHEMA')):
            constants[node.targets[0].id] = ast.literal_eval(node.value)
    require(all(type(constants.get(k)) is str for k in ('INSTRUCTION', 'CHECK_INSTRUCTION'))
            and constants.get('SCHEMA') == SCHEMA and constants.get('CHECK_SCHEMA') == CHECK_SCHEMA,
            'frozen public constants unavailable or mismatched', faults)
    freeze = read(base/'FREEZE.json', faults) or {}
    frozen = freeze.get('sha256', {})
    require(NEEDED <= set(frozen), 'freeze omits required study files', faults)
    for name, digest in frozen.items():
        safe = not Path(name).is_absolute() and '..' not in Path(name).parts
        require(safe, 'unsafe frozen path', faults)
        if safe:
            require(sha(base/name) == digest, 'frozen file changed: ' + name, faults)
    require(campaign.get('source_freeze_sha256') == sha(base/'FREEZE.json'), 'campaign freeze differs', faults)
    require(utc(freeze['frozen_utc']) <= utc(campaign['started_utc']), 'freeze follows campaign', faults)
    sources = read(base/'SOURCE_MANIFEST.json', faults)
    source_map = {s['id']: s for s in sources}
    require(len(sources) == len(source_map) == 6, 'six distinct source packets required', faults)
    for s in sources:
        require(bool(re.fullmatch(r'[0-9a-f]{40}', s['commit'])), 'source not commit-pinned', faults)
        for filekey, hashkey in (('source_file', 'sha256'), ('license_file', 'license_sha256')):
            name = s[filekey]
            safe = not Path(name).is_absolute() and '..' not in Path(name).parts
            require(safe, 'unsafe source/license path', faults)
            if safe:
                require(sha(base/name) == s[hashkey] == frozen.get(name), 'source/license hash mismatch', faults)
    cases = read(base/'cases.json', faults)
    prior = read(base/'PRIOR_CLAIMS.json', faults)
    controls = read(base/'controls.json', faults)
    require(type(cases) is list and len(cases) == 24
            and len({c['request_id'] for c in cases}) == 24, '24 distinct cases required', faults)
    require(Counter(c['label'] for c in cases) == Counter(dict.fromkeys(LABELS, 8))
            and Counter(c['source_id'] for c in cases) == Counter(dict.fromkeys(source_map, 4)),
            'case source/label composition differs', faults)
    require(type(prior) is list and all(type(x) is str for x in prior), 'prior claim list malformed', faults)
    for c in cases:
        require(type(c['claim']) is str and bool(c['claim']) and c['claim'] not in prior
                and type(c['max_output_tokens']) is int and c['max_output_tokens'] == 256,
                'claim freshness/cap mismatch', faults)
        expected = hashlib.sha256(('coop-evidence-check-20261012:' + c['source_id'] + ':' + c['claim']).encode()).hexdigest()[:20]
        require(c['request_id'] == expected, 'case ID hash mismatch', faults)
        src = source_map[c['source_id']]
        raw = (base/src['source_file']).read_text()
        ids = {p['id'] for p in c['passages']}
        require(3 <= len(c['passages']) <= 4 and len(ids) == len(c['passages']),
                'three or four distinct excerpts required', faults)
        for p in c['passages']:
            start, end = p['source_char_start'], p['source_char_end']
            require(type(start) is int and type(end) is int and 0 <= start < end <= len(raw), 'bad excerpt offsets', faults)
            piece = raw[start:end]
            require(p['source_file'] == src['source_file'] and hashlib.sha256(piece.encode()).hexdigest() == p['source_text_sha256'],
                    'excerpt source/hash differs', faults)
            if p['transformation'] == 'verbatim':
                shown = piece
            elif p['transformation'] == 'strip_html_and_collapse_whitespace':
                shown = ' '.join(html.unescape(re.sub(r'<[^>]*>', ' ', piece)).split())
            else:
                shown = None
            require(shown == p['text'], 'excerpt transform differs', faults)
        proofs, relevant = c['acceptable_evidence'], c['relevant_evidence']
        require(type(relevant) is list and all(type(x) is str for x in relevant)
                and len(relevant) == len(set(relevant)) and set(relevant) <= ids, 'bad relevant evidence', faults)
        if c['label'] == 'insufficient':
            require(proofs == relevant == [], 'insufficient gold cites proof', faults)
        else:
            require(type(proofs) is list and bool(proofs) and all(type(p) is list and 1 <= len(p) <= 3
                    and len(set(p)) == len(p) and set(p) <= set(relevant) for p in proofs), 'bad accepted proof', faults)
    require(cases == sorted(cases, key=lambda c: hashlib.sha256(('order:' + c['request_id']).encode()).hexdigest()),
            'case order differs', faults)
    validate_controls(cases, controls, faults)
    return config, cases, controls, constants


def wire_check(row, config, prompt, cap, schema, faults):
    require(row.get('request_model') == MODEL and row.get('request_think') is False,
            'request model/think differs', faults)
    require(row.get('request_format') == schema and row.get('request_options') ==
            dict(config.get('options', {}), num_predict=cap), 'request schema/options/cap differs', faults)
    require(row.get('request_prompt') == prompt, 'exact prompt/proposal binding differs', faults)
    require(number(row.get('arrival_offset_s')) and row['arrival_offset_s'] == 0, 'arrival offset not zero', faults)


def duration(start, end):
    return dict(lower_s=(end['monotonic_before_ns']-start['monotonic_after_ns'])/1e9,
                upper_s=(end['monotonic_after_ns']-start['monotonic_before_ns'])/1e9)


def stage_check(path, config, cases, controls, constants):
    faults, records, stored, checker_rows = [], [], {}, []
    stage = read(path/'STAGE.json', faults) or {}
    order = order_for(cases, controls)
    by_case = {c['request_id']: c for c in cases}
    assignments = {'p_' + c['request_id']: ('primary', c['request_id']) for c in cases}
    assignments.update({'n_' + c['request_id']: ('checker', c['request_id']) for c in cases})
    assignments.update({c['request_id']: ('checker', c['case_id']) for c in controls})
    by_control = {c['request_id']: c for c in controls}
    for file in sorted(path.glob('*.json')):
        if file.name in ('STAGE.json', 'WARMUP.json', 'SERVER_CONTROL.json'):
            continue
        raw = read(file, faults)
        rows = raw.get('requests') if type(raw) is dict else None
        if type(rows) is not list:
            faults.append(file.name + ': missing raw rows'); continue
        require(len(rows) == 1, file.name + ': expected one raw row', faults)
        for row in rows:
            local = []
            identifier = row.get('request_id') if type(row) is dict else None
            try:
                api, text = raw_api(raw, row, MODEL, local)
            except (ValueError, TypeError, KeyError, IndexError, AttributeError) as error:
                api, text = False, ''; local.append('malformed raw: ' + str(error))
            assignment = assignments.get(identifier) if type(identifier) is str else None
            require(assignment is not None and file.name == str(identifier)+'.json', 'unknown/misfiled raw ID', local)
            require(api, 'API completion not verified', local)
            final = row.get('final') if type(row) is dict else None
            final = final if type(final) is dict else {}
            cap = 256 if assignment and assignment[0] == 'primary' else 64
            margin = 4096-final['prompt_eval_count']-cap if api else None
            if api:
                require(margin >= 128 and final['eval_count'] <= cap, 'context allowance/output cap failed', local)
            record = dict(request_id=identifier, raw_file=file.name, phase=assignment[0] if assignment else None,
                          case_id=assignment[1] if assignment else None, api_completed=api,
                          dispatched=type(row) is dict and number(row.get('dispatch_offset_s')),
                          observed_context_margin=margin, output_tokens=final.get('eval_count'),
                          done_reason=final.get('done_reason'), completion_s=None, faults=local)
            if type(row) is dict and number(row.get('terminal_offset_s')) and number(row.get('arrival_offset_s')):
                record['completion_s'] = row['terminal_offset_s']-row['arrival_offset_s']
            records.append(record)
            if type(identifier) is str and identifier.startswith(('n_', 'c_')):
                checker_rows.append(row)
            if type(identifier) is str:
                require(identifier not in stored, 'duplicate raw ID', local)
                stored.setdefault(identifier, (raw, row, text, record))
    primary_answers, checker_answers, proposal_contexts = {}, {}, {}
    for identifier, (raw, row, text, record) in stored.items():
        if identifier not in assignments:
            continue
        phase, case_id = assignments[identifier]
        local = record['faults']
        if phase == 'primary':
            prompt, cap, schema = prompt_for(by_case[case_id], constants), 256, SCHEMA
            if record['api_completed']:
                primary_answers[case_id] = text
        else:
            if identifier.startswith('n_'):
                primary = stored.get('p_' + case_id)
                require(primary is not None and primary[3]['api_completed'], 'native checker lacks completed primary binding', local)
                proposal = primary[2] if primary is not None else ''
            else:
                proposal = json.dumps(by_control[identifier]['candidate'], sort_keys=True, separators=(',', ':'), allow_nan=False)
            prompt, cap, schema = prompt_for(by_case[case_id], constants, proposal), 64, CHECK_SCHEMA
            suffix = '\n\nAudit JSON:'
            empty_prompt = prompt_for(by_case[case_id], constants, '')
            proposal_contexts[identifier] = (empty_prompt[:-len(suffix)], suffix)
            if record['api_completed']:
                checker_answers[identifier] = text
        wire_check(row, config, prompt, cap, schema, local)
    entries = stage.get('requests', [])
    if type(entries) is not list or any(type(x) is not dict for x in entries):
        entries = []; faults.append('stage entries malformed')
    ids = [r['request_id'] for r in records]
    entry_ids = [e.get('request_id') for e in entries]
    require(entry_ids == order[:len(entry_ids)], 'summary is not expected-order prefix', faults)
    require(Counter(str(x) for x in ids) == Counter(order) and entry_ids == order and len(order) == 72,
            'missing/extra/duplicate offered IDs', faults)
    for entry in entries:
        item = stored.get(entry.get('request_id'))
        require(item is not None, 'summary lacks raw capture', faults)
        if item is None:
            continue
        record = item[3]
        for key in ('phase', 'case_id', 'raw_file', 'api_completed', 'observed_context_margin',
                    'output_tokens', 'done_reason', 'completion_s'):
            if stage.get('status') != 'completed' and entry.get(key) is None:
                continue
            equal = same_number(entry.get(key), record[key]) if key == 'completion_s' else entry.get(key) == record[key]
            require(equal, 'summary ' + key + ' differs: ' + str(record['request_id']), faults)
    orphan = [x for x in ids if x not in entry_ids]
    require(not orphan, 'orphan raw rows omitted from summary: ' + str(orphan), faults)
    require(stage.get('status') == 'completed' and stage.get('completed_requests') == 72,
            'collection incomplete/aborted', faults)
    require(stage.get('part') == 'collection' and stage.get('candidate') == MODEL and stage.get('planned') == 72,
            'stage assignment/planned count differs', faults)
    try:
        stamps = stage.get('clock_stamps')
        diag = clock_check(stamps)
        supplied = stage.get('clock_diagnostics', {})
        require(diag['valid'] and supplied.get('valid') is True and all(same_number(supplied.get(k), diag[k])
                for k in ('maximum_bracket_s', 'observed_offset_span_s')), 'clock diagnostics differ/fail', faults)
        require(len(stamps) == 290, 'expected 290 stage clock stamps', faults)
        for i, identifier in enumerate(order if len(stamps) == 290 else []):
            item = stored.get(identifier)
            if item is None:
                continue
            raw = item[0]
            before, start, end, after = stamps[1+4*i:5+4*i]
            require([start, end] == [raw.get('started_stamp'), raw.get('finished_stamp')], 'clock-to-raw binding differs', faults)
            if i < len(entries):
                for name, a, b in (('collector_duration', start, end), ('phase_duration', before, after)):
                    expected = duration(a, b)
                    require(all(same_number(entries[i].get(name, {}).get(k), v) for k, v in expected.items()),
                            'summary duration bounds differ', faults)
            if i and order[i-1] in stored:
                prev = stored[order[i-1]][0]
                require((start['monotonic_before_ns']-prev['finished_stamp']['monotonic_after_ns'])/1e9 >= .2,
                        'scored serial spacing below .2s', faults)
    except (ValueError, TypeError, KeyError, IndexError) as error:
        faults.append('stage clocks: ' + str(error))
    warm = read(path/'WARMUP.json', faults)
    try:
        require(len(warm['requests']) == 1, 'warmup row count differs', faults)
        row = warm['requests'][0]
        ok, _ = raw_api(warm, row, MODEL, faults)
        require(ok and row.get('request_id') == 'warm' and row['final']['eval_count'] <= 32,
                'warmup completion/cap not verified', faults)
        wire_check(row, config, WARM_PROMPT, 32, CHECK_SCHEMA, faults)
        require(ok and 4096-row['final']['prompt_eval_count']-32 >= 128,
                'warmup context allowance failed', faults)
        if order and order[0] in stored:
            require(warm['finished_stamp']['monotonic_after_ns'] <= stored[order[0]][0]['started_stamp']['monotonic_before_ns'],
                    'warmup overlaps first scored call', faults)
    except (ValueError, TypeError, KeyError, IndexError) as error:
        faults.append('warmup malformed: ' + str(error))
    try:
        stage_start, stage_end = utc(stage['started_utc']).timestamp(), utc(stage['finished_utc']).timestamp()
        for raw in ([warm] if type(warm) is dict else []) + [item[0] for item in stored.values()]:
            start_wall = raw['started_stamp']['wall_ns']/1e9
            end_wall = raw['finished_stamp']['wall_ns']/1e9
            require(stage_start <= start_wall <= end_wall <= stage_end,
                    'raw wall interval outside saved stage', faults)
            require(abs(utc(raw['started_utc']).timestamp()-start_wall) <= .00001,
                    'raw started UTC differs from paired wall stamp', faults)
    except (ValueError, TypeError, KeyError, AttributeError) as error:
        faults.append('raw/stage chronology: ' + str(error))
    meta = read(path/'SERVER_CONTROL.json', faults)
    controller_check(meta, config, path, order, faults)
    if type(meta) is dict:
        require(meta.get('dedicated_server_returncode') == 0, 'owned server nonzero exit', faults)
    faults.extend(r['raw_file'] + ': ' + f for r in records for f in r['faults'])
    return dict(reported_stage=stage, records=records, raw_offered=len(records),
                dispatched=sum(r['dispatched'] for r in records), api_completed=sum(r['api_completed'] for r in records),
                summary_recorded=len(entries), orphan_raw_ids=orphan, missing_ids=[x for x in order if x not in ids],
                quality_summary=quality_summary(cases, controls, primary_answers, checker_answers),
                checker_input_duplicates=checker_duplicate_diagnostics(
                    checker_rows, proposal_contexts),
                faults=faults)


def analyze(base, capture):
    base, capture = Path(base), Path(capture)
    faults = []
    campaign = read(capture/'CAMPAIGN.json', faults) or {}
    config, cases, controls, constants = {}, [], [], {}
    try:
        config, cases, controls, constants = source_check(base, campaign, faults)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, SyntaxError, RecursionError) as error:
        faults.append('source invalid: ' + str(error))
        # A source failure must not prevent counting retained raw attempts.
        cases = read(base/'cases.json', faults) or []
        controls = read(base/'controls.json', faults) or []
        config = read(base/'CONFIG.json', faults) or {}
    stage = None
    path = capture/'collection'
    require(path.is_dir(), 'missing collection directory', faults)
    require(not any(p.is_dir() and p.name != 'collection' for p in capture.iterdir()) if capture.is_dir() else False,
            'unexpected capture directory/fallback', faults)
    try:
        stage = stage_check(path, config, cases, controls, constants)
    except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError, RecursionError) as error:
        faults.append('malformed collection: ' + str(error))
    if stage is None:
        observed = 0
        for p in path.glob('*.json'):
            if p.name in ('STAGE.json', 'WARMUP.json', 'SERVER_CONTROL.json'):
                continue
            raw = read(p, faults)
            if type(raw) is dict and type(raw.get('requests')) is list:
                observed += len(raw['requests'])
        stage = dict(reported_stage={}, records=[], raw_offered=observed, dispatched=0, api_completed=0,
                     summary_recorded=0, orphan_raw_ids=[], missing_ids=[], faults=[],
                     quality_summary=quality_summary([], [], {}, {}),
                     checker_input_duplicates=checker_duplicate_diagnostics([]))
    require(campaign.get('status') == 'completed' and campaign.get('planned_requests') == 72
            and campaign.get('scored_requests') == 72, 'campaign incomplete/count differs', faults)
    require(campaign.get('stages') == [stage['reported_stage']], 'campaign stage snapshot differs', faults)
    try:
        times = [utc(campaign['started_utc']), utc(stage['reported_stage']['started_utc']),
                 utc(stage['reported_stage']['finished_utc']), utc(campaign['finished_utc'])]
        require(times == sorted(times), 'campaign/stage chronology invalid', faults)
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        faults.append('campaign chronology: ' + str(error))
    faults.extend(stage['faults'])
    valid = not faults
    quality = stage['quality_summary']
    duplicates = stage['checker_input_duplicates']
    return dict(schema_version=1, evidence='Independent raw primary/checker recount; no primary scorer imports',
                data_complete_valid=valid, qualified=bool(valid and quality['engineering_gate_passed']),
                engineering_gate_passed=bool(valid and quality['engineering_gate_passed']),
                counts=dict(planned=72, planned_primary=24, planned_checker=48, raw_offered=stage['raw_offered'],
                            dispatched=stage['dispatched'], api_completed=stage['api_completed'],
                            summary_recorded=stage['summary_recorded'],
                            checker_exact_unique_inputs=duplicates['exact_payload']['unique_inputs'],
                            checker_exact_excess_duplicate_calls=duplicates['exact_payload']['excess_duplicate_calls'],
                            checker_json_equivalent_unique_inputs=duplicates['proposal_json_equivalence']['unique_inputs'],
                            checker_json_equivalent_excess_duplicate_calls=duplicates['proposal_json_equivalence']['excess_duplicate_calls']),
                quality_summary=quality, checker_input_duplicates=duplicates,
                orphan_raw_ids=stage['orphan_raw_ids'], missing_ids=stage['missing_ids'],
                records=stage['records'], faults=faults,
                limitations=['Constructed dependent cohort, not population reliability or operational authorization.',
                             'REVIEW is a referral, not a corrected insufficient verdict or successful answer.',
                             'No schema-valid natural primary error means natural semantic sensitivity is unobserved.',
                             'Saved host/blob metadata are not live continuous attestation; unseen attempts are unreconstructable.',
                             'No throughput, energy, productivity or economic-pooling effect is measured.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base', type=Path)
    parser.add_argument('capture', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.base, args.capture)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n')
    print(json.dumps({k: result[k] for k in ('data_complete_valid', 'qualified', 'counts')}))


if __name__ == '__main__':
    main()
