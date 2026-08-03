"""Extract and check compact unsatisfiable cores for the bridge lemma.

The full KKT verifier proves eleven cases.  Four have realizable payoff-stratum
patterns, so their contradiction genuinely uses positive richer-suffix slack.
For each of those four cases this script:

1. labels every assertion in the exact theorem query;
2. obtains a Z3 unsatisfiable core;
3. greedily deletes redundant assertions to local irreducibility;
4. rechecks the reduced, unlabelled formula as unsatisfiable; and
5. checks that deleting any one retained assertion makes it satisfiable.

The resulting JSON is a compact solver-checkable core, not a standalone
Farkas certificate or a substitute for the independent primal verifier.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import z3

from verify_n4_exact_lmin_pes_bridge import build_query


if sys.flags.optimize:
    raise RuntimeError("run this exact verifier without Python -O")


REALIZABLE_SUFFIX_CASES = (
    (3, [1, 2]),
    (4, [2, 2]),
    (4, [1, 3]),
    (4, [1, 1, 2]),
)


def status_of(assertions):
    solver = z3.Solver()
    solver.add(*assertions)
    return solver.check()


def locally_irreducible_core(player_count, composition):
    full_solver, suffixes = build_query(player_count, composition)
    assertions = list(full_solver.assertions())
    labels = [z3.Bool(f"core_label_{index}") for index in range(len(assertions))]
    labelled = z3.Solver()
    for label, assertion in zip(labels, assertions):
        labelled.add(z3.Implies(label, assertion))
    status = labelled.check(*labels)
    if status != z3.unsat:
        raise RuntimeError(
            f"full query is not unsatisfiable for n={player_count}, "
            f"composition={composition}: {status}"
        )
    active = sorted(
        int(str(label).removeprefix("core_label_"))
        for label in labelled.unsat_core()
    )
    changed = True
    while changed:
        changed = False
        for index in list(active):
            trial = [other for other in active if other != index]
            trial_status = labelled.check(*[labels[other] for other in trial])
            if trial_status == z3.unsat:
                active = trial
                changed = True
            elif trial_status != z3.sat:
                raise RuntimeError(f"unknown during core minimization: {trial_status}")

    reduced = [assertions[index] for index in active]
    if status_of(reduced) != z3.unsat:
        raise RuntimeError("reduced unlabelled core did not replay as unsatisfiable")
    deletion_statuses = []
    for position in range(len(reduced)):
        deletion_status = status_of(reduced[:position] + reduced[position + 1:])
        if deletion_status != z3.sat:
            raise RuntimeError(
                f"core is not locally irreducible at position {position}: "
                f"{deletion_status}"
            )
        deletion_statuses.append("satisfiable")
    return {
        "player_count": player_count,
        "payoff_stratum_composition": composition,
        "richer_suffixes": suffixes,
        "full_assertion_count": len(assertions),
        "core_assertion_count": len(active),
        "core": [
            {
                "original_index": index,
                "assertion": assertions[index].sexpr(),
            }
            for index in active
        ],
        "core_status": "unsatisfiable",
        "every_single_deletion": deletion_statuses,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = {
        "status": "locally irreducible bridge suffix-slack cores verified",
        "solver": f"z3 {z3.get_version_string()} exact rational arithmetic",
        "scope": (
            "the four realizable payoff-stratum patterns; impossible stratum "
            "patterns are covered by the two exhaustive bridge verifiers"
        ),
        "certificate_type": (
            "unsatisfiable subsets of the original KKT/exact-face assertions; "
            "locally irreducible under single-assertion deletion"
        ),
        "cases": [
            locally_irreducible_core(player_count, composition)
            for player_count, composition in REALIZABLE_SUFFIX_CASES
        ],
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
