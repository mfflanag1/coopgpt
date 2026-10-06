#!/usr/bin/env python3
"""Replay the integrated hierarchy and probability checks in a fresh directory."""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, tempfile

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('validation/hierarchy_replay'))
    args = parser.parse_args()
    source = Path(__file__).resolve().parent / 'hierarchy'
    manifest = json.loads((source / 'SOURCE_HASHES.json').read_text())
    require(set(manifest) == {'verify.py', 'hierarchy_certificate.py', 'verify_small_ball.py'},
            'Unexpected source manifest')
    for name, wanted in manifest.items():
        require(hashlib.sha256((source / name).read_bytes()).hexdigest() == wanted,
                'Source mismatch: ' + name)
    output = args.output.resolve()
    require(output != source and source not in output.parents,
            'Output must be outside verifier sources')
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='coopgt-hierarchy-') as tmp:
        scratch = Path(tmp)
        tasks = [('hierarchy_certificate.py', scratch / 'hierarchy'),
                 ('verify_small_ball.py', scratch / 'small_ball.json')]
        for index, (name, target) in enumerate(tasks):
            proc = subprocess.run([sys.executable, '-B', '-O', str(source / name),
                                   '--output', str(target)], capture_output=True,
                                  text=True, cwd=scratch, timeout=120)
            (output / (name + '.stdout.txt')).write_text(proc.stdout)
            (output / (name + '.stderr.txt')).write_text(proc.stderr)
            require(proc.returncode == 0, 'Verifier failed: ' + name)
        hierarchy = json.loads((scratch / 'hierarchy/VERIFICATION.json').read_text())
        probability = json.loads((scratch / 'small_ball.json').read_text())
        require(hierarchy['status'] == 'EXACT_SPECIALIZATIONS_CHECKED', 'Hierarchy failed')
        require(len(hierarchy['cases']) == 14, 'Hierarchy coverage changed')
        require(probability['status'] == 'EXACT_FINITE_PROBABILITY_CHECKS_PASS', 'Probability failed')
        require(len(probability['cases']) == 24, 'Probability coverage changed')
        # Fresh validated reports replace earlier output only after successful checks.
        import shutil
        shutil.copytree(scratch / 'hierarchy', output / 'hierarchy', dirs_exist_ok=True)
        shutil.copy2(scratch / 'small_ball.json', output / 'small_ball.json')
    summary = {'status': 'PASS', 'sources_verified': manifest,
               'hierarchy_cases': 14, 'probability_cases': 24,
               'scope': 'Exact finite specializations; universal claims require the written proofs.'}
    (output / 'SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n')
    print('PASS: 14 hierarchy certificates and 24 exact pairwise comparisons; ' + str(output))

if __name__ == '__main__':
    main()
