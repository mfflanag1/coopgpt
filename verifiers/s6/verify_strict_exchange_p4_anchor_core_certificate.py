#!/usr/bin/env python3
"""Regenerate and verify the anchor-localized p4 one-witness certificate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import z3
from z3.z3util import get_vars

from audit_strict_exchange_p4_anchor_core import make_solver, selected_implications, source_row
from export_core_closure_smt import qf_lra_smt2


HERE = Path(__file__).resolve().parent
CERTIFICATES = HERE / "p4_anchor_core_certificates"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    audit = json.loads((HERE / "strict_exchange_p4_anchor_core.json").read_text())
    assert audit["schema"] == "strict-exchange-p4-anchor-core-v1"
    assert audit["status"] == "PASS"
    assert audit["case"] == "p4_n2_t0"
    assert audit["anchor_roles"]["same_player_four_inequality_verdict"] == "unsat"
    assert audit["declared_real_count"] == 18
    assert audit["base_assertion_count"] == 39
    assert audit["blocker_comparison_sources"] == ["opposite", "q1"]
    assert audit["base_without_exchange_verdict"] == "sat"
    assert audit["unguarded_rebuild_verdict"] == "unsat"
    assert audit["selected_labeled_direction_count"] == 19
    assert audit["selected_residual_orbit_count"] == 10
    assert len(audit["residual_orbits"]) == 10
    assert all(item["verdict"] == "sat" for item in audit["single_direction_ablations"])
    assert len(audit["single_direction_ablations"]) == 19
    assert all(
        item["verdict"] == "sat" for item in audit["single_residual_orbit_ablations"]
    )
    assert len(audit["single_residual_orbit_ablations"]) == 10
    assert audit["single_blocker_source_ablations"] == [
        {"removed": "opposite", "verdict": "sat"},
        {"removed": "q1", "verdict": "sat"},
    ]

    base, canonical, implications, _ = selected_implications(source_row())
    assert len(base) + len(canonical) == 39
    assert len(implications) == 19
    for implication in implications:
        assert z3.is_implies(implication)
        consequent = implication.children()[1]
        alternatives = consequent.children() if z3.is_or(consequent) else (consequent,)
        for alternative in alternatives:
            comparisons = alternative.children() if z3.is_and(alternative) else (alternative,)
            assert len(comparisons) == 2
            variable_sets = [
                {str(variable) for variable in get_vars(comparison)}
                for comparison in comparisons
            ]
            q1_flags = [
                any(name.startswith("equality_exchange_q_1_") for name in names)
                for names in variable_sets
            ]
            assert sorted(q1_flags) == [False, True]
    regenerated = qf_lra_smt2(make_solver(base, canonical, implications))
    formula = CERTIFICATES / "strict_exchange_p4_anchor_core.smt2"
    if formula.read_text() != regenerated:
        raise AssertionError("anchor-localized formula did not byte-regenerate")
    declaration_lines = [
        line for line in regenerated.splitlines() if line.startswith("(declare-fun")
    ]
    assertion_lines = [line for line in regenerated.splitlines() if line.startswith("(assert")]
    assert len(declaration_lines) == 18
    assert len(assertion_lines) == 58
    assert all(
        "equality_exchange_q_" not in line or "equality_exchange_q_1_" in line
        for line in declaration_lines
    )

    proof = CERTIFICATES / "strict_exchange_p4_anchor_core.cpc"
    record = json.loads((CERTIFICATES / "strict_exchange_p4_anchor_core.json").read_text())
    assert record["status"] == "PASS"
    assert record["z3"]["status"] == "unsat"
    assert record["cvc5"]["status"] == "unsat"
    assert record["formula_sha256"] == sha256(formula)
    cpc = record["cpc_proof"]
    assert cpc["status"] == "PASS"
    assert cpc["ethos"]["status"] == "correct"
    assert cpc["forbidden_markers"] == []
    assert cpc["proof_sha256"] == sha256(proof)
    print(
        json.dumps(
            {
                "status": "PASS",
                "formula_sha256": record["formula_sha256"],
                "formula_bytes": record["formula_bytes"],
                "proof_sha256": cpc["proof_sha256"],
                "proof_bytes": cpc["proof_bytes"],
                "declared_reals": len(declaration_lines),
                "assertions": len(assertion_lines),
                "directions": len(implications),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
