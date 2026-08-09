#!/usr/bin/env python3
"""Verify frozen exact proof-object controls for the positive handover."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from export_core_closure_smt import qf_lra_smt2
from export_positive_handover_smt import build as direction_build
from export_positive_lmax_boundary_smt import build as boundary_build
from search_positive_handover_directions import critical_all_witness_solver


HERE = Path(__file__).resolve().parent
CERTIFICATES = HERE / "certificates"
CASES = (
    ("positive_lmax_direction_index0040", 40),
    ("positive_lmax_direction_index0200", 200),
    ("positive_lmax_direction_index0504", 504),
)
BOUNDARY_CASES = (
    ("positive_lmax_boundary_n_l", "n-l"),
    ("positive_lmax_boundary_n_j_k_r", "n-j-k-r"),
    ("positive_lmax_boundary_n_j_l_r", "n-j-l-r"),
    ("positive_lmax_boundary_n_k_l_r", "n-k-l-r"),
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
            direction_build(
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
    for stem, case in BOUNDARY_CASES:
        formula = CERTIFICATES / f"{stem}.smt2"
        proof = CERTIFICATES / f"{stem}.cpc"
        record = json.loads((CERTIFICATES / f"{stem}.json").read_text())
        assert formula.read_text() == qf_lra_smt2(boundary_build(case))
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
                "abstract_boundary_case": case,
                "formula_regenerates_from_current_source": True,
            }
        )
    print(json.dumps({"status": "PASS", "certificates": rows}, indent=2))


if __name__ == "__main__":
    main()
