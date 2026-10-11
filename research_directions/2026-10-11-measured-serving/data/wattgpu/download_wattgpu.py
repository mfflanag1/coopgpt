#!/usr/bin/env python3
"""Reproduce the unmodified, selected WattGPU CSV rows from an immutable revision.

No credentials, package install, GPU execution, or paid endpoint is used.
The full 22.3 MB source is kept only in the requested cache directory.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import urllib.request

REVISION = '4e010359c167ac8c65b55aabd1aafbf765ae5d91'
BASE = 'https://raw.githubusercontent.com/maufadel/wattgpu/' + REVISION + '/'
SOURCE = 'data/watt_counts_subset.csv'
EXPECTED = '280510e119b2ea75105f5fa46f4813930045cf90d027d3834813c022568740ba'
LIMIT = 30_000_000
MODEL = 'meta-llama/Llama-3.1-8B-Instruct'
GPUS = ('NVIDIA A100-SXM4-40GB', 'NVIDIA H100 NVL')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--cache', type=Path, required=True)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    args.cache.mkdir(parents=True, exist_ok=True)
    raw = args.cache / 'watt_counts_subset.csv'
    if raw.exists():
        data = raw.read_bytes()
    else:
        with urllib.request.urlopen(BASE + SOURCE, timeout=60) as response:
            data = response.read(LIMIT + 1)
        if len(data) > LIMIT:
            raise ValueError('Source exceeds declared 30 MB cap')
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED:
        raise ValueError(f'Unexpected source hash: {digest}')
    raw.write_bytes(data)
    reader = csv.DictReader(io.StringIO(data.decode('utf-8'), newline=''))
    selected = [row for row in reader if row['model'] == MODEL and row['gpu_type'] in GPUS]
    if len(selected) != 30:
        raise ValueError(f'Expected 30 selected runs, found {len(selected)}')
    selected_path = args.output / 'llama31_8b_a100_h100_runs.csv'
    with selected_path.open('w', newline='') as output:
        writer = csv.DictWriter(output, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(selected)
    print(json.dumps({'source_sha256': digest, 'source_bytes': len(data),
                      'selected_runs': len(selected),
                      'selected_sha256': hashlib.sha256(selected_path.read_bytes()).hexdigest()}, indent=2))

if __name__ == '__main__':
    main()
