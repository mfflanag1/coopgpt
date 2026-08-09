#!/usr/bin/env python3
"""Audit the comparison-overlap formulation of the fixed-n conjecture.

This is a bug-finding tool, not proof evidence.  It recursively visits JSON
objects and tests every dictionary carrying equally sized ``lmin`` and
``lmax`` arrays.  Exact strings and integers are parsed as Fractions.

For x=Lmin and z=Lmax, put O=sum_i min(x_i,z_i).  The candidate sharp
fixed-n upper bound is equivalent to

    O/T >= n/floor(n^2/4).

The stronger comparison-cut version assigns coordinates tied between x and z
to whichever side maximizes the cut product.  If p coordinates have x>z and
t are tied, set P=max_{p<=a<=p+t} a(n-a) and test O/T >= n/P.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterator


def as_fraction(value: Any) -> Fraction:
    if isinstance(value, bool):
        raise ValueError("boolean is not a payoff")
    if isinstance(value, (int, str)):
        return Fraction(value)
    if isinstance(value, float):
        return Fraction(str(value))
    raise ValueError(f"unsupported payoff {value!r}")


def records(node: Any, source: Path, trail: str = "$") -> Iterator[tuple]:
    if isinstance(node, dict):
        lower = {str(k).lower(): k for k in node}
        if "lmin" in lower and "lmax" in lower:
            x_raw = node[lower["lmin"]]
            z_raw = node[lower["lmax"]]
            if isinstance(x_raw, list) and isinstance(z_raw, list):
                try:
                    x = tuple(as_fraction(q) for q in x_raw)
                    z = tuple(as_fraction(q) for q in z_raw)
                except ValueError:
                    pass
                else:
                    if len(x) == len(z) and x:
                        yield source, trail, x, z
        for key, value in node.items():
            yield from records(value, source, f"{trail}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from records(value, source, f"{trail}[{index}]")


def best_cut_product(n: int, positive: int, ties: int) -> int:
    return max(a * (n - a) for a in range(positive, positive + ties + 1))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    files = []
    for path in args.paths:
        files.extend(sorted(path.rglob("*.json")) if path.is_dir() else [path])

    seen = 0
    global_failures = []
    cut_failures = []
    equalities = []
    by_n = {}
    for source in files:
        try:
            data = json.loads(source.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        for source, trail, x, z in records(data, source):
            if sum(x) != sum(z) or sum(x) <= 0:
                continue
            seen += 1
            n = len(x)
            total = sum(x)
            overlap = sum(min(a, b) for a, b in zip(x, z))
            positive = sum(a > b for a, b in zip(x, z))
            ties = sum(a == b for a, b in zip(x, z))
            global_product = (n * n) // 4
            global_margin = overlap * global_product - n * total
            product = best_cut_product(n, positive, ties)
            cut_margin = overlap * product - n * total if product else None
            row = {
                "source": str(source),
                "trail": trail,
                "n": n,
                "overlap_ratio": str(overlap / total),
                "positive": positive,
                "ties": ties,
                "cut_product": product,
                "global_margin": str(global_margin),
                "cut_margin": None if cut_margin is None else str(cut_margin),
            }
            by_n.setdefault(n, {"records": 0, "global_min": None, "cut_min": None})
            by_n[n]["records"] += 1
            gm = by_n[n]["global_min"]
            by_n[n]["global_min"] = global_margin if gm is None else min(gm, global_margin)
            if cut_margin is not None:
                cm = by_n[n]["cut_min"]
                by_n[n]["cut_min"] = cut_margin if cm is None else min(cm, cut_margin)
            if n >= 6 and global_margin < 0:
                global_failures.append(row)
            if n >= 6 and cut_margin is not None and cut_margin < 0:
                cut_failures.append(row)
            if n >= 6 and global_margin == 0:
                equalities.append(row)

    report = {
        "records": seen,
        "by_n": {
            str(n): {
                **summary,
                "global_min": None if summary["global_min"] is None else str(summary["global_min"]),
                "cut_min": None if summary["cut_min"] is None else str(summary["cut_min"]),
            }
            for n, summary in sorted(by_n.items())
        },
        "global_failures_n_ge_6": global_failures[:20],
        "cut_failures_n_ge_6": cut_failures[:20],
        "global_equalities_n_ge_6": equalities[:20],
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
