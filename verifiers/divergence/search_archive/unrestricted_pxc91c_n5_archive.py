#!/usr/bin/env python3
"""Exact finite PXC91c audit of the two-top games in n5_hits_1.json.

This is an exhaustive audit of the 36 two-top divergent games among the 165
distinct exact games retained by that finite source archive.  It is not an
exhaustion of all five-player exact games.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent))

import unrestricted_pxc91c_exact_search as core  # noqa: E402

SOURCE = ROOT / "verifiers/cc/n5_hits_1.json"


def exact_games():
    payload = json.loads(SOURCE.read_text())
    unique = {}
    for index, hit in enumerate(payload["hits"]):
        values = tuple(map(F, hit["v"]))
        if len(values) != 32 or values[0] != 0:
            raise AssertionError(("malformed archived game", index))
        unique.setdefault(values, {"first_index": index, "tag": hit["tag"],
                                   "generating_core_allocations": hit["rows"],
                                   "duplicate_indices": []})
        unique[values]["duplicate_indices"].append(index)
    if len(payload["hits"]) != 659 or len(unique) != 165:
        raise AssertionError(("archive cardinality changed", len(payload["hits"]),
                              len(unique)))
    for values, provenance in unique.items():
        rows = tuple(tuple(map(F, row))
                     for row in provenance["generating_core_allocations"])
        total = values[-1]
        if any(any(q < 0 for q in row) or sum(row, F(0)) != total for row in rows):
            raise AssertionError(("bad generating allocation", provenance))
        reconstructed = tuple(
            min(core.csum(row, coalition) for row in rows)
            for coalition in range(32)
        )
        if reconstructed != values:
            raise AssertionError(("allocation witnesses do not reconstruct game", provenance))
    return payload, unique


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    source_payload, unique = exact_games()
    selected = []
    classification = {"coincident": 0, "divergent_other_top_count": 0,
                      "divergent_two_top": 0}
    for values, provenance in unique.items():
        if any(values[1 << i] for i in range(5)):
            raise AssertionError(("archive lost singleton normalization", provenance))
        x, z = core.selectors(values, 5)
        if x == z:
            classification["coincident"] += 1
            continue
        top = tuple(i for i, q in enumerate(z) if q == max(z))
        if len(top) != 2:
            classification["divergent_other_top_count"] += 1
            continue
        classification["divergent_two_top"] += 1
        selected.append((provenance["first_index"], values, x, z, provenance))
    selected.sort()
    if len(selected) != 36:
        raise AssertionError(("two-top archive count changed", len(selected)))

    audits, witnesses = [], []
    for first_index, values, x, z, provenance in selected:
        label = f"n5_hits_1.json:$.hits[{first_index}]"
        item = core.audit_game(label, values, x, z, 30, replay_exact=False)
        if item is None:
            raise AssertionError(("selected archive game rejected", label))
        if not item["cx_subsets_exhausted"]:
            raise AssertionError(("Cx enumeration incomplete", label))
        item["source"] = provenance
        item["top_players"] = [i for i, q in enumerate(z) if q == max(z)]
        item["full_game_replayed"] = True
        item["exact_game_replay"] = (
            "all 32 coalition values equal the coordinatewise minima of the "
            "listed feasible generating core allocations"
        )
        if "pin" in item:
            item["pin"]["independent_replay"] = item["exact_game_replay"]
        audits.append(item)
        if item.get("no_qualifying_cover") or item["strong_fixed_cx_counterexample"]:
            witnesses.append(item)

    payload = {
        "claim": "exact finite audit of all archived n=5 two-top games",
        "source": str(SOURCE.relative_to(ROOT)),
        "source_stats": source_payload["stats"],
        "archive_hit_count": len(source_payload["hits"]),
        "distinct_exact_game_count": len(unique),
        "classification": classification,
        "audited_two_top_count": len(audits),
        "all_complete_cx_subsets_exhausted": all(
            q["cx_subsets_exhausted"] for q in audits
        ),
        "all_qualifying_extreme_covers_exhausted_through_support": 3,
        "strong_fixed_cx_witness_count": sum(
            q["strong_fixed_cx_counterexample"] for q in audits
        ),
        "existential_cx_witness_count": sum(
            q["existential_cx_counterexample"] for q in audits
        ),
        "witnesses": witnesses,
        "audits": audits,
        "provenance": {
            "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "driver": str(HERE.relative_to(ROOT)),
            "driver_sha256": hashlib.sha256(HERE.read_bytes()).hexdigest(),
            "core_driver_sha256": hashlib.sha256(
                (HERE.parent / "unrestricted_pxc91c_exact_search.py").read_bytes()
            ).hexdigest(),
            "exactlp_sha256": hashlib.sha256(
                (ROOT / "src/exactlp.py").read_bytes()
            ).hexdigest(),
            "replay_command": (
                "python3 verifiers/divergence/search_archive/"
                "unrestricted_pxc91c_n5_archive.py --output "
                "verifiers/divergence/search_archive/"
                "unrestricted_pxc91c_n5_archive.json"
            ),
            "completed": True,
        },
        "scope": ("Exhaustive only for the 36 two-top divergent games among the 165 "
                  "distinct exact games in the pinned 659-hit archive. Every selected "
                  "game is independently reconstructed by exact generating core-allocation "
                  "witnesses for all 32 coalition minima; "
                  "every x-tight row subset and every positive extreme z-tight top cover "
                  "of support at most n-2 is tested. This is finite evidence, not an n=5 "
                  "theorem."),
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
