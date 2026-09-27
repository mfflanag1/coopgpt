"""Independently reconstruct the compact example and its conventional proof.

Standard library only. The sparse construction, witnesses, and proof rows below
are explicit, rather than read from the discovery program's budget fields.
"""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def main():
    sparse = (
        ((0, 1, 2), (2, 1, 2), (5, 5, 1), (5, 6, 1)),
        ((0, 0, 2), (0, 3, 2), (1, 2, 1), (2, 5, 2),
         (3, 3, 3), (5, 4, 1), (5, 5, 2)),
        ((1, 1, 2), (1, 3, 2), (4, 4, 1), (6, 4, 1), (6, 6, 1)),
    )
    matrices = [[[0 for _ in range(7)] for _ in range(7)] for _ in range(3)]
    for matrix, entries in zip(matrices, sparse):
        for i, j, value in entries:
            matrix[i][j] = value
    A, B, C = matrices

    def value(team):
        i, j, k = team
        return A[i][j] + B[i][k] + C[j][k]

    def players(team):
        i, j, k = team
        return i, 7 + j, 14 + k

    matching = ((0, 0, 0), (1, 2, 2), (2, 1, 1), (3, 3, 3),
                (4, 4, 4), (5, 5, 5), (6, 6, 6))
    floor = [Q(v, 3) for v in
             (4, 1, 4, 1, 1, 7, 1, 1, 7, 1, 1, 1, 1, 1,
              1, 1, 1, 7, 1, 1, 1)]
    ideal = list(map(Q, (2, 0, 0, 3, 0, 1, 0, 0, 4, 0, 0, 0, 0, 1,
                         0, 0, 1, 0, 1, 2, 0)))
    T = sum(map(value, matching))
    require(T == 15, "matching value")
    require(sorted(v for team in matching for v in players(team)) == list(range(21)),
            "matching partition")
    checked = 0
    for allocation in (floor, ideal):
        require(min(allocation) >= 0 and sum(allocation) == T, "cover efficiency")
        for team in product(range(7), repeat=3):
            require(sum(allocation[v] for v in players(team)) >= value(team),
                    "full triple cover")
            checked += 1
        require(all(sum(allocation[v] for v in players(team)) == value(team)
                    for team in matching), "matching equalities")

    coefficient = [0] * 21
    rhs = 0
    for team, multiplier in zip(matching, (3, 1, 1, 1, 1, 1, 1)):
        for v in players(team):
            coefficient[v] += multiplier
        rhs += multiplier * value(team)
    proof_triples = ((0, 1, 3), (0, 4, 0), (0, 5, 0), (1, 3, 2),
                     (2, 2, 5), (5, 6, 4))
    for team in proof_triples:
        for v in players(team):
            coefficient[v] -= 1
        rhs -= value(team)
    expected = {3: 1, 4: 1, 6: 1, 7: 3, 14: 1, 15: 1, 20: 1}
    require(coefficient == [expected.get(i, 0) for i in range(21)] and rhs == 3,
            "independent coefficient identity")
    require(sum(coefficient) == 9 and min(floor) == Q(1, 3), "first floor")
    require(all(floor[v] == Q(1, 3) for v in expected), "first-face fixed support")
    require(value((3, 3, 3)) == ideal[3] == 3, "matching ideal cap and attainment")

    source = ROOT.parent / "experiment" / "reduced_candidate.json"
    raw = source.read_bytes()
    saved = json.loads(raw)
    require(matrices == [[[Q(v) for v in row] for row in mat]
                         for mat in saved["matrices"]], "saved matrices agree")
    require(list(map(list, matching)) == saved["matching"], "saved matching agrees")
    require(floor == list(map(Q, saved["floor_witness"])) and
            ideal == list(map(Q, saved["ideal_witness"])) and saved["target"] == 3,
            "saved points and target agree")
    report = dict(status="PASS", source_sha256=hashlib.sha256(raw).hexdigest(),
                  players=21, complete_triple_checks=checked, matching_value=T,
                  matching_weights=list(map(value, matching)),
                  subtracted_triple_weights=list(map(value, proof_triples)),
                  budget_coefficients=coefficient, budget_rhs=rhs,
                  target_full_leximin="1/3", target_ideal="3", ratio="1/9",
                  proof_scope="Target fixed on the whole first optimal face; no claim about other full-selector coordinates")
    (ROOT / "compact_proof_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
