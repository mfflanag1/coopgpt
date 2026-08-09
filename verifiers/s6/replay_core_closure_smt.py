#!/usr/bin/env python3
"""Replay one frozen six-player QF_LRA query with Z3 and cvc5.

This is an independent-solver cross-check, not a rational Farkas certificate.
The JSON record binds both verdicts to the exact SMT-LIB bytes by SHA-256.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
import time
from pathlib import Path


def first_line(text: str) -> str:
    return next((line.strip().lower() for line in text.splitlines() if line.strip()), "")


def run(command: list[str], timeout: int) -> dict:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        output = completed.stdout.strip()
        return {
            "command": command,
            "elapsed_seconds": round(time.monotonic() - started, 6),
            "exit_code": completed.returncode,
            "output": output,
            "status": first_line(output),
        }
    except subprocess.TimeoutExpired as error:
        output = error.stdout if isinstance(error.stdout, str) else ""
        return {
            "command": command,
            "elapsed_seconds": round(time.monotonic() - started, 6),
            "exit_code": None,
            "output": output.strip(),
            "status": "external_timeout",
        }


def version(command: list[str]) -> str:
    return first_line(
        subprocess.run(
            command,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ).stdout
    )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--formula", type=Path, required=True)
    parser.add_argument("--z3", type=Path, required=True)
    parser.add_argument("--cvc5", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cpc-proof", type=Path)
    parser.add_argument("--ethos", type=Path)
    parser.add_argument("--cpc-signatures", type=Path)
    args = parser.parse_args()
    proof_options = (args.cpc_proof, args.ethos, args.cpc_signatures)
    if any(proof_options) and not all(proof_options):
        parser.error("--cpc-proof, --ethos, and --cpc-signatures must be used together")

    formula = args.formula.resolve()
    z3_path = args.z3.resolve()
    cvc5_path = args.cvc5.resolve()
    z3_record = run(
        [str(z3_path), f"-T:{args.timeout_seconds}", str(formula)],
        args.timeout_seconds + 60,
    )
    cvc5_record = run(
        [
            str(cvc5_path),
            "--strict-parsing",
            f"--tlimit={args.timeout_seconds * 1000}",
            str(formula),
        ],
        args.timeout_seconds + 60,
    )
    agreed = z3_record["status"] == cvc5_record["status"]
    decisive = z3_record["status"] in {"sat", "unsat"}
    payload = {
        "schema": "s6-generator-qf-lra-dual-replay-v1",
        "status": "PASS" if agreed and decisive else "FAIL",
        "scope": "independent-solver cross-check; not a rational infeasibility certificate",
        "formula": str(formula),
        "formula_bytes": formula.stat().st_size,
        "formula_sha256": hashlib.sha256(formula.read_bytes()).hexdigest(),
        "z3_version": version([str(z3_path), "--version"]),
        "cvc5_version": version([str(cvc5_path), "--version"]),
        "z3_binary_sha256": sha256_file(z3_path),
        "cvc5_binary_sha256": sha256_file(cvc5_path),
        "z3": z3_record,
        "cvc5": cvc5_record,
    }
    if all(proof_options):
        proof_run = run(
            [
                str(cvc5_path),
                "--strict-parsing",
                "--produce-proofs",
                "--proof-pedantic=1",
                "--no-proof-allow-trust",
                "--dump-proofs",
                f"--tlimit={args.timeout_seconds * 1000}",
                str(formula),
            ],
            args.timeout_seconds + 60,
        )
        proof_lines = proof_run["output"].splitlines()
        if (
            proof_run["status"] != "unsat"
            or len(proof_lines) < 4
            or proof_lines[1].strip() != "("
            or proof_lines[-1].strip() != ")"
        ):
            raise RuntimeError("cvc5 did not emit the expected CPC proof envelope")
        signatures = args.cpc_signatures.resolve()
        proof_body = "\n".join(proof_lines[2:-1]) + "\n"
        forbidden_markers = tuple(
            marker
            for marker in ("trust", "hole", "warning")
            if marker in proof_body.lower()
        )
        if forbidden_markers:
            raise RuntimeError(f"CPC proof contains forbidden markers: {forbidden_markers}")
        args.cpc_proof.write_text(proof_body)
        proof_text = (
            f'(include "{signatures / "Cpc.eo"}")\n'
            f'(include "{signatures / "expert" / "CpcExpert.eo"}")\n'
            + proof_body
        )
        with tempfile.TemporaryDirectory(prefix="s6-ethos-") as temporary:
            wrapper = Path(temporary) / "proof-with-signatures.cpc"
            wrapper.write_text(proof_text)
            ethos_record = run(
                [str(args.ethos.resolve()), str(wrapper)],
                args.timeout_seconds + 60,
            )
        proof_ok = ethos_record["exit_code"] == 0 and ethos_record["status"] == "correct"
        payload["cpc_proof"] = {
            "status": "PASS" if proof_ok else "FAIL",
            "proof": str(args.cpc_proof.resolve()),
            "proof_bytes": args.cpc_proof.stat().st_size,
            "proof_sha256": hashlib.sha256(args.cpc_proof.read_bytes()).hexdigest(),
            "forbidden_markers": list(forbidden_markers),
            "ethos_binary_sha256": sha256_file(args.ethos.resolve()),
            "cpc_signatures_sha256": sha256_tree(signatures),
            "cvc5_generation": {
                key: value for key, value in proof_run.items() if key != "output"
            },
            "ethos": ethos_record,
            "scope": "independently checked exact CPC proof",
        }
        if not proof_ok:
            payload["status"] = "FAIL"
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
