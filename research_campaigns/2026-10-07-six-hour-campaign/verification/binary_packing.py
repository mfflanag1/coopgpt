#!/usr/bin/env python3
"""Finite exact checks for the binary resource-packing Bernoulli mechanism.

Stdlib only; Python 3.8+.  All LP arithmetic uses Fraction.  Dual and primal
vertices are independently enumerated from active constraints.  Every check is
always active, including under ``python -O``.  These tests are finite evidence,
not a proof of a general or asymptotic theorem.
"""

from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations
import json
import sys


COUNTS = Counter()


class VerificationError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def dot(left, right):
    return sum((a * b for a, b in zip(left, right)), Q(0))


def solve_square(rows, rhs):
    """Unique rational solution, or None for a singular square system."""
    size = len(rows)
    require(len(rhs) == size, "solver RHS dimension")
    require(all(len(row) == size for row in rows), "solver matrix dimension")
    matrix = [[Q(value) for value in row] + [Q(value)]
              for row, value in zip(rows, rhs)]
    for column in range(size):
        pivot = next((row for row in range(column, size)
                      if matrix[row][column]), None)
        if pivot is None:
            return None
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        scale = matrix[column][column]
        matrix[column] = [value / scale for value in matrix[column]]
        for row in range(size):
            if row == column or not matrix[row][column]:
                continue
            scale = matrix[row][column]
            matrix[row] = [value - scale * base
                           for value, base in zip(matrix[row], matrix[column])]
    return tuple(matrix[row][-1] for row in range(size))


def canonical_recipes(n, recipes):
    normalized = tuple(sorted(set(tuple(sorted(set(recipe)))
                                  for recipe in recipes)))
    require(n >= 1, "at least one resource is required")
    require(all(recipe for recipe in normalized), "empty recipe is forbidden")
    require(all(0 <= e < n for recipe in normalized for e in recipe),
            "recipe resource out of range")
    return normalized


@lru_cache(maxsize=None)
def dual_vertices(n, recipes):
    """Vertices of w >= 0, sum_{e in recipe} w_e >= 1."""
    inequalities = []
    for e in range(n):
        inequalities.append((tuple(Q(int(e == h)) for h in range(n)), Q(0)))
    for recipe in recipes:
        inequalities.append((tuple(Q(int(e in recipe)) for e in range(n)), Q(1)))
    result = set()
    for active in combinations(inequalities, n):
        solution = solve_square([row for row, _ in active],
                                [bound for _, bound in active])
        if solution is not None and all(dot(row, solution) >= bound
                                        for row, bound in inequalities):
            result.add(solution)
    require(result, "dual enumeration returned no vertex")
    require(all(Q(0) <= value <= Q(1) for vertex in result for value in vertex),
            "dual vertex outside [0,1]")
    COUNTS["dual_systems_enumerated"] += 1
    COUNTS["dual_vertices_enumerated"] += len(result)
    return tuple(sorted(result))


@lru_cache(maxsize=None)
def primal_vertices(n, recipes, capacities):
    """Vertices of x >= 0 and recipe use of each resource <= capacity."""
    m = len(recipes)
    require(len(capacities) == n and all(value >= 0 for value in capacities),
            "invalid primal capacities")
    # Express all inequalities as row*x <= bound, independently of the dual.
    inequalities = []
    for j in range(m):
        inequalities.append((tuple(Q(-int(j == h)) for h in range(m)), Q(0)))
    for e in range(n):
        inequalities.append((tuple(Q(int(e in recipe)) for recipe in recipes),
                             capacities[e]))
    result = set()
    for active in combinations(inequalities, m):
        solution = solve_square([row for row, _ in active],
                                [bound for _, bound in active])
        if solution is not None and all(dot(row, solution) <= bound
                                        for row, bound in inequalities):
            result.add(solution)
    require(result, "primal enumeration returned no vertex")
    COUNTS["primal_systems_enumerated"] += 1
    COUNTS["primal_vertices_enumerated"] += len(result)
    return tuple(sorted(result))


def replace(values, e, report):
    return tuple(Q(report) if h == e else value for h, value in enumerate(values))


def mask_vector(values, mask):
    return tuple(value if mask & (1 << e) else Q(0)
                 for e, value in enumerate(values))


class Technology:
    def __init__(self, name, n, recipes):
        self.name = name
        self.n = n
        self.recipes = canonical_recipes(n, recipes)
        self.vertices = dual_vertices(n, self.recipes)
        self.restricted = tuple(dual_vertices(n, tuple(recipe for recipe in self.recipes
                                                       if e in recipe))
                                for e in range(n))
        self.profile_cache = {}
        self.effective_cache = {}
        self.qs = (Q(1, 2), Q(1, 3))
        self.masks = tuple(range(1 << n))
        self.probabilities = {
            q: tuple(q ** (n - bin(mask).count("1"))
                     * (1 - q) ** bin(mask).count("1") for mask in self.masks)
            for q in self.qs
        }
        for q, probabilities in self.probabilities.items():
            require(sum(probabilities) == 1, "mask probabilities do not sum to 1")
            for e in range(n):
                require(sum(probabilities[mask] for mask in self.masks
                            if not mask & (1 << e)) == q,
                        "conditional mask probability is not q")
        COUNTS["technologies"] += 1

    def value(self, capacities):
        return min(dot(capacities, vertex) for vertex in self.vertices)

    def effective(self, capacities):
        if capacities not in self.effective_cache:
            self.effective_cache[capacities] = tuple(
                min(dot(capacities, vertex) for vertex in vertices)
                for vertices in self.restricted)
        return self.effective_cache[capacities]

    def context(self, capacities):
        return "%s c=%s" % (self.name, tuple(str(value) for value in capacities))

    def profile(self, capacities):
        capacities = tuple(Q(value) for value in capacities)
        if capacities in self.profile_cache:
            return self.profile_cache[capacities]
        require(len(capacities) == self.n and all(value >= 0 for value in capacities),
                "invalid profile")
        context = self.context(capacities)
        total = self.value(capacities)
        effective = self.effective(capacities)
        require(all(Q(0) <= d <= min(c, total) for d, c in zip(effective, capacities)),
                "effective bounds: " + context)
        require(self.value(effective) == total, "effective value: " + context)
        require(self.effective(effective) == effective, "effective idempotence: " + context)
        COUNTS["profiles"] += 1
        COUNTS["effective_coordinate_bounds"] += self.n
        COUNTS["effective_idempotence_profiles"] += 1

        optimal_families = []
        winners = []
        raw_mask_values = []
        for mask in self.masks:
            raw = mask_vector(capacities, mask)
            normalized = mask_vector(effective, mask)
            scores = tuple(dot(normalized, vertex) for vertex in self.vertices)
            minimum = min(scores)
            raw_value = self.value(raw)
            require(minimum == raw_value, "masked value preservation: " + context)
            require(self.effective(raw) == self.effective(normalized),
                    "masked effective preservation: " + context)
            require(minimum <= total, "selected masked score exceeds T: " + context)
            family = tuple(index for index, score in enumerate(scores) if score == minimum)
            optimal_families.append(family)
            winners.append(self.vertices[family[0]])
            raw_mask_values.append(raw_value)
            COUNTS["masked_value_equalities"] += 1
            COUNTS["masked_effective_coordinate_equalities"] += self.n
            COUNTS["selected_score_bounds"] += 1

        for e in range(self.n):
            for off_mask in self.masks:
                if off_mask & (1 << e):
                    continue
                on_mask = off_mask | (1 << e)
                require(winners[off_mask][e] >= winners[on_mask][e],
                        "revealed preference: " + context)
                # Stronger tie-independent claim whenever D_e is positive.
                if effective[e] > 0:
                    require(min(self.vertices[j][e] for j in optimal_families[off_mask])
                            >= max(self.vertices[j][e] for j in optimal_families[on_mask]),
                            "all-optima revealed preference: " + context)
                    COUNTS["all_optima_revealed_preference_pairs"] += 1
                else:
                    require(optimal_families[off_mask] == optimal_families[on_mask],
                            "zero effective-capacity tie families: " + context)
                COUNTS["selected_revealed_preference_pairs"] += 1

        payments = {}
        for q, probabilities in self.probabilities.items():
            z = tuple(effective[e] * sum((probabilities[mask] * winners[mask][e]
                                         for mask in self.masks), Q(0))
                      for e in range(self.n))
            p = tuple(effective[e] * sum((probabilities[mask] * winners[mask][e] / q
                                         for mask in self.masks if not mask & (1 << e)), Q(0))
                      for e in range(self.n))
            require(all(Q(0) <= ze <= pe and q * pe <= ze
                        for ze, pe in zip(z, p)), "p/z sandwich: " + context)
            COUNTS["payment_coordinate_sandwiches"] += self.n
            for coalition in self.masks:
                coalition_value = raw_mask_values[coalition]
                require(sum(z[e] for e in range(self.n) if coalition & (1 << e))
                        >= coalition_value, "z coalition coverage: " + context)
                require(sum(p[e] for e in range(self.n) if coalition & (1 << e))
                        >= coalition_value, "p coalition coverage: " + context)
                COUNTS["z_coalition_coverage_checks"] += 1
                COUNTS["p_coalition_coverage_checks"] += 1
            payments[q] = (z, p)

        for vertex in self.vertices:
            require(all(effective[e] * vertex[e] <= total for e in range(self.n)),
                    "normalized Chernoff coefficient bound: " + context)
            COUNTS["coefficient_bounds"] += self.n
            for coalition in self.masks:
                require(dot(mask_vector(effective, coalition), vertex)
                        >= raw_mask_values[coalition],
                        "vertex-by-vertex coalition certificate: " + context)
                COUNTS["vertex_coalition_certificates"] += 1

        result = {"D": effective, "T": total, "families": tuple(optimal_families),
                  "payments": payments}
        self.profile_cache[capacities] = result
        return result

    def own_report_family(self, context, e):
        reports = (Q(0), Q(1, 3), Q(1), Q(2), Q(5, 2))
        profiles = [self.profile(replace(context, e, report)) for report in reports]
        zero = profiles[0]
        high = profiles[-1]
        reference = profiles[1]
        for index in range(1, len(reports)):
            report = reports[index]
            current = profiles[index]
            for h in range(self.n):
                require(current["D"][h] >= zero["D"][h]
                        + report / reports[-1] * (high["D"][h] - zero["D"][h]),
                        "strictness concavity: " + self.name)
                require((current["D"][h] > zero["D"][h])
                        == (high["D"][h] > zero["D"][h]),
                        "positive-report support invariance: " + self.name)
                COUNTS["strict_support_coordinate_checks"] += 1
            for mask in self.masks:
                if mask & (1 << e):
                    continue
                require(current["families"][mask] == reference["families"][mask],
                        "ENTIRE conditional-zero optimal family changed: " + self.name)
                COUNTS["conditional_zero_entire_family_comparisons"] += 1
                # Check the proof's stronger exact characterization of this family.
                expected = tuple(j for j in zero["families"][mask]
                                 if all(not (mask & (1 << h)) or self.vertices[j][h] == 0
                                        or current["D"][h] == zero["D"][h]
                                        for h in range(self.n)))
                require(current["families"][mask] == expected,
                        "conditional-zero family characterization: " + self.name)
                COUNTS["conditional_zero_family_characterizations"] += 1
            previous = profiles[index - 1]
            for q in self.qs:
                require(previous["payments"][q][1][e] <= current["payments"][q][1][e],
                        "own-report p monotonicity: " + self.name)
                COUNTS["own_payment_monotonicity_checks"] += 1
                for lower in profiles[:index + 1]:
                    require(lower["payments"][q][0][e] <= current["payments"][q][1][e],
                            "finite underreport z bounded by current p: " + self.name)
                    COUNTS["finite_underreport_domination_checks"] += 1
        COUNTS["own_report_families"] += 1

    def crosscheck_primal(self, capacities):
        capacities = tuple(Q(value) for value in capacities)
        vertices = primal_vertices(self.n, self.recipes, capacities)
        total = max(sum(vertex, Q(0)) for vertex in vertices)
        effective = tuple(max(sum((vertex[j] for j, recipe in enumerate(self.recipes)
                                   if e in recipe), Q(0)) for vertex in vertices)
                          for e in range(self.n))
        require(total == self.value(capacities), "independent primal F: " + self.context(capacities))
        require(effective == self.effective(capacities),
                "independent primal D: " + self.context(capacities))
        normalized_vertices = primal_vertices(self.n, self.recipes, effective)
        require(vertices == normalized_vertices,
                "entire feasible packing polytope preservation: " + self.context(capacities))
        COUNTS["primal_dual_value_crosschecks"] += 1
        COUNTS["primal_effective_coordinate_crosschecks"] += self.n
        COUNTS["primal_polytope_vertex_set_equalities"] += 1


def base_profiles(n):
    zero = (Q(0),) * n
    one = (Q(1),) * n
    positive = tuple((Q(1, 5), Q(7, 6), Q(3), Q(2, 3), Q(5, 2))[e % 5]
                     for e in range(n))
    mixed = tuple((Q(0), Q(2), Q(5, 4), Q(0), Q(7, 3))[e % 5]
                  for e in range(n))
    profiles = {zero, one, positive, mixed, (Q(1, 2),) * n}
    for e in range(n):
        profiles.add(replace(zero, e, Q(1)))
        profiles.add(replace(one, e, Q(0)))
    return tuple(sorted(profiles)), (one, positive, mixed)


def calibrate():
    require(solve_square(((2, 1), (1, -1)), (1, 2)) == (Q(1), Q(-1)),
            "Gaussian solver calibration")
    require(solve_square(((1, 1), (2, 2)), (1, 2)) is None,
            "singular solver calibration")
    caught = False
    try:
        require(False, "deliberate always-active check")
    except VerificationError:
        caught = True
    require(caught, "require is disabled")
    caught = False
    try:
        canonical_recipes(1, ((),))
    except VerificationError:
        caught = True
    require(caught, "empty recipes accepted")
    triangle = canonical_recipes(3, ((0, 1), (0, 2), (1, 2)))
    expected = tuple(sorted(((Q(0), Q(1), Q(1)), (Q(1), Q(0), Q(1)),
                             (Q(1), Q(1), Q(0)), (Q(1, 2),) * 3)))
    require(dual_vertices(3, triangle) == expected, "triangle dual vertices")
    require(max(sum(v, Q(0)) for v in primal_vertices(3, triangle, (Q(1),) * 3))
            == Q(3, 2), "triangle fractional packing optimum")
    COUNTS["calibration_checks"] += 6


def simple_path_recipes(edges, pairs):
    recipes = set()
    for source, sink in pairs:
        def visit(node, seen, used):
            if node == sink:
                recipes.add(tuple(sorted(used)))
                return
            for e, (tail, head) in enumerate(edges):
                if tail == node and head not in seen:
                    visit(head, seen | {head}, used + (e,))
        visit(source, {source}, ())
    return tuple(sorted(recipes))


def graph_application_checks():
    # Back arc participates in a circulation, but no simple source-sink path.
    cyclic = ((0, 1), (1, 2), (1, 0), (0, 2))
    recipes = simple_path_recipes(cyclic, ((0, 2),))
    require(recipes == ((0, 1), (3,)), "cyclic path enumeration")
    expected = ((Q(0), Q(1), Q(0), Q(1)), (Q(1), Q(0), Q(0), Q(1)))
    require(dual_vertices(4, recipes) == expected, "cyclic graph dual cuts")
    technology = Technology("cyclic-dual-check", 4, recipes)
    require(technology.effective((Q(1),) * 4)[2] == 0,
            "circulation-only resource incorrectly included in path usage")
    triangle_edges = ((0, 1), (1, 2), (2, 0))
    multi = simple_path_recipes(triangle_edges, ((0, 2), (1, 0), (2, 1)))
    require(multi == ((0, 1), (0, 2), (1, 2)), "multicommodity path enumeration")
    require((Q(1, 2),) * 3 in dual_vertices(3, multi),
            "multicommodity fractional dual vertex missing")
    COUNTS["graph_application_checks"] += 5
    return recipes, multi


def main():
    calibrate()
    cyclic, multicommodity = graph_application_checks()
    specifications = (
        ("nested-recipes", 2, ((0,), (0, 1))),
        ("cyclic-path-packing", 4, cyclic),
        ("three-commodity-cycle", 3, multicommodity),
        ("empty-family", 2, ()),
        ("single-resource", 1, ((0,),)),
        ("serial-pair", 2, ((0, 1),)),
        ("parallel-three", 3, ((0,), (1,), (2,))),
        ("triangle-fractional", 3, ((0, 1), (0, 2), (1, 2))),
        ("square-diagonal", 4, ((0, 1), (1, 2), (2, 3), (0, 3), (0, 2))),
        ("tetrahedron-triples", 4, ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3))),
        ("unused-resource", 4, ((0, 1), (1, 2))),
        ("five-cycle", 5, ((0, 1), (1, 2), (2, 3), (3, 4), (0, 4))),
        ("five-mixed-clutter", 5, ((0, 1), (0, 2, 3), (1, 2, 4), (3, 4))),
        ("five-triple-clutter", 5, ((0, 1, 2), (0, 3, 4), (1, 2, 4), (2, 3, 4))),
    )
    technologies = [Technology(*specification) for specification in specifications]
    inventory = []
    for technology in technologies:
        profiles, contexts = base_profiles(technology.n)
        for capacities in profiles:
            technology.profile(capacities)
        for context in contexts:
            for e in range(technology.n):
                technology.own_report_family(context, e)
        # Independently enumerate the primal on every mask of a heterogeneous
        # positive profile, plus unit, zero, and mixed-capacity profiles.
        primal_profiles = {mask_vector(contexts[1], mask) for mask in technology.masks}
        primal_profiles.update((contexts[0], contexts[2], (Q(0),) * technology.n))
        for capacities in sorted(primal_profiles):
            technology.crosscheck_primal(capacities)
        inventory.append({"name": technology.name, "resources": technology.n,
                          "recipes": len(technology.recipes),
                          "dual_vertices": len(technology.vertices),
                          "tested_profiles": len(technology.profile_cache),
                          "primal_test_profiles": len(primal_profiles)})
    print("PASS: exact finite binary resource-packing checks")
    print("q values: 1/2, 1/3; own-report grid: 0, 1/3, 1, 2, 5/2")
    print(json.dumps({"technologies": inventory, "counts": dict(sorted(COUNTS.items()))},
                     indent=2, sort_keys=True))
    print("Finite verification only; no general or asymptotic claim is inferred.")


if __name__ == "__main__":
    try:
        main()
    except VerificationError as error:
        print("FAIL: " + str(error), file=sys.stderr)
        sys.exit(1)
