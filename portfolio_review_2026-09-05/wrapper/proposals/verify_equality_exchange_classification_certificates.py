#!/usr/bin/env python3
"""Check frozen proof-record integrity and complete case coverage.

These ordinary guards remain active under Python -O. This wrapper checks
record consistency; it does not rerun the external CPC proof checker.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTIFICATES = HERE / "certificates"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


EXPECTED_CASES = {
    f"p{positive}_n{negative}_t{6-positive-negative}"
    for positive in range(1, 6)
    for negative in range(1, 7-positive)
}


def complete_rows(audit, expected, label):
    require(audit.get("status") == "PASS", f"{label}: status is not PASS")
    rows = audit.get("rows")
    require(isinstance(rows, list), f"{label}: rows must be a list")
    require(len(rows) == len(expected), f"{label}: actual row count changed")
    require(all(isinstance(row, dict) and isinstance(row.get("case"), str) for row in rows), f"{label}: invalid case row")
    cases = [row["case"] for row in rows]
    require(len(set(cases)) == len(cases), f"{label}: duplicate case")
    require(set(cases) == set(expected), f"{label}: missing or unexpected case")
    if "case_count" in audit:
        require(audit["case_count"] == len(rows), f"{label}: declared row count changed")
    return rows


def direction_rows(audit, schema, relation):
    require(audit.get("schema") == schema, "direction audit schema changed")
    require(audit.get("case_count") == 15, "direction audit case count changed")
    require(audit.get("distance_relation", "eq") == relation, "direction audit relation changed")
    rows = complete_rows(audit, EXPECTED_CASES, "direction audit")
    for row in rows:
        positive, negative, tied = row["positive_count"], row["negative_count"], row["tie_count"]
        require(all(type(v) is int for v in (positive, negative, tied)), "invalid role counts")
        require(positive >= 1 and negative >= 1 and tied >= 0 and positive+negative+tied == 6, "invalid six-player roles")
        require(row["case"] == f"p{positive}_n{negative}_t{tied}", "case label disagrees with roles")
        require(row.get("rebuilt_verdict") == "unsat", "direction rebuild is not UNSAT")
        require(row.get("distance_relation", "eq") == relation, "row distance relation changed")
        menu = row.get("retained_menu")
        require(isinstance(menu, list), "missing retained menu")
        require(row.get("retained_direction_count") == len(menu), "retained direction count disagrees with menu")
        signatures = []
        for item in menu:
            direction = item.get("direction")
            require(item.get("side") in ("min", "max"), "invalid menu side")
            require(isinstance(direction, list) and len(direction) == 6, "invalid direction length")
            require(all(type(v) is int for v in direction) and any(direction) and sum(direction) == 0, "invalid transfer direction")
            signatures.append((item["side"], tuple(direction)))
        require(len(set(signatures)) == len(signatures), "duplicate retained direction")
    return rows


def proof_record(record, formula, proof):
    require(record.get("status") == "PASS", "record status is not PASS")
    for solver in ("z3", "cvc5"):
        require(record[solver].get("status") == "unsat", f"{solver}: recorded status is not UNSAT")
        require(record[solver].get("exit_code") == 0, f"{solver}: recorded nonzero exit")
    require(record.get("formula_sha256") == sha256(formula), "formula hash mismatch")
    require(record.get("formula_bytes") == formula.stat().st_size, "formula byte count mismatch")
    cpc = record["cpc_proof"]
    require(cpc.get("status") == "PASS", "CPC status is not PASS")
    require(cpc["ethos"].get("status") == "correct" and cpc["ethos"].get("exit_code") == 0, "Ethos record is not correct")
    require(cpc.get("forbidden_markers") == [], "CPC record contains forbidden markers")
    require(cpc.get("proof_sha256") == sha256(proof), "proof hash mismatch")
    require(cpc.get("proof_bytes") == proof.stat().st_size, "proof byte count mismatch")
    return cpc


def main():
    audit = json.loads((HERE / "equality_exchange_direction_cores.json").read_text())
    rows = direction_rows(audit, "equality-exchange-direction-cores-v1", "eq")
    checked = []
    for row in rows:
        stem = f"equality_exchange_{row['case']}"
        formula = CERTIFICATES / f"{stem}.smt2"
        proof = CERTIFICATES / f"{stem}.cpc"
        record = json.loads((CERTIFICATES / f"{stem}.json").read_text())
        cpc = proof_record(record, formula, proof)
        checked.append({
            "case": row["case"],
            "directions": row["retained_direction_count"],
            "proof_bytes": cpc["proof_bytes"],
            "formula_sha256": record["formula_sha256"],
            "proof_sha256": cpc["proof_sha256"],
        })
    print(json.dumps({"status": "PASS", "checked": checked}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
