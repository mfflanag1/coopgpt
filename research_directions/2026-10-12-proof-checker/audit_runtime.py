"""Independent saved-data audit of the 24 inventory + 24 primary experiment.

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
import itertools
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
PROOF_SCHEMA = {'type': 'array', 'items': {'type': 'array', 'items': {'type': 'string'},
                'minItems': 1, 'maxItems': 3, 'uniqueItems': True}, 'maxItems': 3, 'uniqueItems': True}
ATOM_SCHEMA = {'type': 'object', 'properties': {'support': PROOF_SCHEMA, 'contradict': PROOF_SCHEMA},
               'required': ['support', 'contradict'], 'additionalProperties': False}
INVENTORY_SCHEMA = {'type': 'object', 'properties': {'a1': ATOM_SCHEMA, 'a2': ATOM_SCHEMA},
                    'required': ['a1', 'a2'], 'additionalProperties': False}
WARM_PROMPT = 'Return {"verdict":"insufficient","evidence":[]} exactly. /no_think' 
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


def parse_primary(text):
    invalid = dict(schema_valid=False, prediction=None)
    try:
        obj = strict_json(text)
    except (ValueError, TypeError, UnicodeError, RecursionError):
        return invalid
    if (type(obj) is not dict or set(obj) != {'verdict', 'evidence'}
            or type(obj['verdict']) is not str or obj['verdict'] not in LABELS
            or type(obj['evidence']) is not list or len(obj['evidence']) > 3
            or any(type(x) is not str for x in obj['evidence'])
            or len(set(obj['evidence'])) != len(obj['evidence'])):
        return invalid
    return dict(schema_valid=True, prediction=obj)


def score_output(text, job):
    parsed = parse_primary(text)
    if not parsed['schema_valid']:
        return dict(schema_valid=False, verdict_correct=False, evidence_correct=False,
                    quality_pass=False, prediction=None)
    obj = parsed['prediction']
    ids = set(obj['evidence'])
    evidence = (not ids if job['label'] == 'insufficient' else
                ids <= {p['id'] for p in job['passages']} and ids <= set(job['relevant_evidence'])
                and any(set(proof) <= ids for proof in job['acceptable_evidence']))
    verdict = obj['verdict'] == job['label']
    return dict(schema_valid=True, verdict_correct=verdict, evidence_correct=bool(evidence),
                quality_pass=bool(verdict and evidence), prediction=obj)


def parse_inventory(text, case):
    result = dict(schema_valid=False, usable=False, conflict=False, prediction=None, aggregate=None)
    try:
        obj = strict_json(text)
        known = {p['id'] for p in case['passages']}
        if type(obj) is not dict or set(obj) != {'a1', 'a2'}:
            return result
        unknown = False
        for atom in obj.values():
            if type(atom) is not dict or set(atom) != {'support', 'contradict'}:
                return result
            for proofs in atom.values():
                if type(proofs) is not list or len(proofs) > 3:
                    return result
                seen = set()
                for proof in proofs:
                    if (type(proof) is not list or not 1 <= len(proof) <= 3
                            or any(type(x) is not str for x in proof)
                            or len(set(proof)) != len(proof)):
                        return result
                    unknown = unknown or not set(proof) <= known
                    key = frozenset(proof)
                    if key in seen:
                        return result
                    seen.add(key)
        conflict = any(a['support'] and a['contradict'] for a in obj.values())
        verdict = None if conflict or unknown else ('contradicted' if any(a['contradict'] for a in obj.values())
                  else 'supported' if all(a['support'] for a in obj.values()) else 'insufficient')
        return dict(schema_valid=True, usable=not conflict and not unknown, conflict=bool(conflict),
                    prediction=obj, aggregate=verdict)
    except (ValueError, TypeError, KeyError, UnicodeError, RecursionError):
        return result


def decision(text, inventory_text, case):
    baseline = parse_primary(text)
    inv = parse_inventory(inventory_text, case)
    reason = 'accepted'
    if not baseline['schema_valid']:
        reason = 'proposal_schema'
    elif not inv['usable']:
        reason = 'inventory_unusable'
    elif baseline['prediction']['verdict'] != inv['aggregate']:
        reason = 'verdict_mismatch'
    else:
        ids = set(baseline['prediction']['evidence'])
        if inv['aggregate'] == 'insufficient':
            valid = not ids
        else:
            side = 'support' if inv['aggregate'] == 'supported' else 'contradict'
            families = [atom[side] for atom in inv['prediction'].values()]
            covered = [any(set(proof) <= ids for proof in family) for family in families]
            relevant = {x for family in families for proof in family for x in proof}
            valid = ids <= relevant and (all(covered) if side == 'support' else any(covered))
        if not valid:
            reason = 'evidence_mismatch'
    return dict(accept=reason == 'accepted', reason=reason, inventory=inv)


def inventory_quality(text, case):
    parsed = parse_inventory(text, case)
    rows = []
    for gold in case['components']:
        correct = parsed['usable']
        complete = parsed['usable']
        if parsed['usable']:
            atom = parsed['prediction'][gold['id']]
            for side in ('support', 'contradict'):
                wanted = {frozenset(p) for p in gold[side]}
                given = {frozenset(p) for p in atom[side]}
                relevant = set().union(*wanted) if wanted else set()
                presence = bool(wanted) == bool(given)
                sound = all(proof <= relevant and any(minimal <= proof for minimal in wanted) for proof in given)
                correct = correct and presence and sound
                complete = complete and wanted <= given
        rows.append(dict(component_id=gold['id'], correct=bool(correct),
                         all_alternatives_recovered=bool(correct and complete)))
    return dict(parsed=parsed, components=rows, quality_pass=all(r['correct'] for r in rows),
                all_alternatives_recovered=all(r['all_alternatives_recovered'] for r in rows))


def quality_summary(cases, controls, primary_answers, inventory_answers):
    natural, controlled, inventories = [], [], []
    case_ids = {c['request_id'] for c in cases}
    complete = (len(cases) == len(controls) == 24 and len(case_ids) == 24
                and set(primary_answers) == case_ids and set(inventory_answers) == case_ids)
    by_case = {c['request_id']: c for c in cases}
    for case in cases:
        key = case['request_id']
        baseline = score_output(primary_answers.get(key, ''), case)
        checked = decision(primary_answers.get(key, ''), inventory_answers.get(key, ''), case)
        automatic, good = checked['accept'], baseline['quality_pass']
        natural.append(dict(case_id=key, label=case['label'], baseline=baseline, decision=checked,
                            automatic=automatic, retained_correct=automatic and good,
                            accepted_error=automatic and not good,
                            semantic_catch=baseline['schema_valid'] and not good and
                                checked['inventory']['usable'] and not automatic,
                            format_referral=not baseline['schema_valid'], lost_correct=good and not automatic))
        inventories.append(dict(case_id=key, **inventory_quality(inventory_answers.get(key, ''), case)))
    for item in controls:
        case = by_case[item['case_id']]
        checked = decision(json.dumps(item['candidate'], allow_nan=False),
                           inventory_answers.get(item['case_id'], ''), case)
        controlled.append(dict(request_id=item['request_id'], pair_id=item['pair_id'],
                               case_id=item['case_id'], error_group=item['error_group'],
                               expected_accept=item['expected_accept'], decision=checked,
                               correct_decision=checked['inventory']['usable'] and
                               checked['accept'] is item['expected_accept']))
    baseline = sum(r['baseline']['quality_pass'] for r in natural)
    retained = sum(r['retained_correct'] for r in natural)
    accepted_errors = sum(r['accepted_error'] for r in natural)
    rejected_bad = sum(r['correct_decision'] for r in controlled if not r['expected_accept'])
    retained_good = sum(r['correct_decision'] for r in controlled if r['expected_accept'])
    schemas = sum(r['parsed']['schema_valid'] for r in inventories)
    usable = sum(r['parsed']['usable'] for r in inventories)
    native_gate = accepted_errors == 0 and retained >= 18 and 10 * retained >= 9 * baseline
    control_gate = rejected_bad == 12 and retained_good >= 11
    variants = format_diagnostics(cases, controls, primary_answers, inventory_answers)
    return dict(input_complete=complete, engineering_gate_passed=bool(complete and usable == 24 and
                native_gate and control_gate and not variants['decision_mismatches']), native_gate_passed=native_gate,
                control_gate_passed=control_gate, inventory_schema_valid=schemas, inventory_usable=usable,
                baseline_correct=baseline, baseline_errors=24-baseline,
                baseline_schema_valid=sum(r['baseline']['schema_valid'] for r in natural),
                automatic_correct=retained, automatic_errors=accepted_errors,
                automatic_total=sum(r['automatic'] for r in natural),
                referrals=24-sum(r['automatic'] for r in natural), correct_referred=baseline-retained,
                format_referrals=sum(r['format_referral'] for r in natural),
                semantic_errors_caught=sum(r['semantic_catch'] for r in natural),
                native_sensitivity_observed=any(r['baseline']['schema_valid'] and
                                               not r['baseline']['quality_pass'] for r in natural),
                constructed_invalid_rejected=rejected_bad, constructed_valid_retained=retained_good,
                correct_automatic_per_offered=retained/24, baseline_correct_per_offered=baseline/24,
                inventory_quality_correct=sum(r['quality_pass'] for r in inventories),
                inventory_component_correct=sum(c['correct'] for r in inventories for c in r['components']),
                inventory_all_alternatives_recovered=sum(r['all_alternatives_recovered'] for r in inventories),
                format_variant_checks=variants['variants_checked'],
                format_variant_failures=len(variants['decision_mismatches']),
                natural=natural, controlled=controlled, inventories=inventories)


def prompt_for(case, constants, phase='primary'):
    instruction = constants['INSTRUCTION' if phase == 'primary' else 'INVENTORY_INSTRUCTION']
    text = (instruction + '\nDocumentation packet:\n'
            + '\n\n'.join('[' + p['id'] + '] ' + p['text'] for p in case['passages']))
    if phase == 'primary':
        return text + '\n\nClaim:\n' + case['claim'] + '\n\nJSON verdict:'
    return (text + '\n\nComponent statements:\n'
            + '\n'.join('[' + p['id'] + '] ' + p['claim'] for p in case['components'])
            + '\n\nEvidence inventory JSON:')


def order_for(cases, controls=None):
    return ['i_' + c['request_id'] for c in cases] + ['p_' + c['request_id'] for c in cases]


def format_diagnostics(cases, controls, primary_answers, inventory_answers):
    by_case = {c['request_id']: c for c in cases}
    candidates = [('native:' + c['request_id'], c, primary_answers.get(c['request_id'], '')) for c in cases]
    candidates += [(c['request_id'], by_case[c['case_id']], json.dumps(c['candidate'])) for c in controls]
    checked, malformed, mismatches = 0, 0, []
    for key, case, text in candidates:
        scored = parse_primary(text)
        if not scored['schema_valid']:
            malformed += 1
            continue
        obj = scored['prediction']
        variants = [json.dumps(obj, sort_keys=True, separators=(',', ':')),
                    json.dumps(dict(verdict=obj['verdict'], evidence=list(reversed(obj['evidence']))), indent=2)]
        expected = decision(text, inventory_answers.get(case['request_id'], ''), case)['accept']
        for variant in variants:
            checked += 1
            if decision(variant, inventory_answers.get(case['request_id'], ''), case)['accept'] != expected:
                mismatches.append(key)
    return dict(diagnostic_only=True, candidate_objects=len(candidates), malformed_candidates=malformed,
                variants_checked=checked, decision_mismatches=mismatches,
                definition='Local parser/comparator invariance; no model calls or independent replications.')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc(text):
    value = datetime.fromisoformat(text.replace('Z', '+00:00'))
    if value.tzinfo is None:
        raise ValueError('timezone missing')
    return value


def prescribed_controls(cases):
    """Reconstruct the frozen control rule without importing the builder/scorer."""
    ordered = sorted(cases, key=lambda c: hashlib.sha256(('order:' + c['request_id']).encode()).hexdigest())
    planned = []
    for label in LABELS:
        selected = [case for case in ordered if case['label'] == label][:4]
        for position, case in enumerate(selected):
            valid = dict(verdict=label, evidence=[] if label == 'insufficient' else case['acceptable_evidence'][0])
            if label != 'insufficient' and position < 2:
                group, invalid = 'false_insufficient', dict(verdict='insufficient', evidence=[])
            else:
                true_part = next(part for part in case['components'] if part['support'])
                invalid = dict(verdict=label, evidence=true_part['support'][0])
                if label == 'insufficient':
                    group = 'unsupported_decisive'
                    invalid['verdict'] = 'supported' if position < 2 else 'contradicted'
                else:
                    group = 'citation'
                    if score_output(json.dumps(invalid), case)['quality_pass']:
                        invalid['evidence'] = []
                        for passage in case['passages']:
                            singleton = dict(verdict=label, evidence=[passage['id']])
                            if not score_output(json.dumps(singleton), case)['quality_pass']:
                                invalid['evidence'] = singleton['evidence']
                                break
            pair = 'pair_' + case['request_id']
            for accepted, proposal in ((True, valid), (False, invalid)):
                identifier = 'c_' + hashlib.sha256(
                    ('coop-proof-control:' + pair + ':' + str(accepted)).encode()).hexdigest()[:20]
                planned.append(dict(request_id=identifier, pair_id=pair, case_id=case['request_id'],
                                    error_group=group, expected_accept=accepted, candidate=proposal))
    return sorted(planned, key=lambda item: hashlib.sha256(
        ('control-order:' + item['request_id']).encode()).hexdigest())


def validate_controls(cases, controls, faults):
    by_id = {c['request_id']: c for c in cases}
    require(type(controls) is list and len(controls) == 24, '24 controls required', faults)
    require(controls == prescribed_controls(cases),
            'controls differ from prospective selection/construction/order', faults)
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
        require(group in ('unsupported_decisive', 'false_insufficient', 'citation'), 'unknown control group', faults)
        pairs.setdefault(c['pair_id'], []).append(c)
        if not c['expected_accept']:
            pred = c['candidate']['verdict']
            valid = ((group == 'unsupported_decisive' and case['label'] == 'insufficient' and pred in LABELS[:2])
                     or (group == 'false_insufficient' and case['label'] in LABELS[:2] and pred == 'insufficient')
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
            Counter(dict.fromkeys(('unsupported_decisive', 'false_insufficient', 'citation'), 4)),
            'control group balance differs', faults)
    require(Counter(by_id[c['case_id']]['label'] for c in controls if c['expected_accept']) ==
            Counter(dict.fromkeys(LABELS, 4)), 'valid control label balance differs', faults)
    for group in ('unsupported_decisive',):
        require(Counter(c['candidate']['verdict'] for c in controls if not c['expected_accept']
                        and c['error_group'] == group) == Counter(supported=2, contradicted=2),
                'positive/negative control balance differs', faults)

    for group in ('false_insufficient', 'citation'):
        require(Counter(by_id[c['case_id']]['label'] for c in controls if not c['expected_accept']
                        and c['error_group'] == group) == Counter(supported=2, contradicted=2),
                'decisive control gold-label balance differs', faults)


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
                and node.targets[0].id in ('INSTRUCTION', 'INVENTORY_INSTRUCTION')):
            constants[node.targets[0].id] = ast.literal_eval(node.value)
    require(all(type(constants.get(k)) is str for k in ('INSTRUCTION', 'INVENTORY_INSTRUCTION')),
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
        expected = hashlib.sha256(('coop-proof-check-20261012:' + c['source_id'] + ':' + c['claim']).encode()).hexdigest()[:20]
        require(c['request_id'] == expected, 'case ID hash mismatch', faults)
        src = source_map[c['source_id']]
        raw = (base/src['source_file']).read_text()
        ids = {p['id'] for p in c['passages']}
        require(3 <= len(c['passages']) <= 4 and len(ids) == len(c['passages']),
                'three or four distinct excerpts required', faults)
        require(100 <= sum(len(p['text'].split()) for p in c['passages']) <= 450,
                'packet word count outside 100..450', faults)
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
        parts = c['components']
        require(type(parts) is list and len(parts) == 2 and [p['id'] for p in parts] == ['a1', 'a2'],
                'two ordered component IDs required', faults)
        gold = {p['id']: {side: p[side] for side in ('support', 'contradict')} for p in parts}
        parsed = parse_inventory(json.dumps(gold, allow_nan=False), c)
        require(parsed['usable'], 'gold component proof schema/conflict invalid', faults)
        require(all(type(p['claim']) is str and p['claim'].strip() and type(p['rationale']) is str
                    and p['rationale'].strip() and p['label'] == ('supported' if p['support']
                    else 'contradicted' if p['contradict'] else 'insufficient') for p in parts),
                'gold component relation/text differs', faults)
        require(c['claim'] == 'Both statements hold: (a1) ' + parts[0]['claim'] + ' (a2) ' + parts[1]['claim'],
                'whole claim differs from explicit component conjunction', faults)
        require(parsed['aggregate'] == c['label'], 'gold aggregate label differs', faults)
        if c['label'] == 'supported':
            require(not any(set(a) <= set(b) or set(b) <= set(a)
                            for a in parts[0]['support'] for b in parts[1]['support']),
                    'supported components lack genuinely distinct premises', faults)
            gold_proofs = [set(a) | set(b) for a, b in itertools.product(parts[0]['support'], parts[1]['support'])
                           if len(set(a) | set(b)) <= 3]
        elif c['label'] == 'contradicted':
            gold_proofs = [set(p) for part in parts for p in part['contradict']]
        else:
            gold_proofs = []
        gold_proofs = [proof for proof in gold_proofs if not any(other < proof for other in gold_proofs)]
        gold_relevant = {x for proof in gold_proofs for x in proof}
        require(c['acceptable_evidence'] == [list(proof) for proof in sorted({tuple(sorted(p)) for p in gold_proofs})]
                and c['relevant_evidence'] == sorted(gold_relevant),
                'whole gold proof families differ from component derivation', faults)
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
    faults, records, stored = [], [], {}
    stage = read(path/'STAGE.json', faults) or {}
    order = order_for(cases, controls)
    by_case = {c['request_id']: c for c in cases}
    assignments = {'p_' + c['request_id']: ('primary', c['request_id']) for c in cases}
    assignments.update({'i_' + c['request_id']: ('inventory', c['request_id']) for c in cases})
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
            cap = 256 if assignment and assignment[0] == 'primary' else 384
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
            if type(identifier) is str:
                require(identifier not in stored, 'duplicate raw ID', local)
                stored.setdefault(identifier, (raw, row, text, record))
    primary_answers, inventory_answers = {}, {}
    for identifier, (raw, row, text, record) in stored.items():
        if identifier not in assignments:
            continue
        phase, case_id = assignments[identifier]
        local = record['faults']
        cap = 256 if phase == 'primary' else 384
        schema = SCHEMA if phase == 'primary' else INVENTORY_SCHEMA
        prompt = prompt_for(by_case[case_id], constants, phase)
        if record['api_completed']:
            (primary_answers if phase == 'primary' else inventory_answers)[case_id] = text
        wire_check(row, config, prompt, cap, schema, local)
    entries = stage.get('requests', [])
    if type(entries) is not list or any(type(x) is not dict for x in entries):
        entries = []; faults.append('stage entries malformed')
    ids = [r['request_id'] for r in records]
    entry_ids = [e.get('request_id') for e in entries]
    require(entry_ids == order[:len(entry_ids)], 'summary is not expected-order prefix', faults)
    require(Counter(str(x) for x in ids) == Counter(order) and entry_ids == order and len(order) == 48,
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
    require(stage.get('status') == 'completed' and stage.get('completed_requests') == 48,
            'collection incomplete/aborted', faults)
    require(stage.get('part') == 'collection' and stage.get('candidate') == MODEL and stage.get('planned') == 48,
            'stage assignment/planned count differs', faults)
    try:
        stamps = stage.get('clock_stamps')
        diag = clock_check(stamps)
        supplied = stage.get('clock_diagnostics', {})
        require(diag['valid'] and supplied.get('valid') is True and all(same_number(supplied.get(k), diag[k])
                for k in ('maximum_bracket_s', 'observed_offset_span_s')), 'clock diagnostics differ/fail', faults)
        require(len(stamps) == 194, 'expected 194 stage clock stamps', faults)
        for i, identifier in enumerate(order if len(stamps) == 194 else []):
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
        wire_check(row, config, WARM_PROMPT, 32, SCHEMA, faults)
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
                quality_summary=quality_summary(cases, controls, primary_answers, inventory_answers),
                format_variants=format_diagnostics(cases, controls, primary_answers, inventory_answers),
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
                     format_variants=format_diagnostics([], [], {}, {}))
    require(campaign.get('status') == 'completed' and campaign.get('planned_requests') == 48
            and campaign.get('scored_requests') == 48, 'campaign incomplete/count differs', faults)
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
    return dict(schema_version=1, evidence='Independent raw inventory/primary recount; no primary scorer imports',
                data_complete_valid=valid, qualified=bool(valid and quality['engineering_gate_passed']),
                engineering_gate_passed=bool(valid and quality['engineering_gate_passed']),
                counts=dict(planned=48, planned_primary=24, planned_inventory=24, raw_offered=stage['raw_offered'],
                            dispatched=stage['dispatched'], api_completed=stage['api_completed'],
                            summary_recorded=stage['summary_recorded']),
                quality_summary=quality, format_variants=stage['format_variants'],
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
