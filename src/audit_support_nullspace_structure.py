"""Audit whether aggregate support nullspaces contain only player-twin swaps."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

from analyze_two_color_box_capacity import circuit_data
from audit_canonical_optimal_face_ranges import rational_rank


REPRESENTATIVE_FILES = (
    "disjoint_n6_222_milp_dynamic_cuts20.json",
    "disjoint_n6_222_milp_seeded_probe30.json",
    "disjoint_n6_222_milp_seeded_probe30_b.json",
    "disjoint_n6_330_milp_probe30.json",
    "disjoint_n6_330_milp_seeded_probe30.json",
    "disjoint_n6_321_milp_probe30.json",
    "disjoint_n6_420_milp_probe25.json",
    "disjoint_n7_223_milp_probe15.json",
    "disjoint_n7_322_milp_probe15.json",
    "disjoint_n7_331_milp_probe15.json",
    "disjoint_n7_421_milp_probe15.json",
    "disjoint_n7_430_milp_probe15.json",
    "disjoint_n7_520_milp_probe15.json",
)


def structure_from_aggregate(n, aggregate, potential=None, extreme_sets=()):
    support = tuple(sorted(coalition for coalition, weight in aggregate.items() if weight))
    incidence_rows = [[1] * n]
    incidence_rows.extend([
        [int(coalition >> player & 1) for player in range(n)]
        for coalition in support
    ])
    nullity = n - rational_rank(incidence_rows)
    signatures = [
        tuple(int(coalition >> player & 1) for coalition in support)
        for player in range(n)
    ]
    twin_nullity = n - len(set(signatures))
    rank = rational_rank(incidence_rows)
    result = {
        "support_size": len(support),
        "support_nullity": n - rank,
        "twin_swap_nullity": twin_nullity,
        "twin_generated": n - rank == twin_nullity,
    }
    if potential is not None:
        result["potential_support_orthogonal"] = (
            rational_rank(incidence_rows + [list(potential)]) == rank
        )
    if extreme_sets:
        result["extreme_sets"] = {
            str(coalition): {
                "support_rigid": rational_rank(
                    incidence_rows
                    + [[int(coalition >> player & 1) for player in range(n)]]
                )
                == rank
            }
            for coalition in extreme_sets
        }
    return result


def structure(payload, circuit_index):
    n, _A, _B, aggregate, _required_A, _required_B = circuit_data(
        payload, circuit_index
    )
    return structure_from_aggregate(n, aggregate)


def glued_structure(record, n):
    aggregate = {}
    for row, weight in zip(record["active_rows"], record["circuit_weights"]):
        if row[0] != "core":
            continue
        coalition = row[2]
        aggregate[coalition] = aggregate.get(coalition, 0) + weight
    capacity = record.get("capacity", record.get("ordinary_capacity", {}))
    potential = tuple(Fraction(value) for value in capacity["player_potential"])
    extreme_sets = (capacity["maximum_set"], capacity["minimum_set"])
    return structure_from_aggregate(n, aggregate, potential, extreme_sets)


def source_record(label, payload, exhaustive):
    details = payload.get("circuits")
    if details is None:
        details = [
            circuit for batch in payload["batches"] for circuit in batch["circuits"]
        ]
        payload = {
            "n": payload["n"],
            "A_mask": payload["A_mask"],
            "B_mask": payload["B_mask"],
            "circuits": details,
        }
    records = [structure(payload, index) for index in range(1, len(details) + 1)]
    return {
        "source": label,
        "exhaustive": exhaustive,
        "circuit_count": len(records),
        "nontrivial_nullspace_count": sum(
            item["support_nullity"] > 0 for item in records
        ),
        "non_twin_nullspace_count": sum(
            not item["twin_generated"] for item in records
        ),
        "maximum_support_nullity": max(
            (item["support_nullity"] for item in records), default=0
        ),
    }


def glued_source_record(label, records, n):
    details = [glued_structure(record, n) for record in records]
    return {
        "source": label,
        "exhaustive": False,
        "circuit_count": len(details),
        "nontrivial_nullspace_count": sum(
            item["support_nullity"] > 0 for item in details
        ),
        "non_twin_nullspace_count": sum(
            not item["twin_generated"] for item in details
        ),
        "maximum_support_nullity": max(
            (item["support_nullity"] for item in details), default=0
        ),
        "all_potentials_support_orthogonal": all(
            item["potential_support_orthogonal"] for item in details
        ),
        "all_extreme_sets_support_rigid": all(
            extreme["support_rigid"]
            for item in details
            for extreme in item["extreme_sets"].values()
        ),
        "records": details,
    }


def audit(results_dir, supplement_dir):
    sources = []
    for filename in ("circuit_frontier.json", "circuit_frontier_221.json"):
        payload = json.loads((supplement_dir / filename).read_text())
        sources.append(source_record(filename, payload, exhaustive=True))
    for filename in REPRESENTATIVE_FILES:
        payload = json.loads((results_dir / filename).read_text())
        sources.append(source_record(filename, payload, exhaustive=False))
    forbidden = json.loads(
        (results_dir / "forbidden_ratio_glued_circuit_n6.json").read_text()
    )
    forbidden_record = dict(forbidden["circuits"][0])
    forbidden_record["ordinary_capacity"] = forbidden["ordinary_capacity"]
    sources.append(glued_source_record(
        "forbidden_ratio_glued_circuit_n6.json",
        [forbidden_record],
        forbidden["n"],
    ))
    glued = json.loads(
        (results_dir / "glued_local_circuit_hunt_n6_321.json").read_text()
    )
    sources.append(glued_source_record(
        "glued_local_circuit_hunt_n6_321.json",
        glued["deficient_records"],
        glued["geometry"]["n"],
    ))
    return {
        "status": "exact aggregate-support nullspace structure audit",
        "circuit_count": sum(item["circuit_count"] for item in sources),
        "exhaustive_five_player_circuit_count": sum(
            item["circuit_count"] for item in sources if item["exhaustive"]
        ),
        "representative_six_seven_player_circuit_count": sum(
            item["circuit_count"] for item in sources if not item["exhaustive"]
        ),
        "nontrivial_nullspace_count": sum(
            item["nontrivial_nullspace_count"] for item in sources
        ),
        "non_twin_nullspace_count": sum(
            item["non_twin_nullspace_count"] for item in sources
        ),
        "all_nullspaces_twin_generated": all(
            item["non_twin_nullspace_count"] == 0 for item in sources
        ),
        "glued_potentials_support_orthogonal": all(
            item.get("all_potentials_support_orthogonal", True)
            for item in sources
        ),
        "glued_extreme_sets_support_rigid": all(
            item.get("all_extreme_sets_support_rigid", True)
            for item in sources
        ),
        "sources": sources,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument(
        "--supplement-dir", type=Path, default=Path("paper/supplement")
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = audit(args.results_dir, args.supplement_dir)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
