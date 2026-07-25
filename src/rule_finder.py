"""STRIP-SELECTION RULE finder (team-lead assignment).

For many non-ES games (random balanced, n=5 and n=6): compute egalitarian claims
gamma, excess e=gamma(N)-v(N), strong set D, CEA lambda, core-max ceiling M_i.
For every CAPPED player j (gamma_j > lambda) with gamma_j >= e, test EXACTLY whether the
single-strip vertex y^j (j lowered to gamma_j - e, others at claim) is an undominated
imputation outside the core. Cross-tabulate WORKS vs the candidate separating feature
(ceiling: gamma_j < M_j  vs  gamma_j == M_j  vs  gamma_j > M_j). Also record per game
whether >=1 single-strip works; dump games where none works.
"""
import random, sys
from fractions import Fraction as F
from tugame import Game, is_balanced_game
from eshunt import is_ES, egalitarian_procedure
from pes import pes, _cea_lambda
from core_stability import is_dominated_by_core, in_core, is_imputation

LOG = "/Users/maxf/projects/counterexample-hunt/coopgames/results/rule_finder.txt"


def rand_game(rng, n, hi=3):
    v = [F(0)] * (1 << n)
    for S in range(1, 1 << n):
        mem = [i for i in range(n) if S >> i & 1]
        if len(mem) == 1:
            v[S] = F(0)
        else:
            base = max((v[S ^ (1 << i)] for i in mem), default=F(0))
            v[S] = base + F(rng.randint(0, hi))
    return Game(n, v)


def study(g):
    n, N = g.n, g.N
    gamma, A, k, Nadm = egalitarian_procedure(g)
    p, D = pes(g)
    e = sum(gamma) - g.v[N]
    strong = [i for i in range(n) if D >> i & 1]
    nonstrong = [i for i in range(n) if not (D >> i & 1)]
    lam = _cea_lambda([gamma[i] for i in nonstrong], g.v[N] - sum(gamma[i] for i in strong))
    M = [g.v[N] - g.v[N ^ (1 << i)] for i in range(n)]
    rows = []  # (j, capped?, gamma_j>=e?, ceiling_rel, works?)
    for j in range(n):
        capped = gamma[j] > lam
        can = gamma[j] >= e
        if gamma[j] < M[j]:
            crel = "below"
        elif gamma[j] == M[j]:
            crel = "at"
        else:
            crel = "above"
        works = None
        if capped and can:
            y = list(gamma); y[j] = gamma[j] - e
            if is_imputation(g, y) and not in_core(g, y):
                dom, _ = is_dominated_by_core(g, y)
                works = (not dom)
            else:
                works = False
        rows.append((j, capped, can, crel, works, gamma[j], lam, M[j], j in strong))
    return gamma, e, lam, M, strong, rows


def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    seeds = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [0]
    ns = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else [5, 6]
    log = open(LOG, "a")
    def emit(s):
        print(s, flush=True); log.write(s + "\n"); log.flush()
    emit(f"\n===== RULE FINDER trials={trials} seeds={seeds} ns={ns} =====")
    # contingency: crel(below/at/above) x works(True/False) among capped,gamma_j>=e
    cont = {c: {True: 0, False: 0} for c in ("below", "at", "above")}
    games = games_with_strip = games_no_strip = 0
    no_capped_can = 0
    for n in ns:
        for seed in seeds:
            rng = random.Random(1000 * n + seed)
            for t in range(trials):
                g = rand_game(rng, n)
                if not is_balanced_game(g):
                    continue
                es, _ = is_ES(g)
                if es:
                    continue
                games += 1
                gamma, e, lam, M, strong, rows = study(g)
                anywork = False
                any_candidate = False
                for (j, capped, can, crel, works, gj, l, mj, isstrong) in rows:
                    if capped and can:
                        any_candidate = True
                        cont[crel][bool(works)] += 1
                        if works:
                            anywork = True
                if not any_candidate:
                    no_capped_can += 1
                if anywork:
                    games_with_strip += 1
                else:
                    games_no_strip += 1
                    emit(f"NO single-strip works: n={n} v={[str(x) for x in g.v]} "
                         f"gamma={[str(x) for x in gamma]} e={e} lam={lam} M={[str(x) for x in M]} strong={strong}")
                if games % 20 == 0:
                    emit(f"  [progress] games={games} with_strip={games_with_strip} "
                         f"no_strip={games_no_strip} cont={cont}")
    emit(f"games(nonES)={games} with_single_strip={games_with_strip} "
         f"NO_single_strip={games_no_strip} (no capped j with gamma_j>=e: {no_capped_can})")
    emit(f"contingency [ceiling_rel x works] among capped, gamma_j>=e:")
    for c in ("below", "at", "above"):
        emit(f"   gamma_j {c} M_j : works=True {cont[c][True]}   works=False {cont[c][False]}")
    log.close()


if __name__ == "__main__":
    main()
