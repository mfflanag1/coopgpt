#!/usr/bin/env python3
"""Archive bounded public documentation only; never downloads telemetry.

Every response body is counted and hashed. Dataset-byte ledger remains zero.
No authentication, cookies, credentials, external executables, or dependencies.
"""
import datetime as dt
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
SOURCES = [
    ("author_readme.md", "https://raw.githubusercontent.com/at-aaims/summit_power_and_thermal_data/main/README.md"),
    ("official_record.html", "https://doi.ccs.ornl.gov/dataset/086578e9-8a9f-56b1-a657-0ed8b7393deb"),
    ("repository_commit.json", "https://api.github.com/repos/at-aaims/summit_power_and_thermal_data/commits/main"),
]
MAX_BODY = 1_000_000


def main():
    out = ROOT / "metadata"
    out.mkdir(exist_ok=True)
    log = ROOT / "metadata_requests.jsonl"
    for name, url in SOURCES:
        record = {"utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                  "url": url, "kind": "documentation", "dataset_bytes": 0,
                  "body_bytes": 0, "body_limit": MAX_BODY}
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "ResearchMetadataAudit/1.0", "Accept-Encoding": "identity"})
            with urllib.request.urlopen(request, timeout=30) as response:
                record.update(status=response.status, final_url=response.url,
                              content_type=response.headers.get("Content-Type"),
                              content_length=response.headers.get("Content-Length"),
                              etag=response.headers.get("ETag"))
                body = response.read(MAX_BODY)
                record["body_bytes"] = len(body)
                record["sha256"] = hashlib.sha256(body).hexdigest()
                record["at_limit"] = len(body) == MAX_BODY
                (out / name).write_bytes(body)
                record["saved_path"] = str((out / name).relative_to(ROOT))
        except (urllib.error.URLError, TimeoutError) as error:
            record["error"] = str(error)
        with log.open("a") as stream:
            stream.write(json.dumps(record, sort_keys=True) + "\n")
        print(json.dumps(record, sort_keys=True))


if __name__ == "__main__":
    main()
