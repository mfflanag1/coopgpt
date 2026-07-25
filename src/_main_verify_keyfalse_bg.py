"""Background half of main-session verification: exactness + d*(S)=0."""
import json, sys, time
from fractions import Fraction as F
sys.path.insert(0, "src")
from tugame import Game
from lemD import is_exact_game, max_exact_bump, xS

D = json.load(open("results/WITNESS_KEY_FALSE_n6.json"))
n = 6; N = 63
v = [F(x) for x in D["v"]]
g = Game(n, v)
t0 = time.time()
Smask = 1+4+8+16
d = max_exact_bump(g, Smask)
print(f"d*(S={{0,2,3,4}}) = {d}   [{'ok' if d == 0 else 'FAIL'}]  ({time.time()-t0:.0f}s)", flush=True)
t0 = time.time()
ex = is_exact_game(g)
print(f"exact game: {ex}   [{'ok' if ex else 'FAIL'}]  ({time.time()-t0:.0f}s)", flush=True)
print("BG VERIFICATION " + ("PASSED" if (d == 0 and ex) else "FAILED"))
