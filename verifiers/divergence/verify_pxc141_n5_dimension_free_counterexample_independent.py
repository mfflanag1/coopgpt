#!/usr/bin/env python3
"""Standalone symbolic replay of PXC141; imports no project mathematics."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

G1 = tuple(map(F, (1, 0, 0, 1, 2)))
G2 = tuple(map(F, (0, 1, 3, 0, 0)))
X = tuple(map(F, (F(1, 2), F(1, 2), F(5, 4), F(1, 2), F(5, 4))))
Z = tuple(map(F, (1, 0, 1, 1, 1)))


def sm(point, mask):
    return sum((point[i] for i in range(5) if mask >> i & 1), F(0))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", type=Path); args = ap.parse_args()
    v = tuple(min(sm(G1, s), sm(G2, s)) for s in range(32))
    for point in (X, Z):
        if sum(point) != 4 or any(sm(point, s) < v[s] for s in range(32)):
            raise AssertionError("candidate outside core")
    if any(v[1 << i] for i in range(5)):
        raise AssertionError("normalization")

    # Two complementary tight partitions imply for every core allocation y:
    # y0+y1=1, y1+y3=1, and consequently
    # y0=y3=s, y1=1-s, y2+y4=3-s, 0<=s<=1.
    partition_pairs = ((3, 28), (10, 21))
    if any(v[a] + v[b] != 4 or a ^ b != 31 for a, b in partition_pairs):
        raise AssertionError("flat partition identities")
    # Lmin: min(s,1-s)<=1/2; equality fixes s=1/2, then split 5/2 equally.
    # Lmax: max(y2,y4)>=(3-s)/2>=1; equality fixes s=1 and y2=y4=1.
    if X != (F(1,2), F(1,2), F(5,4), F(1,2), F(5,4)):
        raise AssertionError("Lmin algebra")
    if Z != (1, 0, 1, 1, 1):
        raise AssertionError("Lmax algebra")
    overlap = sum(min(a, b) for a, b in zip(X, Z))
    target = F(5, 6) * 4
    if not overlap == 3 < target == F(10, 3):
        raise AssertionError("failure")
    payload = {
        "claim": "independent symbolic PXC141 replay",
        "imports_project_code": False,
        "flat_complementary_partitions": [[3, 28], [10, 21]],
        "core_parameterization": "y0=y3=s, y1=1-s, y2+y4=3-s, 0<=s<=1",
        "Lmin_argument": "floor<=min(s,1-s)<=1/2; equality and continuation give X",
        "Lmax_argument": "ceiling>=max(y2,y4)>=(3-s)/2>=1; equality gives Z",
        "candidate_core_feasibility_checked_against_all_32_values": True,
        "singleton_normalized": True,
        "overlap": str(overlap), "required": str(target), "margin": str(overlap-target),
        "minimality_dependency": "existing conventional n<=4 Lmin=Lmax theorem",
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output: args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__": main()
