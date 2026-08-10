#!/usr/bin/env python3
"""Verify the frozen table-free starved exchange formulas and CPC records."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CERTIFICATES = HERE / "certificates"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checked = []
    for side in ("min", "max"):
        stem = f"starved_universal_exchange_{side}"
        formula = CERTIFICATES / f"{stem}.smt2"
        proof = CERTIFICATES / f"{stem}.cpc"
        record = json.loads((CERTIFICATES / f"{stem}.json").read_text())
        assert record["status"] == "PASS"
        assert record["z3"]["status"] == "unsat"
        assert record["cvc5"]["status"] == "unsat"
        assert record["formula_sha256"] == sha256(formula)
        cpc = record["cpc_proof"]
        assert cpc["status"] == "PASS"
        assert cpc["ethos"]["status"] == "correct"
        assert cpc["forbidden_markers"] == []
        assert cpc["proof_sha256"] == sha256(proof)
        checked.append(
            {
                "side": side,
                "formula_sha256": record["formula_sha256"],
                "proof_sha256": cpc["proof_sha256"],
                "proof_bytes": cpc["proof_bytes"],
                "ethos": cpc["ethos"]["status"],
            }
        )
    abstract = json.loads((HERE / "starved_universal_exchange_lemma_audit.json").read_text())
    assert abstract["verdict_summary"] == {"unsat": 2}
    mapping = json.loads((HERE / "starved_universal_exchange_mapping_audit.json").read_text())
    assert mapping["status"] == "PASS"
    ablation = json.loads((HERE / "starved_universal_shape_ablation_audit.json").read_text())
    verdicts = {row["variant"]: row["verdicts"] for row in ablation["rows"]}
    assert verdicts["swaps_plus_two_for_two"] == {"max": "unsat", "min": "sat"}
    assert verdicts["swaps_plus_two_and_three"] == {"max": "unsat", "min": "sat"}
    assert verdicts["final_three_shapes"] == {"max": "unsat", "min": "unsat"}
    print(json.dumps({"status": "PASS", "checked": checked}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
