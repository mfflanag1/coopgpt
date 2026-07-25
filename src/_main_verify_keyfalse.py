"""Main-session independent verification of WITNESS_KEY_FALSE_n6."""
import json, sys
from fractions import Fraction as F
sys.path.insert(0, "src")
from tugame import Game
from leximin import leximin_core_exact
from lemD import star_holds, core_max_xS, core_min_xT, is_exact_game, xS, binding_bumpable

D = json.load(open("results/WITNESS_KEY_FALSE_n6.json"))
n = 6; N = 63
v = [F(x) for x in D["v"]]
g = Game(n, v)

ok = True
def chk(label, cond):
    global ok
    print(("ok   " if cond else "FAIL "), label)
    ok = ok and cond

# 1. exactness (62 exact LPs)
print("     (exactness deferred to background job)")

# 2. leximin recompute
phi = leximin_core_exact(g)
phi_stated = [F(x) for x in D["phi_leximin"]]
chk(f"leximin phi recomputed = stated {phi_stated}", list(phi) == phi_stated)
chk("phi in core", sum(phi) == v[N] and all(xS(phi, S, n) >= v[S] for S in range(1, N)))

# 3. star_S fails for S={0,2,3,4}
Smask = 1+4+8+16
holds, val, _ = star_holds(g, phi, Smask)
chk(f"star_S FAILS at S={{0,2,3,4}} (max y(S)={val} = phi(S))", holds is False and val == xS(phi, Smask, n))

# 4. (KEY) arithmetic from stated cover
W = 1+2+4+8+32; Tstar = 1+4+8; P = 2+32
lhs = v[W]; rhs = xS(phi, P, n) + v[Tstar]
chk(f"(KEY) v(W)={lhs} >= phi(P)+v(T*)={rhs} is FALSE, margin {lhs-rhs}", lhs < rhs and lhs - rhs == F(-1,3))

# 5. cover coalitions tight at phi
for cS, lam in [(2+4,1),(1+2+32,2),(4+8+32,1)]:
    chk(f"cover coalition {cS:06b} tight at phi", xS(phi, cS, n) == v[cS])

# 6. Step-6 refutation: M^(T*) = max{x(S): core, x(T*)=v(T*)} > phi(S), via witness
x = [F(u) for u in ["7","2","8","4","5","3"]]
chk("witness x in core", sum(x) == v[N] and all(xS(x, S, n) >= v[S] for S in range(1, N)))
chk("x(T*) = v(T*) = 19", xS(x, Tstar, n) == v[Tstar] == 19)
chk("x(S) = 24 > phi(S) = 71/3", xS(x, Smask, n) == 24 and xS(phi, Smask, n) == F(71,3))

# 7. Lemma D NOT refuted: S not binding-bumpable (d* = 0)
mx = core_max_xS(g, Smask)
dstar = mx - xS(phi, Smask, n)
chk(f"d*(S) = max_core x(S) - phi(S) = {dstar}", dstar == 0)
chk("S not binding-bumpable (Lemma D survives)", not binding_bumpable(g, phi, Smask))

print("\n" + ("ALL INDEPENDENT CHECKS PASSED" if ok else "*** VERIFICATION FAILED ***"))
sys.exit(0 if ok else 1)
