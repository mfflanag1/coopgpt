"""Bounded local execution of the frozen Mac calibration; no network or serving."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_freeze(binary):
    path = ROOT / "DESIGN_FREEZE.json"
    data = path.read_bytes()
    freeze = json.loads(data)
    for name, expected in freeze["source_sha256"].items():
        if digest(ROOT / name) != expected:
            raise ValueError("Frozen source changed: " + name)
    if digest(binary) != freeze["binary_sha256"]:
        raise ValueError("Calibration binary does not match freeze")
    return hashlib.sha256(data).hexdigest()


def diagnostic(kind):
    command = ["/usr/bin/pmset", "-g", kind]
    try:
        p = subprocess.run(command, capture_output=True, text=True, timeout=10,
                           shell=False, check=False)
        return {"command": command, "returncode": p.returncode,
                "stdout": p.stdout, "stderr": p.stderr}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": command, "status": "unavailable", "error_type": type(exc).__name__}


def run(binary, output):
    frozen = verify_freeze(binary)
    output.mkdir(parents=False, exist_ok=False)
    from capture_inventory import capture
    inventory = capture("mac-local")
    (output / "INVENTORY.json").write_text(json.dumps(inventory, indent=2, allow_nan=False) + "\n")
    before = {kind: diagnostic(kind) for kind in ("batt", "therm")}
    start = datetime.now(timezone.utc).isoformat()
    tick = time.monotonic()
    command = [str(binary), "--output", str(output / "RAW.json")]
    metadata = {"command": command, "started_utc": start, "timeout_seconds": 120,
                "before": before, "freeze_sha256": frozen, "source_changed": False}
    try:
        p = subprocess.run(command, capture_output=True, text=True, timeout=120,
                           shell=False, check=False)
        metadata.update(returncode=p.returncode, process_status="completed")
        stdout, stderr = p.stdout, p.stderr
    except subprocess.TimeoutExpired as exc:
        metadata.update(returncode=None, process_status="timed_out")
        stdout, stderr = exc.stdout or b"", exc.stderr or b""
    except OSError as exc:
        metadata.update(returncode=None, process_status="launch_failed", error_type=type(exc).__name__)
        stdout, stderr = "", ""
    metadata.update(finished_utc=datetime.now(timezone.utc).isoformat(),
                    process_elapsed_seconds=time.monotonic() - tick,
                    after={kind: diagnostic(kind) for kind in ("batt", "therm")})
    for name, value in (("STDOUT.txt", stdout), ("STDERR.txt", stderr)):
        (output / name).write_bytes(value if isinstance(value, bytes) else value.encode())
    try:
        if verify_freeze(binary) != frozen:
            metadata["source_changed"] = True
    except (ValueError, OSError, KeyError):
        metadata["source_changed"] = True
    metadata["raw_output_present"] = (output / "RAW.json").is_file()
    metadata["interpretation"] = "Process completion is not correctness approval; independently validate RAW.json against WORKLOAD.json."
    (output / "EXECUTION.json").write_text(json.dumps(metadata, indent=2, allow_nan=False) + "\n")
    return metadata["returncode"] == 0 and not metadata["source_changed"] and metadata["raw_output_present"]


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--binary", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path, help="New directory")
    a = p.parse_args()
    ok = run(a.binary.resolve(), a.output.resolve())
    print(json.dumps({"capture_directory": str(a.output), "process_completed": ok}))
    raise SystemExit(0 if ok else 1)
