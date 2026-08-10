#!/usr/bin/env python3
"""Generate all frozen equality exchange formulas and checked CPC proofs."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--z3", type=Path, required=True)
    parser.add_argument("--cvc5", type=Path, required=True)
    parser.add_argument("--ethos", type=Path, required=True)
    parser.add_argument("--cpc-signatures", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument("--certificates", type=Path, default=HERE / "certificates")
    args = parser.parse_args()
    audit = json.loads((HERE / "equality_exchange_direction_cores.json").read_text())
    args.certificates.mkdir(parents=True, exist_ok=True)
    for row in audit["rows"]:
        case = row["case"]
        stem = f"equality_exchange_{case}"
        formula = args.certificates / f"{stem}.smt2"
        proof = args.certificates / f"{stem}.cpc"
        record = args.certificates / f"{stem}.json"
        subprocess.run(
            [
                sys.executable,
                str(HERE / "export_equality_exchange_classification_smt.py"),
                "--case", case,
                "--output", str(formula),
            ],
            check=True,
        )
        subprocess.run(
            [
                sys.executable,
                str(HERE / "replay_core_closure_smt.py"),
                "--formula", str(formula),
                "--z3", str(args.z3),
                "--cvc5", str(args.cvc5),
                "--ethos", str(args.ethos),
                "--cpc-signatures", str(args.cpc_signatures),
                "--timeout-seconds", str(args.timeout_seconds),
                "--cpc-proof", str(proof),
                "--output", str(record),
            ],
            check=True,
        )
        print(f"certified {case}", flush=True)


if __name__ == "__main__":
    main()
