"""Post-outcome quote-interval sensitivity; deliberately leaves primary outputs intact."""
from pathlib import Path
from datetime import date
import csv, hashlib, json
import numpy as np
import run_gate as frozen

ROOT = Path(__file__).parent

def available_quotes():
    assert hashlib.sha256(frozen.RAW.read_bytes()).hexdigest() == frozen.RAW_SHA
    lines = frozen.RAW.read_text().splitlines()
    header = next(i for i, line in enumerate(lines) if line.startswith('Date,'))
    rows = sorted(csv.DictReader(lines[header:]), key=lambda r: r['Date'])
    last = None
    observations, excluded = [], []
    for row in rows:
        day = date.fromisoformat(row['Date'])
        if not date(2009, 12, 1) <= day <= date(2025, 12, 31):
            continue
        try:
            value = np.array([float(row['SVENY02']), float(row['SVENY10'])])
            valid = bool(np.all(np.isfinite(value)) and np.all(value > -900))
        except ValueError:
            valid = False
        if not valid:
            excluded.append({'date': str(day), 'reason': 'invalid quote; prior available quote retained, no interpolation'})
            continue
        if last is not None:
            gap = (day-last[0]).days
            if gap > 7:
                excluded.append({'date': str(day), 'reason': 'gap over7 days', 'gap': gap})
            elif day >= date(2010, 1, 1):
                observations.append((day, (value-last[1])*100))
        last = day, value
    return [d for d, _ in observations], np.array([x for _, x in observations]), excluded

if __name__ == '__main__':
    destination = ROOT/'quote_interval_diagnostic'
    destination.mkdir(exist_ok=True)
    if (destination/'results.json').exists():
        raise SystemExit('Diagnostic already exists; preserve it instead of overwriting.')
    frozen.P = destination
    frozen.load_data = available_quotes
    frozen.main()
    (destination/'STATUS.txt').write_text(
        'POST-OUTCOME MEASUREMENT DIAGNOSTIC. Uses consecutive valid quotes, gaps <=7 calendar days. '
        'Shares the frozen numerical pipeline; independent verification is in ../verify_results.py. '
        'Not a replacement primary analysis, prospective test, or retuned book.\n')
