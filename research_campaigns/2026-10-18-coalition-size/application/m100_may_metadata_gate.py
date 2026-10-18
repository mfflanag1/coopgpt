#!/usr/bin/env python3
"""Inspect May M100 archive headers only; never read Parquet value payloads.

Adapted from the previously reviewed April range intake. Unlike that script,
there is no read-ahead cache and no member download: every tar header fetch is
exactly 512 bytes. GNU long-name records are metadata and explicitly counted.
The month is fixed chronologically before any May outcomes are inspected.
"""
from pathlib import Path
import datetime as dt
import hashlib
import json
import re
import tarfile
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "m100_may_metadata"
API = "https://zenodo.org/api/records/7588815"
URL = "https://zenodo.org/records/7588815/files/20-05.tar?download=1"
LIMIT = 100_000_000
REQUEST_LIMIT = 500
TARGETS = {("ipmi_pub", "ps0_input_power"), ("ipmi_pub", "ps1_input_power"),
           ("ipmi_pub", "total_power"), ("nagios_pub", "state")}


def main():
    if OUT.exists():
        raise RuntimeError("Refusing to overwrite a prior intake; inspect its ledger first")
    OUT.mkdir()
    used = 0
    count = 0
    last = 0.0
    total = None
    entries = []
    offset = 0
    pending_name = None
    status = "STOPPED"
    error = None

    def journal(record):
        with (OUT / "requests.jsonl").open("a") as stream:
            stream.write(json.dumps(record, sort_keys=True) + "\n")

    def fetch(start, length):
        nonlocal used, count, last
        if length <= 0 or used + length > LIMIT or count >= REQUEST_LIMIT:
            raise RuntimeError("Metadata range budget reached")
        time.sleep(max(0, 0.8 - (time.monotonic() - last)))
        end = start + length - 1
        request = urllib.request.Request(URL, headers={"Range": f"bytes={start}-{end}",
            "Accept-Encoding": "identity", "User-Agent": "CoopGPT-public-metadata-gate/1.0"})
        record = {"utc": dt.datetime.now(dt.timezone.utc).isoformat(), "url": URL,
                  "start": start, "length": length, "body_bytes": 0,
                  "kind": "dataset_archive_metadata", "request_number": count + 1}
        count += 1
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                record.update(status=response.status, content_range=response.headers.get("Content-Range"),
                              content_length=response.headers.get("Content-Length"))
                if response.status != 206:
                    raise RuntimeError(f"Range not honored ({response.status}); body not read")
                if record["content_range"] != f"bytes {start}-{end}/{total}":
                    raise RuntimeError("Unexpected Content-Range; body not read")
                body = response.read(length)
                record["body_bytes"] = len(body)
                used += len(body)
                record["sha256"] = hashlib.sha256(body).hexdigest()
                (OUT / f"range_{start}_{length}.bin").write_bytes(body)
                if len(body) != length:
                    raise RuntimeError("Incomplete range body")
                return body
        except Exception as exc:
            record["error"] = type(exc).__name__ + ": " + str(exc)
            raise
        finally:
            last = time.monotonic()
            journal(record)

    try:
        request = urllib.request.Request(API, headers={"Accept-Encoding": "identity",
            "User-Agent": "CoopGPT-public-metadata-gate/1.0"})
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read(200_000)
            (OUT / "zenodo_record.json").write_bytes(body)
            journal({"utc": dt.datetime.now(dt.timezone.utc).isoformat(), "url": API,
                     "kind": "documentation", "status": response.status, "body_bytes": len(body),
                     "sha256": hashlib.sha256(body).hexdigest(), "dataset_bytes": 0})
        source = json.loads(body)
        file_record = next(f for f in source["files"] if f["key"] == "20-05.tar")
        total = file_record["size"]
        print(json.dumps({"archive_bytes": total, "source_file": file_record}), flush=True)
        while offset + 512 <= total:
            header = fetch(offset, 512)
            if not any(header):
                status = "COMPLETE_TO_FIRST_END_MARKER"
                break
            ti = tarfile.TarInfo.frombuf(header, "utf-8", "surrogateescape")
            data_at = offset + 512
            if ti.type == tarfile.GNUTYPE_LONGNAME:
                if ti.size > 16384:
                    raise RuntimeError("Unexpected long-name metadata over 16KB")
                pending_name = fetch(data_at, ti.size).rstrip(b"\x00").decode("utf-8")
            elif ti.type in (tarfile.XHDTYPE, tarfile.XGLTYPE):
                raise RuntimeError("PAX metadata needs an explicit parser; stop")
            else:
                name = pending_name or ti.name
                pending_name = None
                match = re.search(r"/plugin=([^/]+)/metric=([^/]+)/", name)
                selected = bool(ti.isfile() and match and tuple(match.groups()) in TARGETS and name.endswith(".parquet"))
                row = {"name": name, "size": ti.size, "offset": data_at,
                       "type": ti.type.decode("ascii", "replace"), "selected": selected}
                entries.append(row)
                if selected:
                    print(json.dumps({"target_member_metadata": row}), flush=True)
            offset = data_at + ((ti.size + 511) // 512) * 512
        else:
            status = "NO_END_MARKER"
    except Exception as exc:
        error = type(exc).__name__ + ": " + str(exc)
    finally:
        selected = [r for r in entries if r["selected"]]
        report = {"utc": dt.datetime.now(dt.timezone.utc).isoformat(), "status": status,
                  "error": error, "source": URL, "archive_bytes": total,
                  "dataset_bytes_read": used, "dataset_payload_values_read": 0,
                  "range_requests": count, "request_cap": REQUEST_LIMIT,
                  "aggregate_dataset_byte_cap": LIMIT, "next_offset": offset,
                  "entries": entries, "selected_members": selected,
                  "selected_member_total_bytes": sum(r["size"] for r in selected),
                  "scope": "Tar metadata only. No Parquet footer or telemetry values inspected."}
        (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({k: v for k, v in report.items() if k not in ("entries", "selected_members")}), flush=True)


if __name__ == "__main__":
    main()
