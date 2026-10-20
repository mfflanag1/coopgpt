"""Replay the gate's exact finite checks; Python standard library only.

This does not prove the notes' continuous or unbounded quantifiers and does
not rerun the exploratory floating-point optimizations.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
CHECKS = [
    ("scalar_price_lift", "price_lift_route", "check_price_lift.py", []),
    ("min_production_repairs", "price_lift_route", "additive_followup.py", []),
    ("positive_defect_diagnostic", "certificate_route", "check_positive_defects.py", []),
    ("frozen_background", "certificate_route", "signed_followup.py", []),
    ("balanced_two_terminal", "certificate_route", "layer_followup.py", []),
    ("single_terminal_boundaries", "certificate_route", "single_terminal_followup.py", []),
    ("capped_fractional_stop", "root", "check_capped_fractional.py", []),
    ("finite_lower_certificates", "finite_diagnostics", "check_certificate.py",
     ["case_48_certificate.json", "case_27_certificate.json", "case_35_certificate.json"]),
    ("finite_price_reselection", "finite_diagnostics", "check_reselection.py", []),
    ("optimal_price_normalization", "price_selection_diagnostic", "verify_exact.py", []),
    ("budget_adapted_prices", "budget_price_relaxation", "verify_exact.py", []),
    ("local_null_normalization", "root", "check_local_normalization.py", []),
]


def main():
    records = []
    for name, directory, script, arguments in CHECKS:
        completed = subprocess.run(
            [sys.executable, script, *arguments], cwd=ROOT / directory,
            text=True, capture_output=True, timeout=120, check=False,
        )
        record = {"name": name, "returncode": completed.returncode,
                  "command": [script, *arguments], "directory": directory}
        try:
            record["result"] = json.loads(completed.stdout)
        except json.JSONDecodeError:
            record["stdout"] = completed.stdout
        if completed.stderr:
            record["stderr"] = completed.stderr
        records.append(record)
        if completed.returncode:
            print(json.dumps({"status": "FAILED", "checks": records}, indent=2))
            return completed.returncode
    print(json.dumps({
        "status": "EXACT FINITE REPLAY PASSED",
        "utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "limits": "Finite certificates only; symbolic proofs and source priority require separate review.",
        "checks": records,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
