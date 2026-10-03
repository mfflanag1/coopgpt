"""Reproduce the manuscript's exact checks using only Python's standard library.

Run: python3 -B -O verification/verify.py --output /tmp/sharp-subsidy-check.json
No solver, network, repository checkout, or writable source directory is required.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional detailed JSON report')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    provenance = json.loads((root / 'PROVENANCE.json').read_text())
    for name, record in provenance.items():
        require(sha256(root / name) == record['sha256'], 'Changed input: ' + name)
    with tempfile.TemporaryDirectory(prefix='coopgt-sharp-check-') as directory:
        temp = Path(directory)
        aggregation_path = temp / 'aggregation.json'
        subprocess.run([sys.executable, '-B', '-O', str(root / 'verify_sharp_aggregation.py'), str(root / 'data'), str(aggregation_path)], check=True, capture_output=True, text=True)
        aggregation = json.loads(aggregation_path.read_text())
        require(aggregation['status'] == 'PASS' and aggregation['optimized_python'] == 1, 'Aggregation failed or wrong Python mode')
        require(aggregation['symbolic'] == {
            'repeated_label_team_patterns': 27,
            'per_label_polynomial_identities': 4,
            'global_slack_identities': 2,
            'symbolic_corruptions_rejected': 28,
        }, 'Unexpected symbolic coverage')
        require(len(aggregation['calibration']) == 48 and len(aggregation['enriched_points']) == 4 and len(aggregation['negative_controls']) == 3, 'Unexpected semantic coverage')
        # Preserve the historical script unchanged, including its output convention.
        tree_script = temp / 'tree_certificate.py'
        shutil.copyfile(root / 'tree_certificate.py', tree_script)
        subprocess.run([sys.executable, '-B', '-O', str(tree_script)], check=True, capture_output=True, text=True)
        tree_path = temp / 'TREE_CERTIFICATES.json'
        tree = json.loads(tree_path.read_text())
        require(tree['status'] == 'PASS' and tree['q_range'] == [1, 12], 'Construction check failed')
        require(tree['full_triple_checks'] == 3603804 and tree['negative_controls'] == 12 and len(tree['cases']) == 12, 'Unexpected construction coverage')
        report = {
            'status': 'PASS',
            'python': sys.version.split()[0],
            'worker_optimization': 1,
            'scope': 'Exact symbolic identities and finite corroboration; not a formal or universal proof.',
            'aggregation': aggregation,
            'construction': {key: value for key, value in tree.items() if key != 'cases'},
            'construction_certificate_sha256': sha256(tree_path),
            'inputs_sha256': {name: sha256(root / name) for name in sorted(provenance)},
            'runner_sha256': sha256(Path(__file__)),
            'provenance_sha256': sha256(root / 'PROVENANCE.json'),
        }
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'symbolic': aggregation['symbolic'], 'rational_packing_cases': len(aggregation['calibration']), 'enriched_points': len(aggregation['enriched_points']), 'construction': report['construction']}, indent=2))


if __name__ == '__main__':
    main()
