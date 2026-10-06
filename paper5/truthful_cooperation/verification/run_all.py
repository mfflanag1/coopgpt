#!/usr/bin/env python3
"""Replay the bundled exact checks in isolation (Python 3.9+, standard library).

Report identity ignores only the Python-version metadata. Expected reports are
finite regression evidence, not proofs. All acceptance checks survive -O.
"""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_report(report):
    content = dict(report)
    content.pop('python', None)
    return hashlib.sha256(json.dumps(content, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('validation/replay'))
    parser.add_argument('--jobs', type=int, default=3)
    parser.add_argument('--timeout', type=int, default=1800, help='Seconds per script')
    args = parser.parse_args()
    require(args.jobs >= 1 and args.timeout > 0, 'Positive jobs and timeout required')
    root = Path(__file__).resolve().parent.parent
    entries = json.loads((root / 'verification/SOURCE_MANIFEST.json').read_text())
    expected = json.loads((root / 'verification/EXPECTED_REPORTS.json').read_text())
    require(len(entries) == len(expected) == 6, 'Expected six distinct verifiers')
    require(len({e['copy'] for e in entries}) == 6, 'Duplicate verifier path')
    for entry in entries:
        source = root / entry['copy']
        require(source.is_file() and sha(source) == entry['sha256'], 'Source mismatch: ' + entry['copy'])
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='coopgt-replay-') as tmp:
        scratch = Path(tmp)
        shutil.copytree(root / 'verification', scratch / 'verification')
        def replay(entry):
            source = scratch / entry['copy']
            spec = expected[entry['copy']]
            report_path = source.with_name(spec['report'])
            # Never accept a pre-existing report, including one copied accidentally.
            if report_path.exists():
                report_path.unlink()
            task_started = time.monotonic()
            process = subprocess.run([sys.executable, '-B', '-O', str(source)],
                                     cwd=source.parent, text=True, capture_output=True,
                                     timeout=args.timeout)
            task_output = output / source.parent.name / source.stem
            task_output.mkdir(parents=True, exist_ok=True)
            (task_output / 'stdout.txt').write_text(process.stdout)
            (task_output / 'stderr.txt').write_text(process.stderr)
            require(process.returncode == 0, 'Verifier failed: ' + entry['copy'])
            require(report_path.is_file(), 'Missing fresh report: ' + entry['copy'])
            report = json.loads(report_path.read_text())
            require(report.get('status') == 'PASS', 'Non-PASS report: ' + entry['copy'])
            require(report.get('source_sha256') == entry['sha256'], 'Report/source mismatch')
            if 'payment_source_sha256' in report:
                require(report['payment_source_sha256'] == sha(source.with_name('verify_continuous.py')),
                        'Payment dependency mismatch')
            require(canonical_report(report) == spec['canonical_sha256'], 'Report regression: ' + entry['copy'])
            shutil.copy2(report_path, task_output / spec['report'])
            return {'script': entry['copy'], 'status': 'PASS', 'source_sha256': entry['sha256'],
                    'report_sha256': sha(report_path), 'canonical_report_sha256': canonical_report(report),
                    'seconds': round(time.monotonic() - task_started, 3)}
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
            for result in pool.map(replay, entries):
                results.append(result)
                print('PASS ' + result['script'], flush=True)
    summary = {'status': 'PASS', 'python': platform.python_version(),
               'runner_sha256': sha(Path(__file__)), 'scripts': results,
               'seconds': round(time.monotonic() - started, 3),
               'scope': 'Finite exact checks and regression hashes; universal theorems require the written proofs.'}
    (output / 'SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n')
    print('All six verifiers passed. Reports: ' + str(output), flush=True)


if __name__ == '__main__':
    main()
