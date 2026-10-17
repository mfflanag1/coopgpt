"""Exact certificate checks; bounded diagnostics supplement the analytic proof."""
from fractions import Fraction as Q
import json
import random
from pathlib import Path


def demand(condition, message):
    if not condition:
        raise RuntimeError(message)


def cycles(vertices, edges):
    adjacency = {v: [] for v in vertices}
    weight = {}
    for a, b, w in edges:
        adjacency[a].append(b)
        adjacency[b].append(a)
        weight[a, b] = weight[b, a] = Q(w)
    result = []
    for start in vertices:
        def visit(path):
            u = path[-1]
            for v in adjacency[u]:
                if v == start and len(path) >= 4:
                    if path[1] < path[-1]:
                        result.append(tuple(path))
                elif v > start and v not in path:
                    visit(path + [v])
        visit([start])
    return result, weight


def certify(left, right, edges):
    vertices = list(left) + list(right)
    cs, weight = cycles(vertices, edges)
    rho, witness = Q(1), None
    for cycle in cs:
        demand(len(cycle) % 2 == 0, "nonbipartite input")
        ws = [weight[cycle[k], cycle[(k + 1) % len(cycle)]]
              for k in range(len(cycle))]
        a, b = sum(ws[::2]), sum(ws[1::2])
        candidate = max(a / b, b / a)
        if candidate > rho:
            rho, witness = candidate, (cycle, a, b)
    arcs = [(a, b, rho * Q(w)) for a, b, w in edges]
    arcs += [(b, a, -Q(w)) for a, b, w in edges]
    potential = {v: Q(0) for v in vertices}
    for iteration in range(len(vertices)):
        changed = False
        for u, v, cost in arcs:
            if potential[v] > potential[u] + cost:
                potential[v] = potential[u] + cost
                changed = True
        if not changed:
            break
        demand(iteration + 1 < len(vertices), "negative cycle at claimed rho")
    low = min(potential.values(), default=0)
    potential = {v: x - low for v, x in potential.items()}
    for a, b, w in edges:
        s = potential[b] - potential[a]
        demand(Q(w) <= s <= rho * Q(w), "majorant constraint violation")
    if rho > 1:
        demand(witness is not None, "missing lower witness")
        _, a, b = witness
        demand(max(a / b, b / a) == rho, "wrong lower witness")
    return rho, potential, len(cs), witness


def double_cover(n, original_edges):
    doubled = []
    for u, v, w in original_edges:
        doubled.extend([(u, n + v, w), (v, n + u, w)])
    rho, pi, count, witness = certify(range(n), range(n, 2 * n), doubled)
    alpha = {v: (pi[n + v] - pi[v]) / 2 for v in range(n)}
    for u, v, w in original_edges:
        demand(Q(w) <= alpha[u] + alpha[v] <= rho * Q(w),
               "averaged additive majorant failed")
    return rho, alpha, count, witness


def main():
    rng = random.Random(202610170444)
    cases = cycles_checked = 0
    for na in range(1, 5):
        for nb in range(1, 5):
            for _ in range(15):
                edges = [(a, na + b, rng.randint(1, 10))
                         for a in range(na) for b in range(nb)
                         if rng.random() < .55]
                if not edges:
                    edges = [(0, na, 1)]
                rho, pi, nc, witness = certify(range(na), range(na, na + nb), edges)
                cases += 1
                cycles_checked += nc
    rho, _, nc, _ = certify(range(2), range(2, 4),
                            [(0, 2, 10), (1, 2, 10), (1, 3, 10), (0, 3, 11)])
    demand(rho == Q(21, 20), "four-cycle example")
    general_cases = general_cycles = 0
    for n in range(2, 7):
        for _ in range(20):
            edges = [(u, v, rng.randint(1, 7))
                     for u in range(n) for v in range(u + 1, n)
                     if rng.random() < .34]
            if not edges:
                edges = [(0, 1, 1)]
            rho, alpha, nc, witness = double_cover(n, edges)
            general_cases += 1
            general_cycles += nc
    dumbbell = [(0, 1, 1), (1, 2, 1), (2, 0, 1),
                (3, 4, 1), (4, 5, 1), (5, 3, 1), (2, 3, 2)]
    rho, alpha, nc, witness = double_cover(6, dumbbell)
    demand(rho == Q(3, 2), "odd-cycle-pair example")
    triangles = [([(0, 1, 1), (1, 2, 1), (2, 0, 100)], 3),
                 ([(0, 1, 1), (1, 2, 7), (2, 3, 3),
                   (3, 4, 9), (4, 0, 2)], 5)]
    for edges, n in triangles:
        r, _, _, _ = double_cover(n, edges)
        demand(r == 1, "odd unicycle should be exact additive")
    result = {
        "status": "PASS",
        "arithmetic": "fractions.Fraction throughout",
        "bipartite_profiles": cases,
        "bipartite_simple_cycles_checked": cycles_checked,
        "undirected_profiles": general_cases,
        "double_cover_simple_cycles_checked": general_cycles,
        "four_cycle_distortion": "21/20",
        "two_odd_cycles_joined_by_bridge_distortion": str(rho),
        "dumbbell_additive_majorant": {str(k): str(v) for k, v in alpha.items()},
        "scope": "Finite exact certificate diagnostics; all-real theorem is analytic."
    }
    Path(__file__).with_name("route_distortion_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
