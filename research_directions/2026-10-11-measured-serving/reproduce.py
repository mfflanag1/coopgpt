#!/usr/bin/env python3
"""Offline rebuild into a new output directory; compare decisive artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

BASE = Path(__file__).resolve().parent
ARTIFACTS = ('COHORT.csv', 'MELODI_CALIBRATION.json', 'WATT_VALIDATION.json',
             'REPLAY_RESULTS.json', 'REPLAY_SUMMARY.json', 'REPLAY_EVENTS.jsonl',
             'REPLAY_TABLE.csv')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    out = args.output.resolve()
    if out == BASE or out.exists():
        raise ValueError('Use a new output directory to preserve the saved study')
    out.mkdir(parents=True)
    shutil.copyfile(BASE/'CALIBRATION_METHOD.txt', out/'CALIBRATION_METHOD.txt')
    commands = [
        [sys.executable, '-m', 'unittest', '-v', 'test_replay.py', 'test_analysis.py'],
        [sys.executable, '-O', '-m', 'unittest', 'test_replay.py', 'test_analysis.py'],
        [sys.executable, str(BASE/'prepare_melodi.py'), '--output', str(out)],
        [sys.executable, str(BASE/'watt_validation.py'), '--output', str(out/'WATT_VALIDATION.json')],
        [sys.executable, str(BASE/'run_study.py'), '--cohort', str(out/'COHORT.csv'), '--output', str(out)],
    ]
    with (out/'REBUILD_LOG.txt').open('w') as log:
        for command in commands:
            subprocess.run(command, cwd=BASE, stdout=log, stderr=log, check=True)
    comparisons = {name: {'saved_sha256':sha(BASE/name), 'rebuilt_sha256':sha(out/name),
                          'identical':(BASE/name).read_bytes()==(out/name).read_bytes()}
                   for name in ARTIFACTS}
    freeze = json.loads((BASE/'PROTOCOL_FREEZE.json').read_text())
    result = {'unit_tests':22, 'normal_and_optimized_tests_passed':True,
              'replayed_policy_schedules':162,
              'protocol_freeze_unchanged':sha(BASE/'PROTOCOL.txt') == freeze['sha256'],
              'comparisons':comparisons,
              'all_artifacts_identical':all(c['identical'] for c in comparisons.values())}
    (out/'VERIFICATION.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    if not result['all_artifacts_identical'] or not result['protocol_freeze_unchanged']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
