#!/usr/bin/env python3
"""Exact independent dual replay; standard library only, no assertion reliance."""
from fractions import Fraction
import json


def require(test, message):
    if not test:
        raise ValueError(message)


def tree():
    levels = [0]
    adj = [[]]
    for d in range(4):
        for v in [v for v, z in enumerate(levels) if z == d]:
            for _ in range(3):
                u = len(adj)
                adj.append([v])
                adj[v].append(u)
                levels.append(d + 1)
    return adj, levels


def replay(name, edge, vertex, costs):
    adj, levels = tree()
    require(len(adj) == 121, 'wrong tree size')
    edges = [(u, v) for u in range(len(adj)) for v in adj[u] if u < v]
    require(len(edges) == 120, 'wrong edge count')
    a = {frozenset((u, v)): edge[max(levels[u], levels[v]) - 1] for u, v in edges}
    g = [vertex[d] for d in levels]
    normalizer = sum(g)
    total = sum(a.values())
    require(normalizer > 0 and total > 2 * normalizer, 'dual does not exceed two')
    require(all(x >= 0 for x in g) and all(x >= 0 for x in a.values()), 'negative dual')

    def w(u, v):
        return a[frozenset((u, v))]

    # Independent exact maximum-profit separation, rather than the exploratory
    # LP's symmetry-quotiented component enumeration.
    star_cost, double_cost, depth_cost = map(Fraction, costs)
    star_scores = [
        -star_cost * g[v] + sum(max(0, w(v, u) - star_cost * g[u]) for u in adj[v])
        for v in range(len(adj))
    ]
    double_scores = [
        w(u, v) - double_cost * (g[u] + g[v])
        + sum(max(0, w(u, z) - double_cost * g[z]) for z in adj[u] if z != v)
        + sum(max(0, w(v, z) - double_cost * g[z]) for z in adj[v] if z != u)
        for u, v in edges
    ]
    depth_scores = [
        -depth_cost * g[v]
        + sum(max(0, w(v, u) - depth_cost * g[u]
                  + sum(max(0, w(u, z) - depth_cost * g[z]) for z in adj[u] if z != v))
              for u in adj[v])
        for v in range(len(adj))
    ]
    for label, scores in [('star', star_scores), ('double_star', double_scores), ('depth_two', depth_scores)]:
        require(max(scores) <= 0, name + ': violated ' + label + ' component constraint')

    # Replay the production meaning of the capacity profiles directly by
    # recursive weighted vertex cover for selected component edge sets.
    def production(capacity, allowed):
        dp = [None] * len(adj)
        for v in reversed(range(len(adj))):
            inside = Fraction(capacity[v])
            outside = Fraction(0)
            for u in adj[v]:
                if levels[u] <= levels[v]:
                    continue
                if frozenset((u, v)) in allowed:
                    inside += min(dp[u])
                    outside += dp[u][1]
                else:
                    inside += min(dp[u])
                    outside += min(dp[u])
            dp[v] = (outside, inside)
        return min(dp[0])

    full = set(a)
    # Each star-centered profile has F=1; for every single-edge, full-star,
    # and full-radius-two component, F_C is the claimed activation indicator.
    components = [set([e]) for e in full]
    components += [{frozenset((v, u)) for u in adj[v]} for v in range(len(adj))]
    components += [
        {frozenset((v, u)) for u in adj[v]}
        | {frozenset((u, z)) for u in adj[v] for z in adj[u] if z != v}
        for v in range(len(adj))
    ]
    profile_checks = 0
    for v in range(len(adj)):
        cap = [int(u == v or u in adj[v]) for u in range(len(adj))]
        require(production(cap, full) == 1, 'star profile full value differs from one')
        for component in components:
            target = int(any(v in edge_key for edge_key in component))
            require(production(cap, component) == target, 'wrong activation production identity')
            profile_checks += 1
    return {'name': name, 'status': 'PASS', 'arithmetic': 'exact Fraction/integer',
            'vertices': len(adj), 'edges': len(edges), 'normalizer': normalizer,
            'edge_total': total, 'dual_lower_bound': str(Fraction(total, normalizer)),
            'costs': list(costs), 'edge_weights_by_depth': edge, 'vertex_weights_by_depth': vertex,
            'star_centers_checked': len(star_scores), 'double_star_centers_checked': len(double_scores),
            'depth_two_centers_checked': len(depth_scores),
            'maximum_component_profits': [str(max(x)) for x in [star_scores, double_scores, depth_scores]],
            'production_profile_checks': profile_checks}


if __name__ == '__main__':
    witnesses = [
        ('robust_discounted_costs', [5859, 4221, 1500, 280], [4914, 3402, 2520, 720, 0], ['7/6', '4/3', '3/2']),
        ('current_depth_two_cost', [28431, 18954, 8112, 1300], [24057, 16038, 10692, 3300, 0], ['13/11', '7/5', '7/4']),
    ]
    print(json.dumps([replay(*witness) for witness in witnesses], indent=2))
