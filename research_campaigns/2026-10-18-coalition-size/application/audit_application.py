#!/usr/bin/env python3
"""Offline artifact integrity/byte audit; no network and no telemetry queries."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import struct
import tarfile

ROOT = Path(__file__).resolve().parent


def read_json(name):
    return json.loads((ROOT / name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    dataset_bytes = 0
    documentation_bytes = 0
    range_count = 0
    failures = []
    for folder, ledger in [("metadata", "metadata_requests.jsonl"),
                           ("m100_may_metadata", "m100_may_metadata/requests.jsonl"),
                           ("m100_may_footers", "m100_may_footers/requests.jsonl")]:
        rows = [json.loads(line) for line in (ROOT / ledger).read_text().splitlines()]
        for r in rows:
            if r.get("error"):
                failures.append({"url": r["url"], "error": r["error"], "body_bytes": r["body_bytes"]})
            if r["kind"].startswith("dataset_"):
                dataset_bytes += r["body_bytes"]
                range_count += 1
                assert r["status"] == 206
                assert r["body_bytes"] == r["length"]
                file = ROOT / folder / f"range_{r['start']}_{r['length']}.bin"
                assert file.stat().st_size == r["body_bytes"] and sha(file) == r["sha256"]
            else:
                documentation_bytes += r["body_bytes"]
                if "saved_path" in r:
                    file = ROOT / r["saved_path"]
                    assert file.stat().st_size == r["body_bytes"] and sha(file) == r["sha256"]
                elif r["body_bytes"]:
                    file = ROOT / folder / "zenodo_record.json"
                    assert file.stat().st_size == r["body_bytes"] and sha(file) == r["sha256"]
    assert dataset_bytes <= 100_000_000
    headers = read_json("m100_may_metadata/report.json")
    assert headers["status"] == "COMPLETE_TO_FIRST_END_MARKER" and headers["error"] is None
    # Reparse every retained tar header's checksum/name/size without reading members.
    for row in headers["entries"]:
        at = row["offset"] - 512
        file = ROOT / "m100_may_metadata" / f"range_{at}_512.bin"
        info = tarfile.TarInfo.frombuf(file.read_bytes(), "utf-8", "surrogateescape")
        assert info.size == row["size"] and info.type.decode("ascii", "replace") == row["type"]
        # No GNU long-name entries occurred in this archive; exact name comparison is valid.
        assert info.name == row["name"]
    footers = read_json("m100_may_footers/report.json")
    assert footers["status"] == "COMPLETE_METADATA_ONLY" and footers["error"] is None
    assert footers["cumulative_dataset_bytes"] == dataset_bytes
    assert footers["power_state_payload_values_read"] == 0
    for member in footers["members"]:
        original = next(r for r in headers["selected_members"] if r["name"] == member["name"])
        file = ROOT / "m100_may_footers" / (member["metric"] + "_FOOTER_ONLY_SPARSE.parquet")
        assert file.stat().st_size == original["size"]
        with file.open("rb") as stream:
            assert stream.read(4) == b"PAR1"
            stream.seek(-8, 2)
            tail = stream.read(8)
            length = struct.unpack("<I", tail[:4])[0]
            assert tail[4:] == b"PAR1" and length == member["footer_size"]
            stream.seek(-8-length, 2)
            assert hashlib.sha256(stream.read(length)).hexdigest() == member["footer_sha256"]
        assert member["chunk_columns"] == ["row_group_id", "row_group_num_rows", "path_in_schema", "physical_type", "total_compressed_size", "data_page_offset", "dictionary_page_offset"]
        assert member["timestamp_range_columns"] == ["row_group_id", "minimum", "maximum"]
    planned = read_json("m100_training_day_plan.json")
    assert planned["already_downloaded_dataset_bytes"] == dataset_bytes
    assert planned["additional_selected_chunk_bytes"] == sum(m["merged_range_bytes"] for m in planned["members"])
    assert planned["coalesced_projected_cumulative_dataset_bytes"] < 100_000_000
    assert all(m["candidate_groups_extend_outside_day"] for m in planned["members"])
    witness = read_json("three_owner_witness.json")
    assert witness["cone_checks"] == "PASS" and witness["strict_loss_sign_certificate"] == "625 > 545"
    keyfiles = ["THREE_INTEREST_CONTRACT.txt", "MISSING_EVIDENCE.json", "CONDITIONAL_VALIDATION_PROTOCOL.txt",
                "SUMMIT_ACCESS_GATE.txt", "THREE_OWNER_ALGEBRAIC_WITNESS.txt", "three_owner_witness.json",
                "m100_may_metadata/report.json", "m100_may_footers/report.json", "m100_training_day_plan.json",
                "M100_MAY_ACCESS_GATE.txt", "FINAL_FEASIBILITY_GATE.txt", "NEXT_PREREGISTRATION_DECISION.txt",
                "fetch_metadata.py", "m100_may_metadata_gate.py", "m100_may_footer_gate.py",
                "plan_m100_training_day.py", "check_three_owner_witness.py", "audit_application.py",
                "metadata_requests.jsonl", "m100_may_metadata/requests.jsonl", "m100_may_footers/requests.jsonl",
                "metadata/author_readme.md", "metadata/official_record.html", "metadata/repository_commit.json",
                "m100_may_metadata/zenodo_record.json"]
    report = {"utc": dt.datetime.now(dt.timezone.utc).isoformat(), "status": "PASS",
              "dataset_body_bytes": dataset_bytes, "dataset_cap_bytes": 100_000_000,
              "remaining_cap_bytes": 100_000_000-dataset_bytes,
              "dataset_range_requests": range_count, "logged_documentation_body_bytes": documentation_bytes,
              "metadata_fetch_failures_preserved": failures,
              "critical_artifact_sha256": {p: sha(ROOT / p) for p in keyfiles},
              "limits": "Integrity and safe-query artifact checks only; not independent proof of physical/contractual feasibility or live remote archive hash."}
    (ROOT / "audit_application.json").write_text(json.dumps(report, indent=2)+"\n")
    (ROOT / "SOURCE_AND_LEDGER_SHA256.json").write_text(json.dumps(report["critical_artifact_sha256"], indent=2)+"\n")
    api = read_json("m100_may_metadata/zenodo_record.json")
    manifest = {"as_of_utc": report["utc"], "scope": "Application access/schema/contract gate",
                "sum_dataset_body_bytes": dataset_bytes, "cap_bytes": 100_000_000,
                "summit_dataset_body_bytes": 0,
                "m100_tar_header_bytes": headers["dataset_bytes_read"],
                "m100_footer_marker_and_footer_bytes": footers["footer_dataset_bytes"],
                "power_state_data_pages_fetched": False,
                "power_state_column_statistics_exposed": False,
                "timestamp_extrema_metadata_exposed": True,
                "logged_documentation_body_bytes": documentation_bytes,
                "network_accounting_definition": "Exact response bodies read by saved acquisition scripts; excludes HTTP/TLS/browser/Web-tool documentation overhead. All fetched bytes from dataset archive count, including headers/footers.",
                "sources": [
                    {"name":"Summit official record", "url":"https://doi.ccs.ornl.gov/dataset/086578e9-8a9f-56b1-a657-0ed8b7393deb", "doi":"10.13139/OLCF/1861393", "owner":"ORNL/OLCF authors", "release_date":"2022-04-11", "status":"Globus authentication boundary; no listing or telemetry"},
                    {"name":"Summit author schema", "url":"https://github.com/at-aaims/summit_power_and_thermal_data", "commit":"2214562d619b5393e7e77f6ef6d2ffc7ffd8940e", "license":"CC BY4.0 per README", "readme_sha256":sha(ROOT/"metadata/author_readme.md"), "status":"Declared ten-second persistent100host panel; actual schema/timezone unverified"},
                    {"name":"M100 May2020", "url":headers["source"], "owner":"M100/CINECA release authors", "doi":"10.5281/zenodo.7588815", "version":api["metadata"]["version"], "license":api["metadata"]["license"]["id"], "release_date":api["metadata"]["publication_date"], "archive_bytes":headers["archive_bytes"], "remote_archive_md5":"acc17e344755ef58a009592b362fd6bf", "full_archive_checksum_verified":False, "status":"Real header/footer metadata only; UTC millis schema; no observed simultaneous panel"}
                ],
                "transformations": ["Tar metadata parsing and selected member-size accounting", "Synthetic sparse footer wrappers with zero data holes", "Safe schema/chunk metadata projection excluding power/state statistics", "Chronological May12 candidate selection from timestamp extrema only"],
                "interpretation": "Institution-unverified; Summit access-limited; M100 selective training-day byte-feasible but alignment/state/holdout-safe value access unverified"}
    (ROOT / "data_manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k not in ("critical_artifact_sha256", "metadata_fetch_failures_preserved")}, indent=2))


if __name__ == "__main__":
    main()
