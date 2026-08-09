#!/usr/bin/env python3
"""Verify frozen exact proof-object controls for the positive handover."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from export_core_closure_smt import qf_lra_smt2
from export_positive_handover_smt import build
from search_positive_handover_directions import critical_all_witness_solver


HERE = Path(__file__).resolve().parent
CERTIFICATES = HERE / "certificates"
CASES = (
    ("positive_lmax_direction_index0040", 40),
    ("positive_lmax_direction_index0200", 200),
    ("positive_lmax_direction_index0504", 504),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    rows = []
    for stem, survivor_index in CASES:
        formula = CERTIFICATES / f"{stem}.smt2"
        proof = CERTIFICATES / f"{stem}.cpc"
        record = json.loads((CERTIFICATES / f"{stem}.json").read_text())
        triage = json.loads((HERE / "triage32.json").read_text())
        base, _, _ = critical_all_witness_solver(
            survivor_index, triage["survivors"][survivor_index]
        )
        assert str(base.check()) == "sat"
        regenerated = qf_lra_smt2(
            build(
                survivor_index,
                HERE / "triage32.json",
                HERE / "positive_lmax_handover_directions.json",
            )
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
                "base_critical_system": "sat",
                "formula_regenerates_from_current_source": True,
            }
        )
    print(json.dumps({"status": "PASS", "certificates": rows}, indent=2))


if __name__ == "__main__":
    main()
