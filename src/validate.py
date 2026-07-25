"""Validation: reproduce known nucleolus values before trusting the pipeline."""
from fractions import Fraction as F
import sys
from tugame import Game, is_balanced_game, kohlberg_certify_prenucleolus
from nucleolus import certified_prenucleolus

def mk(n, d):
    v = [F(0)] * (1 << n)
    for S, val in d.items():
        v[S] = F(val)
    return Game(n, v)

def bankruptcy_game(E, d):
    """v(S) = max(0, E - d(N\\S))"""
    n = len(d)
    N = (1 << n) - 1
    v = [F(0)] * (1 << n)
    for S in range(1, 1 << n):
        out = sum(d[i] for i in range(n) if not (S >> i & 1))
        v[S] = max(F(0), F(E) - out)
    return Game(n, v)

tests = []

# 1. Talmud: E=200, d=(100,200,300) -> nucleolus (50,75,75)
g = bankruptcy_game(200, [100, 200, 300])
x = certified_prenucleolus(g)
tests.append(("Talmud E=200", x == [F(50), F(75), F(75)], x))

# 2. Talmud: E=300, d=(100,200,300) -> (50,100,150)
g = bankruptcy_game(300, [100, 200, 300])
x = certified_prenucleolus(g)
tests.append(("Talmud E=300", x == [F(50), F(100), F(150)], x))

# 3. Talmud: E=100 -> (100/3,100/3,100/3)
g = bankruptcy_game(100, [100, 200, 300])
x = certified_prenucleolus(g)
tests.append(("Talmud E=100", x == [F(100, 3)] * 3, x))

# 4. Symmetric 3-player majority: v(N)=1, v(ij)=1 -> (1/3,1/3,1/3)
g = mk(3, {0b011: 1, 0b101: 1, 0b110: 1, 0b111: 1})
x = certified_prenucleolus(g)
tests.append(("3-majority", x == [F(1, 3)] * 3, x))

# 5. Gloves 2L-1R: players 0,1 left, 2 right; v(S)=min(#L,#R)
v = {}
for S in range(1, 8):
    L = sum(1 for i in (0, 1) if S >> i & 1)
    R = 1 if S >> 2 & 1 else 0
    v[S] = min(L, R)
g = mk(3, v)
x = certified_prenucleolus(g)
# core = {(0,0,1)}; nucleolus must be (0,0,1)
tests.append(("gloves 2-1", x == [F(0), F(0), F(1)], x))

# 6. 4-player: prenucleolus of unanimity game u_{12} (players 0,1): (1/2,1/2,0,0)
v = {}
for S in range(1, 16):
    v[S] = 1 if (S & 0b0011) == 0b0011 else 0
g = mk(4, v)
x = certified_prenucleolus(g)
tests.append(("unanimity u12 n=4", x == [F(1, 2), F(1, 2), F(0), F(0)], x))

# 7. Kohlberg must REJECT a wrong vector (verifier soundness)
g = bankruptcy_game(200, [100, 200, 300])
ok, why = kohlberg_certify_prenucleolus(g, [F(200, 3)] * 3)
tests.append(("Kohlberg rejects wrong x", ok is False, why))

# 8. balancedness checker: 3-majority with v(ij)=1 has empty core if v(N)=1?
# core: x_i+x_j>=1 all pairs, sum=1 -> sum of three pair constraints: 2 >= 3 infeasible? 2*sum>=3 -> 1>=3/2 false: empty
tests.append(("3-majority core empty", is_balanced_game(mk(3, {0b011: 1, 0b101: 1, 0b110: 1, 0b111: 1})) is False, None))
# convex game core nonempty
tests.append(("convex core nonempty", is_balanced_game(mk(3, {0b111: 3, 0b011: 1, 0b101: 1, 0b110: 1})) is True, None))

fails = 0
for name, ok, info in tests:
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  -> {info}"))
    fails += 0 if ok else 1
print(f"\n{len(tests) - fails}/{len(tests)} passed")
sys.exit(1 if fails else 0)
