#!/usr/bin/env python3
"""Exploratory ablations prompted by independent review, after primary outcomes.

These do not change the frozen protocol, forecasts, headline or promotion gate.
Very large finite limits approximate removal only in this 92-request instance.
"""
import csv
import json
from pathlib import Path

from run_study import make_jobs, training_reference
from replay import replay


BASE = Path(__file__).resolve().parent


def main():
    rows = list(csv.DictReader((BASE/'COHORT.csv').open()))
    reference, _ = training_reference(BASE/'data/melodi/PAIRED_MEASUREMENTS.csv')
    budget = .75 * len(rows) * reference / 2
    results = {'status':'Exploratory post-review ablations, not prespecified outcomes',
               'cases':{}}
    for deadline, budgets, name in [(60,[budget,budget],'primary'),
            (1e9,[budget,budget],'relaxed_deadline'),(60,[1e12,1e12],'nonbinding_energy')]:
        results['cases'][name] = {}
        for mode in ('autarky','pool'):
            r = replay(make_jobs(rows,10,deadline),budgets,mode)
            results['cases'][name][mode] = {k:r[k] for k in (
                'started','ontime','late','rejected','total_energy_j','remaining_accounts_j')}
    print(json.dumps(results,indent=2))


if __name__ == '__main__':
    main()
