#!/usr/bin/env python3
"""Combine consecutive collection segments without changing frozen metrics.

Read-only inputs; temporary links are removed after analysis. The first segment
may stand alone. A second segment is allowed only after a completed attempted
prefix stopped for budget, and must cover only the immediately following suffix.
Partial suffixes remain explicit missing windows. Energy is recomputed separately
from each segment's own capture, never from concatenated telemetry.

Limitations: segment completion is prospective protocol provenance, not additional
independent replication. Recorded timestamps/file hashes do not independently
prove when an amendment was first written. Original energy assumptions and all
single-device/finite-window limits remain applicable. Recount agreement does not
replace original metadata validity or establish energy validity.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import zlib


class CombineError(ValueError):
    pass


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    try:
        raw = path.read_bytes()
        return json.loads(raw, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value))), digest(raw)
    except (OSError, ValueError, UnicodeError) as error:
        raise CombineError(f'{path}: unreadable/invalid JSON ({type(error).__name__})') from error


def equal(a, b):
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def stamp(value):
    try:
        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if value.utcoffset() is None:
            raise ValueError('naive timestamp')
        return value
    except (ValueError, TypeError, AttributeError) as error:
        raise CombineError('missing/invalid timezone-aware campaign timestamp') from error


def relative_path(value):
    if not isinstance(value, str) or not value or Path(value).is_absolute() or '..' in Path(value).parts:
        raise CombineError('unsafe relative provenance filename')
    return Path(value)


def frozen_inputs(source):
    config, config_hash = read(source/'CONFIG.json')
    plan, plan_hash = read(source/'PLAN.json')
    freeze, freeze_hash = read(source/'FREEZE.json')
    if not isinstance(config, dict) or not isinstance(plan, list) or len(plan) != 18:
        raise CombineError('expected CONFIG object and 18-window PLAN')
    if any(not isinstance(p, dict) or type(p.get('index')) is not int or p['index'] != i for i, p in enumerate(plan, 1)):
        raise CombineError('PLAN indices must be exactly 1..18 in order')
    if not isinstance(freeze, dict) or not isinstance(freeze.get('sha256'), dict):
        raise CombineError('FREEZE.sha256 mapping absent')
    required = {'CONFIG.json', 'PLAN.json', 'analyze.py', 'energy.py'} | {p['trace_file'] for p in plan}
    if not required <= set(freeze['sha256']):
        raise CombineError('required design/analysis files absent from FREEZE')
    for name, expected in freeze['sha256'].items():
        path = source/relative_path(name)
        try:
            actual = digest(path.read_bytes())
        except OSError as error:
            raise CombineError('missing frozen source: ' + name) from error
        if actual != expected:
            raise CombineError('frozen source hash mismatch: ' + name)
    modules = {}
    for name in ('analyze.py', 'energy.py', 'independent_check.py'):
        try:
            modules[name] = digest((source/name).read_bytes())
        except OSError as error:
            raise CombineError('missing original analysis module: ' + name) from error
    return config, plan, dict(freeze_sha256=freeze_hash, config_sha256=config_hash,
                             plan_sha256=plan_hash, module_sha256=modules,
                             frozen_utc=freeze.get('frozen_utc'))


def inspect_segment(path, source, config, plan):
    campaign, campaign_hash = read(path/'CAMPAIGN.json')
    if not isinstance(campaign, dict) or campaign.get('status') not in ('completed', 'budget_stopped', 'aborted'):
        raise CombineError('segment must have a terminal campaign status: ' + path.name)
    start, finish = stamp(campaign.get('started_utc')), stamp(campaign.get('finished_utc'))
    if finish < start:
        raise CombineError('campaign finish precedes start: ' + path.name)
    provenance = {'CAMPAIGN.json': campaign_hash}
    for name, expected in (('CONFIG.json', config), ('PLAN.json', plan)):
        value, hashed = read(path/name)
        if not equal(value, expected):
            raise CombineError('segment ' + name + ' differs from frozen source: ' + path.name)
        provenance[name] = hashed
    rows = campaign.get('windows')
    if not isinstance(rows, list):
        raise CombineError('campaign.windows must be a list')
    indices = []
    for row in rows:
        if not isinstance(row, dict) or type(row.get('index')) is not int or not 1 <= row['index'] <= 18:
            raise CombineError('invalid campaign window index')
        index = row['index']
        if any(not equal(row.get(key), value) for key, value in plan[index-1].items()):
            raise CombineError('RUN assignment differs from PLAN: ' + str(index))
        value, hashed = read(path/f'window-{index:02d}'/'RUN.json')
        if not equal(value, row):
            raise CombineError('campaign record differs from RUN: ' + str(index))
        indices.append(index)
        provenance[f'window-{index:02d}/RUN.json'] = hashed
    if indices and indices != list(range(indices[0], indices[0]+len(indices))):
        raise CombineError('segment windows must be a consecutive ordered range')
    directories = sorted(p.name for p in path.glob('window-*'))
    expected = [f'window-{i:02d}' for i in indices]
    if directories != expected or any(not (path/name).is_dir() for name in expected):
        raise CombineError('window directories differ from campaign records; refusing selection/overwrite')
    if campaign['status'] == 'completed' and (not indices or indices[-1] != 18 or any(row.get('status') != 'completed' for row in rows)):
        raise CombineError('completed campaign does not end with completed window18')
    return dict(path=path, campaign=campaign, indices=indices, start=start, finish=finish,
                provenance=provenance, all_attempted_completed=all(row.get('status') == 'completed' for row in rows))


def validate_segments(source, paths, config, plan, frozen):
    if not 1 <= len(paths) <= 2 or len(set(paths)) != len(paths):
        raise CombineError('supply one or two distinct named segment directories')
    segments = [inspect_segment(path, source, config, plan) for path in paths]
    first = segments[0]
    if not first['indices'] or first['indices'] != list(range(1, len(first['indices'])+1)):
        raise CombineError('first segment must be nonempty and start at window1 without gaps')
    if stamp(frozen['frozen_utc']) > first['start']:
        raise CombineError('source freeze timestamp follows first campaign start')
    if len(segments) == 2:
        second = segments[1]
        if first['campaign']['status'] != 'budget_stopped' or not first['all_attempted_completed']:
            raise CombineError('continuation requires budget_stopped with every attempted prefix window completed')
        if not 0 < len(first['indices']) < 18 or second['indices'] != list(range(len(first['indices'])+1, len(first['indices'])+1+len(second['indices']))):
            raise CombineError('second segment overlaps/skips the strictly unrun suffix')
        if any(not (first['path']/f'window-{i:02d}'/'REQUESTS.json').is_file() for i in first['indices']):
            raise CombineError('completed prefix request capture is missing')
        campaign = second['campaign']
        if campaign.get('continuation_of') != first['path'].name or not equal(campaign.get('completed_prefix'), first['indices']):
            raise CombineError('continuation lineage/completed_prefix mismatch')
        if campaign.get('source_freeze_sha256') != frozen['freeze_sha256']:
            raise CombineError('continuation source-freeze identity mismatch')
        if second['start'] < first['finish']:
            raise CombineError('continuation begins before original campaign ends')
        amendment = relative_path(campaign.get('amendment'))
        candidates = [p for p in (second['path']/amendment, source/amendment) if p.is_file()]
        if not candidates:
            raise CombineError('referenced prospective continuation protocol is absent')
        hashes = {digest(path.read_bytes()) for path in candidates}
        if len(hashes) != 1:
            raise CombineError('ambiguous continuation protocol copies')
        second['amendment'] = dict(path=str(candidates[0]), sha256=next(iter(hashes)))
        if campaign.get('amendment_sha256') != second['amendment']['sha256']:
            raise CombineError('continuation amendment hash mismatch')
        for field, path in (('original_campaign_sha256', first['path']/'CAMPAIGN.json'),
                            ('original_power_sha256', first['path']/'POWER.txt.gz'),
                            ('continuation_script_sha256', source/'continue_study.py')):
            if not path.is_file() or campaign.get(field) != digest(path.read_bytes()):
                raise CombineError('continuation provenance mismatch: ' + field)
        claim, claim_hash = read(first['path']/'CONTINUATION_CLAIM.json')
        if (not isinstance(claim, dict) or claim.get('output_directory') != str(second['path'])
                or claim.get('source_freeze_sha256') != frozen['freeze_sha256']
                or not first['finish'] <= stamp(claim.get('created_utc')) <= second['start']):
            raise CombineError('exclusive continuation claim lineage/time mismatch')
        first['provenance']['CONTINUATION_CLAIM.json'] = claim_hash
        manifest_path = source/'CONTINUATION_FREEZE.json'
        manifest, hashed = read(manifest_path)
        required = {'independent_check.py', 'combine_analysis.py', 'continue_study.py', str(amendment)}
        if not isinstance(manifest, dict) or not isinstance(manifest.get('sha256'), dict) or not required <= set(manifest['sha256']):
            raise CombineError('continuation freeze lacks required analysis/wrapper/protocol hashes')
        for name, expected in manifest['sha256'].items():
            target = source/relative_path(name)
            if not target.is_file() or digest(target.read_bytes()) != expected:
                raise CombineError('continuation frozen hash mismatch: ' + name)
        if stamp(manifest.get('frozen_utc')) > second['start']:
            raise CombineError('continuation freeze timestamp follows suffix start')
        if manifest['sha256']['combine_analysis.py'] != digest(Path(__file__).read_bytes()):
            raise CombineError('executing combiner differs from continuation-frozen combiner')
        second['continuation_freeze'] = dict(path=str(manifest_path), sha256=hashed,
                                           frozen_utc=manifest['frozen_utc'], file_sha256=manifest['sha256'])
    union = [index for segment in segments for index in segment['indices']]
    if union != list(range(1, len(union)+1)):
        raise CombineError('combined attempts must be a disjoint consecutive prefix')
    return segments


@contextmanager
def frozen_modules(source):
    """Load exact source bytes without writing bytecode beside frozen files."""
    loaded = {}
    for name in ('energy', 'analyze', 'independent_check'):
        path = source/(name+'.py')
        spec = importlib.util.spec_from_file_location('_coop_frozen_'+name, path)
        module = importlib.util.module_from_spec(spec)
        exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
        loaded[name] = module
    old = sys.modules.get('energy')
    sys.modules['energy'] = loaded['energy']
    try:
        yield loaded['analyze'], loaded['energy'], loaded['independent_check']
    finally:
        if old is None:
            sys.modules.pop('energy', None)
        else:
            sys.modules['energy'] = old


def segment_power(segment, energy):
    errors, samples = [], []
    path = segment['path']
    try:
        stop, hashed = read(path/'POWER_STOP.json')
        segment['provenance']['POWER_STOP.json'] = hashed
        if not isinstance(stop, dict) or stop.get('stop_confirmed') is not True or type(stop.get('returncode')) is not int or stop['returncode'] != 0:
            errors.append('normal sampler termination unverified')
        if 'power_stop_error' in segment['campaign'] or not equal(segment['campaign'].get('power_stop'), stop):
            errors.append('campaign power-stop record missing/different or records an error')
    except CombineError as error:
        errors.append(str(error))
    try:
        raw = (path/'POWER.txt.gz').read_bytes()
        segment['provenance']['POWER.txt.gz'] = digest(raw)
        parsed = energy.parse_text(gzip.decompress(raw).decode('utf-8'))
        samples = parsed['samples']
        errors.extend(parsed['errors'])
    except (OSError, EOFError, zlib.error, UnicodeError, ValueError) as error:
        errors.append('power archive unreadable: ' + type(error).__name__)
    return dict(samples=samples, errors=errors)


def grouped(rows, analyzer):
    """Reuse frozen metrics, including its quantile and outcome definitions."""
    return dict(overall=analyzer.metrics(rows),
                by_cap={str(cap): analyzer.metrics([r for r in rows if r['cap'] == cap]) for cap in analyzer.CAPS},
                by_input_rows={str(size): analyzer.metrics([r for r in rows if r['input_rows'] == size]) for size in analyzer.INPUTS},
                by_cross_class={f'{size}x{cap}': analyzer.metrics([r for r in rows if r['input_rows'] == size and r['cap'] == cap]) for size in analyzer.INPUTS for cap in analyzer.CAPS})


def compare_recounts(summary, independent, analyzer):
    keys = ('planned_count', 'api_completed_count', 'quality_pass_count', 'api_slo_count', 'quality_slo_count',
            'api_completed_fraction', 'quality_pass_fraction', 'api_slo_fraction', 'quality_slo_fraction',
            'api_failure_or_unverified_count', 'recorded_failure_count', 'completion_latency_s', 'first_content_latency_s')
    mismatches, compared = [], 0
    def check(label, first, second):
        nonlocal compared
        compared += 1
        if not equal(first, second):
            mismatches.append(dict(field=label, analyzer=first, independent=second))
    def groups(label, first, second):
        for group in ('overall', 'by_cap', 'by_input_rows', 'by_cross_class'):
            for name in ([None] if group == 'overall' else sorted(set(first[group]) | set(second.get(group, {})))):
                a = first[group] if name is None else first[group].get(name, {})
                b = second.get(group, {}) if name is None else second.get(group, {}).get(name, {})
                for key in keys:
                    check(f'{label}/{group}/{name}/{key}', a.get(key), b.get(key))
    check('planned_count', summary['analyzed_planned_count'], independent['recounted_planned_count'])
    check('window_indices', [w['index'] for w in summary['windows']], [w['index'] for w in independent['windows']])
    by_index = {window['index']: window for window in independent['windows']}
    for window in summary['windows']:
        groups('window'+str(window['index']), grouped(window['requests'], analyzer), by_index.get(window['index'], {}).get('metrics', {}))
    check('cell_identities', sorted((c['rate'], c['parallel']) for c in summary['rate_parallel_cells']),
          sorted((c['rate'], c['parallel']) for c in independent['rate_parallel_cells']))
    for cell in independent['rate_parallel_cells']:
        rows = [row for window in summary['windows'] if window['rate'] == cell['rate'] and window['parallel'] == cell['parallel'] for row in window['requests']]
        groups(f"rate{cell['rate']}/P{cell['parallel']}", grouped(rows, analyzer), cell['metrics'])
    groups('aggregate', grouped([r for w in summary['windows'] for r in w['requests']], analyzer), independent['aggregate_mixed_class_totals'])
    matches = {(m['rate'], m['rep'], m['contrast']): m for m in independent['matched_comparisons']}
    check('matched_identities', sorted((m['rate'], m['rep'], m['contrast']) for m in summary['matched_comparisons']),
          sorted((m['rate'], m['rep'], m['contrast']) for m in independent['matched_comparisons']))
    for match in summary['matched_comparisons']:
        identity = (match['rate'], match['rep'], match['contrast'])
        check('matched/'+str(identity), match.get('difference'), matches.get(identity, {}).get('difference'))
    check('independent_design_errors', [], independent.get('design_errors'))
    return dict(passed=not mismatches, exact_comparisons=compared, mismatches=mismatches)


def combine(source_dir, segment_dirs):
    source = Path(source_dir).resolve(strict=True)
    paths = [Path(path).resolve(strict=True) for path in segment_dirs]
    config, plan, frozen = frozen_inputs(source)
    segments = validate_segments(source, paths, config, plan, frozen)
    membership = {index: number for number, segment in enumerate(segments) for index in segment['indices']}
    with frozen_modules(source) as (analyzer, energy, checker):
        powers = [segment_power(segment, energy) for segment in segments]
        with tempfile.TemporaryDirectory(prefix='coop-combine-') as temporary:
            merged = Path(temporary)
            for name in ('CONFIG.json', 'PLAN.json'):
                (merged/name).symlink_to(segments[0]['path']/name)
            for index, number in membership.items():
                (merged/f'window-{index:02d}').symlink_to(segments[number]['path']/f'window-{index:02d}', target_is_directory=True)
            # No global power file is invented. Original serving metrics are
            # independent of missing power; each energy result is replaced below.
            summary = analyzer.analyze(merged, source_dir=source)
            independent = checker.independent_check(source, merged)
        for window in summary['windows']:
            number = membership.get(window['index'])
            parsed = powers[number] if number is not None else dict(samples=[], errors=['window unrun in supplied segments'])
            window['energy'] = analyzer.energy_diagnostics(parsed, window['phases'])
            window['energy']['source_segment'] = segments[number]['path'].name if number is not None else None
            denominator = window['metrics']['quality_slo_count']
            for interval in window['energy']['intervals'].values():
                interval['quality_slo_denominator'] = denominator
                interval['combined_j_per_quality_slo_success'] = ({edge: interval[edge+'_j']['combined']/denominator for edge in ('lower', 'upper')} if interval['valid'] and denominator > 0 else None)
        energy_segments = [dict(name=s['path'].name, sample_count=len(p['samples']), parse_errors=p['errors']) for s, p in zip(segments, powers)]
        summary['energy_capture'] = dict(segmented=True, segments=energy_segments,
                                       parse_errors=[s['name']+': '+error for s in energy_segments for error in s['parse_errors']])
        checks = compare_recounts(summary, independent, analyzer)
    present = sorted(membership)
    complete = len(present) == 18 and all(s['all_attempted_completed'] for s in segments) and segments[-1]['campaign']['status'] == 'completed'
    provenance = [dict(name=s['path'].name, path=str(s['path']), status=s['campaign']['status'], indices=s['indices'],
                       started_utc=s['campaign']['started_utc'], finished_utc=s['campaign']['finished_utc'],
                       planned_offered=s['campaign'].get('planned_offered'), full_planned_offered=s['campaign'].get('full_planned_offered'),
                       all_attempted_completed=s['all_attempted_completed'], sha256=s['provenance'], amendment=s.get('amendment'),
                       continuation_freeze=s.get('continuation_freeze')) for s in segments]
    return dict(schema_version=1, full_collection_completed=complete, all_planned_windows_present=len(present) == 18,
                attempted_window_indices=present, unrun_window_indices=[i for i in range(1, 19) if i not in membership],
                source_dir=str(source), source_provenance=frozen, combiner_sha256=digest(Path(__file__).read_bytes()), segments=provenance,
                summary=summary, independent_counts=independent, reproduction_checks=checks,
                limitations=['Segments are one prospectively completed study, not additional independent repetitions.',
                             'No repeated, overlapping, skipped, or selectively substituted window is accepted.',
                             'Partial suffixes remain missing and cannot constitute a completed study.',
                             'Energy uses each segment separately and retains original validity/coverage assumptions.',
                             'Serving validity and energy validity remain distinct.',
                             'File identity and recorded chronology alone do not prove prospective amendment creation.',
                             'Existing single-device, finite-window, observational and no-causal-energy limits remain.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_dir', type=Path)
    parser.add_argument('segments', type=Path, nargs='+')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = combine(args.source_dir, args.segments)
    encoded = json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n'
    if args.output:
        protected = [args.source_dir.resolve()] + [path.resolve() for path in args.segments]
        output = args.output.resolve()
        if any(output == root or root in output.parents for root in protected):
            raise CombineError('output must be outside immutable source/segment directories')
        args.output.write_text(encoded)
        print(json.dumps(dict(output=str(args.output), full_collection_completed=result['full_collection_completed'], reproduction_passed=result['reproduction_checks']['passed']), sort_keys=True))
    else:
        print(encoded, end='')
    return 0 if result['reproduction_checks']['passed'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
