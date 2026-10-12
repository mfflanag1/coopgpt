#!/usr/bin/env python3
"""Read-only independent quality diagnosis; imports no study scoring code."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError('nonfinite JSON constant: ' + value)


def inspect_request(row):
    marker = 'Input records:\n'
    if marker not in row['request_prompt']:
        raise ValueError('missing input-record marker')
    triples = re.findall(r'^(R[0-9]{4}) value=([0-9]{3}) flag=(KEEP|DROP)$',
                         row['request_prompt'].rsplit(marker, 1)[1], re.M)
    source = {key: (value, flag) for key, value, flag in triples}
    if not triples or len(source) != len(triples):
        raise ValueError('empty input or duplicate source ID')
    gold = [{'id': key, 'value': value} for key, value, flag in triples if flag == 'KEEP']
    text = ''.join(chunk['data'].get('response', '') for chunk in row['chunks'])
    malformed = None
    try:
        parsed = json.loads(text, object_pairs_hook=strict_object, parse_constant=reject_constant)
    except ValueError as exc:
        parsed = None
        malformed = str(exc)
    schema = (isinstance(parsed, dict) and set(parsed) == {'records'}
              and isinstance(parsed['records'], list)
              and all(isinstance(x, dict) and set(x) == {'id', 'value'}
                      and isinstance(x['id'], str) and re.fullmatch(r'R[0-9]{4}', x['id'])
                      and isinstance(x['value'], str) and re.fullmatch(r'[0-9]{3}', x['value'])
                      for x in parsed['records']))
    records = parsed['records'] if schema else []
    ids = [x['id'] for x in records]
    missing = [x['id'] for x in gold if x['id'] not in ids] if schema else []
    excluded = [key for key in ids if key in source and source[key][1] == 'DROP']
    wrong = [{'id': x['id'], 'returned': x['value'], 'source': source[x['id']][0]}
             for x in records if x['id'] in source and x['value'] != source[x['id']][0]]
    unknown = [key for key in ids if key not in source]
    duplicates = [key for key, count in collections.Counter(ids).items() if count > 1]
    final = row.get('final') or {}
    complete = (row.get('completed') is True and row.get('http_status') == 200
                and row.get('error') is None and row.get('deadline_exceeded') is False
                and final.get('done') is True
                and all('error' not in c['data'] for c in row['chunks']))
    exact = bool(complete and schema and records == gold)
    order_only = bool(complete and schema and not exact
                      and not (missing or excluded or wrong or unknown or duplicates)
                      and sorted(records, key=lambda x: x['id']) == gold)
    cap = row['request_options']['num_predict']
    tokens = final.get('eval_count')
    return dict(request_id=row['request_id'], input_records=len(source), keep_records=len(gold),
                returned_records=len(records) if schema else None, completed=complete,
                exact=exact, malformed_json=malformed, schema_valid=bool(schema),
                omitted_keep=missing, included_drop=excluded, wrong_values=wrong,
                unknown_ids=unknown, duplicate_ids=duplicates, order_only=order_only,
                output_ids=ids, expected_records=gold, returned_text=text,
                done_reason=final.get('done_reason'), eval_count=tokens, requested_cap=cap,
                below_cap=isinstance(tokens, int) and tokens < cap,
                context_margin=4096-final['prompt_eval_count']-cap if 'prompt_eval_count' in final else None)


def controller_summary(meta):
    states = [meta['before'], meta['after']] + [x['state'] for x in meta['host_checks']]
    percentages = [x['battery_percent'] for x in states]
    idle = [v for k, v in meta.items() if k.startswith('original_endpoint_idle_')]
    return dict(status=meta['status'], errors=meta['errors'],
                clean_unload_verified=meta['clean_unload_verified'],
                loaded_after_unload=meta['loaded_after_unload'],
                server_returncode=meta['dedicated_server_returncode'],
                snapshot_count=len(states), battery_min=min(percentages), battery_max=max(percentages),
                raw_battery_percent_matches=all(
                    (m := re.search(r'\b(\d{1,3})%;', x['power'])) is not None
                    and int(m.group(1)) == x['battery_percent'] for x in states),
                all_battery_power=all(x['power_source'] == 'Battery Power' for x in states),
                all_external_disconnected=all(x['external_power_connected'] is False for x in states),
                original_idle_all=bool(idle) and all(x is True for x in idle),
                host_check_phases=[x['phase'] for x in meta['host_checks']],
                host_checks_all_passed=all(x['passed'] is True for x in meta['host_checks']),
                thermal_texts=sorted({x['thermal'] for x in states}),
                runtime_parallel_values=meta['runtime_parallel_values'])


def diagnose(source_dir, capture_dir=None):
    source_dir = Path(source_dir).resolve()
    capture_dir = Path(capture_dir).resolve() if capture_dir else source_dir / 'capture'
    campaign_path = capture_dir / 'CAMPAIGN.json'
    campaign = json.loads(campaign_path.read_text())
    result = {'source_dir': str(source_dir), 'capture_dir': str(capture_dir),
              'campaign_sha256': hashlib.sha256(campaign_path.read_bytes()).hexdigest(),
              'campaign': {k: campaign.get(k) for k in ('status', 'qualified', 'selected', 'started_utc', 'finished_utc')},
              'stages': {}}
    for directory in sorted(capture_dir.glob('development-*')):
        if not directory.is_dir():
            continue
        rows = []
        for path in sorted(directory.glob('dev-*.json')):
            saved = json.loads(path.read_text())
            if len(saved['requests']) != 1:
                raise ValueError('expected one request in ' + str(path))
            rows.append(inspect_request(saved['requests'][0]))
        count = collections.Counter()
        for row in rows:
            count.update(requests=1, completed=int(row['completed']), exact=int(row['exact']),
                         schema_valid=int(row['schema_valid']), malformed_json=int(row['malformed_json'] is not None),
                         schema_failures=int(not row['schema_valid']),
                         omission_requests=int(bool(row['omitted_keep'])), omitted_records=len(row['omitted_keep']),
                         drop_requests=int(bool(row['included_drop'])), included_drop_records=len(row['included_drop']),
                         wrong_value_requests=int(bool(row['wrong_values'])), wrong_value_records=len(row['wrong_values']),
                         unknown_requests=int(bool(row['unknown_ids'])), duplicate_requests=int(bool(row['duplicate_ids'])),
                         order_only=int(row['order_only']), stop=int(row['done_reason'] == 'stop'),
                         length=int(row['done_reason'] == 'length'), below_cap=int(row['below_cap']))
        meta = json.loads((directory / 'SERVER_CONTROL.json').read_text())
        result['stages'][directory.name] = dict(counts=dict(count), requests=rows, controller=controller_summary(meta))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--capture-dir', type=Path, help='defaults to SOURCE_DIR/capture')
    args = parser.parse_args()
    print(json.dumps(diagnose(args.source_dir, args.capture_dir), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
