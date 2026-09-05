from pathlib import Path
import json
import shutil
import subprocess
import sys

SOURCE = Path('/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/review_packages/2026-09-05')
OUT = Path(__file__).resolve().parent
rows = []
for name in ('stable_core', 'asymptotic', 'assignment'):
    for optimized in (False, True):
        target = OUT / 'startup_probes' / f'{name}_{int(optimized)}'
        if target.exists():
            raise RuntimeError('Probe directory already exists')
        shutil.copytree(SOURCE / name / 'verification', target)
        output = target / 'results' / ('verification_summary.json' if name == 'assignment' else 'verification.json')
        output.parent.mkdir(exist_ok=True)
        output.write_text(json.dumps({'status': 'PASS', 'old_marker': 'seeded-old-result'}))
        flags = ['-O'] if optimized else []
        if name == 'stable_core':
            (target / 'verify_claims.py').rename(target / 'verify_claims.disabled')
            fault = 'missing local verification module'
        else:
            flags.append('-S')
            fault = 'third-party dependencies unavailable because site loading is disabled'
        command = [sys.executable, *flags, str(target / 'run_checks.py')]
        run = subprocess.run(command, capture_output=True, text=True, timeout=20)
        record = json.loads(output.read_text())
        rows.append({'package': name, 'optimization': optimized, 'fault': fault,
                     'exit_code': run.returncode, 'record_after': record,
                     'stderr_tail': run.stderr.splitlines()[-1:]})
        if run.returncode == 0:
            raise RuntimeError('Injected missing dependency was accepted')
(OUT / 'startup_failure_before.json').write_text(json.dumps(rows, indent=2) + '\n')
print(json.dumps(rows, indent=2))
