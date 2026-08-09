#!/usr/bin/env python3
"""Check the logical joins in the six-player equality checkpoint."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CERTIFICATES = HERE / "certificates"
EQUALITY_INDICES = (1408, 2236)


def read(path):
    return json.loads(path.read_text())


def main():
    strict = read(HERE / "core_generator_census.json")
    triple = read(HERE / "equality_triple_census.json")
    no_triple = read(HERE / "equality_no_triple_census.json")
    reconstruction = read(HERE / "core_closure_reconstruction_audit.json")

    assert strict["tally"] == {"sat": 0, "unsat": 3350, "unknown": 0}
    assert triple["tally"] == {"sat": 2, "unsat": 3348, "unknown": 0}
    assert no_triple["tally"] == {"sat": 0, "unsat": 3350, "unknown": 0}
    assert len(strict["rows"]) == len(triple["rows"]) == len(no_triple["rows"]) == 3350

    for strict_row, triple_row, no_triple_row in zip(
        strict["rows"], triple["rows"], no_triple["rows"]
    ):
        for key in ("index", "lmin", "lmax", "table"):
            assert strict_row[key] == triple_row[key] == no_triple_row[key]
    sat_rows = [row for row in triple["rows"] if row["result"] == "sat"]
    assert tuple(row["index"] for row in sat_rows) == EQUALITY_INDICES

    assert reconstruction["audited_sat_indices"] == list(EQUALITY_INDICES)
    assert reconstruction["all_displayed_sat_models_recomputed"] is True
    models = {row["census_index"]: row for row in reconstruction["models"]}
    for source, index in zip(sat_rows, EQUALITY_INDICES):
        model = models[index]
        assert model["lmin"]["point"] == source["candidate_lmin"]
        assert model["lmax"]["point"] == source["candidate_lmax"]
        assert model["overlap"] == model["l1_distance"] == "2/3"
        assert model["exact_dispersion_optimal_lmax_anchor"]["theta"] == "1/3"
        assert model["common_lmin_lmax_tight_top_triples"]
        assert set(model["solver_reported_tight_lmax_top_triples"]) <= set(
            model["all_reconstructed_tight_lmax_top_triples"]
        )
        assert len(model["lmin"]["pinning_certificates"]) == 6
        assert len(model["lmax"]["pinning_certificates"]) == 6

    checked_cpc = []
    for index in EQUALITY_INDICES:
        for stem in (
            f"equality_noncanonical_index{index}",
            f"equality_no_common_triple_index{index}",
            f"equality_no_triple_index{index}",
            f"equality_subthird_index{index}",
        ):
            record = read(CERTIFICATES / f"{stem}.json")
            assert record["status"] == "PASS"
            assert record["z3"]["status"] == record["cvc5"]["status"] == "unsat"
            assert record["cpc_proof"]["status"] == "PASS"
            assert record["cpc_proof"]["ethos"]["status"] == "correct"
            checked_cpc.append(stem)

    print(
        json.dumps(
            {
                "status": "PASS",
                "strict_tally": strict["tally"],
                "equality_with_triple_tally": triple["tally"],
                "equality_without_triple_tally": no_triple["tally"],
                "reconstructed_indices": list(EQUALITY_INDICES),
                "checked_equality_cpc_objects": checked_cpc,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
