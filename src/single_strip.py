"""EXACT test of the single-strip escape construction (converging with prove-stES).

For a non-ES game with egalitarian claims gamma and excess e = gamma(N)-v(N) > 0:
a SINGLE-STRIP of player j lowers gamma_j to gamma_j - e (needs gamma_j >= e), keeping
all others at their claim. The result y^j is efficient (sum = v(N)). Test EXACTLY
whether y^j is an imputation outside the core and UNDOMINATED by the core.

Record, for every non-ES game, whether ANY single strip works and WHICH players j do,
tagging each j: strong(in D)?, capped(gamma_j>lambda)?, gamma_j vs M_j. Goal: find the
SELECTION RULE (the last lemma) and confirm a single strip ALWAYS exists.
"""
import random, sys
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from eshunt import is_ES, egalitarian_procedure
from pes import pes, _cea_lambda
from core_stability import is_dominated_by_core, in_core, is_imputation


def analyze(g):
    n, N = g.n, g.N
    gamma, A, k, Nadm = egalitarian_procedure(g)
    p, D = pes(g)
    e = sum(gamma) - g.v[N]
    strong = [i for i in range(n) if D >> i & 1]
    nonstrong = [i for i in range(n) if not (D >> i & 1)]
    lam = _cea_lambda([gamma[i] for i in nonstrong], g.v[N] - sum(gamma[i] for i in strong))
    M = [g.v[N] - g.v[N ^ (1 << i)] for i in range(n)]
    working = []
    for j in range(n):
        if gamma[j] < e:
            continue
        y = list(gamma); y[j] = gamma[j] - e
        if not is_imputation(g, y) or in_core(g, y):
            continue
        dom, _ = is_dominated_by_core(g, y)
        if not dom:
            capped = gamma[j] > lam
            working.append((j, "strong" if D >> j & 1 else "nonstrong",
                            "capped" if capped else "uncapped",
                            f"g={gamma[j]} lam={lam} M={M[j]}"))
    return gamma, e, strong, lam, M, working


def rand_nonES_game(rng, n=6, hi=3):
    v = [F(0)] * (1 << n)
    for S in range(1, 1 << n):
        mem = [i for i in range(n) if S >> i & 1]
        if len(mem) == 1:
            v[S] = F(0)
        else:
            base = max((v[S ^ (1 << i)] for i in mem), default=F(0))
            v[S] = base + F(rng.randint(0, hi))
    return Game(n, v)


if __name__ == "__main__":
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    rng = random.Random(seed)
    nonES = has_single = no_single = 0
    rule_hits = {"strong": 0, "nonstrong": 0, "capped": 0, "uncapped": 0}
    for t in range(trials):
        g = rand_nonES_game(rng, 6)
        if not is_balanced_game(g):
            continue
        es, _ = is_ES(g)
        if es:
            continue
        nonES += 1
        gamma, e, strong, lam, M, working = analyze(g)
        if working:
            has_single += 1
            for (j, sc, cc, info) in working:
                rule_hits[sc] += 1; rule_hits[cc] += 1
        else:
            no_single += 1
            print(f"NO single-strip escape: v={[str(x) for x in g.v]} gamma={[str(x) for x in gamma]} e={e} strong={strong} lam={lam}", flush=True)
    print(f"seed={seed} nonES={nonES} has_single_strip_escape={has_single} "
          f"NO_single={no_single} rule_tag_hits={rule_hits}", flush=True)
