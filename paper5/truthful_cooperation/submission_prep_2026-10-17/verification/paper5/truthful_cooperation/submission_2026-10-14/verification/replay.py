#!/usr/bin/env python3
"""Replay only the 14 October central-theorem and comparison checks.
Standard library; preserves source files and requires an explicit output file.
This is bounded computational corroboration, not formal verification.
"""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error("--output must be a new file; existing paths and symlinks are refused")
    root=(args.repo_root or Path(__file__).resolve().parents[4]).resolve()
    local=Path('paper5/truthful_cooperation/submission_2026-10-14/verification')
    campaign=Path('research_campaigns/2026-10-07-six-hour-campaign/verification')
    jobs=[('general_production',campaign/'general_production.py',[]),
          ('simple_dag_lower',campaign/'simple_dag_lower.py',['--skip-subdivision']),
          ('core_projection',campaign/'core_projection.py',[]),
          ('two_owner_scope',local/'two_owner_scope.py',[]),
          ('lower_symmetry',local/'lower_symmetry_checks.py',['--repo-root',str(root)])]
    sources=[path for _,path,_ in jobs]+[campaign/'binary_packing.py',local/'replay.py']
    hashes={str(p):digest(root/p) for p in sources}
    for path in sources:
        if any(isinstance(n,ast.Assert) for n in ast.walk(ast.parse((root/path).read_text()))):
            raise RuntimeError('Optimization-disabled assertion: '+str(path))
    records=[];started=datetime.now(timezone.utc).isoformat()
    for name,path,extra in jobs:
        command=[sys.executable,'-B','-O',str(path),*extra]
        before=time.monotonic()
        try:
            p=subprocess.run(command,cwd=root,capture_output=True,text=True,timeout=600)
        except subprocess.TimeoutExpired as e:
            def decode(x):return x.decode(errors='replace') if isinstance(x,bytes) else x or ''
            p=subprocess.CompletedProcess(command,124,decode(e.stdout),decode(e.stderr)+'\n600-second timeout')
        passed=p.returncode==0 and 'PASS' in p.stdout
        records.append(dict(name=name,command=command,exit_code=p.returncode,
                            status='PASS' if passed else 'FAIL',seconds=time.monotonic()-before,
                            stdout=p.stdout,stderr=p.stderr))
        print(name,records[-1]['status'],flush=True)
        if not passed:break
    unchanged=all(digest(root/p)==h for p,h in hashes.items())
    status='PASS' if unchanged and len(records)==len(jobs) and all(x['status']=='PASS' for x in records) else 'FAIL'
    result=dict(status=status,started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),
                python_version=sys.version,source_sha256=hashes,sources_unchanged=unchanged,runs=records,
                scope='Five bounded checks, not complete replay of historical supplement or formal proof verification.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as stream:
        stream.write(json.dumps(result,indent=2)+'\n')
    return 0 if status=='PASS' else 1

if __name__=='__main__':sys.exit(main())
