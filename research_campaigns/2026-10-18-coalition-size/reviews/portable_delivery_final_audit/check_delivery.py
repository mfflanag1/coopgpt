#!/usr/bin/env python3
"""Bounded delivery audit. No original-paper or outcome-data copies/downloads.

Checks selected-input closure, current saved replay hashes, a metadata-only
relocation, and a negative assertion-disabled certificate fixture. Does not
repeat the basic/extended mathematical suites or build a final archive.
"""
from pathlib import Path
from datetime import datetime, timezone
import ast
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
CAMP = HERE.parents[1]
VIS = CAMP.parents[1]
BUILDER = VIS / 'mega-build/build_campaign_index.py'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(relative):
    return json.loads((CAMP / relative).read_text())

def main():
    if sys.flags.optimize:
        raise SystemExit('Audit requires assertions enabled; unset PYTHONOPTIMIZE and omit -O/-OO.')
    # Compile ONLY the pure exclusion function, never execute its file-writing
    # top-level builder. All selection predicates remain the author's own code.
    tree = ast.parse(BUILDER.read_text())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'exclusion')
    namespace = {'CAMP': CAMP, 'INDEX': CAMP / 'campaign-index.html'}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(BUILDER), 'exec'), namespace)
    selected = {str(p.relative_to(CAMP)) for p in CAMP.rglob('*')
                if p.is_file() and p.name not in {'campaign-index.html', 'PORTABLE_MANIFEST.json'}
                and namespace['exclusion'](p) is None}

    reports = [read('checks/portable_runner_validation/basic_REPLAY_REPORT.json'),
               read('checks/portable_runner_validation/extended_REPLAY_REPORT.json')]
    replay_inputs = {}
    for report in reports:
        assert report['status'] == 'PASS'
        for job in report['jobs']:
            assert job['returncode'] == 0 and job['verdict'] == 'PASS'
            for path, expected in job['inputs_sha256'].items():
                assert digest(CAMP / path) == expected
                assert path in selected
                replay_inputs[path] = expected

    # Ensure current runner's job source paths are the same paths whose saved
    # executions were inspected. Fixtures are checked below through exact input
    # inventories and direct checker-source inspection.
    runner = CAMP / 'reproduce_campaign.py'
    literals = {node.value for node in ast.walk(ast.parse(runner.read_text()))
                if isinstance(node, ast.Constant) and isinstance(node.value, str)}
    current_jobs = {x for x in literals if x.endswith('.py')}
    assert current_jobs == {p for p in replay_inputs if p.endswith('.py')}
    assert {x for x in literals if x in {'PROFILE_TABLE.json', 'ACTION_GROUPS.json',
                                       'LIFTED_CERTIFICATE_ROWS.jsonl.gz'}} == {
        Path(p).name for p in replay_inputs if not p.endswith('.py')}

    meta_saved = read('checks/portable_runner_validation/metadata_integrity_v2_PASS.json')
    meta_inputs = {'application/' + name: expected
                   for name, expected in meta_saved['inputs_sha256'].items()}
    assert len(meta_inputs) == 339
    for path, expected in meta_inputs.items():
        assert path in selected and digest(CAMP / path) == expected
    owned_sources = ['reproduce_campaign.py', 'application/verify_portable_metadata.py',
                     'REPRODUCTION_GUIDE.txt',
                     'reviews/delivery_integrity_audit/REPAIR_DISPOSITION.txt']
    before = {p: digest(CAMP / p) for p in set(replay_inputs) | set(meta_inputs) | set(owned_sources)}
    assert before['application/verify_portable_metadata.py'] == 'a6d92ecb2eb9f5fb8c7a887b37fc408a0da85b3c9675c88014903097d33503ce'
    clean_env = dict(os.environ)
    clean_env.pop('PYTHONOPTIMIZE', None)
    with tempfile.TemporaryDirectory(prefix='selected-extraction-', dir=HERE) as temporary:
        extracted = Path(temporary) / 'research-campaigns/2026-10-18-coalition-size'
        extracted.mkdir(parents=True)
        for rel in set(replay_inputs) | set(meta_inputs) | {'reproduce_campaign.py',
                                                        'application/verify_portable_metadata.py'}:
            destination = extracted / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(CAMP / rel, destination)
            assert digest(destination) == digest(CAMP / rel)
        help_run = subprocess.run([sys.executable, str(extracted / 'reproduce_campaign.py'), '--help'],
                                  cwd=temporary, env=clean_env, text=True, capture_output=True)
        assert help_run.returncode == 0 and '--suite' in help_run.stdout
        metadata_run = subprocess.run([sys.executable, str(extracted / 'application/verify_portable_metadata.py')],
                                      cwd=temporary, env=clean_env, text=True, capture_output=True)
        assert metadata_run.returncode == 0, metadata_run.stderr
        metadata = json.loads(metadata_run.stdout)
        expected = {k: v for k, v in meta_saved.items() if k != 'checked_utc'}
        assert {k: v for k, v in metadata.items() if k != 'checked_utc'} == expected

        # Deliberately invalid evidence ONLY in the temporary copy. The budget
        # row is K*F-total >=0, so changing its RHS to1 makes it an illegal row.
        fixture = extracted / 'reviews/projective_dual_lift'
        rows_path = fixture / 'LIFTED_CERTIFICATE_ROWS.jsonl.gz'
        rows = [json.loads(line) for line in gzip.decompress(rows_path.read_bytes()).splitlines()]
        position = next(i for i, row in enumerate(rows) if row['kind'] == 'budget')
        assert rows[position]['rhs'] == 0
        rows[position]['rhs'] = 1
        rows_path.write_bytes(gzip.compress(('\n'.join(json.dumps(row) for row in rows)+'\n').encode(), mtime=0))
        command = [sys.executable, str(fixture / 'verify_lifted_certificate.py')]
        ordinary = subprocess.run(command, cwd=temporary, env=clean_env, text=True, capture_output=True)
        optimized_env = dict(clean_env, PYTHONOPTIMIZE='1')
        optimized = subprocess.run(command, cwd=temporary, env=optimized_env, text=True, capture_output=True)
        assert ordinary.returncode != 0 and 'AssertionError' in ordinary.stderr
        assert optimized.returncode == 0, optimized.stderr
        false_pass = json.loads(optimized.stdout)
        assert false_pass['status'] == 'PASS' and false_pass['rhs'] != '4/3'
        negative = {'changed_temporary_row': position, 'kind': 'budget', 'old_rhs': 0, 'new_rhs': 1,
                    'normal_returncode': ordinary.returncode,
                    'normal_result': 'REJECTED by legal budget-row assertion',
                    'PYTHONOPTIMIZE_1_returncode': optimized.returncode,
                    'PYTHONOPTIMIZE_1_status': false_pass['status'],
                    'reported_rhs_despite_PASS': false_pass['rhs'],
                    'expected_valid_rhs': '4/3',
                    'scope': 'Controlled invalid temporary fixture; sealed evidence unchanged.'}

    assert all(digest(CAMP / p) == h for p, h in before.items())
    result = {'status': 'PASS_WITH_VERIFIED_DELIVERY_FINDING',
              'checked_utc': datetime.now(timezone.utc).isoformat(),
              'selected_input_closure': 'PASS', 'replay_checker_count': len(current_jobs),
              'replay_selected_input_count': len(replay_inputs),
              'all_saved_basic_extended_input_hashes_match_current_sources': True,
              'metadata_selected_input_count': len(meta_inputs),
              'relocated_metadata_result_matches_saved_v2_except_timestamp': True,
              'relocated_metadata_dataset_bytes': metadata['dataset_body_bytes'],
              'relocated_runner_help': 'PASS',
              'assertion_disabled_negative_fixture': negative,
              'sealed_inputs_unchanged': True, 'temporary_copies_removed': True,
              'no_network_original_paper_copy_outcome_copy_or_decode': True,
              'scope': 'Delivery/input closure and one controlled negative fixture; no broad mathematical rerun, no final-archive assertion.',
              'source_hashes': {**{p: before[p] for p in owned_sources},
                                'VIS/mega-build/build_campaign_index.py': digest(BUILDER)},
              'replay_inputs': replay_inputs}
    output = HERE / 'CHECK_RESULT.json'
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
