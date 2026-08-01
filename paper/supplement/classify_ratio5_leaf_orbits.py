"""Classify ratio-five seven-player leaves under distinguished-arm symmetry."""
from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path


PLAYERS = 7
CANONICAL_SELECTED = 6
CANONICAL_ARM_OTHERS = (4,5)
CANONICAL_OUTSIDE = (0,1,2,3)


def permute_mask(mask, permutation):
    return sum(
        1 << permutation[player]
        for player in range(PLAYERS)
        if mask >> player & 1
    )


def canonical_form(record):
    singleton = int(record["singleton_mask"])
    selected = singleton.bit_length()-1
    arm = int(record["arm_mask"])
    arm_others = tuple(
        player for player in range(PLAYERS)
        if arm >> player & 1 and player != selected
    )
    outside = tuple(
        player for player in range(PLAYERS) if not arm >> player & 1
    )
    collection = tuple(
        (int(mask),F(weight)) for mask,weight in record["collection"]
    )
    forms = []
    for arm_image in itertools.permutations(CANONICAL_ARM_OTHERS):
        for outside_image in itertools.permutations(CANONICAL_OUTSIDE):
            permutation = [None]*PLAYERS
            permutation[selected] = CANONICAL_SELECTED
            for source,target in zip(arm_others,arm_image):
                permutation[source] = target
            for source,target in zip(outside,outside_image):
                permutation[source] = target
            forms.append(tuple(sorted(
                (permute_mask(mask,permutation),weight)
                for mask,weight in collection
            )))
    return min(forms)


def classify(payload):
    groups = defaultdict(list)
    for index,record in enumerate(payload["records"],1):
        groups[canonical_form(record)].append(index)
    records = []
    for orbit_index,(form,indices) in enumerate(sorted(groups.items()),1):
        weights = Counter(str(weight) for _mask,weight in form)
        records.append({
            "orbit_index": orbit_index,
            "record_count": len(indices),
            "source_record_indices_1based": indices,
            "canonical_collection": [
                [mask,str(weight)] for mask,weight in form
            ],
            "weight_histogram": dict(sorted(weights.items())),
        })
    return {
        "status": "exact distinguished-arm symmetry classification",
        "input_record_count": len(payload["records"]),
        "distinguished_singleton_mask": 1 << CANONICAL_SELECTED,
        "distinguished_arm_mask": (
            (1 << CANONICAL_SELECTED)
            | sum(1 << player for player in CANONICAL_ARM_OTHERS)
        ),
        "symmetry_group_order": 2*24,
        "orbit_count": len(records),
        "orbit_size_histogram": dict(sorted(Counter(
            record["record_count"] for record in records
        ).items())),
        "orbits": records,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",type=Path)
    parser.add_argument("--output",type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rendered = json.dumps(classify(json.loads(args.input.read_text())),indent=2)+"\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered,end="")
