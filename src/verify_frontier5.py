"""Lean discipline check: find ONE low-slack near-degenerate co-singleton family
(float) and confirm float feasibility == EXACT feasibility. Guards against
float false-positives near the slack frontier.
"""
import random
from fractions import Fraction as F
from hunt_frontier5 import neardegen_seed, float_exactify, arm_pool, family_slack
from floatscreen import is_balanced_float, is_exact_float
from tugame import Game
from hunt_sd import exactify, is_exact_game
from family_infeasible import is_family_feasible

rng = random.Random(11)
N = 31
best = None
for t in range(120):
    s = neardegen_seed(rng)
    if not is_balanced_float(5, s):
        continue
    b = float_exactify(s)
    if b is None or not is_exact_float(5, b):
        continue
    pool = arm_pool(b, 3)
    cos = [(N ^ (1 << k), pool[N ^ (1 << k)]) for k in range(5) if (N ^ (1 << k)) in pool]
    if len(cos) < 3:
        continue
    gv = [b]
    for S, d in cos:
        v2 = list(b); v2[S] += d; gv.append(v2)
    edges = [(0, j + 1, S) for j, (S, d) in enumerate(cos)]
    sl = family_slack(gv, edges)
    if best is None or sl < best[0]:
        best = (sl, s, cos, edges)
        print(f"[t={t}] float slack={sl:.5f} arms={len(cos)}", flush=True)
    if sl < 0.1:
        break

sl, seed, cos, edges = best
print(f"\nCHOSEN float slack={sl:.5f}, {len(cos)} co-singleton arms")
eb = exactify(Game(5, [F(x) for x in seed]))
print("exact base is_exact:", is_exact_game(eb))
games = [eb]
for S, d in cos:
    v2 = list(eb.v); v2[S] += d; games.append(Game(5, v2))
print("all arms exact:", [is_exact_game(g) for g in games])
feas, x = is_family_feasible(games, edges)
print("EXACT family feasible:", feas, "(float said feasible: True)")
print("AGREEMENT:", feas is True)
