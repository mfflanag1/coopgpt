#!/usr/bin/env python3
"""Verify hashes and recorded verdicts for the frozen CPC controls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CERTIFICATES = HERE / "certificates"
STEMS = (
    "failure_index0000",
    "equality_no_triple_index2236",
    "equality_subthird_index2236",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    rows = []
    for stem in STEMS:
        formula = CERTIFICATES / f"{stem}.smt2"
        proof = CERTIFICATES / f"{stem}.cpc"
        record = json.loads((CERTIFICATES / f"{stem}.json").read_text())
        assert record["status"] == "PASS"
        assert record["z3"]["status"] == "unsat"
        assert record["cvc5"]["status"] == "unsat"
        assert record["formula_sha256"] == sha256(formula)
        cpc = record["cpc_proof"]
        assert cpc["status"] == "PASS"
        assert cpc["ethos"]["status"] == "correct"
        assert cpc["proof_sha256"] == sha256(proof)
        assert cpc["forbidden_markers"] == []
        lowered = proof.read_text().lower()
        assert not any(marker in lowered for marker in ("trust", "hole", "warning"))
        rows.append(
            {
                "stem": stem,
                "formula_sha256": record["formula_sha256"],
                "proof_sha256": cpc["proof_sha256"],
                "ethos": cpc["ethos"]["status"],
            }
        )
    print(json.dumps({"status": "PASS", "certificates": rows}, indent=2))


if __name__ == "__main__":
    main()
