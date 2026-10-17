#!/usr/bin/env python3
"""Replay the curated finite evidence in a disposable copy, not the research tree."""
from pathlib import Path
import argparse, concurrent.futures, datetime, hashlib, json, shutil
import subprocess, sys, tempfile, time

def main():
    if sys.flags.optimize:
        raise SystemExit('Assertions must remain enabled; do not use python -O.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--only', nargs='*', help='Manifest check IDs; omit for all.')
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    manifest = json.loads((source/'handoff/CURATED_CHECKS.json').read_text())
    checks = manifest['checks']
    if args.only:
        unknown = set(args.only)-{r['id'] for r in checks}
        if unknown:
            raise SystemExit('Unknown check IDs: '+', '.join(sorted(unknown)))
        checks = [r for r in checks if r['id'] in args.only]
    records = []
    with tempfile.TemporaryDirectory(prefix='coopgpt-curated-replay-') as folder:
        copy = Path(folder)
        for lane in ('composition', 'energy', 'unrestricted', 'root'):
            for path in (source/lane).rglob('*'):
                rel = path.relative_to(source)
                if path.is_symlink() or any(x in {'.venv','__pycache__','.git'} for x in rel.parts):
                    continue
                if path.is_file() and path.suffix in {'.py','.json','.txt'}:
                    dst = copy/rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, dst)
        def run(row):
            start = time.monotonic()
            command = [sys.executable, '-I', str(copy/row['script']), *row['args']]
            script_digest = hashlib.sha256((copy/row['script']).read_bytes()).hexdigest()
            try:
                result = subprocess.run(command, cwd=copy, text=True, capture_output=True, timeout=180)
                status = 'PASS' if result.returncode == 0 else 'FAIL'
                output, error, code = result.stdout, result.stderr, result.returncode
            except subprocess.TimeoutExpired as exc:
                status, output, error, code = 'TIMEOUT', str(exc.stdout or ''), str(exc.stderr or ''), None
            return {**row, 'status':status, 'returncode':code,
                    'seconds':round(time.monotonic()-start, 3),
                    'script_sha256':script_digest,
                    'stdout':output, 'stderr':error}
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            for record in executor.map(run, checks):
                records.append(record)
                print(record['id']+': '+record['status'], flush=True)
    report = {'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'python':sys.version, 'isolated_copy':True, 'assertions_enabled':True,
              'scope':manifest['purpose'], 'checks':records,
              'status':'PASS' if all(r['status']=='PASS' for r in records) else 'FAIL'}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='checks'}, indent=2))
    raise SystemExit(0 if report['status']=='PASS' else 1)

if __name__ == '__main__':
    main()
