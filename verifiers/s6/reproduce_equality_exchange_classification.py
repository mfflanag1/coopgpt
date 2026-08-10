#!/usr/bin/env python3
"""Byte-regenerate all equality formulas and verify their proof records."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main():
    audit = json.loads((HERE / "equality_exchange_direction_cores.json").read_text())
    with tempfile.TemporaryDirectory(prefix="equality-exchange-") as name:
        temporary = Path(name)
        for row in audit["rows"]:
            case = row["case"]
            regenerated = temporary / f"{case}.smt2"
            subprocess.run(
                [
                    sys.executable,
                    str(HERE / "export_equality_exchange_classification_smt.py"),
                    "--case", case,
                    "--output", str(regenerated),
                ],
                check=True,
            )
            expected = HERE / "certificates" / f"equality_exchange_{case}.smt2"
            if regenerated.read_bytes() != expected.read_bytes():
                raise SystemExit(f"regenerated {case} formula differs")
    subprocess.run(
        [sys.executable, str(HERE / "verify_equality_exchange_classification_certificates.py")],
        check=True,
    )
    print("PASS: 15 equality formulas byte-reproduce and proof records verify")


if __name__ == "__main__":
    main()
