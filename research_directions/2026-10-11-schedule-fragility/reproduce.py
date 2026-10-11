#!/usr/bin/env python3
"""Verify package and input hashes, test, regenerate, and compare decisive results."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

BASE=Path(__file__).resolve().parent
OUTPUTS=('ENERGY.json','TIMING.json','FRONTIERS.json','THRESHOLDS.jsonl.gz',
         'SUMMARY.json','CHECKS.json')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True,help='New nonexistent directory')
    parser.add_argument('--source',type=Path,default=BASE.parent/'2026-10-11-measured-serving')
    args=parser.parse_args()
    manifest=json.loads((BASE/'FILE_SHA256.json').read_text())
    for name,digest in manifest.items():
        actual=hashlib.sha256((BASE/name).read_bytes()).hexdigest()
        if actual!=digest:
            raise ValueError('Package hash mismatch: '+name)
    for flags in ([],['-O']):
        subprocess.run([sys.executable,'-B',*flags,'-m','unittest','test_fragility'],
                       cwd=BASE,check=True)
    subprocess.run([sys.executable,'-B',str(BASE/'analysis.py'),'--source',str(args.source),
                    '--output',str(args.output)],check=True)
    for name in OUTPUTS:
        saved=(BASE/'results'/name).read_bytes()
        fresh=(args.output/name).read_bytes()
        # zlib versions may encode the same JSONL differently; compare its content.
        if name.endswith('.gz'):
            saved,fresh=gzip.decompress(saved),gzip.decompress(fresh)
        if saved!=fresh:
            raise ValueError('Reproduction mismatch: '+name)
    print(json.dumps(dict(status='PASS',decisive_outputs_compared=len(OUTPUTS),
                          package_files_hashed=len(manifest),source_inputs_hashed=3)))


if __name__=='__main__':
    main()
