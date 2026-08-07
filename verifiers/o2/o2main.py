"""(*) f({j}) >= T/8 in CFG at n=5 -- the full finite check.

Hypotheses used (all necessary consequences of CFG; derivation in REPORT.txt):
  (A) z0 in Core            v(S) <= (|S| - [j in S])/4
  (B) nu = 1/4 attained     v(S*) = |S*|/4, and 4 v(S) <= |S|            [A3]
  (C) failure               mu = f({j}) = 1 - v(N\\{j}),  0 <= mu < 1/8   [A3 + C2]
  (D) x0 = (mu,mu,mu,rho,rho) in Core,  rho = (1-3mu)/2                  [j poor]
  (E) L = {j,a,b} is PINNED at mu: the dual certificate
          c*alpha + sum_S beta_S f'(S) <= 0,   c = 1-5mu, f'(S)=f(S)-mu|S|
      for one of the 354 vertices (alpha,beta) of D_L.
  (F) the 280 exact-cone inequalities.
Relabelling j = 0, L = {0,1,2}, R = {3,4} is free.  Everything is linear in
(v, mu), so this is 31 x 354 exact linear programs.
"""
from __future__ import annotations
import json, sys
from fractions import Fraction as F
import z3

SCR = "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad"
sys.path.insert(0, SCR); sys.path.insert(0, SCR + "/sel/a3check"); sys.path.insert(0, SCR + "/sel/o2")
from cone import inequalities

N, FULL, J = 5, 31, 0
L, R = [0, 1, 2], [3, 4]
sz = lambda S: bin(S).count("1")
nm = lambda S: "".join("abcde"[i] for i in range(N) if S >> i & 1) or "0"


def load_pinverts():
    raw = json.load(open(f"{SCR}/sel/o2/pinverts.json"))
    return [(F(al), [(int(S), F(x)) for S, x in be]) for al, be in raw]


def prog(Sstar, pin, ineqs, use_cone=True, use_pin=True, budget=400):
    v = [z3.Real(f"v{S}") for S in range(32)]
    mu = z3.Real("mu")
    rho = (1 - 3 * mu) / 2
    s = z3.Solver()
    s.add(v[0] == 0)
    for i in range(N):
        s.add(v[1 << i] == 0)
    s.add(v[FULL] == 1)
    for S in range(1, FULL + 1):
        s.add(v[S] <= F(sz(S) - (1 if S >> J & 1 else 0), 4))            # (A)
        s.add(4 * v[S] <= sz(S))                                          # (B)
        s.add(v[S] <= mu * len([i for i in L if S >> i & 1])
              + rho * len([i for i in R if S >> i & 1]))                  # (D)
    s.add(v[Sstar] == F(sz(Sstar), 4))                                    # (B)
    s.add(mu == 1 - v[FULL ^ (1 << J)])                                   # (C)
    s.add(mu >= 0)
    s.add(mu < F(1, 8))
    if use_pin:                                                           # (E)
        al, be = pin
        fp = lambda S: (1 - v[FULL ^ S]) - mu * sz(S)
        s.add(z3.RealVal(f"{al.numerator}/{al.denominator}") * (1 - 5 * mu)
              + z3.Sum([z3.RealVal(f"{x.numerator}/{x.denominator}") * fp(S)
                        for S, x in be] or [z3.RealVal(0)]) <= 0)
    if not use_cone:
        return s.check() == z3.sat, None
    for _ in range(budget):
        r = s.check()
        assert r in (z3.sat, z3.unsat), f"z3 returned {r}"
        if r == z3.unsat:
            return False, None
        m = s.model()

        def val(e):
            q = z3.simplify(m.eval(e, model_completion=True))
            return (F(q.as_long()) if z3.is_int_value(q)
                    else F(q.numerator_as_long(), q.denominator_as_long()))
        vv = [val(v[S]) for S in range(32)]
        bad = None
        for c in ineqs:
            if sum(F(c[S]) * vv[S] for S in range(1, 32) if c[S]) > 0:
                bad = c; break
        if bad is None:
            return True, {"v": [str(q) for q in vv], "mu": str(val(mu))}
        s.add(z3.Sum([z3.RealVal(bad[S]) * v[S] for S in range(1, 32) if bad[S]]) <= 0)
    raise RuntimeError("cut budget exhausted")


def main():
    ineqs = inequalities(N)
    pins = load_pinverts()
    print(f"{len(ineqs)} cone inequalities, {len(pins)} pinning certificates, "
          f"{FULL} choices of S* -> {len(pins)*FULL} programs", flush=True)
    hits = []
    done = 0
    for Sstar in range(1, FULL + 1):
        for pin in pins:
            feas, wit = prog(Sstar, pin, ineqs)
            done += 1
            if feas:
                hits.append({"Sstar": nm(Sstar), "alpha": str(pin[0]),
                             "beta": {nm(S): str(x) for S, x in pin[1]}, **wit})
                print(f"  FEASIBLE S*={nm(Sstar)} alpha={pin[0]} "
                      f"beta={ {nm(S): str(x) for S, x in pin[1]} } mu={wit['mu']}",
                      flush=True)
        if Sstar % 6 == 0:
            print(f"  ... {done}/{len(pins)*FULL} programs, {len(hits)} feasible",
                  flush=True)
    print(f"MAIN RESULT: {len(hits)} feasible of {done} programs")

    ctrl = 0
    for Sstar in range(1, FULL + 1):
        for pin in pins:
            f, _ = prog(Sstar, pin, ineqs, use_cone=False)
            ctrl += bool(f)
    print(f"  control [no cone]: {ctrl} of {done} programs feasible")
    json.dump({"programs": done, "feasible": hits, "control_no_cone": ctrl},
              open(f"{SCR}/sel/o2/o2main.json", "w"), indent=1)


if __name__ == "__main__":
    main()
