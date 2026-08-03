"""Regenerate and byte-compare every committed four-player bridge artifact."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


if not __debug__:
    raise RuntimeError("run this exact verifier without Python -O")


ROOT = Path(__file__).resolve().parents[1]
CASES = (
    (
        "verify_n4_exact_lmin_pes_bridge.py",
        "n4_exact_lmin_pes_bridge.json",
    ),
    (
        "verify_n4_exact_lmin_pes_bridge_cores.py",
        "n4_exact_lmin_pes_bridge_cores.json",
    ),
    (
        "verify_n4_exact_lmin_pes_bridge_primal.py",
        "n4_exact_lmin_pes_bridge_primal.json",
    ),
    (
        "verify_n4_exact_lmin_pes_bridge_witnesses.py",
        "n4_exact_lmin_pes_bridge_witnesses.json",
    ),
)


def main():
    records = []
    with tempfile.TemporaryDirectory(prefix="n4-bridge-artifacts-") as directory:
        temporary = Path(directory)
        for script_name, artifact_name in CASES:
            generated = temporary / artifact_name
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "src" / script_name),
                    "--output",
                    str(generated),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    f"{script_name} failed:\n{completed.stderr}\n{completed.stdout}"
                )
            committed = ROOT / "results" / artifact_name
            if generated.read_bytes() != committed.read_bytes():
                raise RuntimeError(
                    f"{artifact_name} is stale; regenerate it with {script_name}"
                )
            if completed.stdout.encode() != generated.read_bytes():
                raise RuntimeError(
                    f"{script_name} stdout differs from its --output artifact"
                )
            records.append({
                "program": f"src/{script_name}",
                "artifact": f"results/{artifact_name}",
                "byte_identical": True,
            })
    print(json.dumps({
        "status": "all four bridge artifacts replay byte-identically",
        "records": records,
    }, indent=2))


if __name__ == "__main__":
    main()
