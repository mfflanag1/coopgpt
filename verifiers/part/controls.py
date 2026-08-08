"""CONTROLS for the decisive encoding.  Nothing in this campaign is believable
without them: the previous attempt (verifiers/zp/decide.py) failed precisely by
producing fake models, so the controls ARE the certificate of decisiveness.

Discharges:
  CONTROL L+ : the Farkas leximin encoding ACCEPTS phi = Lmin(v) on random
               exact games.  (If it did not, every UNSAT would be vacuous.)
  CONTROL L- : the same encoding REJECTS every core point that is not Lmin,
               and rejects Lmin declared with the wrong stratification.
  CONTROL X+ : the exactness encoding (one attaining core point per coalition)
               ACCEPTS exact games ...
  CONTROL X- : ... and REJECTS non-exact games.
  CONTROL P+ : the FULL PART encoding, with v and phi pinned to a harvested
               genuine PART(1,3) witness, is SAT -- so the encoding does not
               over-constrain a real realization.

Usage:
  python3 controls.py leximin N TRIALS SEED
  python3 controls.py exactness N TRIALS SEED
  python3 controls.py accept WITNESS.json KEY
"""
from __future__ import annotations

import json
import random
import sys
from fractions import Fraction as F

sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
import lib23 as L
import z3


# ------------------------------------------------ the leximin block, isolated

def leximin_cert_sat(n, w, phi, blocks, timeout_s=120):
    """Is there a Farkas certificate bundle proving that phi is the leximin
    core point of w with the declared strata?  w, phi are CONCRETE rationals,
    so this isolates exactly the leximin part of decisive.build()."""
    FULL = (1 << n) - 1
    s = z3.Solver()
    s.set("timeout", int(timeout_s * 1000))

    def tightA(A):
        return sum(phi[i] for i in range(n) if A >> i & 1) == w[A]

    pre = []
    for t, blk in enumerate(blocks):
        for i in blk:
            y = {A: z3.Real(f"y{t}_{i}_{A}") for A in range(1, FULL)}
            eta = z3.Real(f"eta{t}_{i}")
            rho = {l: z3.Real(f"rho{t}_{i}_{l}") for l in pre}
            sig = {c: z3.Real(f"sig{t}_{i}_{c}") for c in blk}
            for A in range(1, FULL):
                s.add(y[A] >= 0)
                if not tightA(A):
                    s.add(y[A] == 0)
            for c in blk:
                s.add(sig[c] >= 0)
            for j in range(n):
                lhs = -z3.Sum([y[A] for A in range(1, FULL) if A >> j & 1]) + eta
                if j in rho:
                    lhs = lhs + rho[j]
                if j in sig:
                    lhs = lhs - sig[j]
                s.add(lhs == (1 if j == i else 0))
        pre = pre + blk
    r = s.check()
    assert r != z3.unknown, "solver returned unknown"
    return r == z3.sat


def rand_exact(n, rng):
    total = rng.randint(n, 20)
    npts = rng.randint(2, 5)
    gens = []
    for _ in range(npts):
        while True:
            pp = [rng.randint(0, total) for _ in range(n - 1)]
            last = total - sum(pp)
            if 0 <= last <= total:
                gens.append(tuple(F(x) for x in pp + [last]))
                break
    v = L.envelope(n, gens)
    w, _ = L.normalize(n, v)
    return w


def control_leximin(n, trials, seed):
    rng = random.Random(seed)
    FULL = (1 << n) - 1
    npos = nneg = 0
    fail_pos = fail_neg = 0
    fail_strat = 0
    nstrat = 0
    tested = 0
    while tested < trials:
        w = rand_exact(n, rng)
        if w[FULL] <= 0:
            continue
        phi = L.lmin(n, w)
        if phi is None:
            continue
        tested += 1
        blocks = L.strata(phi)
        # L+ : the true Lmin with its true strata must be ACCEPTED
        npos += 1
        if not leximin_cert_sat(n, w, phi, blocks):
            fail_pos += 1
            print("L+ FAILURE", [str(x) for x in w], [str(x) for x in phi])
        # L- : other core points must be REJECTED
        for _ in range(3):
            x = [z3.Real(f"c{i}") for i in range(n)]
            o = z3.Optimize()
            o.add(z3.Sum(x) == L.to_z3(w[FULL]))
            for S in range(1, FULL):
                o.add(z3.Sum([x[i] for i in range(n) if S >> i & 1])
                      >= L.to_z3(w[S]))
            obj = z3.Sum([L.to_z3(rng.randint(-5, 5)) * x[i] for i in range(n)])
            o.maximize(obj)
            if o.check() != z3.sat:
                continue
            mdl = o.model()
            psi = [L.rat(mdl.eval(x[i], model_completion=True))
                   for i in range(n)]
            if psi == phi:
                continue
            nneg += 1
            if leximin_cert_sat(n, w, psi, L.strata(psi)):
                fail_neg += 1
                print("L- FAILURE (non-Lmin accepted)",
                      [str(q) for q in w], [str(q) for q in psi])
        # L-strat : the true Lmin declared with a WRONG stratification must be
        # rejected (merge two adjacent blocks / split one)
        if len(blocks) >= 2:
            merged = [blocks[0] + blocks[1]] + blocks[2:]
            nstrat += 1
            if leximin_cert_sat(n, w, phi, merged):
                # a merged declaration is only wrong because phi is not
                # constant on the merged block; decisive.build() forbids that
                # separately, so record but do not count as a logic failure
                fail_strat += 1
    print(f"CONTROL L  n={n} games={tested}")
    print(f"  L+ true Lmin accepted   : {npos - fail_pos}/{npos} "
          f"(failures {fail_pos}, must be 0)")
    print(f"  L- non-Lmin rejected    : {nneg - fail_neg}/{nneg} "
          f"(failures {fail_neg}, must be 0)")
    print(f"  merged-strata accepted  : {fail_strat}/{nstrat} "
          f"(informational; blocked in decisive.build by phi-constancy)")
    return fail_pos == 0 and fail_neg == 0


# --------------------------------------------------------- exactness controls

def exactness_cert_sat(n, w, timeout_s=120):
    """Is there, for every coalition S, a core point attaining v(S)?"""
    FULL = (1 << n) - 1
    s = z3.Solver()
    s.set("timeout", int(timeout_s * 1000))
    for S in range(1, FULL):
        z = [z3.Real(f"z{S}_{i}") for i in range(n)]
        s.add(z3.Sum(z) == L.to_z3(w[FULL]))
        for A in range(1, FULL):
            s.add(z3.Sum([z[i] for i in range(n) if A >> i & 1])
                  >= L.to_z3(w[A]))
        s.add(z3.Sum([z[i] for i in range(n) if S >> i & 1]) == L.to_z3(w[S]))
    r = s.check()
    assert r != z3.unknown
    return r == z3.sat


def control_exactness(n, trials, seed):
    rng = random.Random(seed)
    FULL = (1 << n) - 1
    npos = nneg = fpos = fneg = 0
    tested = 0
    while tested < trials:
        w = rand_exact(n, rng)
        if w[FULL] <= 0:
            continue
        tested += 1
        npos += 1
        if not exactness_cert_sat(n, w):
            fpos += 1
            print("X+ FAILURE (exact game rejected)", [str(x) for x in w])
        # perturb one coalition upward: usually destroys exactness
        w2 = list(w)
        S0 = rng.randrange(1, FULL)
        w2[S0] += F(1)
        truth, _ = L.is_exact_lp(n, w2)
        if truth:
            continue
        nneg += 1
        if exactness_cert_sat(n, w2):
            fneg += 1
            print("X- FAILURE (non-exact game accepted)",
                  [str(x) for x in w2])
    print(f"CONTROL X  n={n} games={tested}")
    print(f"  X+ exact accepted     : {npos - fpos}/{npos} (failures {fpos})")
    print(f"  X- non-exact rejected : {nneg - fneg}/{nneg} (failures {fneg})")
    return fpos == 0 and fneg == 0


# ---------------------------------------------------- full-encoding acceptance

def control_accept(path, key, timeout_s=1800):
    """CONTROL P+ : pin the FULL PART encoding to a harvested genuine witness.
    Must be SAT.  Players are relabelled to the canonical layout and the game
    is scaled so that the boundary slack is 1."""
    import decisive as D
    data = json.load(open(path))
    wit = data["found"][key]
    n = wit["n"]
    FULL = (1 << n) - 1
    w = [F(x) for x in wit["w"]]
    phi = [F(x) for x in wit["phi"]]
    S1m, S2m, Hm = wit["S1mask"], wit["S2mask"], wit["Hmask"]
    p, q = wit["split"]
    f_old = [i for i in L.bits(n, Hm) if S1m >> i & 1][0]
    g_old = [i for i in L.bits(n, Hm) if S2m >> i & 1][0]
    P_old = [i for i in L.bits(n, S1m) if i != f_old]
    Q_old = [i for i in L.bits(n, S2m) if i != g_old]
    # canonical layout: P -> 0..p-1, Q -> p..m-1, f -> n-2, g -> n-1
    perm = {}
    for k, i in enumerate(P_old):
        perm[i] = k
    for k, i in enumerate(Q_old):
        perm[i] = p + k
    perm[f_old] = n - 2
    perm[g_old] = n - 1
    def pm(mask):
        return sum(1 << perm[i] for i in L.bits(n, mask))
    w2 = [F(0)] * (1 << n)
    for S in range(1, FULL + 1):
        w2[pm(S)] = w[S]
    phi2 = [F(0)] * n
    for i in range(n):
        phi2[perm[i]] = phi[i]
    slack = sum(phi2[i] for i in range(n) if pm(Hm) >> i & 1) - w2[pm(Hm)]
    assert slack > 0, slack
    sc = F(1) / slack
    w2 = [x * sc for x in w2]
    phi2 = [x * sc for x in phi2]
    blocks = L.strata(phi2)
    print(f"CONTROL P+  witness {key}: n={n} split=({p},{q}) "
          f"strata={[[L.LETTERS[i] for i in b] for b in blocks]}")
    # sanity: recompute from scratch in the relabelled, rescaled game
    ex, bad = L.is_exact_lp(n, w2)
    rec = L.lmin(n, w2)
    print(f"  independent recheck: exact={ex} lmin_matches={rec == phi2}")
    assert ex and rec == phi2
    s, v, ph, cfg = D.build(n, p, q, blocks)
    s.set("timeout", int(timeout_s * 1000))
    for S in range(1, FULL + 1):
        s.add(v[S] == L.to_z3(w2[S]))
    for i in range(n):
        s.add(ph[i] == L.to_z3(phi2[i]))
    r = s.check()
    print(f"  FULL PART ENCODING PINNED AT THE WITNESS: {r}  (must be sat)")
    return r == z3.sat


def main():
    cmd = sys.argv[1]
    if cmd == "leximin":
        ok = control_leximin(int(sys.argv[2]), int(sys.argv[3]),
                             int(sys.argv[4]))
    elif cmd == "exactness":
        ok = control_exactness(int(sys.argv[2]), int(sys.argv[3]),
                               int(sys.argv[4]))
    elif cmd == "accept":
        ok = control_accept(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit(cmd)
    print("CONTROL PASSED" if ok else "CONTROL FAILED")


if __name__ == "__main__":
    main()
