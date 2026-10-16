#!/usr/bin/env python3
"""Exploratory singleton 6/5 formula; finite falsification only, no theorem."""
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import verify_split_rule as reference


def candidate(profile, blocks, theta=F(1)):
    if tuple(blocks) != tuple(range(len(blocks))):
        raise ValueError('Singleton blocks required')
    ell, residual, L, Q, H, R, G, T, M, E = reference.values(profile, blocks)
    if not L:
        return (F(),)*len(blocks)+(G,)+(F(),)*len(blocks)
    beta = F(6, 5)
    D = max(F(), profile[0]-Q)
    s = [max(F(), profile[0]-Q+r) for r in residual]
    x = tuple(min(l, z, beta*l*z/L) for l, z in zip(ell, s))
    a = tuple(max(F(), l-D, l-y) for l, y in zip(ell, x))
    c = min(G, beta*T-sum(a)-sum(x))
    return a+(c,)+x


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pods', type=int, default=2)
    parser.add_argument('--levels', default='0,1,2')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    reference.candidate = candidate
    try:
        report = reference.run(tuple(range(args.pods)), tuple(map(F, args.levels.split(','))), F(1))
        if F(report['max_observed_factor']) > F(6, 5):
            raise ValueError('Observed factor exceeds 6/5')
    except ValueError as exc:
        report = {'status': 'FAIL', 'message': str(exc)}
    report['scope'] = 'Exploratory formula. A finite PASS proves no universal upper.'
    encoded = json.dumps(report, indent=2)+'\n'
    if args.output:
        args.output.write_text(encoded)
    print(encoded, end='')
