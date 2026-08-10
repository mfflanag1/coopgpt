#!/usr/bin/env python3
"""Regenerate the universal formulas and verify their frozen proof records."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main():
    with tempfile.TemporaryDirectory(prefix="starved-universal-exchange-") as name:
        temporary = Path(name)
        for side in ("min", "max"):
            regenerated = temporary / f"{side}.smt2"
            subprocess.run(
                [
                    sys.executable,
                    str(HERE / "export_starved_universal_exchange_smt.py"),
                    "--side", side,
                    "--output", str(regenerated),
                ],
                check=True,
            )
            expected = HERE / "certificates" / f"starved_universal_exchange_{side}.smt2"
            if regenerated.read_bytes() != expected.read_bytes():
                raise SystemExit(f"regenerated {side} formula differs")
    subprocess.run(
        [sys.executable, str(HERE / "verify_starved_universal_exchange_certificates.py")],
        check=True,
    )
    print("PASS: universal starved formulas byte-reproduce and proof records verify")


if __name__ == "__main__":
    main()
