"""Recompute the package's bounded exact evidence; no stored PASS is trusted."""
from pathlib import Path
from itertools import product
import ast
import hashlib
import json
import platform
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
STAGES = (
    ('exact_assignment.py', 'two_by_two_calibration.json'),
    ('verify_assignment_theorem.py', 'assignment_theorem_calibration.json'),
    ('calibrate_three.py', 'three_calibration.json'),
    ('verify_gadgets.py', 'gadget_exact_results.json'),
    ('verify_family_independent.py', 'independent_family_calibration.json'),
    ('verify_extensions.py', 'extension_checks.json'),
    ('verify_priority_exclusions.py', 'priority_exclusion_checks.json'),
    ('verify_independent.py', 'independent_checks.json'),
)


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def coverage(name, record):
    if name == 'exact_assignment.py':
        rows = record['cases']
        actual = {tuple(a for row in r['matrix'] for a in row) for r in rows}
        expected = {p for p in product(range(4), repeat=4) if any(p)}
        require(len(rows) == 255 and actual == expected, 'pair matrix coverage')
    elif name == 'verify_assignment_theorem.py':
        require(len(record['two_by_two']) == 255, 'pair theorem coverage')
        require(len(record['targeted']) == 7 and len(record['attaining_families']) == 5, 'pair targets')
        require({len(r['matrix']) for r in record['attaining_families']} == {2,3,4,5,6}, 'pair family parameters')
    elif name == 'calibrate_three.py':
        rows = record['binary_cases']
        actual = {tuple(w for layer in r['weights'] for row in layer for w in row) for r in rows}
        require(len(rows) == 256 and actual == set(product(range(2), repeat=8)), 'binary tensor coverage')
        require(len(record['targeted_three']) == 12 and len(record['additive_cases']) == 3, 'triple controls')
    elif name == 'verify_gadgets.py':
        require(len(record['cases']) == 11 and len(record['negative_controls']) == 2, 'gadget coverage')
        expected = {(l,0,False) for l in (0,1,2,3,5)} | {(l,r,True) for l,r in ((1,0),(1,2),(2,0),(2,4),(3,9),(5,12))}
        require({(r['L'],r['R'],r['shifted']) for r in record['cases']} == expected, 'gadget parameters')
    elif name == 'verify_family_independent.py':
        require(len(record) == 4 and {(r['L'],r['R']) for r in record} == {(1,0),(2,1),(3,0),(4,16)}, 'second generator parameters')
    elif name == 'verify_extensions.py':
        require(len(record['graphs']) == 6 and len(record['additive']) == 8, 'extension coverage')
        require(len(record['sharp_additive']) == 3 and {r['m'] for r in record['sharp_additive']} == {2,3,4}, 'additive sharpness coverage')
    elif name == 'verify_priority_exclusions.py':
        require(len(record) == 4, 'source-class exclusion coverage')
    elif name == 'verify_independent.py':
        require(len(record['families']) == 6 and {(r['L'],r['R']) for r in record['families']} == {(1,0),(1,3),(2,1),(3,2),(4,0),(4,16)}, 'raw family parameters')
        require(record['padding']['counts_checked'] == 987, 'padding coverage')
        require(record['sorted_selector_recheck']['cases'] == 255 and record['sorted_selector_recheck']['queries'] == 510, 'independent sorted coverage')


def main():
    results_dir = HERE / 'results'
    results_dir.mkdir(exist_ok=True)
    summary = dict(status='RUNNING', python=platform.python_version(),
                   child_optimization=True, stages=[], evidence_scope='Finite exact rational/SAT corroboration; conventional all-parameter proofs remain essential.')
    summary_path = results_dir / 'verification_summary.json'
    # Persist RUNNING before importing any scientific or package-local dependency.
    summary_path.write_text(json.dumps(summary, indent=2)+'\n')
    try:
        import z3
        from verification_io import RESULTS
        summary['z3'] = z3.get_version_string()
        require(sys.version_info >= (3,10), 'Python 3.10 or later required')
        for path in HERE.glob('*.py'):
            require(not any(isinstance(node, ast.Assert) for node in ast.walk(ast.parse(path.read_text()))), f'assert proof gate in {path.name}')
        for _, output in STAGES:
            (RESULTS/output).unlink(missing_ok=True)
        for script, output in STAGES:
            print(f'RUN {script}', flush=True)
            start = time.monotonic()
            log = RESULTS / (Path(script).stem+'.log')
            with log.open('w') as stream:
                proc = subprocess.run([sys.executable, '-O', str(HERE/script)], cwd=HERE, stdout=stream, stderr=subprocess.STDOUT, timeout=1800)
            require(proc.returncode == 0, f'{script} failed; see {log.name}')
            path = RESULTS/output
            require(path.is_file() and path.stat().st_size > 0, f'{script} did not produce fresh evidence')
            record = json.loads(path.read_text())
            coverage(script, record)
            summary['stages'].append(dict(script=script, status='PASS', seconds=round(time.monotonic()-start,3), output=output,
                                          sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
            summary_path.write_text(json.dumps(summary,indent=2)+'\n')
            print(f'PASS {script}', flush=True)
        summary['status'] = 'PASS'
    except BaseException as exc:
        summary['status'] = 'FAIL'
        summary['error_type'] = type(exc).__name__
        summary['error'] = str(exc)
        summary_path.write_text(json.dumps(summary,indent=2)+'\n')
        raise
    summary_path.write_text(json.dumps(summary,indent=2)+'\n')
    print('PASS all 8 bounded verification stages; results/verification_summary.json', flush=True)


if __name__ == '__main__':
    main()
