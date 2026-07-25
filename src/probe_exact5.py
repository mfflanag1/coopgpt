"""Calibration probe for the n=5 exact-family hunt.
How costly is exactify at n=5, how often does a single bump keep exactness,
and does the float-slack family LP agree with exact feasibility on the
co-singleton (m=n) star?
"""
import random, time
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from hunt_monotonic import rand_game
from hunt_sd import exactify, is_exact_game
from floatscreen import is_balanced_float, is_exact_float, family_feasible_float
from family_infeasible import is_family_feasible

n = 5
N = (1 << n) - 1
rng = random.Random(0)

# generate a few exact bases, timing
t0 = time.time()
bases = []
attempts = 0
while len(bases) < 5 and attempts < 200:
    attempts += 1
    g = rand_game(n, rng, "general")
    if not is_balanced_float(n, [float(x) for x in g.v]):
        continue
    b = exactify(g)
    if b is None:
        continue
    if is_exact_game(b):
        bases.append(b)
dt = time.time() - t0
print(f"generated {len(bases)} exact bases in {dt:.1f}s ({attempts} attempts)")

# for one base, how many single proper bumps (d in 1..3) keep exactness?
b = bases[0]
keep = 0; total = 0
for S in range(1, N):
    for d in (1, 2, 3):
        total += 1
        v2 = [float(x) for x in b.v]; v2[S] += d
        if is_exact_float(n, v2):
            keep += 1
print(f"base0: {keep}/{total} single (S,d) bumps keep exactness (float screen)")

# co-singleton star: bump each N\{k}; find depth keeping exactness
def bump(g, S, d):
    v2 = list(g.v); v2[S] += d
    return Game(g.n, v2)

for bi, b in enumerate(bases[:3]):
    arms = []
    for k in range(n):
        S = N ^ (1 << k)
        found = None
        for d in (1, 2, 3, 4, 5):
            v2 = [float(x) for x in b.v]; v2[S] += d
            if is_exact_float(n, v2):
                found = d
        if found:
            arms.append((S, found, bump(b, S, found)))
    if len(arms) < 2:
        print(f"base{bi}: <2 exact co-singleton arms")
        continue
    games = [b] + [t for (_, _, t) in arms]
    edges = [(0, j + 1, S) for j, (S, _, _) in enumerate(arms)]
    ff = family_feasible_float(n, [[float(x) for x in g.v] for g in games], edges)
    fe, _ = is_family_feasible(games, edges)
    exact_ok = all(is_exact_game(t) for (_, _, t) in arms)
    print(f"base{bi}: {len(arms)} co-singleton arms, all_exact={exact_ok}, float_feas={ff}, exact_feas={fe}")
