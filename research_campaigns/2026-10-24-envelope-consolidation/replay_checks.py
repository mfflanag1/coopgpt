#!/usr/bin/env python3
"""Replay finite diagnostics; these supplement, and do not prove, the theorems."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
SCRIPTS = [
    'selection_cap_two_check.py', 'selection_seed_barrier_check.py',
    'power_certificate_check.py', 'activation_qary_cube_check.py',
    'mass_search_qary_cube_audit.py', 'mass_geometry_qary_verify.py',
    'activation_qary_direct_check.py', 'mass_search_true_envelope_upper.py',
    'activation_qary_sharp_check.py', 'mass_geometry_qary_sharp_verify.py',
]
outdir = ROOT / 'checks' / 'logs'
outdir.mkdir(exist_ok=True)
records = []
for name in SCRIPTS:
    source = ROOT / 'checks' / name
    started = time.monotonic()
    try:
        run = subprocess.run([sys.executable, str(source)], cwd=ROOT,
                             capture_output=True, text=True, timeout=180)
        stdout, stderr, rc = run.stdout, run.stderr, run.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ''
        stderr = exc.stderr or ''
        if isinstance(stdout, bytes): stdout = stdout.decode(errors='replace')
        if isinstance(stderr, bytes): stderr = stderr.decode(errors='replace')
        stderr += '\nTIMEOUT after 180 seconds\n'
        rc = 124
    log = outdir / (source.stem + '.txt')
    log.write_text(stdout + ('\nSTDERR:\n' + stderr if stderr else ''))
    records.append({'script': 'checks/' + name,
                    'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                    'returncode': rc, 'seconds': round(time.monotonic()-started, 3),
                    'log': str(log.relative_to(ROOT)),
                    'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest()})
    print(('PASS' if rc == 0 else 'FAIL') + ' ' + name, flush=True)
report = {'status': 'PASS' if all(r['returncode']==0 for r in records) else 'FAIL',
          'python': sys.version, 'checks': records,
          'scope': 'Finite exact arithmetic and selected local enumerations. '
                   'No exhaustive final-game enumeration or formal proof verification.'}
(ROOT / 'checks' / 'REPLAY_RESULTS.json').write_text(json.dumps(report, indent=2)+'\n')
raise SystemExit(0 if report['status']=='PASS' else 1)
