"""Positive control for the family-infeasibility engine before the n=5 port.

Reproduces the paper Theorem 3.2 minimal 3-game BALANCED family (n=4):
base = [0,0,0,0,0,3,3,1,0,3,3,1,3,1,5,6],
bumps A={0,1,2}=7 by +3, B={1,2,3}=14 by +1.
Must come out INFEASIBLE with a verified exact Farkas certificate.
"""
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from family_infeasible import is_family_feasible, certify_infeasible, verify_witness

base_v = [0,0,0,0,0,3,3,1,0,3,3,1,3,1,5,6]
n = 4
base = Game(n, base_v)

def bump(g, S, d):
    v2 = list(g.v); v2[S] += d
    return Game(g.n, v2)

tA = bump(base, 7, 3)    # {0,1,2}
tB = bump(base, 14, 1)   # {1,2,3}
games = [base, tA, tB]
edges = [(0, 1, 7), (0, 2, 14)]

print("all balanced:", [is_balanced_game(g) for g in games])
feas, x = is_family_feasible(games, edges)
print("family feasible:", feas)
assert not feas, "POSITIVE CONTROL FAILED: family came out feasible!"

cert = certify_infeasible(games, edges)
print("infeasible:", cert["infeasible"])
fk = cert.get("farkas")
assert cert["infeasible"], "recheck says feasible"
assert fk is not None, "no verified Farkas certificate"
print("Farkas rhs (must be <0):", fk["rhs"])
print("active_ineq:", [(m, str(y)) for m, y in fk["active_ineq"]])
print("active_eq:", [(m, str(y)) for m, y in fk["active_eq"]])
print("\nPOSITIVE CONTROL PASSED: engine reproduces the n=4 balanced impossibility with verified Farkas cert.")
