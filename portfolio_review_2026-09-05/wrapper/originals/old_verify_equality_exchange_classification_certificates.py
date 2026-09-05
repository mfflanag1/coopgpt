#!/usr/bin/env python3
"""Verify frozen proof-object controls for the equality exchange theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CERTIFICATES = HERE / "certificates"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    audit = json.loads((HERE / "equality_exchange_direction_cores.json").read_text())
    assert audit["status"] == "PASS"
    assert audit["case_count"] == 15
    checked = []
    for row in audit["rows"]:
        assert row["rebuilt_verdict"] == "unsat"
        stem = f"equality_exchange_{row['case']}"
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
        assert cpc["forbidden_markers"] == []
        assert cpc["proof_sha256"] == sha256(proof)
        checked.append(
            {
                "case": row["case"],
                "directions": row["retained_direction_count"],
                "proof_bytes": cpc["proof_bytes"],
                "formula_sha256": record["formula_sha256"],
                "proof_sha256": cpc["proof_sha256"],
            }
        )
    print(json.dumps({"status": "PASS", "checked": checked}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
