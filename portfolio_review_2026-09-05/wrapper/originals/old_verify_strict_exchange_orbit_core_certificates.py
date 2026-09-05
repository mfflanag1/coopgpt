#!/usr/bin/env python3
"""Regenerate and verify the three reduced large-case orbit-core records."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from audit_strict_exchange_large_case_orbit_cores import SELECTED, build_reduced
from export_core_closure_smt import qf_lra_smt2


HERE = Path(__file__).resolve().parent
CERTIFICATES = HERE / "orbit_core_certificates"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    audit = json.loads((HERE / "strict_exchange_large_case_orbit_cores.json").read_text())
    original = json.loads((HERE / "strict_exchange_direction_cores.json").read_text())
    orbit_counts = {
        row["case"]: row["sign_preserving_orbit_count"]
        for row in json.loads((HERE / "strict_exchange_sign_orbits.json").read_text())["rows"]
    }
    source_rows = {row["case"]: row for row in original["rows"]}
    assert audit["schema"] == "strict-exchange-large-case-orbit-cores-v1"
    assert audit["status"] == "PASS"
    assert audit["base_assertion_count_per_case"] == 71
    assert audit["original_role_orbit_count"] == 44
    assert audit["selected_role_orbit_count"] == 19
    assert audit["selected_labeled_direction_count"] == 136
    checked = []
    for row in audit["rows"]:
        case = row["case"]
        source = dict(source_rows[case])
        source["sign_preserving_orbit_count"] = orbit_counts[case]
        solver, _ = build_reduced(source, SELECTED[case])
        formula = CERTIFICATES / f"strict_exchange_orbit_core_{case}.smt2"
        if formula.read_text() != qf_lra_smt2(solver):
            raise AssertionError(f"{case} formula did not byte-regenerate")
        proof = CERTIFICATES / f"strict_exchange_orbit_core_{case}.cpc"
        record = json.loads((CERTIFICATES / f"strict_exchange_orbit_core_{case}.json").read_text())
        assert record["status"] == "PASS"
        assert record["z3"]["status"] == "unsat"
        assert record["cvc5"]["status"] == "unsat"
        assert record["formula_sha256"] == sha256(formula)
        cpc = record["cpc_proof"]
        assert cpc["status"] == "PASS"
        assert cpc["ethos"]["status"] == "correct"
        assert cpc["forbidden_markers"] == []
        assert cpc["proof_sha256"] == sha256(proof)
        assert all(item["verdict"] == "sat" for item in row["single_orbit_ablations"])
        assert [item["removed"] for item in row["single_cross_anchor_ablations"]] == [
            "lmax_top_cross",
            "lmin_bottom_cross",
        ]
        assert all(item["verdict"] == "sat" for item in row["single_cross_anchor_ablations"])
        expected_sources = ["opposite", "q0", "q1", "q2", "q3"]
        if case != "p4_n2_t0":
            expected_sources += ["q4", "q5"]
        assert row["blocker_comparison_sources"] == expected_sources
        if case == "p4_n2_t0":
            assert [item["removed"] for item in row["single_blocker_source_ablations"]] == row[
                "blocker_comparison_sources"
            ]
            assert all(
                item["verdict"] == "sat" for item in row["single_blocker_source_ablations"]
            )
        else:
            assert row["single_blocker_source_ablations"] == []
        checked.append(
            {
                "case": case,
                "selected_role_orbits": row["selected_role_orbit_count"],
                "selected_labeled_directions": row["selected_labeled_direction_count"],
                "formula_sha256": record["formula_sha256"],
                "proof_bytes": cpc["proof_bytes"],
                "proof_sha256": cpc["proof_sha256"],
            }
        )
    print(json.dumps({"status": "PASS", "checked": checked}, indent=2))


if __name__ == "__main__":
    main()
