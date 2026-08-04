"""Finite audit of the laminar strict-cover partition lemma."""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path


def is_laminar(family):
    for a, b in itertools.combinations(family, 2):
        if a & b and a & b != a and a & b != b:
            return False
    return True


def load(mask, family, weights):
    return sum(w for coalition, w in zip(family, weights) if coalition & mask)


def extracted_partition(n, family, weights):
    loads = tuple(load(1 << i, family, weights) for i in range(n))
    alpha = max(loads)
    rich = sum(1 << i for i, value in enumerate(loads) if value == alpha)
    full = (1 << n) - 1
    if alpha <= 0 or rich == full:
        return None

    minimal = []
    for i in range(n):
        if not rich >> i & 1:
            continue
        containing = [coalition for coalition in family if coalition >> i & 1]
        member = min(containing, key=lambda coalition: coalition.bit_count())
        if member & ~rich:
            raise AssertionError("minimal supported rich set meets poorer side")
        minimal.append(member)

    blocks = tuple(
        member
        for member in set(minimal)
        if not any(member != other and member & ~other == 0 for other in set(minimal))
    )
    if sum(blocks) != rich:
        raise AssertionError("extracted blocks do not partition the rich side")
    if any(a & b for a, b in itertools.combinations(blocks, 2)):
        raise AssertionError("extracted blocks overlap")
    return rich, tuple(sorted(blocks)), loads


def audit(max_n=6, max_support=4, max_weight=2):
    tested = 0
    strict_boundaries = 0
    examples = []
    for n in range(2, max_n + 1):
        full = (1 << n) - 1
        coalitions = range(1, full)
        for size in range(1, min(max_support, len(tuple(coalitions))) + 1):
            for family in itertools.combinations(coalitions, size):
                if not is_laminar(family):
                    continue
                for weights in itertools.product(range(1, max_weight + 1), repeat=size):
                    tested += 1
                    result = extracted_partition(n, family, weights)
                    if result is None:
                        continue
                    strict_boundaries += 1
                    if len(examples) < 8:
                        rich, blocks, loads = result
                        examples.append({
                            "n": n,
                            "family": list(family),
                            "weights": list(weights),
                            "loads": list(loads),
                            "rich": rich,
                            "partition": list(blocks),
                        })

    # Relabeled version of the known five-player support
    # {1,3,5}, {3,4,5}; its intersection is nonempty and neither contains
    # the other, so the laminar theorem correctly does not cover it.
    crossing = ((1 << 0) | (1 << 2) | (1 << 4),
                (1 << 2) | (1 << 3) | (1 << 4))
    if is_laminar(crossing):
        raise AssertionError("known crossing obstruction was called laminar")

    return {
        "proved_by_human_argument": True,
        "finite_audit_is_not_proof": True,
        "parameters": {
            "max_n": max_n,
            "max_support": max_support,
            "positive_integer_weights": [1, max_weight],
        },
        "laminar_weighted_supports_tested": tested,
        "strict_top_load_boundaries_tested": strict_boundaries,
        "sample_extractions": examples,
        "known_five_player_support_is_laminar": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-n", type=int, default=6)
    parser.add_argument("--max-support", type=int, default=4)
    parser.add_argument("--max-weight", type=int, default=2)
    args = parser.parse_args()
    result = audit(args.max_n, args.max_support, args.max_weight)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
