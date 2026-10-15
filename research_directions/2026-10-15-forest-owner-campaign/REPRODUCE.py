"""Portable, optimizer-free exact replay of the curated campaign evidence."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
JOBS = [
    ('portfolio', 'REPRODUCE.py'),
    ('lower', 'check_certificates.py'),
    ('lower', 'check_disconnected_witness.py'),
    ('lower', 'check_fragmented_family.py'),
    ('lower', 'check_three.py'),
    ('constructive', 'verify_double_star.py'),
    ('constructive', 'verify_path_decomposition.py'),
    ('constructive', 'verify_arbitrary_double_star.py'),
    ('constructive', 'verify_weighted_forest.py'),
    ('constructive', 'verify_vcap_obstruction.py'),
    ('constructive', 'check_sampled_counter.py'),
    ('coordinator', 'verify_fixed_masks.py'),
    ('coordinator', 'verify_rational_two_input.py'),
    ('coordinator', 'verify_mixed_softmax.py'),
]

def run(job):
    folder, script = job
    path = BASE / folder / script
    start = time.monotonic()
    proc = subprocess.run(
        [sys.executable, '-B', '-O', str(path)],
        cwd=path.parent, capture_output=True, text=True, timeout=900)
    name = folder + '__' + script[:-3]
    (BASE / 'checks' / (name + '.txt')).write_text(proc.stdout + proc.stderr)
    if proc.returncode:
        raise RuntimeError(f'{folder}/{script} failed ({proc.returncode}); see checks/{name}.txt')
    if 'pass' not in proc.stdout.lower():
        raise RuntimeError(f'{folder}/{script} emitted no PASS record')
    print(f'{folder}/{script}: PASS', flush=True)
    return dict(script=folder+'/'+script, status='PASS',
                script_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                output_sha256=hashlib.sha256((proc.stdout+proc.stderr).encode()).hexdigest(),
                elapsed_seconds=round(time.monotonic()-start, 3))

if __name__ == '__main__':
    (BASE / 'checks').mkdir(exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(run, JOBS))
    report = dict(status='PASS', python=sys.version,
                  optimized=True, checks=rows,
                  limits='Finite exact checks corroborate, but do not prove, all-real theorems or historical novelty.')
    (BASE / 'REPRODUCTION_RESULT.json').write_text(json.dumps(report, indent=2)+'\n')
    print('All curated exact checks PASS', flush=True)
