"""Single standard-library entry point: python3 verification/run_checks.py.

Writes verification/results/verification.json and verification.log; exits nonzero for
any failed check. No network, solver, or pip installation is needed.
"""
import ast
import contextlib
import copy
import hashlib
import io
import json
import platform
from pathlib import Path
import time
import sys
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent


def expect_failure(action, label):
    try:
        action()
    except (ValueError, KeyError):
        return label
    raise ValueError("negative control was wrongly accepted: " + label)


def _run_checks():
    # Load scientific dependencies only after main has invalidated old results.
    from data import require, parse_game, strict_json_load
    import verify_claims
    import verify_additive_ray
    import verify_stability

    started = time.monotonic()
    with (HERE / "supplement_data.json").open() as stream:
        data = strict_json_load(stream)
    # Coverage checks reject omissions even when the omitted value happens to be zero.
    table = copy.deepcopy(data["stable_witness_1"]["game_v"])
    zero_key = next(k for k,v in table.items() if v == "0")
    del table[zero_key]
    negative = [expect_failure(lambda: parse_game(table,6), "missing zero coalition")]
    negative.append(expect_failure(lambda: verify_stability.parse_game(table,6),
                                   "arrangement parser missing zero coalition"))
    negative.append(expect_failure(lambda: strict_json_load(io.StringIO('{"x":1,"x":2}')),
                                   "duplicate JSON key"))
    alias = copy.deepcopy(data["stable_witness_1"]["game_v"])
    alias["{2,1}"] = alias["{1,2}"]
    negative.append(expect_failure(lambda: parse_game(alias,6), "duplicate coalition alias"))
    bad = copy.deepcopy(data)
    bad["stable_witness_1"]["egalitarian_claims"][0] = "999"
    negative.append(expect_failure(lambda: verify_claims.verify(bad), "incorrect claim"))
    negative.append(expect_failure(lambda: require(False, "guard control"),
                                   "guard active under optimized Python"))
    for filename in HERE.glob("*.py"):
        require(not any(isinstance(node,ast.Assert) for node in ast.walk(ast.parse(filename.read_text()))),
                "an optimization-sensitive assert remains in " + filename.name)
    results = {"python":platform.python_version(), "optimization_level":sys.flags.optimize,
               "arithmetic":"fractions.Fraction",
               "negative_controls_rejected":negative,
               "claims_and_controls":verify_claims.verify(data)}
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        results["symbolic_ray"] = verify_additive_ray.main()
    print(log.getvalue().strip(), flush=True)
    results["stability"] = {}
    for name in ("stable_witness_1","stable_witness_2"):
        counts, parameters = verify_stability.verify_witness(name,data[name])
        results["stability"][name] = {"counts":counts,"domination_parameters":list(map(str,parameters))}
        line = name+": "+str(counts["bases"])+" bases; "+str(counts["outside_core"])+" outside-core vertices dominated."
        print(line,flush=True)
        log.write(line+'\n')
    results["input_sha256"] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted(HERE.iterdir()) if p.is_file()}
    results["elapsed_seconds"] = round(time.monotonic()-started,3)
    results["status"] = "PASS"
    audit = HERE / "results"
    audit.mkdir(exist_ok=True)
    (audit / "verification.json").write_text(json.dumps(results,indent=2)+'\n')
    log.write("PASS: all checks, symbolic parameter coverage, and negative controls.\n")
    (audit / "verification.log").write_text(log.getvalue())
    print("PASS: claims, all ray parameters, both arrangements, and six rejected negative controls.")


def main():
    results_dir = HERE / "results"
    results_dir.mkdir(exist_ok=True)
    result_path = results_dir / "verification.json"
    log_path = results_dir / "verification.log"
    attempt = {"status":"RUNNING", "started_utc":datetime.now(timezone.utc).isoformat(),
               "python":platform.python_version(), "optimization_level":sys.flags.optimize}
    # Invalidate a shipped or earlier PASS before scientific imports or checks.
    result_path.write_text(json.dumps(attempt,indent=2)+'\n')
    log_path.write_text("RUNNING: previous result invalidated.\n")
    try:
        _run_checks()
    except BaseException as error:
        attempt.update(status="FAIL", error_type=type(error).__name__, error=str(error))
        result_path.write_text(json.dumps(attempt,indent=2)+'\n')
        log_path.write_text("FAIL: "+type(error).__name__+": "+str(error)+'\n')
        raise


if __name__ == "__main__":
    main()
