"""Audit saved GPU-placement evidence using only the Python standard library.

This module imports no study implementation and performs no optimization. It
rechecks each saved plan, recomputes objectives/summary fractions, reconstructs
the saved GPU-reuse mutations, and checks hashes and recorded inequalities.
"""
import argparse
import copy
from collections import Counter
from datetime import datetime
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re

POLICIES = ('priority_first', 'scarcity_first', 'exact')
IDENTIFIER = re.compile(r'[A-Za-z][A-Za-z0-9_-]{0,31}')
MAX_RAM = 1099511627776
CONSTRUCTED = {
    'empty_queue', 'no_free_gpus', 'vram_cannot_pool', 'gang_cannot_cross_nodes',
    'gang_cannot_mix_families', 'owner_permission_blocks', 'one_cpu_bottleneck',
    'one_ram_bottleneck', 'priority_tie_more_jobs', 'priority_first_gang_trap',
    'scarce_memory_placement', 'exact_cpu_ram_fit',
}


def strict_loads(text):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError('duplicate JSON key: ' + key)
            out[key] = value
        return out
    def nonfinite(value):
        raise ValueError('nonfinite JSON number: ' + value)
    return json.loads(text, object_pairs_hook=unique, parse_constant=nonfinite)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def keys(obj, names, context):
    need(type(obj) is dict and set(obj) == set(names), context + ': object keys differ')


def integer(value, low, high, context):
    need(type(value) is int and low <= value <= high, context + ': integer bound/type')


def identifier(value, context):
    need(type(value) is str and IDENTIFIER.fullmatch(value) is not None, context + ': identifier')


def identifiers(values, low, high, context):
    need(type(values) is list and low <= len(values) <= high, context + ': list size/type')
    for value in values:
        identifier(value, context)
    need(len(set(values)) == len(values), context + ': duplicate identifiers')


def validate_manifest(manifest):
    keys(manifest, ('schema_version', 'nodes', 'jobs'), 'manifest')
    integer(manifest['schema_version'], 1, 1, 'manifest version')
    nodes, jobs = manifest['nodes'], manifest['jobs']
    need(type(nodes) is list and 1 <= len(nodes) <= 4, 'manifest node list')
    need(type(jobs) is list and len(jobs) <= 8, 'manifest job list')
    node_ids, gpu_ids, job_ids = set(), set(), set()
    for node in nodes:
        keys(node, ('id', 'owner', 'cpu_units', 'ram_mib', 'gpus'), 'node')
        identifier(node['id'], 'node ID'); identifier(node['owner'], 'owner ID')
        need(node['id'] not in node_ids, 'duplicate node ID'); node_ids.add(node['id'])
        integer(node['cpu_units'], 0, 65536, 'node CPU')
        integer(node['ram_mib'], 0, MAX_RAM, 'node RAM')
        need(type(node['gpus']) is list and len(node['gpus']) <= 8, 'GPU list')
        for gpu in node['gpus']:
            keys(gpu, ('id', 'family', 'vram_mib'), 'GPU')
            identifier(gpu['id'], 'GPU ID'); identifier(gpu['family'], 'GPU family')
            integer(gpu['vram_mib'], 1, MAX_RAM, 'GPU VRAM')
            need(gpu['id'] not in gpu_ids, 'duplicate global GPU ID'); gpu_ids.add(gpu['id'])
    need(len(gpu_ids) <= 8, 'more than eight GPUs')
    for job in jobs:
        keys(job, ('id', 'priority', 'cpu_units', 'ram_mib', 'gpu_count', 'min_vram_mib',
                   'allowed_families', 'allowed_owners'), 'job')
        identifier(job['id'], 'job ID')
        need(job['id'] not in job_ids, 'duplicate job ID'); job_ids.add(job['id'])
        integer(job['priority'], 1, 1000000, 'job priority')
        integer(job['cpu_units'], 1, 65536, 'job CPU')
        integer(job['ram_mib'], 1, MAX_RAM, 'job RAM')
        integer(job['gpu_count'], 1, 8, 'job GPU count')
        integer(job['min_vram_mib'], 1, MAX_RAM, 'job VRAM')
        identifiers(job['allowed_families'], 1, 16, 'allowed families')
        identifiers(job['allowed_owners'], 1, 16, 'allowed owners')


def objective_from_plan(manifest, plan):
    """Return a score only after checking every modeled placement constraint."""
    validate_manifest(manifest)
    keys(plan, ('schema_version', 'placements', 'deferred'), 'plan')
    integer(plan['schema_version'], 1, 1, 'plan version')
    need(type(plan['placements']) is list and len(plan['placements']) <= 8, 'placements list')
    identifiers(plan['deferred'], 0, 8, 'deferred jobs')
    nodes = {node['id']: node for node in manifest['nodes']}
    jobs = {job['id']: job for job in manifest['jobs']}
    gpus = {gpu['id']: (node['id'], gpu) for node in manifest['nodes'] for gpu in node['gpus']}
    admitted, occupied = set(), set()
    cpu, ram = Counter(), Counter()
    need(set(plan['deferred']) <= jobs.keys(), 'unknown deferred job')
    for placement in plan['placements']:
        keys(placement, ('job', 'node', 'gpus'), 'placement')
        identifier(placement['job'], 'placed job'); identifier(placement['node'], 'placed node')
        identifiers(placement['gpus'], 1, 8, 'placed GPUs')
        job_id, node_id = placement['job'], placement['node']
        need(job_id in jobs and node_id in nodes, 'unknown job/node')
        need(job_id not in admitted and job_id not in plan['deferred'], 'job appears more than once')
        admitted.add(job_id)
        job, node = jobs[job_id], nodes[node_id]
        selected = placement['gpus']
        need(len(selected) == job['gpu_count'], 'partial/wrong GPU count')
        need(node['owner'] in job['allowed_owners'], 'unauthorized node owner')
        families = set()
        for gpu_id in selected:
            need(gpu_id in gpus, 'unknown GPU')
            need(gpu_id not in occupied, 'global GPU reuse'); occupied.add(gpu_id)
            physical_node, gpu = gpus[gpu_id]
            need(physical_node == node_id, 'GPU on different node')
            need(gpu['family'] in job['allowed_families'], 'disallowed GPU family')
            need(gpu['vram_mib'] >= job['min_vram_mib'], 'insufficient per-device VRAM')
            families.add(gpu['family'])
        need(len(families) == 1, 'mixed GPU families in one gang')
        cpu[node_id] += job['cpu_units']; ram[node_id] += job['ram_mib']
    need(admitted | set(plan['deferred']) == jobs.keys(), 'omitted job')
    for node_id, node in nodes.items():
        need(cpu[node_id] <= node['cpu_units'], 'shared CPU overcommit')
        need(ram[node_id] <= node['ram_mib'], 'shared RAM overcommit')
    return sum(jobs[key]['priority'] for key in admitted), len(admitted)


def deep_equal(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return set(left) == set(right) and all(deep_equal(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(deep_equal(a, b) for a, b in zip(left, right))
    return left == right


def tuple_objective(value, manifest, context):
    need(type(value) is list and len(value) == 2, context + ': objective shape')
    integer(value[0], 0, sum(j['priority'] for j in manifest['jobs']), context + ': priority')
    integer(value[1], 0, len(manifest['jobs']), context + ': admitted')
    need((value[0] == 0) == (value[1] == 0), context + ': zero objective inconsistency')
    return tuple(value)


def summarize_recount(recount):
    summary = {}
    for cohort in ('all', 'constructed', 'generated'):
        selected = [r for r in recount if cohort == 'all' or r['kind'] == cohort]
        positive = [r for r in selected if r['optimum'][0] != 0]
        optimum_sum = sum(r['optimum'][0] for r in selected)
        section = dict(cases=len(selected), nonzero_optimum=len(positive),
                       zero_optimum=len(selected)-len(positive), optimal_priority_total=optimum_sum,
                       corruption_checks=sum(r['corruption_applicable'] for r in selected), policies={})
        for policy in POLICIES:
            values = [r['scores'].get(policy) for r in selected]
            valid_values = [v for v in values if v is not None]
            achieved = sum(v[0] for v in valid_values)
            ratios = [Fraction(r['scores'][policy][0], r['optimum'][0]) for r in positive
                      if policy in r['scores']]
            section['policies'][policy] = dict(
                valid_plans=len(valid_values),
                exact_objective_matches=sum(r['scores'].get(policy) == r['optimum'] for r in selected),
                priority_matches=sum(policy in r['scores'] and r['scores'][policy][0] == r['optimum'][0] for r in selected),
                secondary_tie_losses=sum(policy in r['scores'] and r['scores'][policy][0] == r['optimum'][0]
                                         and r['scores'][policy][1] < r['optimum'][1] for r in selected),
                achieved_priority=achieved, priority_regret=optimum_sum-achieved,
                mean_priority_ratio_nonzero=str(sum(ratios, Fraction())/len(positive)) if positive else None,
                aggregate_priority_ratio=str(Fraction(achieved, optimum_sum)) if optimum_sum else None)
        summary[cohort] = section
    return summary


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(study_directory):
    base = Path(study_directory).resolve()
    discrepancies = []
    def issue(where, message):
        discrepancies.append(dict(location=where, message=message))
    def check(condition, where, message):
        if not condition:
            issue(where, message)
    freeze = strict_loads((base/'FREEZE.json').read_text())
    cases = strict_loads((base/'cases.json').read_text())
    saved = strict_loads((base/'RESULTS.json').read_text())
    hash_checks = 0
    for name, expected in freeze['sha256'].items():
        path = Path(name)
        safe = not path.is_absolute() and '..' not in path.parts
        if safe:
            try:
                (base/path).resolve().relative_to(base)
            except ValueError:
                safe = False
        check(safe, 'freeze:'+name, 'unsafe path')
        if not safe:
            continue
        try:
            check(type(expected) is str and re.fullmatch(r'[0-9a-f]{64}', expected) is not None
                  and sha(base/path) == expected, 'freeze:'+name, 'hash mismatch')
            hash_checks += 1
        except OSError as error:
            issue('freeze:'+name, str(error))
    required = {'SPEC.txt', 'PROTOCOL.txt', 'cases.json', 'generate_cases.py', 'solver.py',
                'verifier.py', 'oracle.py', 'run_study.py'}
    check(required <= set(freeze['sha256']), 'freeze', 'missing core frozen files')
    check(saved.get('freeze_sha256') == sha(base/'FREEZE.json'), 'results', 'freeze digest binding mismatch')
    check(type(freeze.get('schema_version')) is int and freeze['schema_version'] == 1
          and type(freeze.get('cohort_cases')) is int and freeze['cohort_cases'] == 140
          and freeze.get('headline_run_started') is False, 'freeze', 'prospective metadata mismatch')
    for field, expected in (('schema_version', 1), ('status', 'complete'), ('expected_cases', 140),
                            ('wall_ceiling_seconds', 180), ('gate_pass', True)):
        check(deep_equal(saved.get(field), expected), 'results:'+field, 'saved completion/gate metadata mismatch')
    elapsed = saved.get('elapsed_seconds')
    check(type(elapsed) in (float, int) and 0 <= elapsed <= 180, 'results:elapsed_seconds', 'wall budget outside bound')
    try:
        dates = [datetime.fromisoformat(s.replace('Z', '+00:00')) for s in
                 (freeze['frozen_utc'], saved['started_utc'], saved['completed_utc'])]
        check(all(d.tzinfo is not None for d in dates) and dates == sorted(dates), 'chronology', 'invalid freeze/run ordering')
    except (KeyError, ValueError, TypeError) as error:
        issue('chronology', str(error))
    need(type(cases) is list, 'cases must be a list')
    rows = saved['rows']; need(type(rows) is list, 'result rows must be a list')
    check(len(cases) == len(rows) == 140, 'cohort', 'expected 140 cases and rows')
    case_ids = [c['case_id'] for c in cases]; row_ids = [r['case_id'] for r in rows]
    check(len(set(case_ids)) == len(case_ids) and len(set(row_ids)) == len(row_ids), 'cohort', 'duplicate case/result ID')
    check(case_ids == row_ids, 'cohort', 'case/result identities or order differ')
    check(Counter(c['kind'] for c in cases) == Counter(constructed=12, generated=128), 'cohort', 'kind composition differs')
    check({c['case_id'] for c in cases if c['kind'] == 'constructed'} == CONSTRUCTED, 'cohort', 'constructed case IDs differ')
    check({c['case_id'] for c in cases if c['kind'] == 'generated'} == {'seed_'+str(i).zfill(3) for i in range(128)},
          'cohort', 'generated seed IDs differ')
    row_map = {r['case_id']: r for r in rows}
    recount = []; comparisons = 0; property_checks = 0; mutation_checks = 0
    for case in cases:
        key = case['case_id']; row = row_map.get(key)
        if row is None:
            continue
        try:
            keys(case, ('case_id', 'kind', 'manifest'), 'case')
            keys(row, ('case_id', 'kind', 'optimum', 'policies', 'properties'), 'result row')
            check(row['kind'] == case['kind'], key, 'cohort kind differs')
            m = case['manifest']; validate_manifest(m)
            optimum = tuple_objective(row['optimum'], m, 'saved oracle')
            keys(row['policies'], POLICIES, 'policy names')
        except (KeyError, ValueError, TypeError) as error:
            issue(key, str(error)); continue
        item = dict(case_id=key, kind=case['kind'], optimum=optimum, scores={}, corruption_applicable=False)
        for policy in POLICIES:
            location = key+':'+policy; output = row['policies'][policy]
            try:
                keys(output, ('objective', 'plan', 'verification'), 'policy result')
                objective = objective_from_plan(m, output['plan'])
                item['scores'][policy] = objective
                check(deep_equal(output['objective'], list(objective)), location, 'saved objective differs from raw plan')
                expected = dict(valid=True, errors=[], priority=objective[0], admitted=objective[1])
                check(deep_equal(output['verification'], expected), location, 'saved verifier fields differ from raw plan')
                check(objective <= optimum, location, 'raw policy objective exceeds saved oracle')
                if policy == 'exact':
                    check(objective == optimum, location, 'raw exact objective differs from saved oracle')
                    comparisons += 1
            except (KeyError, ValueError, TypeError) as error:
                issue(location, str(error))
        try:
            props = row['properties']; keys(props, ('objectives', 'gpu_reuse_rejection'), 'properties')
            keys(props['objectives'], ('reversed', 'relaxed', 'reduced'), 'property names')
            pv = {name: tuple_objective(value, m, 'property '+name) for name, value in props['objectives'].items()}
            check(pv['reversed'] == optimum, key+':reversed', 'order-invariance equality fails')
            check(pv['relaxed'] >= optimum, key+':relaxed', 'resource-relaxation inequality fails')
            check(pv['reduced'] <= optimum, key+':reduced', 'resource-removal inequality fails')
            property_checks += 3
            plan = row['policies']['exact']['plan']
            item['corruption_applicable'] = len(plan['placements']) >= 2
            rejection = props['gpu_reuse_rejection']
            if item['corruption_applicable']:
                bad = copy.deepcopy(plan)
                bad['placements'][1]['gpus'][0] = bad['placements'][0]['gpus'][0]
                try:
                    objective_from_plan(m, bad)
                except ValueError:
                    mutation_checks += 1
                else:
                    issue(key+':gpu_reuse', 'independent checker accepted reconstructed mutation')
                keys(rejection, ('valid', 'errors', 'priority', 'admitted'), 'corruption result')
                check(rejection['valid'] is False and rejection['priority'] is None and rejection['admitted'] is None
                      and type(rejection['errors']) is list and bool(rejection['errors'])
                      and all(type(e) is str and bool(e) for e in rejection['errors']),
                      key+':gpu_reuse', 'saved corruption rejection malformed')
            else:
                check(rejection is None, key+':gpu_reuse', 'unexpected corruption result with fewer than two placements')
        except (KeyError, ValueError, TypeError, IndexError) as error:
            issue(key+':properties', str(error))
        recount.append(item)
    summary = summarize_recount(recount)
    if not deep_equal(summary, saved.get('summary')):
        for cohort in summary:
            if not deep_equal(summary[cohort], saved.get('summary', {}).get(cohort)):
                issue('summary:'+cohort, 'saved summary differs from independent count/exact Fraction reconstruction')
    return dict(schema_version=1, audit='Independent saved-evidence consistency and raw-plan audit',
                study_directory=str(base), results_sha256=sha(base/'RESULTS.json'), freeze_sha256=sha(base/'FREEZE.json'),
                saved_evidence_consistent=not discrepancies, discrepancy_count=len(discrepancies), discrepancies=discrepancies,
                checks=dict(frozen_file_hashes=hash_checks, manifests=len(recount),
                            raw_plans=sum(len(r['scores']) for r in recount),
                            exact_objective_matches_checked=comparisons,
                            saved_property_equalities_inequalities=property_checks,
                            independently_rejected_gpu_reuse_mutations=mutation_checks),
                summary=summary,
                limitations=[
                    'No solver, verifier, oracle, generator, or run_study code was imported or executed.',
                    'Feasible exact plans matching saved oracle tuples do not independently prove global optimality.',
                    'Altered-instance plans and separate oracle traces were not saved; only their objective bounds and inequalities are audited.',
                    'Hashes bind current bytes to the saved freeze manifest; they do not attest external timestamps or absence of unrecorded runs.',
                    'Synthetic cohort ratios are descriptive; priority scores are not measured economic value.',
                    'No live placement, measured serving latency, energy saving, production safety, or independent-owner pooling is established.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study_directory', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        result = audit(args.study_directory)
    except (OSError, ValueError, TypeError, KeyError, IndexError, RecursionError) as error:
        result = dict(saved_evidence_consistent=False, discrepancy_count=1,
                      discrepancies=[dict(location='unreadable_or_malformed_input', message=str(error))])
    rendered = json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n'
    if args.output:
        args.output.write_text(rendered)
        print(json.dumps({key: result[key] for key in ('saved_evidence_consistent', 'discrepancy_count')}))
    else:
        print(rendered, end='')
    return 0 if result['saved_evidence_consistent'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
