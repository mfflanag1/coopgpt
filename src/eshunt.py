"""Egalitarian procedure (Dietzenbacher 2021) + exactness search.

Egalitarian claims via the iterative procedure; ES iff N is egalitarian
admissible iff sum(claims) == v(N).  Exact rational arithmetic.
"""
import sys, random, json
from fractions import Fraction as F
from tugame import Game
from hunt_sd import is_exact_game, exactify, is_totally_balanced
from tugame import is_balanced_game


def egalitarian_procedure(game):
    """Return (gamma, admissible_final, n_iter, N_admissible_bool).
    gamma = egalitarian claims vector (list of Fractions).
    """
    n, N, v = game.n, game.N, game.v
    coals = list(range(1, N + 1))
    P = 0
    gamma = [None] * n
    A = []
    for k in range(1, n + 2):
        chi = {}
        for S in coals:
            fixedsum = F(0); free = 0
            for i in range(n):
                if S >> i & 1:
                    if P >> i & 1: fixedsum += gamma[i]
                    else: free += 1
            d = {}
            if free == 0:
                for i in range(n):
                    if S >> i & 1: d[i] = gamma[i]
            else:
                share = (v[S] - fixedsum) / free
                for i in range(n):
                    if S >> i & 1:
                        d[i] = gamma[i] if (P >> i & 1) else share
            chi[S] = d
        maxval = [None] * n
        for S in coals:
            for i, val in chi[S].items():
                if maxval[i] is None or val > maxval[i]:
                    maxval[i] = val
        A = []
        for S in coals:
            if sum(chi[S].values()) != v[S]:
                continue
            if all(val == maxval[i] for i, val in chi[S].items()):
                A.append(S)
        newP = 0
        for S in A:
            newP |= S
            for i, val in chi[S].items():
                gamma[i] = val
        if newP | P == P and P != N:
            # stuck (should not happen for balanced games); bail
            raise RuntimeError("egalitarian procedure stuck")
        P |= newP
        if P == N:
            N_adm = (N in A)
            return gamma, A, k, N_adm
    raise RuntimeError("did not terminate")


def is_ES(game):
    gamma, A, k, N_adm = egalitarian_procedure(game)
    eff = (sum(gamma) == game.v[game.N])
    assert eff == N_adm, f"efficiency {eff} != N-admissible {N_adm}"
    return N_adm, gamma


def _test_examples():
    # Example 3: N={0,1,2}, v({0,2})=v({1,2})=v(N)=4 else 0. NOT ES, claims (2,2,2)
    v = [F(0)] * 8
    v[0b101] = 4; v[0b110] = 4; v[0b111] = 4
    g = Game(3, v)
    es, gamma = is_ES(g)
    print("Ex3 claims", gamma, "ES", es, "(expect (2,2,2), False)")
    assert gamma == [F(2), F(2), F(2)] and es is False
    # Example 2: N={0,1,2,3}, v({1,3})=v({2,3})=14, v(N)=24 else 0. ES, claims (3,7,7,7)
    v = [F(0)] * 16
    v[0b1010] = 14; v[0b1100] = 14; v[0b1111] = 24
    g = Game(4, v)
    es, gamma = is_ES(g)
    print("Ex2 claims", gamma, "ES", es, "(expect (3,7,7,7), True)")
    assert gamma == [F(3), F(7), F(7), F(7)] and es is True
    print("VALIDATED on Examples 2 and 3")


if __name__ == "__main__":
    _test_examples()


def rand_balanced(n, rng, lo=0, hi=10):
    """Random superadditive-ish game, return Game if balanced else None."""
    v = [F(0)] * (1 << n)
    for S in range(1, (1 << n) - 1):
        v[S] = F(rng.randint(lo, hi))
    v[(1 << n) - 1] = F(rng.randint(hi, 3 * hi))
    g = Game(n, v)
    return g if is_balanced_game(g) else None


def search(n, trials, seed):
    rng = random.Random(seed)
    tested = 0
    for t in range(trials):
        g = rand_balanced(n, rng)
        if g is None:
            continue
        ge = exactify(g)
        if ge is None:
            continue
        # exactify gives an exact game; sanity-verify occasionally
        es, gamma = is_ES(ge)
        tested += 1
        if not es:
            # double check exactness
            assert is_exact_game(ge), "not actually exact!"
            print("COUNTEREXAMPLE: exact non-ES game", flush=True)
            print(json.dumps({"n": n, "v": [str(x) for x in ge.v],
                              "claims": [str(x) for x in gamma],
                              "sum_claims": str(sum(gamma)),
                              "vN": str(ge.v[ge.N])}, indent=1), flush=True)
            return ge
        if tested % 200 == 0:
            print(f"  ...{tested} exact games tested, all ES (t={t})", flush=True)
    print(f"done: n={n} seed={seed}, {tested} exact games tested, ALL egalitarian stable", flush=True)
    return None


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "search":
    n = int(sys.argv[2]); trials = int(sys.argv[3]); seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    search(n, trials, seed)


def rand_balanced_seeded(n, rng, amax=8, slackmax=6):
    """Balanced by construction: pick core point a>=0, set v(S)=max(0, a(S)-slack).
    a stays in core (a(S)>=v(S), a(N)=v(N)), so game is balanced. Then exactify."""
    a = [F(rng.randint(0, amax)) for _ in range(n)]
    v = [F(0)] * (1 << n)
    N = (1 << n) - 1
    for S in range(1, N):
        aS = sum(a[i] for i in range(n) if S >> i & 1)
        slack = F(rng.randint(0, slackmax))
        v[S] = max(F(0), aS - slack)
    v[N] = sum(a)
    return Game(n, v)


def search2(n, trials, seed, report_every=100):
    rng = random.Random(seed)
    tested = 0
    worst = F(0)  # max inflation sum(claims)-v(N) seen (should stay 0 if all ES)
    for t in range(trials):
        g = rand_balanced_seeded(n, rng)
        ge = exactify(g)
        if ge is None:
            continue
        es, gamma = is_ES(ge)
        tested += 1
        infl = sum(gamma) - ge.v[ge.N]
        if infl > worst:
            worst = infl
        if not es:
            assert is_exact_game(ge)
            print("COUNTEREXAMPLE exact non-ES", flush=True)
            print(json.dumps({"n": n, "v": [str(x) for x in ge.v],
                              "claims": [str(x) for x in gamma],
                              "infl": str(infl)}, indent=1), flush=True)
            with open(f"COUNTEREX_es_n{n}_s{seed}.json", "w") as f:
                json.dump({"n": n, "v": [str(x) for x in ge.v],
                           "claims": [str(x) for x in gamma]}, f, indent=1)
            return ge
        if tested % report_every == 0:
            print(f"  n={n} s={seed}: {tested} exact tested, all ES, worst_infl={worst}", flush=True)
    print(f"DONE n={n} s={seed}: {tested} exact games, ALL ES (worst inflation over aspiration only={worst})", flush=True)
    return None


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "search2":
    n = int(sys.argv[2]); trials = int(sys.argv[3]); seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    search2(n, trials, seed)
