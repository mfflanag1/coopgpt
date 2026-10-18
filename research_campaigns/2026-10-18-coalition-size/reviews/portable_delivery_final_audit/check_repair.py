#!/usr/bin/env python3
"""Check assertion-enabled runner preflight only; no scientific suite rerun."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import gzip
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
CAMP = HERE.parents[1]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def require(condition, message):
    if not condition:
        raise ValueError(message)

def main():
    source = CAMP / 'reproduce_campaign.py'
    before = digest(source)
    clean = dict(os.environ)
    clean.pop('PYTHONOPTIMIZE', None)
    tests = []
    with tempfile.TemporaryDirectory(prefix='preflight-repair-', dir=HERE) as temp:
        root = Path(temp)
        script = root / 'reproduce_campaign.py'
        shutil.copy2(source, script)
        require(digest(script) == before, 'Copied runner differs')
        for label, flags, env in [
            ('PYTHONOPTIMIZE_1', [], dict(clean, PYTHONOPTIMIZE='1')),
            ('explicit_O', ['-O'], clean),
        ]:
            output = root / ('must_not_exist_' + label)
            result = subprocess.run([sys.executable, *flags, str(script), '--out', str(output)],
                                    cwd=root, env=env, text=True, capture_output=True)
            require(result.returncode != 0, label + ' unexpectedly succeeded')
            require('assertions' in result.stderr and 'PYTHONOPTIMIZE' in result.stderr,
                    label + ' lacks clear rejection message')
            require(not output.exists(), label + ' created output before rejecting')
            require(list(root.iterdir()) == [script], label + ' created an unexpected file')
            tests.append({'case': label, 'returncode': result.returncode,
                          'output_created': output.exists(),
                          'stderr': result.stderr.strip()})
        normal = subprocess.run([sys.executable, str(script), '--help'], cwd=root,
                                env=clean, text=True, capture_output=True)
        require(normal.returncode == 0 and '--suite' in normal.stdout,
                'Ordinary help was rejected')
        require(list(root.iterdir()) == [script], 'Ordinary help created output')
        tests.append({'case': 'ordinary_help', 'returncode': normal.returncode,
                      'output_created': False, 'result': 'PASS'})
        # Restrict only the job table to the existing lifted-certificate job;
        # retain the exact author's preflight, subprocess/env and verdict code.
        # This avoids rerunning the entire extended mathematical suite.
        fixture = root / 'reviews/projective_dual_lift'
        fixture.mkdir(parents=True)
        names = ['verify_lifted_certificate.py', 'PROFILE_TABLE.json',
                 'ACTION_GROUPS.json', 'LIFTED_CERTIFICATE_ROWS.jsonl.gz']
        fixture_hashes = {}
        for name in names:
            original = CAMP / 'reviews/projective_dual_lift' / name
            fixture_hashes[name] = digest(original)
            shutil.copy2(original, fixture / name)
        rows_path = fixture / names[-1]
        rows = [json.loads(line) for line in gzip.decompress(rows_path.read_bytes()).splitlines()]
        position = next(i for i, row in enumerate(rows) if row['kind'] == 'budget')
        require(rows[position]['rhs'] == 0, 'Unexpected original budget row')
        rows[position]['rhs'] = 1
        rows_path.write_bytes(gzip.compress(('\n'.join(json.dumps(row) for row in rows)+'\n').encode(), mtime=0))
        harness = root / 'restrict_job_table.py'
        harness.write_text('''from pathlib import Path
import ast, json, subprocess, sys
script=Path(sys.argv[1]); output=Path(sys.argv[2]); capture=Path(sys.argv[3])
tree=ast.parse(script.read_text())
main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
assignment=next(n for n in ast.walk(main) if isinstance(n,ast.Assign)
                and any(isinstance(t,ast.Name) and t.id=='jobs' for t in n.targets))
extension=next(n for n in ast.walk(main) if isinstance(n,ast.AugAssign)
               and isinstance(n.target,ast.Name) and n.target.id=='jobs')
lift=next(n for n in extension.value.elts if ast.literal_eval(n)[0]=='actual_variable_lift')
assignment.value=ast.copy_location(ast.List(elts=[lift],ctx=ast.Load()),assignment.value)
ast.fix_missing_locations(tree)
real_run=subprocess.run
observations=[]
def inspect_environment(*args,**kwargs):
    env=kwargs.get('env')
    observations.append({'explicit_environment':env is not None,
                         'PYTHONOPTIMIZE':None if env is None else env.get('PYTHONOPTIMIZE'),
                         'PYTHONPATH':None if env is None else env.get('PYTHONPATH')})
    return real_run(*args,**kwargs)
subprocess.run=inspect_environment
sys.argv=[str(script),'--out',str(output)]
try:
    exec(compile(tree,str(script),'exec'),{'__file__':str(script),'__name__':'__main__'})
finally:
    capture.write_text(json.dumps({'parent_optimization':sys.flags.optimize,'children':observations}))
''')
        output = root / 'negative_certificate_output'
        capture = root / 'child_environment.json'
        sentinel = str(root / 'preserved-pythonpath-sentinel')
        env = dict(clean, PYTHONOPTIMIZE='1', PYTHONPATH=sentinel)
        negative = subprocess.run([sys.executable, '-E', str(harness), str(script),
                                   str(output), str(capture)], cwd=root, env=env,
                                  text=True, capture_output=True)
        require(negative.returncode != 0, 'Corrupted certificate unexpectedly passed under -E')
        report = json.loads((output / 'REPLAY_REPORT.json').read_text())
        child = json.loads(capture.read_text())
        require(report['status'] == 'FAIL' and len(report['jobs']) == 1,
                'Runner did not reject the sole selected invalid certificate')
        require(child['parent_optimization'] == 0 and len(child['children']) == 1,
                'Unexpected parent/child execution')
        require(child['children'][0] == {'explicit_environment': True,
                                        'PYTHONOPTIMIZE': None, 'PYTHONPATH': sentinel},
                'Child environment did not remove optimization only')
        stderr = (output / 'actual_variable_lift/stderr.txt').read_text()
        require('AssertionError' in stderr, 'Invalid certificate was not rejected by assertion')
        for name, expected in fixture_hashes.items():
            require(digest(CAMP / 'reviews/projective_dual_lift' / name) == expected,
                    'Sealed original fixture changed')
        tests.append({'case': 'PYTHONOPTIMIZE_1_parent_E_corrupted_lift',
                      'returncode': negative.returncode, 'runner_verdict': report['status'],
                      'child_returncode': report['jobs'][0]['returncode'],
                      'parent_optimization': child['parent_optimization'],
                      'child_PYTHONOPTIMIZE_removed': True, 'child_PYTHONPATH_preserved': True,
                      'corruption': {'row': position, 'kind': 'budget', 'rhs': '0 -> 1'},
                      'harness_limit': 'Only job table restricted to one existing lift job; author control/env/verdict code unchanged.',
                      'result': 'INVALID_CERTIFICATE_REJECTED'})
    require(digest(source) == before, 'Original runner changed during test')
    out = {'status': 'PASS', 'checked_utc': datetime.now(timezone.utc).isoformat(),
           'runner_sha256': before, 'guide_sha256': digest(CAMP / 'REPRODUCTION_GUIDE.txt'),
           'tests': tests, 'temporary_copies_removed': True, 'original_unchanged': True,
           'scope': 'Preflight and child-environment repair only. Parent runs ordinary patched basic suite; no broad extended rerun or final archive tested.'}
    (HERE / 'REPAIR_CHECK.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()
