#!/usr/bin/env python3
"""Audit EXISTING code/text/JSON only. Never read .bin/.parquet or acquire data.

This establishes retained query/report scope, not unlogged execution history
or DuckDB's internal metadata materialization behavior.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent
CAMP = HERE.parents[1]
APP = CAMP / 'application'

def require(condition, message):
    if not condition:
        raise ValueError(message)

def read(name):
    return json.loads((APP / name).read_text())

def main():
    source = APP / 'm100_may_footer_gate.py'
    tree = ast.parse(source.read_text())
    queries = [n.args[0].value for n in ast.walk(tree)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
               and n.func.attr == 'execute' and n.args
               and isinstance(n.args[0], ast.Constant)
               and isinstance(n.args[0].value, str)]
    expected = [
        "SELECT name, type, repetition_type, logical_type, converted_type FROM parquet_schema(?)",
        "SELECT row_group_id, row_group_num_rows, path_in_schema, type, total_compressed_size, data_page_offset, dictionary_page_offset FROM parquet_metadata(?)",
        "SELECT row_group_id, stats_min_value, stats_max_value FROM parquet_metadata(?) WHERE path_in_schema='timestamp'",
    ]
    require(queries == expected, 'Retained query projections changed')
    report = read('m100_may_footers/report.json')
    require(report['status'] == 'COMPLETE_METADATA_ONLY' and report['error'] is None,
            'Incomplete saved footer report')
    member_keys = {'name', 'metric', 'member_size', 'footer_size', 'footer_sha256',
                   'schema_columns', 'schema', 'chunk_columns', 'chunks',
                   'timestamp_range_columns', 'timestamp_ranges', 'wrapper_note'}
    schema_columns = ['name', 'physical_type', 'repetition_type', 'logical_type', 'converted_type']
    chunk_columns = ['row_group_id', 'row_group_num_rows', 'path_in_schema', 'physical_type',
                     'total_compressed_size', 'data_page_offset', 'dictionary_page_offset']
    members = []
    for member in report['members']:
        require(set(member) == member_keys, 'Unexpected saved member fields')
        require(member['schema_columns'] == schema_columns, 'Unexpected schema projection')
        require(member['chunk_columns'] == chunk_columns, 'Unexpected chunk projection')
        require(member['timestamp_range_columns'] == ['row_group_id', 'minimum', 'maximum'],
                'Unexpected timestamp projection')
        require(all(len(row) == 5 for row in member['schema']), 'Unexpected schema row')
        require(all(len(row) == 7 for row in member['chunks']), 'Unexpected chunk row')
        require(all(len(row) == 3 and isinstance(row[1], str) and isinstance(row[2], str)
                    for row in member['timestamp_ranges']), 'Unexpected timestamp row')
        require({row[0] for row in member['timestamp_ranges']} == {row[0] for row in member['chunks']},
                'Row-group identifiers disagree')
        members.append({'metric': member['metric'], 'schema_columns': schema_columns,
                        'chunk_columns': chunk_columns, 'chunk_count': len(member['chunks']),
                        'chunk_paths': sorted({row[2] for row in member['chunks']}),
                        'timestamp_range_count': len(member['timestamp_ranges']),
                        'power_state_statistic_or_observation_fields_in_saved_projection': False})
    require({m['metric'] for m in members} == {'state', 'ps0_input_power', 'ps1_input_power'},
            'Unexpected selected metric')

    ledger_names = ['metadata_requests.jsonl', 'm100_may_metadata/requests.jsonl',
                    'm100_may_footers/requests.jsonl']
    rows = [json.loads(line) for name in ledger_names
            for line in (APP / name).read_text().splitlines()]
    dataset = [r for r in rows if r['kind'].startswith('dataset_')]
    require(len(dataset) == 334 and sum(r['body_bytes'] for r in dataset) == 468255,
            'Frozen dataset ledger changed')
    require({r['url'] for r in dataset} == {
        'https://zenodo.org/records/7588815/files/20-05.tar?download=1'},
        'Unexpected dataset source')
    counts = Counter(r['kind'] for r in dataset)
    require(counts == {'dataset_archive_metadata': 325, 'dataset_footer_metadata': 9},
            'Unexpected range roles')
    headers = read('m100_may_metadata/report.json')
    selected = {m['name']: m for m in headers['selected_members']}
    expected_ranges = set()
    for m in report['members']:
        owner = selected[m['name']]
        start, size = owner['offset'], owner['size']
        require(size == m['member_size'], 'Member size changed')
        expected_ranges.update({(start, 4), (start + size - 8, 8),
                                (start + size - 8 - m['footer_size'], m['footer_size'])})
    require({(r['start'], r['length']) for r in dataset
             if r['kind'] == 'dataset_footer_metadata'} == expected_ranges,
            'Footer request roles disagree with saved placement')

    plan = read('m100_training_day_plan.json')
    require(plan['candidate_day_start'] == '2020-05-12T00:00:00+00:00', 'Candidate changed')
    require(plan['coalesced_request_count'] == 84 and
            plan['coalesced_projected_cumulative_dataset_bytes'] == 92759641,
            'Byte proposal changed')
    require(all(m['candidate_groups_extend_outside_day'] for m in plan['members']),
            'Later-date mixing disclosure changed')
    collection = read('m100_may_metadata/zenodo_record.json')
    june = [f for f in collection['files'] if f['key'] == '20-06.tar']
    require(len(june) == 1, 'June collection entry absent')
    require(not any('20-06.tar' in r['url'] for r in rows), 'June archive request in ledger')
    output = {'status': 'PASS_WITH_WORDING_CLARIFICATION',
              'checked_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'Existing source, text and JSON only; no raw footer/data file opened, no SQL executed, no acquisition.',
              'footer_queries': queries, 'saved_report_members': members,
              'dataset_requests': len(dataset), 'dataset_bytes': sum(r['body_bytes'] for r in dataset),
              'dataset_requests_by_kind': dict(counts),
              'logged_dataset_urls_are_may_only': True,
              'whole_footer_bytes_acquired': True,
              'encoded_power_state_statistics_presence_or_internal_decode': 'Not inspected or established by this audit.',
              'power_state_statistics_selected_or_displayed_in_retained_projection': False,
              'timestamp_extrema_selected_and_saved': True,
              'june_collection_listing_present': {'key': june[0]['key'], 'size': june[0]['size'],
                                                   'checksum': june[0]['checksum']},
              'june_archive_requests_in_saved_ledgers': 0,
              'complete_unlogged_runtime_history_audited': False}
    (HERE / 'CHECK_RESULT.json').write_text(json.dumps(output, indent=2)+'\n')
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
