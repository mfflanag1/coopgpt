#!/usr/bin/env python3
"""Portable exact checks for SIMPLE_DAG_SHARP_LOWER.txt (stdlib only).

All checks use explicit exceptions and remain active under python -O.
No files are read or written. The weighted-row bookkeeping follows the
manuscript's verification/sharp/{verify,poisson_certificate}.py, with the
strategic auxiliary budget added explicitly; it has no runtime dependency
on those files. Finite checks supplement, rather than establish, asymptotics.
"""

from collections import defaultdict, deque
from fractions import Fraction as F
from itertools import product
from math import factorial
import argparse
import time


class VerificationError(Exception):
    pass


def check(condition, message):
    if not condition:
        raise VerificationError(message)


def maxflow(edges, capacities, source, sink):
    """Independent integer Edmonds-Karp; vertex labels need not be topological."""
    n = 1 + max(max(edge) for edge in edges)
    residual = [[0] * n for _ in range(n)]
    for (u, v), capacity in zip(edges, capacities):
        check(type(capacity) is int and capacity >= 0, "integer capacity")
        residual[u][v] += capacity
    value = 0
    while True:
        parent = [-1] * n
        parent[source] = source
        queue = deque([source])
        while queue and parent[sink] < 0:
            u = queue.popleft()
            for v, capacity in enumerate(residual[u]):
                if capacity and parent[v] < 0:
                    parent[v] = u
                    queue.append(v)
        if parent[sink] < 0:
            return value
        amount = sum(capacities)
        v = sink
        while v != source:
            amount = min(amount, residual[parent[v]][v])
            v = parent[v]
        v = sink
        while v != source:
            u = parent[v]
            residual[u][v] -= amount
            residual[v][u] += amount
            v = u
        value += amount


def make_module(m, fan_count, offset=0):
    a = offset
    left = list(range(a + 1, a + 1 + fan_count))
    inputs = list(range(a + 1 + fan_count, a + 1 + fan_count + m))
    outputs = list(range(a + 1 + fan_count + m, a + 1 + fan_count + 2 * m))
    right = list(range(a + 1 + fan_count + 2 * m,
                       a + 1 + 2 * fan_count + 2 * m))
    b = a + 1 + 2 * fan_count + 2 * m
    edges = []
    kinds = []

    def add(u, v, kind):
        edges.append((u, v))
        kinds.append(kind)

    for i in range(fan_count):
        add(a, left[i], ("al", i))
    for i in range(fan_count):
        for j in range(m):
            add(left[i], inputs[j], ("lu", i, j))
    for j in range(m):
        add(inputs[j], outputs[j], ("var", j))
    for j in range(m):
        for i in range(fan_count):
            add(outputs[j], right[i], ("vr", j, i))
    for i in range(fan_count):
        add(right[i], b, ("rb", i))
    check(len(edges) == len(set(edges)), "module is not simple")
    check(all(u < v for u, v in edges), "module is not acyclic")
    check(len(edges) == 2 * fan_count * m + 2 * fan_count + m,
          "module edge count")
    return edges, kinds, a, b


def make_series(k, m, fan_count):
    edges = []
    modules = []
    offset = 0
    for _ in range(k):
        local, kinds, a, b = make_module(m, fan_count, offset)
        modules.append((len(edges), kinds, a, b))
        edges.extend(local)
        offset = b
    check(len(edges) == len(set(edges)), "series graph is not simple")
    return edges, modules, 0, offset


def profile_capacities(modules, types, m):
    capacities = []
    for h, (_, kinds, _, _) in zip(types, modules):
        capacities.extend(m if kind[0] == "var" and kind[1] < h
                          else 1 if kind[0] == "var" else m * m
                          for kind in kinds)
    return capacities


def check_coalition_modules():
    coalition_checks = 0
    full_flow_checks = 0
    owner_transition_checks = 0
    for m, d in ((2, 1), (3, 2)):
        fan_count = m
        k = 2
        edges, modules, source, sink = make_series(k, m, fan_count)
        for types in product(range(d + 1), repeat=k):
            capacities = profile_capacities(modules, types, m)
            expected = min(m + (m - 1) * h for h in types)
            check(maxflow(edges, capacities, source, sink) == expected,
                  "full module flow formula")
            full_flow_checks += 1

            for pool, h in enumerate(types):
                if h == d:
                    continue
                destination_types = list(types)
                destination_types[pool] += 1
                destination = profile_capacities(modules, destination_types, m)
                changed = [e for e in range(len(edges))
                           if capacities[e] != destination[e]]
                check(len(changed) == 1, "transport changes more than one owner")
                e = changed[0]
                start, kinds, _, _ = modules[pool]
                check(kinds[e - start] == ("var", h), "transported owner identity")
                check((capacities[e], destination[e]) == (1, m),
                      "transport report levels")
                owner_transition_checks += 1

            for which in (0, 1):
                selected_variables = []
                for h in types:
                    if which == 0:
                        selected_variables.append({h})
                    elif h < d:
                        selected_variables.append(set(range(h, h + m - d + 1)))
                    else:
                        selected_variables.append({0})
                worth = (1 if which == 0 else
                         m if all(h == d for h in types) else m - d + 1)
                auxiliary_counts = [0] * len(edges)
                trials = 0
                for fans in product(range(fan_count), repeat=2 * k):
                    coalition_capacities = [0] * len(edges)
                    for pool, (start, kinds, _, _) in enumerate(modules):
                        left, right = fans[2 * pool:2 * pool + 2]
                        chosen = selected_variables[pool]
                        for local, kind in enumerate(kinds):
                            take = (
                                kind[0] == "al" and kind[1] == left
                                or kind[0] == "lu" and kind[1] == left and kind[2] in chosen
                                or kind[0] == "var" and kind[1] in chosen
                                or kind[0] == "vr" and kind[1] in chosen and kind[2] == right
                                or kind[0] == "rb" and kind[1] == right
                            )
                            if take:
                                coalition_capacities[start + local] = capacities[start + local]
                                if kind[0] != "var":
                                    auxiliary_counts[start + local] += 1
                    check(maxflow(edges, coalition_capacities, source, sink) == worth,
                          "selected fan coalition worth")
                    trials += 1
                    coalition_checks += 1
                check(max(auxiliary_counts) * fan_count <= trials,
                      "auxiliary inclusion exceeds 1/R")
    check(coalition_checks == 1586, "coalition-check scope changed")
    return {"coalition_flows": coalition_checks, "full_profile_flows": full_flow_checks,
            "single_owner_transitions": owner_transition_checks}


def minimal_cut_sets(edges, source, sink):
    """Enumerate s-side cuts; test each cut edge for indispensability."""
    vertices = sorted({v for edge in edges for v in edge} - {source, sink})
    cuts = set()
    for mask in range(1 << len(vertices)):
        source_side = {source} | {v for i, v in enumerate(vertices) if mask >> i & 1}
        reachable = {source}
        # Generated module/series vertices and edges are in topological order.
        for u, v in edges:
            if u in reachable and v in source_side:
                reachable.add(v)
        coreachable = {sink}
        for u, v in reversed(edges):
            if v in coreachable and u not in source_side:
                coreachable.add(u)
        cut = tuple(e for e, (u, v) in enumerate(edges)
                    if u in source_side and v not in source_side)
        if all(edges[e][0] in reachable and edges[e][1] in coreachable for e in cut):
            cuts.add(cut)
    return cuts


def check_cut_counts():
    counts = {}
    for m, expected in ((1, 5), (2, 39), (3, 689)):
        edges, _, source, sink = make_module(m, m)
        actual = len(minimal_cut_sets(edges, source, sink))
        check(actual == expected, "small module structural-cut count")
        check(actual <= 2 ** (4 * m), "module structural-cut upper bound")
        counts[m] = actual
    return counts


def compositions(total, parts):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def weighted_certificate(k, d, m, alpha, fan_count):
    """Reconstruct every row, including the auxiliary aggregate coefficient."""
    check(k >= 2 and m > d >= 1 and alpha > 0 and fan_count >= 1,
          "weighted parameter domain")
    A = (d + 1) * m - d * d
    lam = F(A) / alpha
    Z = sum((lam ** h / factorial(h) for h in range(d + 1)), F(0))
    probabilities = [lam ** h / factorial(h) / Z for h in range(d + 1)]
    histograms = list(compositions(k, d + 1))
    mass = {}
    for state in histograms:
        weight = F(factorial(k))
        for h, n in enumerate(state):
            weight *= probabilities[h] ** n / factorial(n)
        mass[state] = weight
    check(sum(mass.values(), F(0)) == 1, "multinomial probability mass")

    budget_multiplier = max(1 + alpha, F(m, fan_count))
    coefficients = defaultdict(F)
    constant = F(0)
    budget_coefficient = F(0)
    expected_T = F(0)
    transport_checks = 0
    for state in histograms:
        mu = mass[state]
        present = [h for h, n in enumerate(state) if n]
        T = min((m - h) + m * h for h in present)
        expected_T += mu * T

        # Budget row, including every auxiliary owner's aggregate payment Q.
        budget_weight = mu * budget_multiplier
        budget_coefficient += budget_weight * T
        coefficients[state, "aux"] -= budget_weight
        for h in present:
            coefficients[state, h, "low"] -= budget_weight * state[h] * (m - h)
            coefficients[state, h, "high"] -= budget_weight * state[h] * h

        # Actual two coalition rows. Each Q/R term is a verified nonnegative
        # relaxation of the finite average of actual auxiliary incidences.
        for which, multiplier in ((0, m - d), (1, d)):
            row_weight = mu * multiplier
            selected_caps = []
            for h in present:
                if which == 0:
                    lows, highs = 1, 0
                elif h < d:
                    lows, highs = m - d + 1, 0
                else:
                    lows, highs = 0, 1
                check(0 <= lows <= m - h and 0 <= highs <= h,
                      "coalition multiplicities")
                selected_caps.append(lows + m * highs)
                coefficients[state, h, "low"] += row_weight * state[h] * lows
                coefficients[state, h, "high"] += row_weight * state[h] * highs
            constant += row_weight * min(selected_caps)
            coefficients[state, "aux"] += row_weight / fan_count

        # Only the changing ORIGINAL variable owner's monotonicity row.
        for h in range(d):
            if not state[h]:
                continue
            destination = list(state)
            destination[h] -= 1
            destination[h + 1] += 1
            destination = tuple(destination)
            check(mu * state[h] == probabilities[h] / probabilities[h + 1]
                  * mass[destination] * destination[h + 1], "multinomial transport")
            row_weight = A * mu * state[h]
            coefficients[state, h, "low"] -= row_weight
            coefficients[destination, h + 1, "high"] += row_weight
            transport_checks += 1

    tail_T = m + (m - 1) * sum((sum(probabilities[r:]) ** k
                               for r in range(1, d + 1)), F(0))
    check(expected_T == tail_T, "two expected-flow formulas")
    check(constant == A + d * (d - 1) * probabilities[d] ** k,
          "actual coalition constant")
    check(budget_coefficient == budget_multiplier * expected_T,
          "weighted budget coefficient")
    check(all(coefficient <= 0 for coefficient in coefficients.values()),
          "positive uncancelled payment coefficient")
    for state, mu in mass.items():
        check(coefficients[state, "aux"]
              == mu * (F(m, fan_count) - budget_multiplier),
              "disjoint auxiliary budget absorption")
    check(constant / budget_coefficient >= F(A) / (budget_multiplier * expected_T),
          "finite lower theorem bound")
    return len(histograms), transport_checks


def check_weighted_rows():
    histograms = transports = cases = 0
    for k in (2, 3, 5):
        for d, m in ((1, 2), (2, 3), (2, 6), (3, 6)):
            for alpha in (F(1), F(1, 3)):
                nh, nt = weighted_certificate(k, d, m, alpha, m)
                histograms += nh
                transports += nt
                cases += 1
    # One small R<m case also checks max(1+alpha,m/R), without claiming sharpness.
    nh, nt = weighted_certificate(2, 2, 3, F(1, 3), 1)
    return {"cases": cases + 1, "histograms": histograms + nh,
            "transport_identities": transports + nt}


def check_subdivision(grid=(0, 1, 2)):
    """All 3^10 pair-report profiles on subdivided five-edge Wheatstone.

    Checks actual subdivided maxflow, efficiency, nonnegativity, every
    original-owner coalition (2^10), and every adjacent own-report comparison.
    Doubled payments are integers, including equal-report splits.
    """
    original = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)]
    source, sink = 0, 3
    cut_edges = []
    for mask in range(4):
        side = {source} | {i + 1 for i in range(2) if mask >> i & 1}
        cut_edges.append(tuple(e for e, (u, v) in enumerate(original)
                               if u in side and v not in side))
    subdivided = []
    for e, (u, v) in enumerate(original):
        middle = 4 + e
        subdivided.extend([(u, middle), (middle, v)])
    check(len(subdivided) == len(set(subdivided)), "subdivision simplicity")

    virtual = {}
    for capacities in product(grid, repeat=5):
        selected = min(range(len(cut_edges)),
                       key=lambda i: sum(capacities[e] for e in cut_edges[i]))
        chosen = set(cut_edges[selected])
        Q = tuple(capacities[e] if e in chosen else 0 for e in range(5))
        T = sum(Q)
        check(maxflow(original, capacities, source, sink) == T, "original mincut allocation")
        virtual[capacities] = (T, Q)
    coalition_values = {}
    for capacities in virtual:
        coalition_values[capacities] = tuple(
            virtual[tuple(capacities[e] if mask >> e & 1 else 0 for e in range(5))][0]
            for mask in range(32)
        )

    complete_pairs = []
    lowbit_owner = [0] * 1024
    previous_mask = [0] * 1024
    for mask in range(1024):
        complete_pairs.append(sum(1 << e for e in range(5)
                                  if mask >> (2 * e) & 3 == 3))
        if mask:
            bit = mask & -mask
            lowbit_owner[mask] = bit.bit_length() - 1
            previous_mask[mask] = mask ^ bit

    all_payments = []
    own_checks = coalition_checks = 0
    radix = len(grid)
    steps = [radix ** (9 - e) for e in range(10)]
    for index, reports in enumerate(product(grid, repeat=10)):
        capacities = tuple(min(reports[2 * e], reports[2 * e + 1]) for e in range(5))
        T, Q = virtual[capacities]
        check(maxflow(subdivided, reports, source, sink) == T,
              "subdivision flow projection")
        payment = [0] * 10
        for e in range(5):
            a, b = reports[2 * e:2 * e + 2]
            if a > b:
                payment[2 * e] = 2 * Q[e]
            elif b > a:
                payment[2 * e + 1] = 2 * Q[e]
            else:
                payment[2 * e] = payment[2 * e + 1] = Q[e]
        check(all(value >= 0 for value in payment), "subdivision payment nonnegativity")
        check(sum(payment) == 2 * T, "subdivision efficiency")
        for e, report in enumerate(reports):
            if report != grid[0]:
                check(all_payments[index - steps[e]][e] <= payment[e],
                      "subdivision own-report monotonicity")
                own_checks += 1
        all_payments.append(tuple(payment))
        sums = [0] * 1024
        values = coalition_values[capacities]
        for mask in range(1, 1024):
            sums[mask] = sums[previous_mask[mask]] + payment[lowbit_owner[mask]]
            check(sums[mask] >= 2 * values[complete_pairs[mask]],
                  "subdivision coalition coverage")
            coalition_checks += 1
    return {"profiles": len(all_payments), "nonempty_coalitions": coalition_checks,
            "adjacent_own_report_comparisons": own_checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-subdivision", action="store_true",
                        help="Run only shared-fan and weighted-certificate checks.")
    arguments = parser.parse_args()
    started = time.monotonic()
    print("Shared-fan flows:", check_coalition_modules(), flush=True)
    print("Structural module cuts:", check_cut_counts(), flush=True)
    print("Exact weighted rows:", check_weighted_rows(), flush=True)
    if not arguments.skip_subdivision:
        print("Two-owner subdivision:", check_subdivision(), flush=True)
    print("PASS: all requested exact checks; explicit checks remain active under -O;"
          f" elapsed={time.monotonic() - started:.2f}s", flush=True)


if __name__ == "__main__":
    main()
