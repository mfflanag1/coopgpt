"""Fixed-box slack scan for big boss games.

Fix the core box: choose non-boss marginals M and v(N)=V (with c=V-sum(M)>=0 the boss
floor). This fixes v(N) and every v(N\\{i})=V-M_i, hence the box core {0<=x_i<=M_i}.
The union property forces v(S) <= u(S) := c + sum_{i in S cap nonboss} M_i (union-tight
upper bound). We SCAN a slack parameter theta that lowers the INTERIOR coalition values
below union-tight, staying monotone. At theta=0 the game is union-tight (convex).

For each theta we record: is_big_boss, convex, ES, and EXACT core-stability. Prediction:
increasing slack breaks STABILITY while ES keeps holding => stable region ⊆ ES region
=> no stable non-ES big boss game (positive companion result). A stable+nonES at any
theta would be a COUNTEREXAMPLE (kills Dietzenbacher's 2nd half).
"""
from fractions import Fraction as F
from tugame import Game
from bigboss import is_big_boss, marginals
from bigboss_stability import find_escape_bigboss
from eshunt import is_ES


def build(M, V, theta, boss=None):
    n = len(M) + 1
    if boss is None:
        boss = n - 1
    others = [i for i in range(n) if i != boss]
    c = V - sum(M)
    v = [F(0)] * (1 << n)
    for S in range(1, 1 << n):
        if not (S >> boss & 1):
            continue
        Tsize = sum(1 for k, pl in enumerate(others) if S >> pl & 1)
        u = F(c) + sum(F(M[k]) for k, pl in enumerate(others) if S >> pl & 1)
        # lower STRICTLY interior coalitions (1<=Tsize<=n-3) by theta; keep boss-alone,
        # every N\{i} (Tsize=n-2, fixes the marginals/box), and N fixed at union-tight.
        if 1 <= Tsize <= n - 3:
            v[S] = u - F(theta)
        else:
            v[S] = u
    g = Game(n, v)
    return g, boss


def monotone(g):
    n = g.n
    for S in range(g.N + 1):
        for i in range(n):
            if not (S >> i & 1) and g.v[S | (1 << i)] < g.v[S]:
                return False
    return True


def scan(M, V, thetas, boss=None):
    print(f"M={M} V={V} boss floor c={V-sum(M)}  box=prod[0,M_i]", flush=True)
    print(f"{'theta':>6} {'bigboss':>7} {'monot':>5} {'convex':>6} {'ES':>5} {'stable':>6}  note", flush=True)
    results = []
    for theta in thetas:
        g, b = build(M, V, theta, boss)
        mono = monotone(g)
        bb, why = is_big_boss(g, b)
        if not (mono and bb):
            print(f"{str(theta):>6} {str(bb):>7} {str(mono):>5} {'-':>6} {'-':>5} {'-':>6}  not a big boss game ({why if not bb else 'nonmono'})", flush=True)
            continue
        cvx = g.is_convex()
        es, gamma = is_ES(g)
        esc, K = find_escape_bigboss(g, b)
        stable = esc is None
        note = ""
        if stable and not es:
            note = "*** STABLE + NON-ES => COUNTEREXAMPLE CANDIDATE ***"
        print(f"{str(theta):>6} {str(bb):>7} {str(mono):>5} {str(cvx):>6} {str(es):>5} {str(stable):>6}  {note}", flush=True)
        results.append((theta, cvx, es, stable, gamma, g))
    return results


if __name__ == "__main__":
    # a few boxes; scan theta from 0 (union-tight/convex) upward in fine steps
    for M, V in [([2, 2, 2, 2, 2], 13), ([3, 2, 2, 1, 1], 12), ([2, 2, 1, 1, 1], 9),
                 ([4, 3, 2, 1, 1], 14)]:
        thetas = [F(k, 4) for k in range(0, 4 * (min(M) + 2) + 1)]
        scan(M, V, thetas)
        print(flush=True)
