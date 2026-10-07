#!/usr/bin/env python3
"""Replay the six-hour campaign's bounded exact checks from any checkout.

Standard library only. Run from any directory. Each verifier runs in a separate
optimized Python process, preserving repository-relative dependencies. Results
include actual commands, source/dependency hashes, and unabridged outputs.
This is finite computational corroboration, not formal proof verification.
"""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


NAMES = (
    "aggregate_envelope", "balanced_shapley", "bernoulli", "binary_packing",
    "common_clip", "concave_production", "core_projection", "cut_height", "frozen",
    "general_production", "hybrid", "linear_envelope", "one_sided", "owner_count_lower",
    "personal_ceiling", "pointwise", "potential", "profile_certificate",
    "resource_dimension", "sampling", "scale_envelope", "seed_certificate",
    "sensitivity", "shapley", "simple_dag_lower", "uniform_mixture",
)


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        help="Also save the complete JSON record to this file")
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent
    root = directory.parents[2]
    campaign = directory.parent
    relative = directory.relative_to(root)
    dependencies = (
        root / "research_campaigns/2026-10-06-monotone-envelope/verification/verify.py",
        root / "research_campaigns/2026-10-06-series-parallel/verification/verify.py",
        campaign / "discovery/network_profile_lp.json",
        root / "paper5/truthful_cooperation/verification/sharp/verify.py",
        root / "paper5/truthful_cooperation/verification/sharp/poisson_certificate.py",
    )
    sources = tuple(directory / (name + ".py") for name in NAMES)
    for path in sources + dependencies:
        require(path.is_file(), "Missing portable verification input: " + str(path))
    for path in sources + tuple(p for p in dependencies if p.suffix == ".py"):
        require(not any(isinstance(node, ast.Assert)
                        for node in ast.walk(ast.parse(path.read_text()))),
                "Optimization-disabled assertion remains: " + str(path))
    hashes = {str(path.relative_to(root)): digest(path)
              for path in sources + dependencies + (Path(__file__).resolve(),)}
    records = []
    started = datetime.now(timezone.utc).isoformat()
    for name in NAMES:
        command = [sys.executable, "-B", "-O", str(relative / (name + ".py"))]
        if name == "profile_certificate":
            command.append(str((campaign / "discovery/network_profile_lp.json").relative_to(root)))
        before = time.monotonic()
        try:
            result = subprocess.run(command, cwd=root, text=True, capture_output=True,
                                    timeout=600)
        except subprocess.TimeoutExpired as error:
            def decoded(value):
                return value.decode(errors="replace") if isinstance(value, bytes) else value or ""
            result = subprocess.CompletedProcess(command, 124, decoded(error.stdout),
                        decoded(error.stderr) + "\nVerifier exceeded its 600-second ceiling.")
        success_marker = ("PASS" in result.stdout or
                          "All exact subset, permutation, tie-correction, and record checks passed."
                          in result.stdout)
        record = dict(verifier=name, command=command,
                      working_directory="repository root", exit_code=result.returncode,
                      seconds=round(time.monotonic()-before, 3),
                      status="PASS" if result.returncode == 0 and success_marker else "FAIL",
                      stdout=result.stdout, stderr=result.stderr)
        records.append(record)
        print(name + ": " + record["status"], file=sys.stderr, flush=True)
        # Preserve a complete failure record rather than silently skipping it.
        if record["status"] != "PASS":
            break
    status = "PASS" if len(records) == len(NAMES) and all(r["status"] == "PASS" for r in records) else "FAIL"
    result = dict(status=status, started_utc=started,
                  finished_utc=datetime.now(timezone.utc).isoformat(),
                  python_version=sys.version, expected_verifiers=len(NAMES),
                  completed_verifiers=len(records), optimization="-B -O; no asserts in checked code",
                  sha256=hashes, runs=records,
                  scope="Bounded exact checks and negative controls only; universal/asymptotic claims require the accompanying proofs.")
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
