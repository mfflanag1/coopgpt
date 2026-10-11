#!/usr/bin/env python3
"""Optional free-source refresh into a separate cache; immutable hashes required."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import urllib.request

BASE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cache', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    melodi_output = args.output/'melodi'
    melodi_output.mkdir(parents=True, exist_ok=True)
    provenance = json.loads((BASE/'data/melodi/PROVENANCE.json').read_text())
    for source in provenance['source_downloads']:
        name = source['url'].rsplit('/', 1)[1]
        path = args.cache/name
        if path.exists():
            body = path.read_bytes()
        else:
            with urllib.request.urlopen(source['url'], timeout=60) as response:
                body = response.read(20_000_001)
            if len(body) > 20_000_000:
                raise ValueError('MELODI file exceeds 20 MB acquisition cap')
        if hashlib.sha256(body).hexdigest() != source['sha256']:
            raise ValueError('Unexpected immutable source hash: '+name)
        path.write_bytes(body)
    subprocess.run([sys.executable, str(BASE/'data/melodi/extract_pairs.py'),
                    '--source-dir', str(args.cache), '--output-dir', str(melodi_output)], check=True)
    subprocess.run([sys.executable, str(BASE/'data/wattgpu/download_wattgpu.py'),
                    '--cache', str(args.cache), '--output', str(args.output/'wattgpu')], check=True)


if __name__ == '__main__':
    main()
