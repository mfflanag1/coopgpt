"""Ablate witness sources on every known subunit-capacity circuit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_potential_guided_exactness import MODE_SOURCES, analyze


CASES = (
    ("n6-222-1", "disjoint_n6_222_milp_dynamic_cuts20.json",
     "disjoint_n6_222_recoloring_capacity.json", 1),
    ("n6-321-5", "disjoint_n6_321_milp_probe30.json",
     "disjoint_n6_321_probe30_recoloring_capacity.json", 5),
    ("n6-330a-1", "disjoint_n6_330_milp_probe30.json",
     "disjoint_n6_330_probe30_recoloring_capacity.json", 1),
    ("n6-330a-4", "disjoint_n6_330_milp_probe30.json",
     "disjoint_n6_330_probe30_recoloring_capacity.json", 4),
    ("n6-330a-5", "disjoint_n6_330_milp_probe30.json",
     "disjoint_n6_330_probe30_recoloring_capacity.json", 5),
    ("n6-330a-9", "disjoint_n6_330_milp_probe30.json",
     "disjoint_n6_330_probe30_recoloring_capacity.json", 9),
    ("n6-330b-2", "disjoint_n6_330_milp_seeded_probe30.json",
     "disjoint_n6_330_seeded_probe30_recoloring_capacity.json", 2),
    ("n6-330b-3", "disjoint_n6_330_milp_seeded_probe30.json",
     "disjoint_n6_330_seeded_probe30_recoloring_capacity.json", 3),
    ("n6-330b-6", "disjoint_n6_330_milp_seeded_probe30.json",
     "disjoint_n6_330_seeded_probe30_recoloring_capacity.json", 6),
    ("n6-330b-7", "disjoint_n6_330_milp_seeded_probe30.json",
     "disjoint_n6_330_seeded_probe30_recoloring_capacity.json", 7),
    ("n6-330b-8", "disjoint_n6_330_milp_seeded_probe30.json",
     "disjoint_n6_330_seeded_probe30_recoloring_capacity.json", 8),
    ("n6-420-1", "disjoint_n6_420_milp_probe25.json",
     "disjoint_n6_420_milp_probe25_recoloring_capacity.json", 1),
    ("n6-420-2", "disjoint_n6_420_milp_probe25.json",
     "disjoint_n6_420_milp_probe25_recoloring_capacity.json", 2),
    ("n6-420-6", "disjoint_n6_420_milp_probe25.json",
     "disjoint_n6_420_milp_probe25_recoloring_capacity.json", 6),
    ("n6-420-8", "disjoint_n6_420_milp_probe25.json",
     "disjoint_n6_420_milp_probe25_recoloring_capacity.json", 8),
    ("n7-322-1", "disjoint_n7_322_milp_probe15.json",
     "disjoint_n7_322_milp_probe15_recoloring_capacity.json", 1),
    ("n7-322-2", "disjoint_n7_322_milp_probe15.json",
     "disjoint_n7_322_milp_probe15_recoloring_capacity.json", 2),
    ("n7-322-3", "disjoint_n7_322_milp_probe15.json",
     "disjoint_n7_322_milp_probe15_recoloring_capacity.json", 3),
    ("n7-331-1", "disjoint_n7_331_milp_probe15.json",
     "disjoint_n7_331_milp_probe15_recoloring_capacity.json", 1),
    ("n7-331-4", "disjoint_n7_331_milp_probe15.json",
     "disjoint_n7_331_milp_probe15_recoloring_capacity.json", 4),
    ("n7-421-2", "disjoint_n7_421_milp_probe15.json",
     "disjoint_n7_421_milp_probe15_recoloring_capacity.json", 2),
    ("n7-421-3", "disjoint_n7_421_milp_probe15.json",
     "disjoint_n7_421_milp_probe15_recoloring_capacity.json", 3),
    ("n7-430-1", "disjoint_n7_430_milp_probe15.json",
     "disjoint_n7_430_milp_probe15_recoloring_capacity.json", 1),
    ("n7-430-2", "disjoint_n7_430_milp_probe15.json",
     "disjoint_n7_430_milp_probe15_recoloring_capacity.json", 2),
    ("n7-430-3", "disjoint_n7_430_milp_probe15.json",
     "disjoint_n7_430_milp_probe15_recoloring_capacity.json", 3),
    ("n7-430-4", "disjoint_n7_430_milp_probe15.json",
     "disjoint_n7_430_milp_probe15_recoloring_capacity.json", 4),
    ("n7-223-3", "disjoint_n7_223_milp_probe15.json",
     "disjoint_n7_223_milp_probe15_recoloring_capacity.json", 3),
    ("n7-520-1", "disjoint_n7_520_milp_probe15.json",
     "disjoint_n7_520_milp_probe15_recoloring_capacity.json", 1),
    ("n7-520-2", "disjoint_n7_520_milp_probe15.json",
     "disjoint_n7_520_milp_probe15_recoloring_capacity.json", 2),
    ("n7-520-3", "disjoint_n7_520_milp_probe15.json",
     "disjoint_n7_520_milp_probe15_recoloring_capacity.json", 3),
)


def type_i_payload(results_dir):
    circuit = {
        "active_rows": [
            ["core", 0, 20], ["core", 1, 7], ["core", 1, 25],
            ["core", 1, 26], ["core", 2, 5], ["core", 2, 6],
            ["core", 2, 11], ["core", 2, 24],
            ["mono", 0, 1, 2, 7], ["mono", 0, 2, 4, 24],
        ],
        "circuit_weights": [1] * 10,
        "efficiency_weights": [0, 2, 2],
    }
    capacity = json.loads(
        (results_dir / "disjoint_n5_320_full_recoloring_capacity.json").read_text()
    )["circuits"][4]
    capacity = dict(capacity)
    capacity["circuit_index"] = 1
    return (
        {"n": 5, "A_mask": 7, "B_mask": 24, "circuits": [circuit]},
        {"circuits": [capacity]},
        1,
    )


def audited_record(label, circuit, capacity, index):
    modes = {}
    for mode in MODE_SOURCES:
        result = analyze(circuit, capacity, index, candidate_mode=mode)
        verified = result["status"] == "POTENTIAL-GUIDED EXACTNESS CERTIFICATE VERIFIED"
        modes[mode] = {
            "verified": verified,
            "status": result["status"],
            "candidate_tight_count": len(result["candidate_tights"]),
            "used_tight_count": result.get("used_tight_count"),
            "block_count": result.get("block_count"),
            "circuit_margin": result.get("circuit_margin"),
            "primal_exact": result.get("primal_exact"),
            "dual_exact": result.get("dual_exact"),
        }
    return {"label": label, "modes": modes}


def audit(results_dir):
    records = []
    circuit, capacity, index = type_i_payload(results_dir)
    records.append(audited_record("n5-Type-I", circuit, capacity, index))
    for label, circuit_name, capacity_name, index in CASES:
        circuit = json.loads((results_dir / circuit_name).read_text())
        capacity = json.loads((results_dir / capacity_name).read_text())
        records.append(audited_record(label, circuit, capacity, index))
    return {
        "status": "exact potential-guided source ablation",
        "case_count": len(records),
        "modes": {
            mode: {
                "sources": sorted(MODE_SOURCES[mode]),
                "verified_cases": sum(record["modes"][mode]["verified"] for record in records),
            }
            for mode in MODE_SOURCES
        },
        "cases": records,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = audit(args.results_dir)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
