#!/usr/bin/env python3
"""Replay exact diagnostics for the final envelope obstruction; stdlib only.

The all-Q theorem rests on the written proof. These finite checks do not
enumerate the final cover or the enormous rational transport network.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
SCRIPTS = (
    "proofs/activation_qary_cube_check.py",
    "checks/mass_search_qary_cube_audit.py",
    "checks/mass_geometry_qary_verify.py",
    "proofs/activation_qary_direct_check.py",
    "checks/mass_search_true_envelope_upper.py",
)


def main():
    logs = ROOT / "replay-logs"
    logs.mkdir(exist_ok=True)
    results = []
    for relative in SCRIPTS:
        path = ROOT / relative
        started = time.monotonic()
        proc = subprocess.run(
            [sys.executable, str(path)], cwd=ROOT, text=True,
            capture_output=True, timeout=180, check=False,
        )
        log = logs / (path.stem + ".txt")
        log.write_text(proc.stdout + ("\nSTDERR:\n" + proc.stderr if proc.stderr else ""))
        result = {
            "script": relative,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "returncode": proc.returncode,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "log": str(log.relative_to(ROOT)),
        }
        results.append(result)
        print(("PASS " if proc.returncode == 0 else "FAIL ") + relative, flush=True)
        if proc.returncode != 0:
            break
    success = len(results) == len(SCRIPTS) and all(r["returncode"] == 0 for r in results)
    report = {
        "status": "PASS" if success else "FAIL",
        "python": sys.version,
        "scope": "Exact finite diagnostics; general theorem requires the written all-Q proof.",
        "results": results,
    }
    (ROOT / "REPLAY_RESULTS.json").write_text(json.dumps(report, indent=2) + "\n")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
