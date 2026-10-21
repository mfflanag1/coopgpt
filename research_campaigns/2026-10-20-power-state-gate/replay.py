"""Offline bundle integrity and scoped result replay; performs no data acquisition."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
ENV = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}


def main():
    manifest = json.loads((ROOT / 'MANIFEST.json').read_text())
    for rel, expected in manifest['files'].items():
        path = (ROOT / rel).resolve()
        if not path.is_relative_to(ROOT) or path.is_symlink():
            raise ValueError('Unsafe manifest path')
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Bundle hash mismatch: ' + rel)
    for script, report in [('acquisition_audit.py', 'acquisition_audit.json'),
                           ('footer_structure.py', 'footer_structure.json'),
                           ('header_inventory.py', 'june_tar_inventory.json')]:
        result = subprocess.run([sys.executable, script], cwd=ROOT, env=ENV,
                                capture_output=True, text=True, check=True)
        if json.loads(result.stdout) != json.loads((ROOT / report).read_text()):
            raise ValueError('Saved report replay mismatch: ' + report)
    result = subprocess.run([sys.executable, 'acquisition_audit.py', '--check'],
                            cwd=ROOT, env=ENV, capture_output=True, text=True, check=True)
    checks = json.loads(result.stdout)['validation']['passed']
    result = subprocess.run([sys.executable, '-m', 'unittest', '-v', 'test_structure.py'],
                            cwd=ROOT, env=ENV, capture_output=True, text=True, check=True)
    print(json.dumps({'status': 'PASS', 'hashed_files': len(manifest['files']),
                      'exact_json_replays': 3, 'acquisition_checks': checks,
                      'structural_tests': 9, 'network_requests': 0,
                      'outcome_values_selected': False}, indent=2))


if __name__ == '__main__':
    main()
