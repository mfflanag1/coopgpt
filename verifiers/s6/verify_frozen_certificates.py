#!/usr/bin/env python3
"""Verify hashes and recorded verdicts for the frozen CPC controls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from export_core_closure_smt import build, qf_lra_smt2


HERE = Path(__file__).resolve().parent
CERTIFICATES = HERE / "certificates"
CASES = (
    ("failure_index0000", 0, "failure"),
    ("equality_noncanonical_index1408", 1408, "equality-noncanonical"),
    ("equality_noncanonical_index2236", 2236, "equality-noncanonical"),
    ("equality_no_common_triple_index1408", 1408, "equality-no-common-triple"),
    ("equality_no_common_triple_index2236", 2236, "equality-no-common-triple"),
    ("equality_no_triple_index1408", 1408, "equality-no-triple"),
    ("equality_no_triple_index2236", 2236, "equality-no-triple"),
    ("equality_subthird_index1408", 1408, "equality-subthird"),
    ("equality_subthird_index2236", 2236, "equality-subthird"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    rows = []
    for stem, survivor_index, mode in CASES:
        formula = CERTIFICATES / f"{stem}.smt2"
        proof = CERTIFICATES / f"{stem}.cpc"
        record = json.loads((CERTIFICATES / f"{stem}.json").read_text())
        regenerated = qf_lra_smt2(
            build(survivor_index, mode, HERE / "triage32.json")
        )
        assert formula.read_text() == regenerated
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
                "formula_regenerates_from_current_source": True,
            }
        )
    print(json.dumps({"status": "PASS", "certificates": rows}, indent=2))


if __name__ == "__main__":
    main()
