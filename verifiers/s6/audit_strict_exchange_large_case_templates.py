#!/usr/bin/env python3
"""Compress the 52/71/90 strict menus into global exchange templates."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
CASES = ("p3_n2_t1", "p3_n3_t0", "p4_n2_t0")


def role_signature(item, positive, negative):
    direction = item["direction"]
    return (
        item["side"],
        tuple(sorted(direction[:positive])),
        tuple(sorted(direction[positive : positive + negative])),
        tuple(sorted(direction[positive + negative :])),
    )


def reversal_class(shape):
    reversed_shape = tuple(sorted(-value for value in shape))
    return min(shape, reversed_shape)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cores = json.loads((HERE / "strict_exchange_direction_cores.json").read_text())
    frozen_orbits = json.loads((HERE / "strict_exchange_sign_orbits.json").read_text())
    orbit_rows = {row["case"]: row for row in frozen_orbits["rows"]}

    shape_uses = defaultdict(lambda: {"labeled": 0, "role_orbits": set(), "uses": Counter()})
    case_rows = []
    total_labeled = 0
    total_role_orbits = 0
    for row in cores["rows"]:
        if row["case"] not in CASES:
            continue
        signatures = Counter(
            role_signature(item, row["positive_count"], row["negative_count"])
            for item in row["retained_menu"]
        )
        frozen = orbit_rows[row["case"]]
        if len(signatures) != frozen["sign_preserving_orbit_count"]:
            raise AssertionError(f"orbit count changed in {row['case']}")
        if sum(signatures.values()) != row["retained_direction_count"]:
            raise AssertionError(f"labeled coverage changed in {row['case']}")

        for item in row["retained_menu"]:
            shape = tuple(sorted(item["direction"]))
            signature = role_signature(item, row["positive_count"], row["negative_count"])
            record = shape_uses[shape]
            record["labeled"] += 1
            record["role_orbits"].add((row["case"],) + signature)
            record["uses"][(row["case"], item["side"])] += 1

        total_labeled += row["retained_direction_count"]
        total_role_orbits += len(signatures)
        case_rows.append(
            {
                "case": row["case"],
                "labeled_direction_count": row["retained_direction_count"],
                "role_orbit_count": len(signatures),
                "global_template_count": len(
                    {tuple(sorted(item["direction"])) for item in row["retained_menu"]}
                ),
            }
        )

    templates = []
    for index, (shape, record) in enumerate(sorted(shape_uses.items()), 1):
        templates.append(
            {
                "template": f"H{index}",
                "coefficient_multiset": list(shape),
                "labeled_direction_count": record["labeled"],
                "role_orbit_count": len(record["role_orbits"]),
                "uses": [
                    {"case": case, "side": side, "labeled_count": count}
                    for (case, side), count in sorted(record["uses"].items())
                ],
            }
        )

    if total_labeled != 52 + 71 + 90:
        raise AssertionError(total_labeled)
    if total_role_orbits != 17 + 18 + 9:
        raise AssertionError(total_role_orbits)
    if len(templates) != 8:
        raise AssertionError(f"expected eight global templates, got {len(templates)}")
    shape_names = {
        tuple(template["coefficient_multiset"]): template["template"]
        for template in templates
    }
    reversal_classes = defaultdict(list)
    for shape, name in shape_names.items():
        reversal_classes[reversal_class(shape)].append(name)
    reversal_pairs = [sorted(names) for names in reversal_classes.values() if len(names) == 2]
    if len(reversal_classes) != 6 or sorted(reversal_pairs) != [["H1", "H2"], ["H4", "H5"]]:
        raise AssertionError("unexpected sign-reversal quotient")

    payload = {
        "schema": "strict-exchange-large-case-templates-v1",
        "status": "PASS",
        "scope": (
            "exact combinatorial quotient of the retained labeled menus; "
            "not an additional infeasibility proof"
        ),
        "case_count": len(case_rows),
        "labeled_direction_count": total_labeled,
        "sign_role_orbit_count": total_role_orbits,
        "global_template_count": len(templates),
        "unoriented_template_count": len(reversal_classes),
        "sign_reversal_pairs": sorted(reversal_pairs),
        "cases": case_rows,
        "templates": templates,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
