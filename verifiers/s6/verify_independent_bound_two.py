#!/usr/bin/env python3
"""Regenerate and verify the independent coefficient-two reconstruction."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
FROZEN = HERE / "independent_bound_two"
CASES = ("p2_n3_t1", "p3_n3_t0")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    frozen_audit = json.loads((FROZEN / "audit.json").read_text())
    assert frozen_audit["status"] == "PASS"
    assert len(frozen_audit["rows"]) == 2

    with tempfile.TemporaryDirectory(prefix="independent-bound-two-") as name:
        temporary = Path(name)
        subprocess.run(
            [
                sys.executable,
                str(HERE / "independent_bound_two_reconstruction.py"),
                "--output-dir",
                str(temporary),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        regenerated_audit = json.loads((temporary / "audit.json").read_text())
        # Paths differ by construction; the mathematical metadata and bytes do not.
        for row in regenerated_audit["rows"]:
            row["formula"] = f"independent_bound_two/{row['case']}.smt2"
        if regenerated_audit != frozen_audit:
            raise AssertionError("independent reconstruction audit did not regenerate")
        for case in CASES:
            if (temporary / f"{case}.smt2").read_bytes() != (
                FROZEN / f"{case}.smt2"
            ).read_bytes():
                raise AssertionError(f"{case} SMT-LIB did not byte-regenerate")

    checked = []
    for case in CASES:
        formula = FROZEN / f"{case}.smt2"
        proof = FROZEN / f"{case}.cpc"
        record = json.loads((FROZEN / f"{case}.json").read_text())
        assert record["status"] == "PASS"
        assert record["z3"]["status"] == "unsat"
        assert record["cvc5"]["status"] == "unsat"
        assert record["formula_sha256"] == sha256(formula)
        cpc = record["cpc_proof"]
        assert cpc["status"] == "PASS"
        assert cpc["ethos"]["status"] == "correct"
        assert cpc["forbidden_markers"] == []
        assert cpc["proof_sha256"] == sha256(proof)
        checked.append(
            {
                "case": case,
                "formula_sha256": record["formula_sha256"],
                "proof_bytes": cpc["proof_bytes"],
                "proof_sha256": cpc["proof_sha256"],
            }
        )
    print(json.dumps({"status": "PASS", "checked": checked}, indent=2))


if __name__ == "__main__":
    main()
