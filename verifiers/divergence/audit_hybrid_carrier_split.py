#!/usr/bin/env python3
"""Exact audit of a two-carrier strengthening of the hybrid-overlap bound.

For equal-total nonnegative selections x,z, put w_i=min(x_i,z_i).  The
candidate carrier statement asks for a set A of size floor(n/2), with
    B=N\\A, such that

    w(A) >= T/|B|,        w(B) >= T/|A|.

Adding gives the conjectured overlap lower bound.  This script only tests
archived exact pairs and the closed-form balanced G(p,k) pairs.  Passing is
discovery evidence, not a proof that such a carrier always exists.
"""

from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

from audit_lmax_overcover import records


def carrier_witness(x: tuple[F, ...], z: tuple[F, ...]):
    n = len(x)
    a = n // 2
    b = n - a
    total = sum(x, F(0))
    overlap = tuple(min(u, v) for u, v in zip(x, z))
    for chosen in itertools.combinations(range(n), a):
        left = sum((overlap[i] for i in chosen), F(0))
        right = sum(overlap, F(0)) - left
        if left >= total / b and right >= total / a:
            return chosen, left, right
    return None


def balanced_family_pair(n: int):
    k = (n + 1) // 2
    p = n - k - 1
    total = F(p * k)
    floor = F(p, p + 1)
    top = F(p * (k - 1), k)
    x = (F(p * p * (k - 1), p + 1),) + (floor,) * (p + k)
    z = (top,) + (F(1, k),) * p + (top,) * k
    assert sum(x, F(0)) == total == sum(z, F(0))
    return x, z


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows = []
    failures = []
    files = []
    for path in args.paths:
        files.extend(sorted(path.rglob("*.json")) if path.is_dir() else [path])
    for source in files:
        try:
            data = json.loads(source.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        for source, trail, _v, x, z in records(data, source):
            if len(x) not in (6, 7) or sum(x, F(0)) != sum(z, F(0)) or sum(x, F(0)) <= 0:
                continue
            witness = carrier_witness(x, z)
            row = {
                "source": str(source),
                "trail": trail,
                "n": len(x),
                "witness": None if witness is None else list(witness[0]),
                "total": str(sum(x, F(0))),
                "coordinate_overlaps": [str(min(u, v)) for u, v in zip(x, z)],
            }
            rows.append(row)
            if witness is None:
                failures.append(row)

    family = {}
    for n in range(6, 13):
        x, z = balanced_family_pair(n)
        witness = carrier_witness(x, z)
        family[str(n)] = None if witness is None else {
            "A": list(witness[0]),
            "overlap_A": str(witness[1]),
            "overlap_complement": str(witness[2]),
        }
        if witness is None:
            raise AssertionError(f"balanced G family failed at n={n}")

    report = {
        "status": "exact archived-pair discovery audit; not proof evidence",
        "archived_records": len(rows),
        "counts_by_n": {
            str(n): sum(row["n"] == n for row in rows) for n in (6, 7)
        },
        "carrier_failures": failures,
        "balanced_G_family": family,
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
