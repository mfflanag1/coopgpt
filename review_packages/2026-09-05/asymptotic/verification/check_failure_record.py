#!/usr/bin/env python3
"""Fast negative control for stale result files; no scientific cases are run."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


CHILD = r'''
import importlib.util
import json
from pathlib import Path
import sys
runner, output = Path(sys.argv[1]), Path(sys.argv[2])
spec = importlib.util.spec_from_file_location("tested_runner", runner)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
def fail_after_running(*args):
    if json.loads(output.read_text()).get("status") != "RUNNING":
        raise RuntimeError("old PASS was not replaced before checks")
    raise RuntimeError("injected failure after RUNNING")
module.check_case = fail_after_running
sys.argv = [str(runner), "--output", str(output)]
module.main()
'''


def main():
    here = Path(__file__).resolve().parent
    records = []
    with tempfile.TemporaryDirectory() as temporary:
        for flags in ([], ["-O"]):
            output = Path(temporary) / "result.json"
            output.write_text(json.dumps({"status": "PASS", "old_record": True}))
            result = subprocess.run(
                [sys.executable, *flags, "-c", CHILD,
                 str(here / "run_checks.py"), str(output)],
                text=True, capture_output=True, timeout=30,
            )
            payload = json.loads(output.read_text())
            if result.returncode == 0 or payload.get("status") != "FAIL":
                raise RuntimeError("injected failure left a successful record or exit status")
            if payload.get("error", {}).get("message") != "injected failure after RUNNING":
                raise RuntimeError("failure did not occur after the RUNNING transition")
            if payload.get("old_record") or result.stdout:
                raise RuntimeError("old result or scientific success output survived")
            records.append({"flags": flags, "exit_code": result.returncode,
                            "old_pass_replaced_before_checks": True,
                            "final_status": payload["status"]})
    destination = here / "results" / "failure_record_control.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps({"status": "PASS", "controls": records}, indent=2) + "\n")
    print("PASS: injected failure replaces old PASS with RUNNING then FAIL, normally and under -O")


if __name__ == "__main__":
    main()
