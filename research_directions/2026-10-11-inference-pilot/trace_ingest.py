#!/usr/bin/env python3
"""Bounded acquisition and descriptive summary of a public Azure request trace.

Default operation is offline and verifies the stored sample checksum. --fetch
retrieves at most 512 KiB, keeps the first observed complete calendar minute,
and refreshes the adjacent sample/provenance. No serving rates are inferred.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import math
from pathlib import Path
import urllib.request


SOURCE_URL = (
    "https://github.com/Azure/AzurePublicDataset/releases/download/"
    "dataset-llm-2024/AzureLLMInferenceTrace_code_1week.csv"
)
README_URL = (
    "https://github.com/Azure/AzurePublicDataset/blob/master/"
    "AzureLLMInferenceDataset2024.md"
)
LICENSE_URL = "https://github.com/Azure/AzurePublicDataset/blob/master/LICENSE"
BYTE_LIMIT = 524288
ROW_LIMIT = 10000
FIELDS = ["TIMESTAMP", "ContextTokens", "GeneratedTokens"]
UTC = dt.timezone.utc


def parse_rows(raw: bytes) -> list[dict]:
    """Reject malformed or nonchronological data rather than silently cleaning it."""
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if reader.fieldnames != FIELDS:
        raise ValueError(f"Unexpected schema: {reader.fieldnames!r}")
    rows = []
    last = None
    for row in reader:
        if set(row) != set(FIELDS) or any(value is None for value in row.values()):
            raise ValueError("Malformed CSV row")
        timestamp = dt.datetime.fromisoformat(row["TIMESTAMP"])
        if timestamp.tzinfo is None or timestamp.utcoffset() != dt.timedelta(0):
            raise ValueError("Expected explicit UTC timestamps")
        if last is not None and timestamp < last:
            raise ValueError("Source order is not chronological")
        last = timestamp
        values = [int(row[field]) for field in FIELDS[1:]]
        if any(value < 0 for value in values):
            raise ValueError("Token counts must be nonnegative")
        rows.append({"time": timestamp, "context": values[0], "generated": values[1]})
    if not rows:
        raise ValueError("Empty trace")
    return rows


def first_minute(raw: bytes) -> tuple[bytes, list[dict], dt.datetime]:
    # The documented schema has one record per line; discard the final partial
    # line of the HTTP range before parsing. Preserve selected source bytes.
    if b"\n" not in raw:
        raise ValueError("No complete CSV lines in bounded prefix")
    lines = raw[: raw.rfind(b"\n") + 1].splitlines(keepends=True)
    rows = parse_rows(b"".join(lines))
    start = rows[0]["time"].replace(second=0, microsecond=0)
    end = start + dt.timedelta(minutes=1)
    count = next((i for i, row in enumerate(rows) if row["time"] >= end), None)
    if count is None:
        raise ValueError("Prefix does not establish the minute's right boundary")
    if count > ROW_LIMIT:
        raise ValueError("First minute exceeds the declared 10,000-record limit")
    sample = b"".join(lines[: count + 1])
    selected = parse_rows(sample)
    if len(selected) != count:
        raise ValueError("One-record-per-line assumption failed")
    return sample, selected, start


def distribution(values: list[int]) -> dict:
    ordered = sorted(values)
    return {
        "min": ordered[0],
        "mean": sum(ordered) / len(ordered),
        "p50": ordered[math.ceil(0.50 * len(ordered)) - 1],
        "p90": ordered[math.ceil(0.90 * len(ordered)) - 1],
        "p99": ordered[math.ceil(0.99 * len(ordered)) - 1],
        "max": ordered[-1],
        "sum": sum(ordered),
        "quantile_convention": "nearest rank, no interpolation",
    }


def describe(rows: list[dict], start: dt.datetime) -> dict:
    counts = [0] * 60
    for row in rows:
        second = int((row["time"] - start).total_seconds())
        if not 0 <= second < 60:
            raise ValueError("Sample extends outside the declared minute")
        counts[second] += 1
    return {
        "records": len(rows),
        "window_start_utc": start.isoformat(),
        "window_end_exclusive_utc": (start + dt.timedelta(minutes=1)).isoformat(),
        "observation_window_seconds": 60,
        "first_invocation_utc": rows[0]["time"].isoformat(),
        "last_invocation_utc": rows[-1]["time"].isoformat(),
        "requests_per_second_over_full_window": len(rows) / 60,
        "arrivals_per_second": counts,
        "arrivals_per_10_seconds": [sum(counts[i : i + 10]) for i in range(0, 60, 10)],
        "context_tokens": distribution([row["context"] for row in rows]),
        "generated_tokens": distribution([row["generated"] for row in rows]),
        "duplicate_timestamp_records": len(rows) - len({row["time"] for row in rows}),
        "interpretation": (
            "Chronological convenience sample describing request arrival times and "
            "token lengths only. Not a representative estimate of Azure workloads, "
            "a hardware benchmark, a scheduling experiment, or an ownership dataset."
        ),
    }


def acquire(directory: Path) -> dict:
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"Range": f"bytes=0-{BYTE_LIMIT - 1}", "User-Agent": "CoopGPT-research-pilot"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        # Even when a server ignores Range, read only BYTE_LIMIT then close.
        raw = response.read(BYTE_LIMIT)
        transport = {
            "http_status": response.status,
            "requested_range": f"bytes=0-{BYTE_LIMIT - 1}",
            "content_range": response.headers.get("Content-Range"),
            "content_length": response.headers.get("Content-Length"),
            "etag": response.headers.get("ETag"),
            "last_modified": response.headers.get("Last-Modified"),
            "bytes_read": len(raw),
            "maximum_body_bytes_read": BYTE_LIMIT,
            "prefix_sha256": hashlib.sha256(raw).hexdigest(),
        }
    sample, rows, start = first_minute(raw)
    provenance = {
        "dataset": "Azure LLM inference trace 2024, Code",
        "source_url": SOURCE_URL,
        "documentation_url": README_URL,
        "retrieved_at_utc": dt.datetime.now(UTC).isoformat(),
        "license": "Creative Commons Attribution 4.0 International (CC-BY-4.0)",
        "license_url": LICENSE_URL,
        "license_standard_url": "https://creativecommons.org/licenses/by/4.0/",
        "attribution": (
            "AzurePublicDataset; Jovan Stojkovic, Chaojie Zhang, Inigo Goiri, "
            "Josep Torrellas, Esha Choukse. DynamoLLM: Designing LLM Inference "
            "Clusters for Performance and Energy Efficiency. HPCA 2025."
        ),
        "paper_url": "https://arxiv.org/abs/2408.00741",
        "source_documentation_collection_dates": "2024-05-10 through 2024-05-19",
        "field_definitions": {
            "TIMESTAMP": "Invocation datetime; retrieved records explicitly carry UTC +00:00.",
            "ContextTokens": "Number of context tokens per request; count.",
            "GeneratedTokens": "Number of generated tokens per request; count.",
        },
        "selection": (
            "All records in the first observed calendar minute of the source file, "
            "starting at floor(first timestamp to a minute), with the right boundary "
            "confirmed by a subsequent record. At most 10,000 records are retained; "
            "at most 512 KiB of source body are read. This is a chronological, nonrandom, "
            "nonrepresentative convenience sample."
        ),
        "changes_from_source": "Row subset only; header and selected CSV bytes are unaltered.",
        "sample_file": "trace_sample.csv",
        "sample_bytes": len(sample),
        "sample_sha256": hashlib.sha256(sample).hexdigest(),
        "transport": transport,
        "summary": describe(rows, start),
        "exclusions": [
            "No prompt text or user identities are present in these fields.",
            "No hardware service rates, memory use, power, energy, or latency are measured here.",
            "No owner entitlements, payments, reservation values, or market behavior are observed.",
            "The synthetic production coefficients used by the pilot are separate assumptions.",
            "This descriptive slice is not a held-out validation of the economic model.",
        ],
    }
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "trace_sample.csv").write_bytes(sample)
    (directory / "TRACE_PROVENANCE.json").write_text(json.dumps(provenance, indent=2) + "\n")
    return provenance


def offline_summary(directory: Path) -> dict:
    raw = (directory / "trace_sample.csv").read_bytes()
    provenance = json.loads((directory / "TRACE_PROVENANCE.json").read_text())
    if hashlib.sha256(raw).hexdigest() != provenance["sample_sha256"]:
        raise ValueError("Sample SHA-256 does not match provenance")
    if len(raw) != provenance["sample_bytes"]:
        raise ValueError("Sample byte count does not match provenance")
    rows = parse_rows(raw)
    start = dt.datetime.fromisoformat(provenance["summary"]["window_start_utc"])
    summary = describe(rows, start)
    if summary != provenance["summary"]:
        raise ValueError("Recomputed summary differs from saved provenance")
    return summary


def self_test() -> None:
    tiny = (
        b"TIMESTAMP,ContextTokens,GeneratedTokens\r\n"
        b"2024-05-10 00:00:00+00:00,10,2\r\n"
        b"2024-05-10 00:00:59+00:00,20,4\r\n"
        b"2024-05-10 00:01:00+00:00,30,8\r\n"
        b"truncated"
    )
    sample, rows, start = first_minute(tiny)
    if len(rows) != 2 or not sample.endswith(b",20,4\r\n"):
        raise AssertionError("Minute selection or unchanged-byte check failed")
    summary = describe(rows, start)
    if summary["context_tokens"]["mean"] != 15 or sum(summary["arrivals_per_second"]) != 2:
        raise AssertionError("Summary check failed")
    try:
        first_minute(sample)
    except ValueError:
        pass
    else:
        raise AssertionError("Unestablished right boundary should be rejected")
    try:
        parse_rows(tiny.split(b"2024-05-10 00:01:00")[0].replace(
            b"2024-05-10 00:00:00", b"2024-05-10 00:00:59.5"
        ))
    except ValueError:
        pass
    else:
        raise AssertionError("Nonchronological records should be rejected")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="Refresh bounded public-data sample")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--directory", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    if args.self_test:
        self_test()
    if args.fetch:
        acquire(args.directory)
    print(json.dumps(offline_summary(args.directory), indent=2))


if __name__ == "__main__":
    main()
