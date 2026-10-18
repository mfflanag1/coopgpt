#!/usr/bin/env python3
"""Fetch only three Parquet footers and inspect safe structural metadata.

Uses existing DuckDB 1.4.1; installs nothing. Synthetic sparse Parquet wrappers
contain magic/footer bytes and zero holes, never data pages. Never SELECT rows
from read_parquet: only parquet_schema/parquet_metadata are permitted here.
Power/state column statistics are neither selected nor emitted. Only timestamp
min/max metadata may be emitted for chronological feasibility, not outcome fit.
"""
from pathlib import Path
import datetime as dt
import hashlib
import json
import struct
import time
import urllib.request
import duckdb

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "m100_may_footers"
PREV = ROOT / "m100_may_metadata"
LIMIT = 100_000_000


def main():
    if OUT.exists():
        raise RuntimeError("Refusing to overwrite a prior footer intake")
    OUT.mkdir()
    prior = json.loads((PREV / "report.json").read_text())
    prior_bytes = prior["dataset_bytes_read"]
    used = 0
    last = 0.0
    summaries = []
    status = "STOPPED"
    error = None
    url, total = prior["source"], prior["archive_bytes"]

    def fetch(start, length):
        nonlocal used, last
        if length <= 0 or prior_bytes + used + length > LIMIT:
            raise RuntimeError("Cumulative dataset-byte cap reached")
        time.sleep(max(0, 0.8 - (time.monotonic() - last)))
        end = start + length - 1
        rec = {"utc": dt.datetime.now(dt.timezone.utc).isoformat(), "url": url,
               "start": start, "length": length, "body_bytes": 0,
               "kind": "dataset_footer_metadata"}
        try:
            req = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}",
                "Accept-Encoding": "identity", "User-Agent": "CoopGPT-public-footer-gate/1.0"})
            with urllib.request.urlopen(req, timeout=30) as response:
                rec.update(status=response.status, content_range=response.headers.get("Content-Range"),
                           content_length=response.headers.get("Content-Length"))
                if response.status != 206 or rec["content_range"] != f"bytes {start}-{end}/{total}":
                    raise RuntimeError("Unexpected range response; body not read")
                body = response.read(length)
                used += len(body)
                rec["body_bytes"] = len(body)
                rec["sha256"] = hashlib.sha256(body).hexdigest()
                (OUT / f"range_{start}_{length}.bin").write_bytes(body)
                if len(body) != length:
                    raise RuntimeError("Incomplete range")
                return body
        except Exception as exc:
            rec["error"] = type(exc).__name__ + ": " + str(exc)
            raise
        finally:
            last = time.monotonic()
            with (OUT / "requests.jsonl").open("a") as stream:
                stream.write(json.dumps(rec, sort_keys=True) + "\n")

    con = duckdb.connect(config={"autoinstall_known_extensions": "false",
                                 "autoload_known_extensions": "false", "threads": "1"})
    try:
        wanted = [r for r in prior["selected_members"]
                  if "/metric=total_power/" not in r["name"]]
        assert len(wanted) == 3
        for member in wanted:
            metric = member["name"].split("/metric=", 1)[1].split("/", 1)[0]
            start, size = member["offset"], member["size"]
            magic = fetch(start, 4)
            tail = fetch(start + size - 8, 8)
            if magic != b"PAR1" or tail[4:] != b"PAR1":
                raise RuntimeError("Unsupported Parquet magic")
            footer_size = struct.unpack("<I", tail[:4])[0]
            if not 0 < footer_size < min(2_000_000, size - 12):
                raise RuntimeError("Footer size outside bounded metadata gate")
            footer = fetch(start + size - 8 - footer_size, footer_size)
            wrapper = OUT / (metric + "_FOOTER_ONLY_SPARSE.parquet")
            with wrapper.open("wb") as stream:
                stream.write(magic)
                stream.seek(size - 8 - footer_size)
                stream.write(footer)
                stream.write(tail)
            schema = con.execute("SELECT name, type, repetition_type, logical_type, converted_type FROM parquet_schema(?)", [str(wrapper)]).fetchall()
            # Select only structural columns. No power/state min/max/null counts.
            cols = con.execute("SELECT row_group_id, row_group_num_rows, path_in_schema, type, total_compressed_size, data_page_offset, dictionary_page_offset FROM parquet_metadata(?)", [str(wrapper)]).fetchall()
            times = con.execute("SELECT row_group_id, stats_min_value, stats_max_value FROM parquet_metadata(?) WHERE path_in_schema='timestamp'", [str(wrapper)]).fetchall()
            row = {"name": member["name"], "metric": metric, "member_size": size,
                   "footer_size": footer_size, "footer_sha256": hashlib.sha256(footer).hexdigest(),
                   "schema_columns": ["name", "physical_type", "repetition_type", "logical_type", "converted_type"],
                   "schema": schema,
                   "chunk_columns": ["row_group_id", "row_group_num_rows", "path_in_schema", "physical_type", "total_compressed_size", "data_page_offset", "dictionary_page_offset"],
                   "chunks": cols, "timestamp_range_columns": ["row_group_id", "minimum", "maximum"],
                   "timestamp_ranges": times,
                   "wrapper_note": "Zero-filled sparse file; not a telemetry file; must never be analyzed as values"}
            summaries.append(row)
            print(json.dumps({"metric": metric, "footer_size": footer_size,
                              "row_groups": len({r[0] for r in cols}),
                              "timestamp_min": min(r[1] for r in times),
                              "timestamp_max": max(r[2] for r in times)}, default=str), flush=True)
        status = "COMPLETE_METADATA_ONLY"
    except Exception as exc:
        error = type(exc).__name__ + ": " + str(exc)
    finally:
        con.close()
        report = {"utc": dt.datetime.now(dt.timezone.utc).isoformat(), "status": status,
                  "error": error, "source": url, "duckdb_version": duckdb.__version__,
                  "prior_dataset_bytes": prior_bytes, "footer_dataset_bytes": used,
                  "cumulative_dataset_bytes": prior_bytes + used, "cap_bytes": LIMIT,
                  "power_state_payload_values_read": 0, "members": summaries,
                  "scope": "No data pages fetched. Power/state statistics not selected or printed. Timestamp ranges are metadata only."}
        (OUT / "report.json").write_text(json.dumps(report, indent=2, default=str) + "\n")
        print(json.dumps({k:v for k,v in report.items() if k != "members"}), flush=True)


if __name__ == "__main__":
    main()
