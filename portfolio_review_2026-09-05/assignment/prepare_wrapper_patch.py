from pathlib import Path
import shutil
import json
import difflib
SRC=Path('/Users/maxf/projects/economics-research/game-theory/coopgt-recovery/coopgames/verifiers/s6')
ROOT=Path(__file__).resolve().parent/'wrapper_patch'
WORK=ROOT/'worktree';PROPOSALS=ROOT/'proposals'
WORK.mkdir(parents=True,exist_ok=True);PROPOSALS.mkdir(exist_ok=True)
for f in SRC.iterdir():
    if f.is_file() and f.suffix in ('.py','.json'):
        shutil.copy2(f,WORK/f.name)
wrappers=['verify_strict_exchange_bound_certificates.py','verify_equality_exchange_classification_certificates.py','verify_strict_exchange_orbit_core_certificates.py']
for name in wrappers:shutil.copy2(SRC/name,WORK/('old_'+name))
for directory,prefix in [('certificates','strict_exchange_'),('certificates','equality_exchange_'),('orbit_core_certificates','strict_exchange_orbit_core_')]:
    (WORK/directory).mkdir(exist_ok=True)
    for f in (SRC/directory).glob(prefix+'*'):
        if f.suffix in ('.json','.smt2','.cpc'):shutil.copy2(f,WORK/directory/f.name)

COMMON='''def require(condition, message):
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
'''
for kind,name,schema in [
 ('strict','verify_strict_exchange_bound_certificates.py','exactness-exchange-direction-cores-v1'),
 ('equality','verify_equality_exchange_classification_certificates.py','equality-exchange-direction-cores-v1')]:
    relation='gt' if kind=='strict' else 'eq'
    audit_file='strict_exchange_direction_cores.json' if kind=='strict' else 'equality_exchange_direction_cores.json'
    text='''#!/usr/bin/env python3
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


'''+COMMON+f'''

def main():
    audit = json.loads((HERE / "{audit_file}").read_text())
    rows = direction_rows(audit, "{schema}", "{relation}")
    checked = []
    for row in rows:
        stem = f"{kind}_exchange_{{row['case']}}"
        formula = CERTIFICATES / f"{{stem}}.smt2"
        proof = CERTIFICATES / f"{{stem}}.cpc"
        record = json.loads((CERTIFICATES / f"{{stem}}.json").read_text())
        cpc = proof_record(record, formula, proof)
        checked.append({{
            "case": row["case"],
            "directions": row["retained_direction_count"],
            "proof_bytes": cpc["proof_bytes"],
            "formula_sha256": record["formula_sha256"],
            "proof_sha256": cpc["proof_sha256"],
        }})
    print(json.dumps({{"status": "PASS", "checked": checked}}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
'''
    (WORK/name).write_text(text)
name='verify_strict_exchange_orbit_core_certificates.py'
text='''#!/usr/bin/env python3
"""Regenerate three orbit-core formulas and validate complete proof records.

Ordinary guards remain active under Python -O. External CPC checking is
recorded evidence, not rerun by this record-integrity wrapper.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from audit_strict_exchange_large_case_orbit_cores import SELECTED, build_reduced, rendered_signature
from export_core_closure_smt import qf_lra_smt2

HERE = Path(__file__).resolve().parent
CERTIFICATES = HERE / "orbit_core_certificates"


'''+COMMON+'''

def main():
    audit = json.loads((HERE / "strict_exchange_large_case_orbit_cores.json").read_text())
    original = json.loads((HERE / "strict_exchange_direction_cores.json").read_text())
    original_rows = direction_rows(original, "exactness-exchange-direction-cores-v1", "gt")
    source_rows = {row["case"]: row for row in original_rows}
    orbit_audit = json.loads((HERE / "strict_exchange_sign_orbits.json").read_text())
    orbit_rows = complete_rows(orbit_audit, EXPECTED_CASES, "sign-orbit audit")
    orbit_counts = {row["case"]: row["sign_preserving_orbit_count"] for row in orbit_rows}
    require(audit.get("schema") == "strict-exchange-large-case-orbit-cores-v1", "orbit-core schema changed")
    rows = complete_rows(audit, set(SELECTED), "selected orbit audit")
    require(audit.get("base_assertion_count_per_case") == 71, "base assertion count changed")
    require(audit.get("original_role_orbit_count") == 44, "original role count changed")
    require(audit.get("selected_role_orbit_count") == 19, "selected role count changed")
    require(audit.get("selected_labeled_direction_count") == 136, "selected direction count changed")
    totals = {"original_labeled_direction_count": 0, "original_role_orbit_count": 0,
              "selected_labeled_direction_count": 0, "selected_role_orbit_count": 0}
    checked = []
    for row in rows:
        case = row["case"]
        source = dict(source_rows[case])
        source["sign_preserving_orbit_count"] = orbit_counts[case]
        solver, groups = build_reduced(source, SELECTED[case])
        expected_orbits = [rendered_signature(item) for item in SELECTED[case]]
        counts = {"original_labeled_direction_count": source["retained_direction_count"],
                  "original_role_orbit_count": len(groups),
                  "selected_role_orbit_count": len(SELECTED[case]),
                  "selected_labeled_direction_count": sum(len(groups[item]) for item in SELECTED[case])}
        require(row.get("selected_orbits") == expected_orbits, f"{case}: selected orbit list changed")
        require(row.get("unguarded_rebuild_verdict") == "unsat", f"{case}: rebuild record not UNSAT")
        require(len(solver.assertions()) == 71+counts["selected_labeled_direction_count"], f"{case}: rebuilt assertion count changed")
        for field, value in counts.items():
            require(row.get(field) == value, f"{case}: {field} disagrees with rebuilt data")
            totals[field] += value
        formula = CERTIFICATES / f"strict_exchange_orbit_core_{case}.smt2"
        require(row.get("formula") == formula.name, f"{case}: formula filename changed")
        require(formula.read_text() == qf_lra_smt2(solver), f"{case}: formula did not byte-regenerate")
        proof = CERTIFICATES / f"strict_exchange_orbit_core_{case}.cpc"
        record = json.loads((CERTIFICATES / f"strict_exchange_orbit_core_{case}.json").read_text())
        cpc = proof_record(record, formula, proof)
        ablations = row.get("single_orbit_ablations", [])
        require([item.get("removed") for item in ablations] == expected_orbits, f"{case}: incomplete orbit ablations")
        require(all(item.get("verdict") == "sat" for item in ablations), f"{case}: orbit ablation not SAT")
        anchors = row.get("single_cross_anchor_ablations", [])
        require([item.get("removed") for item in anchors] == ["lmax_top_cross", "lmin_bottom_cross"], f"{case}: incomplete anchor ablations")
        require(all(item.get("verdict") == "sat" for item in anchors), f"{case}: anchor ablation not SAT")
        sources = ["opposite", "q0", "q1", "q2", "q3"]
        if case != "p4_n2_t0": sources += ["q4", "q5"]
        require(row.get("blocker_comparison_sources") == sources, f"{case}: blocker source list changed")
        blockers = row.get("single_blocker_source_ablations", [])
        if case == "p4_n2_t0":
            require([item.get("removed") for item in blockers] == sources, f"{case}: incomplete blocker ablations")
            require(all(item.get("verdict") == "sat" for item in blockers), f"{case}: blocker ablation not SAT")
        else:
            require(blockers == [], f"{case}: unexpected blocker ablations")
        checked.append({"case": case,
                        "selected_role_orbits": row["selected_role_orbit_count"],
                        "selected_labeled_directions": row["selected_labeled_direction_count"],
                        "formula_sha256": record["formula_sha256"],
                        "proof_bytes": cpc["proof_bytes"],
                        "proof_sha256": cpc["proof_sha256"]})
    for field, value in totals.items():
        require(audit.get(field) == value, f"aggregate {field} disagrees with complete rows")
    print(json.dumps({"status": "PASS", "checked": checked}, indent=2))


if __name__ == "__main__":
    main()
'''
(WORK/name).write_text(text)
patch=[]
for name in wrappers:
    shutil.copy2(WORK/name,PROPOSALS/name)
    patch.extend(difflib.unified_diff((SRC/name).read_text().splitlines(keepends=True),(WORK/name).read_text().splitlines(keepends=True),fromfile='a/coopgames/verifiers/s6/'+name,tofile='b/coopgames/verifiers/s6/'+name))
(ROOT/'ordinary_guards_and_coverage.patch').write_text(''.join(patch))
print(ROOT)
