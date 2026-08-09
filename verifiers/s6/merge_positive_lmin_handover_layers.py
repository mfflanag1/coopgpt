#!/usr/bin/env python3
"""Merge and validate complete Lmin handover dependency-audit shards."""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path


EXPECTED_TOTALS = {"critical": 901, "direction": 322, "menu": 97}
EXPECTED_SUMMARY = {
    "critical": {
        "common_sign_only": 293,
        "needs_third_triple_comparison": 266,
        "needs_distance_and_witnesses": 342,
    },
    "direction": {
        "premise_light": 71,
        "distance_only": 14,
        "blocker_witnesses_only": 5,
        "distance_and_blocker_witnesses": 232,
    },
    "menu": {
        "premise_light": 13,
        "blocker_witnesses_only": 64,
        "distance_and_blocker_witnesses": 20,
    },
}


def blocker_class(row):
    triple = (
        row["without_distance"],
        row["without_blocker_witnesses"],
        row["without_distance_or_blocker_witnesses"],
    )
    mapping = {
        ("unsat", "unsat", "unsat"): "premise_light",
        ("sat", "unsat", "sat"): "distance_only",
        ("unsat", "sat", "sat"): "blocker_witnesses_only",
        ("sat", "sat", "sat"): "distance_and_blocker_witnesses",
    }
    if triple not in mapping:
        raise ValueError(f"unexpected blocker ablation pattern {triple}")
    return mapping[triple]


def critical_class(row):
    if row["common_sign_only"] == "unsat":
        return "common_sign_only"
    if row["payoff_critical"] == "unsat":
        return "needs_third_triple_comparison"
    if all(
        row[key] == "sat"
        for key in (
            "without_distance",
            "without_witnesses",
            "payoff_critical",
            "common_sign_only",
        )
    ):
        return "needs_distance_and_witnesses"
    raise ValueError("unexpected critical ablation pattern")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("shards", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    by_section = {section: {} for section in EXPECTED_TOTALS}
    for path in args.shards:
        shard = json.loads(path.read_text())
        assert shard["schema"] == "positive-lmin-handover-dependency-shard-v1"
        section = shard["section"]
        assert shard["section_total"] == EXPECTED_TOTALS[section]
        assert len(shard["rows"]) == shard["stop"] - shard["start"]
        for row in shard["rows"]:
            position = row["position"]
            if position in by_section[section]:
                raise ValueError(f"duplicate {section} position {position}")
            by_section[section][position] = row

    summary = {}
    merged = {}
    for section, total in EXPECTED_TOTALS.items():
        if set(by_section[section]) != set(range(total)):
            missing = sorted(set(range(total)) - set(by_section[section]))
            raise ValueError(f"incomplete {section} coverage; first missing {missing[:5]}")
        rows = [by_section[section][position] for position in range(total)]
        classifier = critical_class if section == "critical" else blocker_class
        counts = dict(sorted(collections.Counter(map(classifier, rows)).items()))
        assert counts == EXPECTED_SUMMARY[section]
        summary[section] = counts
        merged[section] = rows
    payload = {
        "schema": "positive-lmin-handover-dependency-audit-v1",
        "scope": "complete exact QF_LRA premise ablation; solver evidence, not proof objects",
        "summary": summary,
        "rows": merged,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
