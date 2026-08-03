"""Classify and exactly verify the first nine disjoint n=5 circuit types."""
from __future__ import annotations

from fractions import Fraction as F
from itertools import permutations

import numpy as np
import sympy as sp
from scipy.optimize import linprog

from search_both_sensitive_circuits import eliminated_matrix


N = 5
GRAND = (1 << N) - 1
A = 0b00111
B = 0b11000
TYPE_I = {
    "core": ((0,20), (1,7), (1,25), (1,26),
             (2,5), (2,6), (2,11), (2,24)),
    "mono": ((0,1,2,A), (0,2,4,B)),
}
TYPE_II = {
    "core": ((0,17), (1,7), (1,26), (1,28),
             (2,3), (2,6), (2,13), (2,24)),
    "mono": ((0,1,0,A), (0,2,4,B)),
}
TYPE_III = {
    "core": ((0,20), (1,7), (1,8), (1,18), (1,25),
             (2,3), (2,5), (2,14), (2,24)),
    "mono": ((0,1,2,A), (0,2,4,B)),
}
TYPE_IV = {
    "name": "IV",
    "core": ((0,23), (0,25), (1,7), (1,26), (1,28),
             (2,5), (2,6), (2,11), (2,24)),
    "mono": ((0,1,0,A), (0,2,4,B)),
    "efficiency": (1,2,2),
}
TYPE_V = {
    "name": "V",
    "core": ((0,21), (0,27), (1,7), (1,26), (1,28),
             (2,3), (2,6), (2,13), (2,24)),
    "mono": ((0,1,0,A), (0,2,4,B)),
    "efficiency": (1,2,2),
}
TYPE_VI = {
    "name": "VI",
    "core": ((0,12), (1,7), (1,9), (1,10), (1,16),
             (2,3), (2,6), (2,21), (2,24)),
    "core_weights": (1,1,1,1,2,1,1,1,1),
    "mono": ((0,1,2,A), (0,2,3,B)),
    "efficiency": (0,2,2),
}
TYPE_VII = {
    "name": "VII",
    "core": ((0,18), (1,7), (1,9), (1,16), (1,28),
             (2,5), (2,6), (2,11), (2,24)),
    "mono": ((0,1,1,A), (0,2,4,B)),
    "efficiency": (0,2,2),
}
TYPE_VIII = {
    "name": "VIII",
    "core": ((0,11), (0,29), (1,7), (1,26), (1,28),
             (2,3), (2,6), (2,21), (2,24)),
    "mono": ((0,1,0,A), (0,2,3,B)),
    "efficiency": (1,2,2),
}
TYPE_IX = {
    "name": "IX",
    "core": ((0,19), (0,29), (1,7), (1,26), (1,28),
             (2,3), (2,5), (2,14), (2,24)),
    "mono": ((0,1,0,A), (0,2,4,B)),
    "efficiency": (1,2,2),
}
NEW_BALANCED_TYPES = (TYPE_IV, TYPE_V, TYPE_VI, TYPE_VII, TYPE_VIII, TYPE_IX)


def build_balanced_lp(circuit):
    worth_offset = 3 * N
    d_A = worth_offset + GRAND - 1
    d_B = d_A + 1
    variable_count = d_B + 1
    objective = np.zeros(variable_count)
    weights = circuit.get(
        "core_weights", circuit.get("weights", (1,) * len(circuit["core"]))
    )
    assert len(weights) == len(circuit["core"])
    for (game, coalition), weight in zip(circuit["core"], weights):
        objective[worth_offset + coalition - 1] -= weight
        if game == 1 and coalition == A:
            objective[d_A] -= weight
        if game == 2 and coalition == B:
            objective[d_B] -= weight

    A_ub, b_ub, rowmeta = [], [], []
    for game in range(3):
        for coalition in range(1, GRAND):
            row = np.zeros(variable_count)
            row[worth_offset + coalition - 1] = 1
            if game == 1 and coalition == A:
                row[d_A] = 1
            if game == 2 and coalition == B:
                row[d_B] = 1
            for player in range(N):
                if coalition >> player & 1:
                    row[game * N + player] = -1
            A_ub.append(row); b_ub.append(0); rowmeta.append((game, coalition))
    A_eq, b_eq = [], []
    for game in range(3):
        row = np.zeros(variable_count)
        row[game * N:(game + 1) * N] = 1
        A_eq.append(row); b_eq.append(1)
    bounds = [(None, None)] * variable_count
    bounds[d_A] = (0, None); bounds[d_B] = (0, None)
    return objective, A_ub, b_ub, A_eq, b_eq, bounds, rowmeta


def discover_balanced_dual(circuit):
    objective, A_ub, b_ub, A_eq, b_eq, bounds, rowmeta = build_balanced_lp(circuit)
    result = linprog(
        objective,
        A_ub=np.asarray(A_ub), b_ub=np.asarray(b_ub),
        A_eq=np.asarray(A_eq), b_eq=np.asarray(b_eq),
        bounds=bounds, method="highs",
    )
    expected = sum(circuit.get("efficiency", (0, 2, 2)))
    assert result.success and F(float(result.fun)).limit_denominator() == -expected
    return {
        "inequalities": [
            (rowmeta[index], F(float(-value)).limit_denominator())
            for index, value in enumerate(result.ineqlin.marginals)
            if abs(value) > 1e-8
        ],
        "equalities": [
            (index, F(float(-value)).limit_denominator())
            for index, value in enumerate(result.eqlin.marginals)
            if abs(value) > 1e-8
        ],
        "lower_bounds": [
            (index, F(float(value)).limit_denominator())
            for index, value in enumerate(result.lower.marginals)
            if abs(value) > 1e-8
        ],
    }


def preserving_permutations():
    for perm_A in permutations((0, 1, 2)):
        for perm_B in permutations((3, 4)):
            yield tuple(perm_A + perm_B)


def permute_mask(mask, permutation):
    result = 0
    for player in range(N):
        if mask >> player & 1:
            result |= 1 << permutation[player]
    return result


def permute_circuit(circuit, permutation):
    result = {
        "core": tuple(
            (game, permute_mask(coalition, permutation))
            for game, coalition in circuit["core"]
        ),
        "mono": tuple(
            (source, target, permutation[player], permute_mask(label, permutation))
            for source, target, player, label in circuit["mono"]
        ),
    }
    for key in ("name", "core_weights", "mono_weights", "efficiency"):
        if key in circuit:
            result[key] = circuit[key]
    return result


def circuit_signature(circuit):
    core_weights = circuit.get("core_weights", (1,) * len(circuit["core"]))
    mono_weights = circuit.get("mono_weights", (1,) * len(circuit["mono"]))
    return (
        tuple(sorted(zip(circuit["core"], core_weights))),
        tuple(sorted(zip(circuit["mono"], mono_weights))),
    )


def verify_stationarity(circuit):
    coefficients = [F(0)] * (3 * N)
    core_weights = circuit.get("core_weights", (1,) * len(circuit["core"]))
    mono_weights = circuit.get("mono_weights", (1,) * len(circuit["mono"]))
    efficiency = circuit.get("efficiency", (0, 2, 2))
    for (game, coalition), weight in zip(circuit["core"], core_weights):
        for player in range(N):
            if coalition >> player & 1:
                coefficients[game * N + player] -= weight
    for (source, target, player, _label), weight in zip(circuit["mono"], mono_weights):
        coefficients[source * N + player] += weight
        coefficients[target * N + player] -= weight
    for game in range(3):
        for player in range(N):
            coefficients[game * N + player] += efficiency[game]
    assert all(value == 0 for value in coefficients)


def verify_exact_circuit(circuit):
    matrix, _inequalities, _equalities, rowmeta = eliminated_matrix(N, A, B)
    metadata_index = {meta: index for index, meta in enumerate(rowmeta)}
    support = [metadata_index[("core", game, coalition)]
               for game, coalition in circuit["core"]]
    support += [metadata_index[("mono", source, target, player, label)]
                for source, target, player, label in circuit["mono"]]
    block = sp.Matrix(np.asarray(matrix[:, support], dtype=int).tolist())
    assert len(support) - block.rank() == 1
    weights = list(circuit.get(
        "core_weights", (1,) * len(circuit["core"])
    )) + list(circuit.get("mono_weights", (1,) * len(circuit["mono"])))
    assert all(weight > 0 for weight in weights)
    assert block * sp.Matrix(weights) == sp.zeros(block.rows, 1)


def add(target, key, value):
    target[key] = target.get(key, F(0)) + value
    if target[key] == 0:
        del target[key]


def verify_generic_balanced_dual(circuit):
    """Recover a float dual, then verify the full certificate exactly."""
    dual = discover_balanced_dual(circuit)
    assert not dual["lower_bounds"]
    collections = [dict() for _ in range(3)]
    for (game, coalition), weight in dual["inequalities"]:
        assert weight > 0
        collections[game][coalition] = weight
    totals = {game: F(0) for game in range(3)}
    totals.update(dual["equalities"])
    assert all(total >= 0 for total in totals.values())
    for game, collection in enumerate(collections):
        coverage = [
            sum(weight for coalition, weight in collection.items()
                if coalition >> player & 1)
            for player in range(N)
        ]
        assert coverage == [totals[game]] * N

    dual_worths = {}
    for game, collection in enumerate(collections):
        for coalition, weight in collection.items():
            add(dual_worths, ("b", coalition), weight)
            if game == 1 and coalition == A:
                add(dual_worths, ("d", "A"), weight)
            if game == 2 and coalition == B:
                add(dual_worths, ("d", "B"), weight)

    circuit_worths = {}
    core_weights = circuit.get("core_weights", (1,) * len(circuit["core"]))
    for (game, coalition), weight in zip(circuit["core"], core_weights):
        add(circuit_worths, ("b", coalition), F(weight))
        if game == 1 and coalition == A:
            add(circuit_worths, ("d", "A"), F(weight))
        if game == 2 and coalition == B:
            add(circuit_worths, ("d", "B"), F(weight))
    assert dual_worths == circuit_worths
    assert sum(totals.values()) == sum(circuit["efficiency"])
    return tuple(totals[game] for game in range(3))


def type_ii_balanced_collections(permutation):
    collection_A = {
        3: F(1, 2), 7: F(1), 13: F(1, 2),
        17: F(1, 2), 26: F(1), 28: F(1),
    }
    collection_B = {
        3: F(1, 2), 6: F(1), 13: F(1, 2),
        17: F(1, 2), 24: F(1),
    }
    return (
        {permute_mask(S, permutation): weight for S, weight in collection_A.items()},
        {permute_mask(S, permutation): weight for S, weight in collection_B.items()},
    )


def verify_type_ii_balanced_dual(permutation):
    circuit = permute_circuit(TYPE_II, permutation)
    collection_A, collection_B = type_ii_balanced_collections(permutation)
    for collection, total in ((collection_A, F(5, 2)), (collection_B, F(3, 2))):
        coverage = [
            sum(weight for coalition, weight in collection.items()
                if coalition >> player & 1)
            for player in range(N)
        ]
        assert coverage == [total] * N

    dual_worths = {}
    for game, collection in ((1, collection_A), (2, collection_B)):
        for coalition, weight in collection.items():
            add(dual_worths, ("b", coalition), weight)
            if game == 1 and coalition == A:
                add(dual_worths, ("d", "A"), weight)
            if game == 2 and coalition == B:
                add(dual_worths, ("d", "B"), weight)
    circuit_worths = {}
    for game, coalition in circuit["core"]:
        add(circuit_worths, ("b", coalition), F(1))
        if game == 1 and coalition == A:
            add(circuit_worths, ("d", "A"), F(1))
        if game == 2 and coalition == B:
            add(circuit_worths, ("d", "B"), F(1))
    assert dual_worths == circuit_worths


def verify_type_iii_balanced_dual(permutation):
    circuit = permute_circuit(TYPE_III, permutation)
    raw_collections = (
        {3:F(1,2), 8:F(1,2), 20:F(1,2)},
        {7:F(1), 8:F(1,2), 14:F(1,2), 18:F(1,2),
         20:F(1,2), 25:F(1)},
        {3:F(1,2), 5:F(1), 14:F(1,2), 18:F(1,2), 24:F(1)},
    )
    collections = tuple(
        {permute_mask(S, permutation): weight for S, weight in collection.items()}
        for collection in raw_collections
    )
    for collection, total in zip(collections, (F(1,2), F(2), F(3,2))):
        coverage = [
            sum(weight for coalition, weight in collection.items()
                if coalition >> player & 1)
            for player in range(N)
        ]
        assert coverage == [total] * N
    dual_worths = {}
    for game, collection in enumerate(collections):
        for coalition, weight in collection.items():
            add(dual_worths, ("b", coalition), weight)
            if game == 1 and coalition == A:
                add(dual_worths, ("d", "A"), weight)
            if game == 2 and coalition == B:
                add(dual_worths, ("d", "B"), weight)
    circuit_worths = {}
    for game, coalition in circuit["core"]:
        add(circuit_worths, ("b", coalition), F(1))
        if game == 1 and coalition == A:
            add(circuit_worths, ("d", "A"), F(1))
        if game == 2 and coalition == B:
            add(circuit_worths, ("d", "B"), F(1))
    assert dual_worths == circuit_worths


def verify():
    for prototype in (TYPE_I, TYPE_II, TYPE_III):
        verify_exact_circuit(prototype)
    orbit_I, orbit_II, orbit_III = set(), set(), set()
    for permutation in preserving_permutations():
        circuit_I = permute_circuit(TYPE_I, permutation)
        circuit_II = permute_circuit(TYPE_II, permutation)
        circuit_III = permute_circuit(TYPE_III, permutation)
        verify_stationarity(circuit_I)
        verify_stationarity(circuit_II)
        verify_stationarity(circuit_III)
        verify_type_ii_balanced_dual(permutation)
        verify_type_iii_balanced_dual(permutation)
        orbit_I.add(circuit_signature(circuit_I))
        orbit_II.add(circuit_signature(circuit_II))
        orbit_III.add(circuit_signature(circuit_III))
    assert len(orbit_I) == 6
    assert len(orbit_II) == 12
    assert len(orbit_III) == 12
    new_orbits = {}
    new_totals = {}
    for prototype in NEW_BALANCED_TYPES:
        verify_exact_circuit(prototype)
        orbit = set()
        canonical_totals = verify_generic_balanced_dual(prototype)
        for permutation in preserving_permutations():
            circuit = permute_circuit(prototype, permutation)
            verify_stationarity(circuit)
            verify_generic_balanced_dual(circuit)
            orbit.add(circuit_signature(circuit))
        assert len(orbit) == 12
        new_orbits[prototype["name"]] = len(orbit)
        new_totals[prototype["name"]] = canonical_totals

    print("NINE DISJOINT CIRCUIT TYPES VERIFIED")
    print("  Type I orbit size: 6 (requires exactness neutralization)")
    print("  Type II orbit size: 12 (neutralized by endpoint balancedness)")
    print("  Type II balanced collections have weights 5/2 and 3/2")
    print("  Type III orbit size: 12 (neutralized by balancedness)")
    print("  Type III balanced collections have weights 1/2, 2, and 3/2")
    for name in ("IV", "V", "VI", "VII", "VIII", "IX"):
        print(
            f"  Type {name} orbit size: {new_orbits[name]} "
            f"(neutralized by exactly verified balanced collections; "
            f"canonical totals {new_totals[name]})"
        )


if __name__ == "__main__":
    verify()
