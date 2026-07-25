"""Hunt: STABLE-CORE non-ES games (second half of Dietzenbacher 2021 open Q).

Route: Solymosi-Raghavan (IJGT 30:177-185, 2001). For an assignment game the
core is a von Neumann-Morgenstern stable set IFF the valuation matrix has a
DOMINANT DIAGONAL: after permuting so the optimal matching is the diagonal,
    a_ii >= a_ij  and  a_ii >= a_ji   for all i, j.
(each matched pair value is a row- and column-maximum.)
They further show large core <=> exact <=> extendable <=> (dominant AND doubly
dominant diagonal), and that these STRICTLY imply stable core. Since
large core => egalitarian stable (Dietzenbacher 2021), the ONLY candidates for
a stable-core non-ES game among assignment games are dominant-diagonal matrices
that are NOT large-core (i.e. not doubly dominant / not exact).

A 3x3 matrix -> 6 players = exactly the open frontier (stable<=>large for n<=5).

Generation: draw diagonal d_i >= 1; each off-diagonal a_ij (i!=j) in
[0, min(d_i,d_j)] -> dominant diagonal by construction, diagonal optimal.
Then build assignment game, run the (validated) egalitarian procedure, test ES.
ANY non-ES dominant-diagonal game => stable-core non-ES witness at n=6.
"""
import random, sys, json
from fractions import Fraction as F
from itertools import permutations
from tugame import Game
from assignment import assignment_game
from eshunt import is_ES, egalitarian_procedure
from hunt_sd import is_exact_game
import es_check_main


def dominant_diagonal(A):
    """True iff a_ii >= a_ij and a_ii >= a_ji for all i,j (square matrix)."""
    m = len(A)
    for i in range(m):
        for j in range(m):
            if i == j:
                continue
            if A[i][i] < A[i][j] or A[i][i] < A[j][i]:
                return False
    return True


def doubly_dominant(A):
    """True iff a_ii + a_jk >= a_ik + a_ji for all i,j,k (Solymosi-Raghavan).
    Dominant AND doubly-dominant <=> exact <=> large core. So dominant but NOT
    doubly-dominant = strictly stable core, NOT large: the counterexample regime."""
    m = len(A)
    for i in range(m):
        for j in range(m):
            for k in range(m):
                if A[i][i] + A[j][k] < A[i][k] + A[j][i]:
                    return False
    return True


def diagonal_is_optimal(A):
    """Confirm the diagonal matching attains the max-weight matching value."""
    m = len(A)
    diag = sum(A[i][i] for i in range(m))
    best = max(sum(A[i][p[i]] for i in range(m)) for p in permutations(range(m)))
    return diag == best, diag, best


def gen_dominant(rng, m=3, dmax=8):
    """Random m x m dominant-diagonal integer matrix (diagonal optimal)."""
    d = [rng.randint(1, dmax) for _ in range(m)]
    A = [[0] * m for _ in range(m)]
    for i in range(m):
        A[i][i] = d[i]
    for i in range(m):
        for j in range(m):
            if i != j:
                A[i][j] = rng.randint(0, min(d[i], d[j]))
    return A


def certify_witness(A):
    """Full certification of a stable-core non-ES witness. Returns dict."""
    assert dominant_diagonal(A)
    diag_opt, diag, best = diagonal_is_optimal(A)
    g = assignment_game(A)
    n = g.n
    # ES via two independent validated implementations
    es_eshunt, gamma = is_ES(g)
    _, _, _, _ = egalitarian_procedure(g)
    fixed, Aadm, es_main = es_check_main.egalitarian_procedure(n, list(g.v))
    gamma_main = [fixed[i] for i in range(n)]
    inflation = sum(gamma) - g.v[g.N]
    return {
        "A": A,
        "n": n,
        "diagonal_optimal": diag_opt,
        "v(N)": str(g.v[g.N]),
        "dominant_diagonal": True,
        "ES_eshunt": es_eshunt,
        "ES_es_check_main": es_main,
        "gamma_eshunt": [str(x) for x in gamma],
        "gamma_es_check_main": [str(x) for x in gamma_main],
        "inflation_sum_claims_minus_vN": str(inflation),
        "is_exact_game": is_exact_game(g),
        "v_bitmask": [str(x) for x in g.v],
    }


def hunt(trials, seed, m=3, dmax=8, log=None):
    """Generate dominant-diagonal (stable-core) games; test ES. Track the
    non-exact (= non-large) subclass separately: those are the only ones that
    could be non-ES, since large core => ES (Dietzenbacher 2021)."""
    rng = random.Random(seed)
    n_valid = n_nonES = 0
    for t in range(trials):
        A = gen_dominant(rng, m, dmax)
        if not dominant_diagonal(A):
            continue
        n_valid += 1
        g = assignment_game(A)
        es, gamma = is_ES(g)  # cheap exact egalitarian procedure
        if not es:
            n_nonES += 1
            exact = is_exact_game(g)  # only on a hit
            msg = (f"[NON-ES] seed={seed} t={t} exact={exact} A={A} "
                   f"claims={[str(x) for x in gamma]} vN={g.v[g.N]}")
            print(msg, flush=True)
            if log:
                log.write(msg + "\n"); log.flush()
            return A  # first witness
    line = (f"seed={seed} trials={trials} valid_domdiag={n_valid} "
            f"non_ES={n_nonES} (all ES)")
    print(line, flush=True)
    if log:
        log.write(line + "\n"); log.flush()
    return None


if __name__ == "__main__":
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    m = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    dmax = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    w = hunt(trials, seed, m, dmax)
    if w:
        import pprint
        cert = certify_witness(w)
        pprint.pprint(cert)
