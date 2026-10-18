#!/usr/bin/env python3
"""Replay selected campaign evidence in a fresh directory; never fetch data.

This runner does not prove the universal theorem or replay every experiment.
Copied checkers keep their original names and hashes. Their generated outputs
are isolated from sealed research records.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    # The preserved scientific checkers use assertions for exact certificates.
    # Refuse optimization before making any output or invoking those checkers.
    if sys.flags.optimize != 0:
        raise SystemExit('Replay refused: Python assertions are disabled. Run without -O/-OO and unset PYTHONOPTIMIZE.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', choices=['basic', 'extended'], default='basic')
    parser.add_argument('--out', type=Path, help='New output directory; must not exist')
    args = parser.parse_args()
    if args.suite == 'extended':
        missing = [name for name in ['numpy', 'scipy'] if importlib.util.find_spec(name) is None]
        if missing:
            parser.error('Extended suite needs existing packages: ' + ', '.join(missing) +
                         '. Nothing was installed or downloaded. Use --suite basic for standard-library checks.')
    if args.out:
        output = args.out.expanduser().resolve()
        output.mkdir(parents=True, exist_ok=False)
    else:
        output = Path(tempfile.mkdtemp(prefix='coopgpt-campaign-replay-')).resolve()

    jobs = [
        ('projective_geometry_and_scalar', 'lower/projective_cube_root_check.py',
         ['--max-geometry-m', '4', '--max-scalar-m', '64'], []),
        ('bounded_coalition_tail', 'checks/projective_bounded_tail.py', [], []),
    ]
    if args.suite == 'extended':
        jobs += [
            ('general_arity', 'lower/general_arity_circuit_check.py', [], []),
            ('actual_variable_lift', 'reviews/projective_dual_lift/verify_lifted_certificate.py', [],
             ['PROFILE_TABLE.json', 'ACTION_GROUPS.json', 'LIFTED_CERTIFICATE_ROWS.jsonl.gz']),
            ('cea_owner_cells', 'reviews/cea_calibration_audit/check_refined_cells.py', [], []),
            ('fixed_partition_synthesis', 'reviews/polyhedral_audit/independent_synthesis.py', [], []),
        ]
    report = {
        'status': 'RUNNING', 'started_utc': datetime.now(timezone.utc).isoformat(),
        'suite': args.suite, 'python': sys.version, 'source_root': str(ROOT),
        'python_optimization': sys.flags.optimize, 'assertions_enabled': True,
        'output_root': str(output), 'jobs': [],
        'scope': 'Selected exact finite evidence only. Universal symmetrization, all-size proof, historical priority and application validity are not certified by this runner.',
        'network_access': 'No requests, downloads, installs or application-data acquisition.',
    }
    report_path = output / 'REPLAY_REPORT.json'
    # A parent started with -E can ignore PYTHONOPTIMIZE while its children
    # would inherit it. Strip only this flag, retaining existing package paths.
    checker_environment = dict(os.environ)
    checker_environment.pop('PYTHONOPTIMIZE', None)

    def save():
        report_path.write_text(json.dumps(report, indent=2) + '\n')

    save()
    for label, relative, arguments, fixtures in jobs:
        source = ROOT / relative
        work = output / label
        work.mkdir()
        selected = [source] + [source.parent / name for name in fixtures]
        inputs = {}
        for original in selected:
            if not original.is_file():
                report['status'] = 'FAIL_MISSING_INPUT'
                report['missing_input'] = str(original)
                save()
                raise SystemExit(f'Missing included evidence: {original}; report {report_path}')
            copied = work / original.name
            shutil.copy2(original, copied)
            inputs[str(original.relative_to(ROOT))] = digest(original)
            if digest(copied) != digest(original):
                report['status'] = 'FAIL_COPY_INTEGRITY'
                report['failed_copy'] = str(copied)
                save()
                raise SystemExit(f'Copied evidence does not match its source; inspect {report_path}')
        command = [sys.executable, source.name, *arguments]
        started = time.monotonic()
        with (work / 'stdout.txt').open('w') as stdout, (work / 'stderr.txt').open('w') as stderr:
            completed = subprocess.run(command, cwd=work, stdout=stdout, stderr=stderr,
                                       env=checker_environment, check=False)
        record = {'name': label, 'command': command, 'inputs_sha256': inputs,
                  'returncode': completed.returncode, 'elapsed_seconds': round(time.monotonic()-started, 3),
                  'stdout': str((work/'stdout.txt').relative_to(output)),
                  'stderr': str((work/'stderr.txt').relative_to(output))}
        report['jobs'].append(record)
        if completed.returncode != 0:
            report['status'] = 'FAIL'
            save()
            raise SystemExit(f'{label} failed; inspect {report_path}')
        try:
            result = json.loads((work/'stdout.txt').read_text())
        except (ValueError, OSError) as error:
            report['status'] = 'FAIL_MALFORMED_RESULT'
            record['error'] = str(error)
            save()
            raise SystemExit(f'{label} returned no parseable result; inspect {report_path}')
        if not (result.get('status') == 'PASS' or result.get('PASS') is True):
            report['status'] = 'FAIL_NO_PASS_VERDICT'
            save()
            raise SystemExit(f'{label} lacks explicit PASS; inspect {report_path}')
        record['verdict'] = 'PASS'
        record['generated_files'] = {str(p.relative_to(work)): digest(p)
                                     for p in work.iterdir() if p.is_file() and p.name != source.name}
        save()
        print(f'{label}: PASS', flush=True)
    report['status'] = 'PASS'
    report['completed_utc'] = datetime.now(timezone.utc).isoformat()
    save()
    print(f'Replay report: {report_path}', flush=True)


if __name__ == '__main__':
    main()
