#!/usr/bin/env python3
"""Exact bounded-diameter-forest DP and an independent small brute-force check.

The DP certifies a finite combinatorial obstruction to one activity-cover proof
strategy. It is not a lower bound for arbitrary truthful payment mechanisms.
"""
import json
from collections import deque


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def regular_tree(branching, height):
    edges = []
    levels = [0]
    frontier = [0]
    for depth in range(1, height + 1):
        following = []
        for parent in frontier:
            for _ in range(branching):
                child = len(levels)
                levels.append(depth)
                edges.append((parent, child, branching ** (height - depth)))
                following.append(child)
        frontier = following
    return levels, edges


def exact_dp(vertex_count, edges, diameter):
    children = [[] for _ in range(vertex_count)]
    for edge_id, (parent, child, weight) in enumerate(edges):
        require(0 <= parent < child < vertex_count, "rooted edge order")
        children[parent].append((child, weight, edge_id))
    profiles = [None] * vertex_count
    for vertex in range(vertex_count - 1, -1, -1):
        # State is the height of the retained component containing this root.
        # Other components already satisfy the diameter bound.
        states = {0: (0, 0)}
        for child, weight, edge_id in children[vertex]:
            child_states = profiles[child]
            child_best = max(child_states.values(), key=lambda pair: pair[0])
            following = {}

            def offer(height, score, mask):
                previous = following.get(height)
                if previous is None or score > previous[0]:
                    following[height] = (score, mask)

            for current_height, (score, mask) in states.items():
                # Delete this edge; the child's entire optimized forest remains.
                offer(current_height, score + child_best[0], mask | child_best[1])
                for child_height, (child_score, child_mask) in child_states.items():
                    new_branch_height = child_height + 1
                    if new_branch_height > diameter:
                        continue
                    if current_height + new_branch_height > diameter:
                        continue
                    offer(max(current_height, new_branch_height),
                          score + child_score + weight,
                          mask | child_mask | (1 << edge_id))
            states = following
        profiles[vertex] = states
    best = max(profiles[0].values(), key=lambda pair: pair[0])
    return best, profiles


def check_forest(vertex_count, edges, mask, diameter):
    adjacency = [[] for _ in range(vertex_count)]
    score = 0
    for edge_id, (left, right, weight) in enumerate(edges):
        if (mask >> edge_id) & 1:
            adjacency[left].append(right)
            adjacency[right].append(left)
            score += weight
    # Independent all-source graph-distance check, not DP height bookkeeping.
    for start in range(vertex_count):
        distances = {start: 0}
        queue = deque([start])
        while queue:
            vertex = queue.popleft()
            for neighbor in adjacency[vertex]:
                if neighbor not in distances:
                    distances[neighbor] = distances[vertex] + 1
                    if distances[neighbor] > diameter:
                        return None
                    queue.append(neighbor)
    return score


def brute_force(vertex_count, edges, diameter):
    maximum = 0
    for mask in range(1 << len(edges)):
        score = check_forest(vertex_count, edges, mask, diameter)
        if score is not None:
            maximum = max(maximum, score)
    return maximum


def main():
    levels, edges = regular_tree(3, 4)
    require(len(levels) == 121 and len(edges) == 120, "main tree dimensions")
    require(sum(weight for _, _, weight in edges) == 324, "total weight")
    for depth in range(1, 5):
        require(sum(weight for _, child, weight in edges if levels[child] == depth) == 81,
                "each level must have weight81")

    records = []
    for diameter, expected in [(2, 189), (4, 243)]:
        (score, mask), profiles = exact_dp(len(levels), edges, diameter)
        require(score == expected, "main exact optimum mismatch")
        require(check_forest(len(levels), edges, mask, diameter) == score,
                "reconstructed optimum is not a valid forest")
        by_level = {}
        for vertex, level in enumerate(levels):
            scores = {str(height): value[0] for height, value in profiles[vertex].items()}
            if level in by_level:
                require(by_level[level] == scores, "symmetric subtree state mismatch")
            else:
                by_level[level] = scores
        records.append(dict(diameter=diameter, optimum=score,
                            states_by_root_depth=by_level,
                            attaining_edge_ids=[j for j in range(len(edges)) if (mask >> j) & 1]))

    calibration = []
    small_levels, small_edges = regular_tree(2, 3)
    require(len(small_edges) == 14, "small exhaustive calibration size")
    for diameter in [2, 4]:
        dp_score = exact_dp(len(small_levels), small_edges, diameter)[0][0]
        brute_score = brute_force(len(small_levels), small_edges, diameter)
        require(dp_score == brute_score, "DP differs from exhaustive graph-distance check")
        calibration.append(dict(diameter=diameter, subsets=1 << len(small_edges),
                                optimum=dp_score))
    print(json.dumps(dict(status="PASS", vertices=121, edges=120, total_weight=324,
                          exact_main_records=records, independent_calibration=calibration,
                          scope="Exact finite bounded-diameter forest optima; mechanism-class cost inference is proved separately"), indent=2))


if __name__ == "__main__":
    main()
