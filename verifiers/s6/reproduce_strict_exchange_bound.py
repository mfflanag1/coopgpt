#!/usr/bin/env python3
"""Byte-regenerate the direct-bound formulas and verify proof records."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main():
    audit = json.loads((HERE / "strict_exchange_direction_cores.json").read_text())
    with tempfile.TemporaryDirectory(prefix="strict-exchange-") as name:
        temporary = Path(name)
        for row in audit["rows"]:
            case = row["case"]
            regenerated = temporary / f"{case}.smt2"
            subprocess.run(
                [
                    sys.executable,
                    str(HERE / "export_strict_exchange_bound_smt.py"),
                    "--case", case,
                    "--output", str(regenerated),
                ],
                check=True,
            )
            expected = HERE / "certificates" / f"strict_exchange_{case}.smt2"
            if regenerated.read_bytes() != expected.read_bytes():
                raise SystemExit(f"regenerated strict {case} formula differs")
    subprocess.run(
        [sys.executable, str(HERE / "verify_strict_exchange_bound_certificates.py")],
        check=True,
    )
    print("PASS: 15 strict-distance formulas byte-reproduce and proof records verify")


if __name__ == "__main__":
    main()
