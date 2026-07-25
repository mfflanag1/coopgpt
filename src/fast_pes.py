"""Float-screened hunt for an exact 5-player game that is NOT egalitarian stable.

Heavy exact Fraction-LP work (is_balanced_game, exactify) is ~7s/game at n=5, far too
slow. Here: scipy/HiGHS float LPs screen balancedness + exactification + run a float
egalitarian procedure. Games whose float aspiration-slack sum(claims)-v(N) exceeds a
loose tol are candidates -> handed to the EXACT certifier (hunt_pes.certify_witness).
Float screen: false positives filtered by exact certification; non-ES slacks are
macroscopic rationals, so false negatives are not a concern at tol=1e-6.
"""
import random, sys, json, time
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
from tugame import Game
from hunt_sd import exactify, is_exact_game
from hunt_monotonic import rand_game
from hunt_pes import rand_thin, certify_witness

LOG = "/Users/maxf/projects/counterexample-hunt/coopgames/results/agent_pes.txt"
WIT = "/Users/maxf/projects/counterexample-hunt/coopgames/results/WITNESS_exact_not_ES.json"


def log(msg):
    print(msg, flush=True)
    with open(LOG, "a") as f:
        f.write(msg + "\n"); f.flush()


def _members(S, n):
    return [i for i in range(n) if S >> i & 1]


def float_core_min(vf, n, N, S):
    """Float min of x(S) over core; returns None if infeasible/unbounded."""
    A_ub, b_ub = [], []
    for T in range(1, N):
        A_ub.append([-1.0 if T >> i & 1 else 0.0 for i in range(n)])
        b_ub.append(-vf[T])
    A_eq = [[1.0] * n]; b_eq = [vf[N]]
    c = [1.0 if S >> i & 1 else 0.0 for i in range(n)]
    r = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                bounds=[(None, None)] * n, method="highs")
    if not r.success:
        return None
    return r.fun


def float_is_balanced(vf, n, N):
    A_ub, b_ub = [], []
    for S in range(1, N):
        A_ub.append([-1.0 if S >> i & 1 else 0.0 for i in range(n)])
        b_ub.append(-vf[S])
    c = [1.0] * n
    r = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(None, None)] * n, method="highs")
    if not r.success:
        return False
    return r.fun <= vf[N] + 1e-7


def float_exactify(vf, n, N):
    """Float min-core cover. Returns ve list or None."""
    ve = [0.0] * (1 << n)
    ve[N] = vf[N]
    for S in range(1, N):
        m = float_core_min(vf, n, N, S)
        if m is None:
            return None
        ve[S] = m
    return ve


def float_egal_slack(ve, n, N, tol=1e-9):
    """Run the egalitarian procedure in float. Return sum(claims)-v(N) (>=~0),
    or None on numerical trouble. Non-ES ~ slack macroscopically > 0."""
    P = 0
    gamma = {}
    for _step in range(n + 1):
        maxchi = [None] * n
        chi = {}
        for S in range(1, N + 1):
            mem = _members(S, n)
            fixed = [i for i in mem if P >> i & 1]
            unfixed = [i for i in mem if not (P >> i & 1)]
            sf = sum(gamma[i] for i in fixed)
            d = {}
            if unfixed:
                share = (ve[S] - sf) / len(unfixed)
                for i in fixed:
                    d[i] = gamma[i]
                for i in unfixed:
                    d[i] = share
            else:
                for i in fixed:
                    d[i] = gamma[i]
            chi[S] = d
            for i in mem:
                if maxchi[i] is None or d[i] > maxchi[i]:
                    maxchi[i] = d[i]
        Pnew = 0
        for S in range(1, N + 1):
            d = chi[S]; mem = _members(S, n)
            if abs(sum(d[i] for i in mem) - ve[S]) > 1e-6:
                continue
            if all(abs(d[i] - maxchi[i]) <= 1e-6 for i in mem):
                Pnew |= S
        newP = Pnew | P
        gnew = {}
        for i in range(n):
            if newP >> i & 1:
                gnew[i] = maxchi[i] if (Pnew >> i & 1) else gamma[i]
        if newP == P and newP != N:
            return None  # stuck (numerical)
        P, gamma = newP, gnew
        if P == N:
            break
    if P != N:
        return None
    return sum(gamma[i] for i in range(n)) - ve[N]


def hunt(n, trials, seed, family, slack_tol=1e-6):
    rng = random.Random(seed)
    t0 = time.time()
    exact_seen = 0
    cand = 0
    confirmed = 0
    max_slack = 0.0
    for t in range(trials):
        if family == "thin":
            g0 = rand_thin(n, rng)
        elif family == "general":
            g0 = rand_game(n, rng, "general")
        else:
            g0 = rand_thin(n, rng) if rng.random() < 0.5 else rand_game(n, rng, "general")
        vf = [float(x) for x in g0.v]
        N = (1 << n) - 1
        if not float_is_balanced(vf, n, N):
            continue
        ve = float_exactify(vf, n, N)
        if ve is None:
            continue
        exact_seen += 1
        slack = float_egal_slack(ve, n, N)
        if slack is None:
            continue
        if slack > max_slack:
            max_slack = slack
        if slack > slack_tol:
            cand += 1
            log(f"[float-cand] t={t} float_slack={slack:.6f} family={family} seed={seed}")
            g = exactify(g0)          # EXACT
            if g is None:
                continue
            rep, ok = certify_witness(g)
            if ok:
                confirmed += 1
                log("*** CONFIRMED exact game NOT egalitarian stable ***")
                log(json.dumps(rep, indent=1))
                from hunt_pes import greedy_minimize
                gm = greedy_minimize(g)
                repm, okm = certify_witness(gm)
                out = {"witness": rep, "minimized": repm if okm else None,
                       "seed": seed, "trial": t, "family": family}
                with open(WIT, "w") as f:
                    json.dump(out, f, indent=1)
                log(f"witness saved; minimized_ok={okm}")
                if okm:
                    log("MINIMIZED:\n" + json.dumps(repm, indent=1))
                return out
            else:
                log(f"[float-cand rejected by exact] is_exact={rep['is_exact']} "
                    f"is_ES={rep['is_ES']} exact_slack={rep['sum_claims_minus_vN']}")
        if exact_seen % 2000 == 0:
            log(f"... t={t} exact_seen={exact_seen} cand={cand} confirmed={confirmed} "
                f"max_float_slack={max_slack:.6f} elapsed={time.time()-t0:.0f}s "
                f"family={family} seed={seed}")
    log(f"DONE fast family={family} seed={seed}: exact_seen={exact_seen} cand={cand} "
        f"confirmed={confirmed} max_float_slack={max_slack:.6f} trials={trials}")
    return None


if __name__ == "__main__":
    n = int(sys.argv[1]); trials = int(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    family = sys.argv[4] if len(sys.argv) > 4 else "mix"
    hunt(n, trials, seed, family)
