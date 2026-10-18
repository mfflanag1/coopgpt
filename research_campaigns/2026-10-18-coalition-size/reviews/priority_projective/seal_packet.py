#!/usr/bin/env python3
"""Hash this bounded audit packet and the specified read-only campaign inputs.

No network, application data, or edits outside this owned audit directory.
Hashes certify the final snapshot; they do not certify original theorem truth.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

HERE = Path(__file__).resolve().parent
CAMP = HERE.parents[1]
INPUTS = (
    "CAMPAIGN_CONTRACT.txt",
    "lower/PROJECTIVE_SQUARE_ROOT_LOWER.txt",
    "lower/GENERAL_ARITY_CIRCUIT_LOWER.txt",
    "root/PROJECTIVE_BOUNDED_COALITION_TAIL.txt",
    "sources/MOULIN_SPRUMONT_PRIMARY_CHECK.txt",
    "sources/PROJECTIVE_STATIC_STABILITY_COMPARISON.txt",
    "sources/moulin_sprumont_2004_demand_responsiveness.pdf",
    "sources/bachrach_etal_2009_cost_of_stability.pdf",
    "constructive/FIXED_LINEAR_WORTH_RULE_QUADRATIC_BARRIER.txt",
    "constructive/SIGNED_FIXED_MARGINAL_POSITIVITY.txt",
)


def record(path, relative_to):
    data = path.read_bytes()
    return {"path": str(path.relative_to(relative_to)), "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest()}


def main():
    output = HERE / "INPUT_AND_ARTIFACT_HASHES.json"
    inputs = [record(CAMP / name, CAMP) for name in INPUTS]
    artifacts = [record(path, HERE) for path in sorted(HERE.iterdir())
                 if path.is_file() and path != output]
    ledger = json.loads((HERE / "source_ledger.json").read_text())
    success = [row for row in ledger
               if row["status"] == "downloaded_and_text_extracted"]
    diagnostic = json.loads((HERE / "min2_population_separation.json").read_text())
    assert diagnostic["status"] == "PASS"
    manifest = {
        "sealed_utc": datetime.now(timezone.utc).isoformat(),
        "task_started_utc": "2026-10-18T22:06:51Z",
        "scope": "bounded original-source comparison, not priority clearance",
        "input_snapshot_note": "Final read-only input snapshot; others may edit later.",
        "inputs": inputs, "owned_artifacts": artifacts,
        "source_downloads": {
            "successful_retrievals": len(success),
            "successful_pdf_bytes": sum(row["bytes"] for row in success),
            "failed_attempts": len(ledger) - len(success),
            "application_dataset_bytes": 0,
        },
        "executed_diagnostic": {
            key: diagnostic[key] for key in
            ("status", "arithmetic", "scope", "profiles", "coverage_rows", "full_out_rows")
        },
    }
    output.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"manifest": str(output), "inputs": len(inputs),
                      "artifacts": len(artifacts),
                      **manifest["source_downloads"]}, sort_keys=True))


if __name__ == "__main__":
    main()
