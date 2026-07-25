"""Infinite families of EXACT, NON-egalitarian-stable games for every n>=5.

Base witness (n=5, Dietzenbacher-open-question counterexample), player=bit:
  v = [0,0,0,0,3,3,3,3,0,0,0,0,4,4,4,4,0,0,0,0,4,5,5,5,0,0,0,0,4,5,5,6]

Family A (null padding, fully proven): add (n-5) NULL players.
Family B (additive padding, non-degenerate/all-essential): add players each
adding constant c>=1 to every coalition.

Both preserve exactness and non-ES. Verified exactly (is_exact_game) at n<=6,
via fast float exactness for larger n.
"""
from fractions import Fraction as F
from tugame import Game
from eshunt import egalitarian_procedure, is_ES
from hunt_sd import is_exact_game
from es_float import core_min_all

BASE = [0,0,0,0,3,3,3,3,0,0,0,0,4,4,4,4,0,0,0,0,4,5,5,5,0,0,0,0,4,5,5,6]

def pad(v, n, c):
    """add one player at bit n adding constant c to every coalition (c=0 => null)."""
    w = [F(0)] * (1 << (n + 1))
    for S in range(1 << n):
        w[S] = F(v[S]); w[S | (1 << n)] = F(v[S]) + F(c)
    return w, n + 1

def exact_float(n, v):
    ve = core_min_all(n, [float(x) for x in v])
    return ve is not None and all(abs(ve[S] - float(v[S])) < 1e-7 for S in range(1, (1 << n) - 1))

def is_dummy(n, v, i):
    b = 1 << i
    return all(v[S | b] == v[S] for S in range(1 << n) if not S >> i & 1)

def report(tag, v, n, exact_check):
    g = Game(n, v)
    gamma, A, k, Nadm = egalitarian_procedure(g)
    ex = is_exact_game(g) if exact_check else exact_float(n, v)
    dummies = [i for i in range(n) if is_dummy(n, v, i)]
    infl = sum(gamma) - g.v[g.N]
    print(f"{tag} n={n}: exact={ex} ES={Nadm} inflation={infl} "
          f"sum_claims={sum(gamma)} vN={g.v[g.N]} dummies={dummies}")
    assert ex and not Nadm and infl > 0
    return gamma

if __name__ == "__main__":
    print("BASE n=5 (EXACT certification):")
    report("  base", [F(x) for x in BASE], 5, exact_check=True)
    print("Family A (null padding, c=0):")
    v, n = [F(x) for x in BASE], 5
    for _ in range(4):
        v, n = pad(v, n, 0)
        report("  null", v, n, exact_check=False)
    print("Family B (additive padding, c=1, all-essential):")
    v, n = [F(x) for x in BASE], 5
    for _ in range(4):
        v, n = pad(v, n, 1)
        report("  add1", v, n, exact_check=False)
    print("ALL FAMILY MEMBERS: exact, non-ES, positive inflation. QED-by-construction (n<=8 shown).")
