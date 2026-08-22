#!/usr/bin/env python3
"""Exhaust all ordered five-player stratum cells for PXC91c."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import itertools
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import z3

HERE = Path(__file__).resolve()
DEFAULT_CELL = HERE.with_name("unrestricted_pxc91c_n5_quantified_cegar.py")


def compositions(total):
    if total == 0:
        yield (); return
    for first in range(1, total + 1):
        for tail in compositions(total - first): yield (first,) + tail


def cell_specs():
    for xcomp in compositions(5):
        for top in itertools.combinations(range(5), 2):
            rest = tuple(i for i in range(5) if i not in top)
            for order in itertools.permutations(rest):
                for zcomp in compositions(3):
                    yield xcomp, top, order, zcomp


def run_cell(spec, timeout_ms, cell_driver, extra=()):
    xcomp, top, order, zcomp = spec
    command = [sys.executable, str(cell_driver), "--x-composition", *map(str, xcomp),
               "--top", *map(str, top), "--z-order", *map(str, order),
               "--z-composition", *map(str, zcomp),
               "--timeout-ms", str(timeout_ms), *extra]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError({"command": command, "stdout": result.stdout,
                            "stderr": result.stderr})
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--cell-timeout-ms", type=int, default=30000)
    parser.add_argument("--cell-driver", type=Path, default=DEFAULT_CELL)
    parser.add_argument("--encoding-label", default="raw PXC92b Farkas")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(); specs = tuple(cell_specs())
    cell_driver = args.cell_driver.resolve()
    if len(specs) != 3840: raise AssertionError(len(specs))
    counts = Counter(); exceptions = []; cell_keys = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(run_cell, spec, args.cell_timeout_ms,
                                   cell_driver): spec
                   for spec in specs}
        for completed, future in enumerate(concurrent.futures.as_completed(futures), 1):
            payload = future.result(); verdict = payload["verdict"]
            counts[verdict] += 1
            key = (tuple(tuple(q) for q in payload["x_blocks"]),
                   tuple(tuple(q) for q in payload["z_blocks"]), verdict)
            cell_keys.append(key)
            if verdict != "unsat": exceptions.append(payload)
            if completed % 100 == 0:
                print(f"cells {completed}/{len(specs)}: {dict(counts)}", flush=True)
    # Both defining hypothesis families must be load-bearing in a representative cell.
    control = ((3, 2), (3, 4), (0, 1, 2), (1, 1, 1))
    drop_singleton = run_cell(control, args.cell_timeout_ms, cell_driver,
                              ("--drop-singleton-normalization",))
    drop_cone = run_cell(control, args.cell_timeout_ms, cell_driver,
                         ("--drop-exact-cone",))
    if drop_singleton["verdict"] != "sat" or drop_cone["verdict"] != "sat":
        raise AssertionError("fail-open controls did not open")
    digest = hashlib.sha256(json.dumps(sorted(cell_keys), sort_keys=True).encode()).hexdigest()
    catalogue = HERE.parents[3] / "verifiers/lib/catalogue.py"
    payload = {
        "claim": "exhaustive exact stratum-cell theorem for unrestricted PXC91c at n=5",
        "cell_count": len(specs), "verdict_counts": dict(counts),
        "exceptions": exceptions,
        "parameters": {"workers": args.workers,
                       "cell_timeout_ms": args.cell_timeout_ms},
        "coverage": {
            "x": "all 16 compositions after sorting x increasingly WLOG",
            "z_top": "all 10 unordered two-player top pairs",
            "z_outsider_orders": "all 6 orders of the remaining players",
            "z_outsider_strata": "all 4 compositions of three outsiders",
            "product": "16*10*6*4=3840",
        },
        "encoding": {
            "exact_game_cone": "all 280 five-player indecomposable min-semi-balanced inequalities",
            "certificate_quantifier": "arbitrary Boolean subset of all 30 nonempty proper x-tight rows",
            "selectors": args.encoding_label + " certificate at every declared stage",
            "old_pin_coefficients": "free in both supported encodings",
            "failure": "every later-stage PXC92b tangent for the tight top-pair lift",
        },
        "fail_open_controls": {
            "drop_singleton": {"verdict": drop_singleton["verdict"]},
            "drop_exact_cone": {"verdict": drop_cone["verdict"]},
        },
        "cell_digest_sha256": digest,
        "driver_sha256": hashlib.sha256(HERE.read_bytes()).hexdigest(),
        "cell_driver": str(cell_driver.relative_to(HERE.parents[3])),
        "cell_driver_sha256": hashlib.sha256(cell_driver.read_bytes()).hexdigest(),
        "catalogue_sha256": hashlib.sha256(catalogue.read_bytes()).hexdigest(),
        "z3_version": z3.get_version_string(),
        "scope": (
            "UNSAT in all cells proves the pair cover preserves both selectors for every "
            "fixed complete Cx at n=5, conditional only on the separately validated exact-cone "
            "catalogue and the PXC92b Farkas equivalence; any SAT/unknown cell blocks promotion"
        ),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output: args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__": main()
