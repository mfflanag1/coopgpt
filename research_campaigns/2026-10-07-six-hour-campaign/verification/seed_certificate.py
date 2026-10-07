#!/usr/bin/env python3
"""Exact, deliberately tiny all-real-profile seed checker; Python 3.8+.

Standalone standard library. No report grid is used. The checker enumerates
all realizable ternary sign faces incrementally, using exact vertex LPs on
the normalized report simplex. Strict feasibility is certified by averaging
all closure vertices: each strict linear constraint must have positive maximum.
Every closure objective retains its originating face's frozen winner/cap rule.

The main routine runs small complementary-resource fixtures and emits one JSON
object. All checks stay active under -O. No files are written. Functions accept
arbitrary explicit rational nonnegative min-linear forms, but enumeration is
only intended for tiny dimensions; no polynomial practicality is claimed.
"""

from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
from math import gcd
import json
import sys


COUNTS = Counter()


class VerificationError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def dot(a, b):
    return sum((x*y for x, y in zip(a, b)), Q(0))


def add(*vectors):
    return tuple(sum((vector[j] for vector in vectors), Q(0))
                 for j in range(len(vectors[0])))


def scale(vector, factor):
    return tuple(factor*x for x in vector)


def sub(a, b):
    return add(a, scale(b, -1))


def lcm(a, b):
    return abs(a*b)//gcd(a, b)


def canonical_hyperplane(vector):
    denominator = 1
    for x in vector:
        denominator = lcm(denominator, x.denominator)
    integers = [int(x*denominator) for x in vector]
    common = 0
    for x in integers:
        common = gcd(common, abs(x))
    if common == 0:
        return None
    integers = [x//common for x in integers]
    first = next(x for x in integers if x)
    if first < 0:
        integers = [-x for x in integers]
    return tuple(map(Q, integers))


def rref(rows, dimension):
    """Return independent augmented equality rows, or None if inconsistent."""
    matrix = [list(row)+[rhs] for row, rhs in rows]
    rank = 0
    for column in range(dimension):
        pivot = next((j for j in range(rank, len(matrix)) if matrix[j][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        factor = matrix[rank][column]
        matrix[rank] = [x/factor for x in matrix[rank]]
        for j in range(len(matrix)):
            if j == rank or not matrix[j][column]:
                continue
            factor = matrix[j][column]
            matrix[j] = [x-factor*y for x, y in zip(matrix[j], matrix[rank])]
        rank += 1
    if any(not any(row[:dimension]) and row[-1] != 0 for row in matrix):
        return None
    return tuple((tuple(row[:dimension]), row[-1]) for row in matrix[:rank])


def solve_square(rows, dimension):
    reduced = rref(rows, dimension)
    if reduced is None or len(reduced) != dimension:
        return None
    return tuple(rhs for _, rhs in reduced)


def affine_on_simplex(form):
    """Eliminate final report coordinate b_p=1-sum_{h<p}b_h."""
    return tuple(x-form[-1] for x in form[:-1]), -form[-1]


def full_report(reduced):
    return tuple(reduced)+(Q(1)-sum(reduced, Q(0)),)


class Arrangement:
    def __init__(self, technology):
        self.technology = technology
        self.p = technology.p
        self.dimension = self.p-1
        candidates = set()
        for mask in technology.masks:
            for v, w in combinations(range(technology.k), 2):
                form = canonical_hyperplane(sub(technology.linear(mask, v), technology.linear(mask, w)))
                if form is not None:
                    candidates.add(form)
        for owner in range(technology.n):
            for v in range(technology.k):
                for w in range(technology.k):
                    form = canonical_hyperplane(sub(technology.linear(1 << owner, v),
                                                   technology.linear(technology.full_mask, w)))
                    if form is not None:
                        candidates.add(form)
        self.forms = tuple(sorted(candidates))
        self.affine_forms = tuple(affine_on_simplex(form) for form in self.forms)
        self.vertex_cache = {}
        self.faces = self.enumerate_faces()

    def vertices(self, signs):
        if signs in self.vertex_cache:
            return self.vertex_cache[signs]
        r = self.dimension
        equalities = []
        inequalities = [(tuple(Q(int(h == j)) for h in range(r)), Q(0)) for j in range(r)]
        inequalities.append((tuple(Q(-1) for _ in range(r)), Q(-1)))
        for sign, (row, rhs) in zip(signs, self.affine_forms):
            if sign == 0:
                equalities.append((row, rhs))
            else:
                inequalities.append((scale(row, sign), sign*rhs))
        basis = rref(equalities, r)
        if basis is None:
            result = ()
        else:
            inequalities = tuple(dict.fromkeys(inequalities))
            result_set = set()
            for active in combinations(inequalities, r-len(basis)):
                solution = solve_square(basis+active, r)
                if solution is not None and all(dot(row, solution) >= rhs for row, rhs in inequalities):
                    result_set.add(full_report(solution))
            result = tuple(sorted(result_set))
        self.vertex_cache[signs] = result
        COUNTS["exact_vertex_LPs"] += 1
        COUNTS["enumerated_closure_vertices_with_repetition"] += len(result)
        return result

    def strict_witness(self, signs, vertices):
        if not vertices:
            return None
        witness = tuple(sum((v[h] for v in vertices), Q(0))/len(vertices) for h in range(self.p))
        for sign, form in zip(signs, self.forms):
            value = dot(form, witness)
            if sign == 0:
                require(value == 0, "equality violated by closure-vertex average")
            elif sign*value <= 0:
                return None
        return witness

    def enumerate_faces(self):
        initial_vertices = tuple(tuple(Q(int(h == j)) for h in range(self.p)) for j in range(self.p))
        current = [((), initial_vertices, tuple(Q(1, self.p) for _ in range(self.p)))]
        for index, form in enumerate(self.forms):
            following = []
            for signs, parent_vertices, _ in current:
                values = tuple(dot(form, vertex) for vertex in parent_vertices)
                low, high = min(values), max(values)
                for sign in (-1, 0, 1):
                    child = signs+(sign,)
                    COUNTS["incremental_sign_branches_considered"] += 1
                    if (sign == 1 and high <= 0) or (sign == -1 and low >= 0):
                        COUNTS["unrealizable_sign_branches_rejected"] += 1
                        continue
                    if sign == 0 and (low > 0 or high < 0):
                        COUNTS["unrealizable_sign_branches_rejected"] += 1
                        continue
                    if ((sign == 1 and low >= 0) or (sign == -1 and high <= 0)
                            or (sign == 0 and low == high == 0)):
                        vertices = parent_vertices
                        COUNTS["unchanged_polytope_reuses"] += 1
                    elif sign == 0 and (low == 0 or high == 0):
                        vertices = tuple(v for v, value in zip(parent_vertices, values) if value == 0)
                        COUNTS["supporting_face_vertex_reuses"] += 1
                    else:
                        vertices = self.vertices(child)
                    witness = self.strict_witness(child, vertices)
                    if witness is None:
                        COUNTS["unrealizable_sign_branches_rejected"] += 1
                        continue
                    following.append((child, vertices, witness))
            current = following
            require(current, "arrangement lost all normalized reports")
        require(len({signs for signs, _, _ in current}) == len(current), "duplicate sign face")
        COUNTS["realizable_final_faces"] += len(current)
        COUNTS["faces_with_at_least_one_tie"] += sum(0 in signs for signs, _, _ in current)
        return tuple(current)


class Technology:
    def __init__(self, owners, forms):
        self.n = owners
        self.forms = tuple(tuple(map(Q, form)) for form in forms)
        require(owners >= 1 and self.forms and self.forms[0], "nonempty technology and owner set")
        self.d, self.k = len(self.forms[0]), len(self.forms)
        require(all(len(form) == self.d for form in self.forms), "form dimensions")
        require(all(x >= 0 for form in self.forms for x in form), "negative technology coefficient")
        self.p = self.n*self.d
        self.full_mask = (1 << self.n)-1
        self.masks = tuple(range(1 << self.n))
        self.linear_forms = {(mask, v): tuple(self.forms[v][h % self.d] if mask & (1 << (h//self.d)) else Q(0)
                                             for h in range(self.p))
                             for mask in self.masks for v in range(self.k)}

    def linear(self, mask, vertex):
        return self.linear_forms[mask, vertex]

    def winner(self, mask, report):
        scores = [dot(self.linear(mask, v), report) for v in range(self.k)]
        return scores.index(min(scores))

    def value(self, mask, report):
        return min(dot(self.linear(mask, v), report) for v in range(self.k))


class SeedRule:
    def __init__(self, technology, masks, theta, eta, budget):
        self.technology = technology
        self.masks = tuple(masks)
        self.theta = tuple(map(Q, theta))
        self.eta, self.budget = Q(eta), Q(budget)
        require(self.masks and all(mask in technology.masks for mask in self.masks), "invalid seed")
        require(len(self.theta) == technology.n+1 and all(0 <= x <= 1 for x in self.theta), "invalid posterior coefficients")
        require(self.eta >= 0, "negative cushion")

    def frozen(self, witness):
        t = self.technology
        winners = {mask: t.winner(mask, witness) for mask in t.masks}
        values = {mask: t.linear(mask, winners[mask]) for mask in t.masks}
        total = values[t.full_mask]
        payments = []
        for owner in range(t.n):
            payment = scale(total, self.eta/t.n)
            for mask in self.masks:
                off, on = mask & ~(1 << owner), mask | (1 << owner)
                contribution = t.linear(1 << owner, winners[off])
                cap = contribution if dot(contribution, witness) <= dot(total, witness) else total
                weight = self.theta[bin(mask).count("1")]
                sample = add(scale(cap, weight), scale(sub(values[on], values[off]), 1-weight))
                payment = add(payment, scale(sample, Q(1, len(self.masks))))
            payments.append(payment)
        return tuple(payments), values

    def actual(self, report):
        t = self.technology
        total = t.value(t.full_mask, report)
        payments = []
        for owner in range(t.n):
            payment = self.eta*total/t.n
            for mask in self.masks:
                off, on = mask & ~(1 << owner), mask | (1 << owner)
                winner = t.winner(off, report)
                contribution = dot(t.linear(1 << owner, winner), report)
                cap = min(contribution, total)
                delta = t.value(on, report)-t.value(off, report)
                weight = self.theta[bin(mask).count("1")]
                payment += (weight*cap+(1-weight)*delta)/len(self.masks)
            payments.append(payment)
        return tuple(payments)


def encode_report(technology, report):
    return [[str(report[i*technology.d+h]) for h in range(technology.d)] for i in range(technology.n)]


def verify_seed(arrangement, rule, inspect_boundaries=False):
    t = rule.technology
    require(arrangement.technology is t, "technology/arrangement mismatch")
    objectives = 0
    boundary_mismatches = 0
    zero_value_vertices = 0
    specification = {"seed_masks": list(rule.masks), "theta": list(map(str, rule.theta)),
                     "eta": str(rule.eta), "budget_cap": str(rule.budget)}
    for signs, vertices, witness in arrangement.faces:
        payments, values = rule.frozen(witness)
        require(tuple(dot(form, witness) for form in payments) == rule.actual(witness), "frozen witness mismatch")
        if inspect_boundaries:
            for vertex in vertices:
                frozen = tuple(dot(form, vertex) for form in payments)
                actual = rule.actual(vertex)
                boundary_mismatches += frozen != actual
                if t.value(t.full_mask, vertex) == 0:
                    require(all(value == 0 for value in frozen+actual), "T=0 closure formula nonzero")
                    zero_value_vertices += 1
                interior = tuple((x+y)/2 for x, y in zip(vertex, witness))
                require(tuple(dot(form, interior) for form in payments) == rule.actual(interior),
                        "frozen/interior actual mismatch")
        slacks = []
        for coalition in t.masks:
            paid = tuple(sum((payments[i][h] for i in range(t.n) if coalition & (1 << i)), Q(0)) for h in range(t.p))
            slacks.append(("coverage", coalition, sub(paid, values[coalition])))
        total_payment = tuple(sum((payments[i][h] for i in range(t.n)), Q(0)) for h in range(t.p))
        slacks.append(("budget", None, sub(scale(values[t.full_mask], rule.budget), total_payment)))
        for kind, coalition, slack in slacks:
            objectives += 1
            optimum, optimizer = min((dot(slack, vertex), vertex) for vertex in vertices)
            if optimum >= 0:
                continue
            witness_value = dot(slack, witness)
            mix = min(Q(1, 2), -optimum/(2*(1+abs(optimum)+abs(witness_value))))
            report = tuple((1-mix)*x+mix*y for x, y in zip(optimizer, witness))
            require(all((dot(form, report) == 0 if sign == 0 else sign*dot(form, report) > 0)
                        for sign, form in zip(signs, arrangement.forms)), "counterexample outside originating face")
            actual = rule.actual(report)
            if kind == "coverage":
                actual_slack = sum((actual[i] for i in range(t.n) if coalition & (1 << i)), Q(0))-t.value(coalition, report)
            else:
                actual_slack = rule.budget*t.value(t.full_mask, report)-sum(actual, Q(0))
            require(actual_slack == dot(slack, report) < 0, "returned report is not an actual violation")
            return {"accepted": False, "rule": specification, "kind": kind, "coalition_mask": coalition,
                    "report": encode_report(t, report), "actual_payments": list(map(str, actual)),
                    "actual_slack": str(actual_slack), "closure_optimum": str(optimum),
                    "originating_signs": list(signs), "objectives_checked": objectives}
    COUNTS["accepted_objective_LPs"] += objectives
    return {"accepted": True, "rule": specification, "faces_checked": len(arrangement.faces), "objectives_checked": objectives,
            "closure_boundary_payment_mismatches": boundary_mismatches,
            "zero_value_closure_vertices_checked": zero_value_vertices}


def required_cushion(arrangement, rule, substitute_actual_boundaries=False):
    """Exact diagnostic to expose an unsound boundary substitution if present."""
    require(rule.eta == 0, "cushion diagnostic needs an uncushioned rule")
    t = rule.technology
    required = Q(0)
    for _, vertices, witness in arrangement.faces:
        payments, values = rule.frozen(witness)
        for vertex in vertices:
            total = t.value(t.full_mask, vertex)
            if not total:
                continue
            paid = rule.actual(vertex) if substitute_actual_boundaries else tuple(dot(form, vertex) for form in payments)
            for coalition in t.masks[1:]:
                count = bin(coalition).count("1")
                missing = t.value(coalition, vertex)-sum((paid[i] for i in range(t.n) if coalition & (1 << i)), Q(0))
                required = max(required, t.n*missing/(count*total))
    return required


def main():
    caught = False
    try:
        require(False, "deliberate -O calibration")
    except VerificationError:
        caught = True
    require(caught, "checks disabled")
    require(solve_square((((Q(2), Q(1)), Q(1)), ((Q(1), Q(-1)), Q(2))), 2) == (Q(1), Q(-1)), "solver calibration")
    require(solve_square((((Q(1), Q(1)), Q(1)), ((Q(2), Q(2)), Q(2))), 2) is None, "singular solver calibration")
    # Hand-enumerable arrangement calibrations exercise both a crossing plane
    # and supporting coordinate faces, as well as zero-dimensional LPs.
    crossing = Arrangement(Technology(1, ((1, 0), (0, 1))))
    require(len(crossing.forms) == 1 and len(crossing.faces) == 3, "one-plane interval calibration")
    supporting = Arrangement(Technology(2, ((1,),)))
    require(len(supporting.forms) == 2 and len(supporting.faces) == 3, "supporting-face interval calibration")
    zero_technology = Technology(1, ((0,),))
    zero_arrangement = Arrangement(zero_technology)
    require(len(zero_arrangement.forms) == 0 and len(zero_arrangement.faces) == 1, "zero-dimensional normalization calibration")
    zero_result = verify_seed(zero_arrangement, SeedRule(zero_technology, (0,), (Q(1, 2), Q(1, 3)), 0, 0), inspect_boundaries=True)
    require(zero_result["accepted"] and zero_result["zero_value_closure_vertices_checked"] == 1, "identically zero technology")
    COUNTS["hand_enumerable_arrangement_calibrations"] += 3
    t = Technology(2, ((1, 0), (0, 1)))
    arrangement = Arrangement(t)
    require(len(arrangement.forms) == 11, "complementary arrangement inventory")
    # Exact posterior E[q | full mask] for n=2 and q uniform on (0,1/2).
    theta = (Q(3, 8), Q(5, 16), Q(11, 56))
    accepted = verify_seed(arrangement, SeedRule(t, (0,), theta, Q(5, 8), Q(2)), inspect_boundaries=True)
    require(accepted["accepted"], "known covering empty-mask seed rejected")
    rejected = verify_seed(arrangement, SeedRule(t, (0,), theta, Q(0), Q(2)))
    require(not rejected["accepted"] and rejected["kind"] == "coverage", "uncovered empty-mask seed accepted")
    corrupt_budget = verify_seed(arrangement, SeedRule(t, (0,), theta, Q(5, 8), Q(3, 2)))
    require(not corrupt_budget["accepted"] and corrupt_budget["kind"] == "budget", "corrupted budget cap accepted")
    tie_rule = verify_seed(arrangement, SeedRule(t, (1,), theta, Q(2), Q(4)), inspect_boundaries=True)
    require(tie_rule["accepted"], "large-cushion tie fixture rejected")
    require(tie_rule["closure_boundary_payment_mismatches"] > 0, "tie-boundary control was vacuous")
    boundary_diagnostics = []
    for mask in t.masks:
        base = SeedRule(t, (mask,), theta, Q(0), Q(4))
        exact = required_cushion(arrangement, base)
        naive = required_cushion(arrangement, base, substitute_actual_boundaries=True)
        item = {"mask": mask, "required_cushion_frozen_faces": str(exact),
                "required_cushion_actual_boundary_substitution": str(naive)}
        if naive < exact:
            eta = (exact+naive)/2
            failure = verify_seed(arrangement, SeedRule(t, (mask,), theta, eta, Q(4)))
            require(not failure["accepted"] and failure["kind"] == "coverage", "boundary-substitution negative control failed")
            item["naive_false_acceptance_cushion"] = str(eta)
            item["true_counterexample"] = failure
            COUNTS["incorrect_boundary_substitution_controls_rejected"] += 1
        boundary_diagnostics.append(item)
    require(accepted["zero_value_closure_vertices_checked"] > 0, "T=0 test was vacuous")
    output = {"status": "PASS", "technology": {"owners": t.n, "resource_types": t.d,
              "ordered_forms": [[str(x) for x in form] for form in t.forms],
              "hyperplanes": len(arrangement.forms), "realizable_faces": len(arrangement.faces)},
              "accepted_seed": accepted, "rejected_seed": rejected,
              "corrupt_budget_control": corrupt_budget, "tie_boundary_fixture": tie_rule,
              "zero_technology_fixture": zero_result,
              "boundary_substitution_diagnostics": boundary_diagnostics,
              "counts": dict(sorted(COUNTS.items())),
              "scope": "Exhaustive all-real-profile checks for the listed fixed tiny configurations; generic rational checker, no report grid, no large-dimension performance claim."}
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except VerificationError as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}))
        sys.exit(1)
