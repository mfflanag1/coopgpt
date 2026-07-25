"""Validation gates for pes.py. All must pass before hunting."""
import random
from fractions import Fraction as F
from tugame import Game
from pes import egalitarian_procedure, pes
from hunt_monotonic import rand_game
from hunt_sd import is_exact_game

FAIL = []


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    if not cond:
        FAIL.append(name)


def vec(x):
    return tuple(str(u) for u in x)


# ---- Gate (a): Example 2 ----
# N={1,2,3,4} 0-indexed 0..3. v(N)=24; v({2,4})=v({3,4})=14 -> masks 0b1010,0b1100.
v = [F(0)] * 16
v[15] = F(24)
v[0b1010] = F(14)   # players {1,3} = 1-indexed {2,4}
v[0b1100] = F(14)   # players {2,3} = 1-indexed {3,4}
g = Game(4, v)
claims, A_hat, is_ES = egalitarian_procedure(g)
p, D = pes(g)
check("ex2 claims (3,7,7,7)", claims == [F(3), F(7), F(7), F(7)], str(claims))
check("ex2 A-hat = {2,4},{3,4},N", set(A_hat) == {0b1010, 0b1100, 15}, str(sorted(A_hat)))
check("ex2 is_ES True", is_ES)
check("ex2 PES (3,7,7,7)", p == [F(3), F(7), F(7), F(7)], str(p))

# ---- Gate (b): Example 3 ----
# N={1,2,3} 0-indexed 0..2. v({1,3})=v({2,3})=v(N)=4.
v = [F(0)] * 8
v[7] = F(4)
v[0b101] = F(4)   # {1,3} -> players {0,2}
v[0b110] = F(4)   # {2,3} -> players {1,2}
g = Game(3, v)
claims, A_hat, is_ES = egalitarian_procedure(g)
p, D = pes(g)
check("ex3 claims (2,2,2)", claims == [F(2), F(2), F(2)], str(claims))
check("ex3 A-hat = {1,3},{2,3}", set(A_hat) == {0b101, 0b110}, str(sorted(A_hat)))
check("ex3 not ES", not is_ES)
check("ex3 D = {3}", D == 0b100, bin(D))
check("ex3 PES (1,1,2)", p == [F(1), F(1), F(2)], str(p))

# ---- Gate (c): convex games are ES with PES in core ----
rng = random.Random(12345)
ok = 0
for _ in range(20):
    g = rand_game(4, rng, "convex")
    claims, A_hat, is_ES = egalitarian_procedure(g)
    p, D = pes(g)
    if is_ES and g.in_core(p):
        ok += 1
check("(c) 20 convex n=4: ES + PES in core", ok == 20, f"{ok}/20")

# ---- Gate (d): the 8 large-core exact games are ES ----
games = {
    "Thm5.1": [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 13, 15, 0, 14, 13, 30],
    "Thm5.1-bump13": None,
    "Thm5.3": [0, 5, 6, 20, 2, 10, 8, 22, 5, 12, 14, 25, 12, 17, 18, 32],
}
t = list(games["Thm5.1"])
t[13] += 1
games["Thm5.1-bump13"] = t
# Prop 7.5: b(N)=5 rest 0, plus four bumps +4 at N\{k} (masks 14,13,11,7).
base = [0] * 16
base[15] = 5
games["Prop7.5-base"] = base
for k, mask in enumerate([14, 13, 11, 7]):
    b = list(base)
    b[mask] += 4
    games[f"Prop7.5-bump{mask}"] = b

for name, vlist in games.items():
    g = Game(4, [F(x) for x in vlist])
    claims, A_hat, is_ES = egalitarian_procedure(g)
    p, D = pes(g)
    exact = is_exact_game(g)
    check(f"(d) {name}: exact & ES & PES in core", exact and is_ES and g.in_core(p),
          f"exact={exact} ES={is_ES} incore={g.in_core(p)}")

print()
print("ALL GATES PASSED" if not FAIL else f"FAILURES: {FAIL}")
