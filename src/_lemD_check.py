import json
from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from lemD import (tight_coalitions, core_max_xS, binding_bumpable, star_holds,
                  star_direction, residual_cover, is_exact_game, xS)

def members(S,n): return [i for i in range(n) if S>>i&1]

# --- non-exact n=5 counterexample: star should FAIL at phi(v) for S={0,1,2} ---
W = json.load(open("../results/WITNESS_leximin_nonexact_n5.json"))
n = W["n"]; v = [F(x) for x in W["v"]]; S = W["S"]
g = Game(n, v)
phi = leximin_core_exact(g)
print("=== non-exact n5 witness ===")
print("phi", [str(p) for p in phi], "exact?", is_exact_game(g))
print("S", members(S,n), "binding_bumpable?", binding_bumpable(g,phi,S),
      "max_core x(S)=", core_max_xS(g,S), "phi(S)=", xS(phi,S,n))
h,val,y = star_holds(g,phi,S)
print("star_holds(Pareto form)?", h, "maxval", val)
hd,e = star_direction(g,phi,S)
print("star_direction(cone)?", hd, "e", [str(t) for t in e] if e else None)
rc = residual_cover(g,phi,S)
print("residual r:", {k:str(val) for k,val in rc["r"].items()} if rc else None,
      "mu", str(rc["mu"]) if rc else None)
