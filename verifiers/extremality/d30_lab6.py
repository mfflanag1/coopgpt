"""d30: the C-C^ decision lab, scaled for n = 6.

NOTE ON THE PREMISE.  The n=5 lab (d2_lab.py) never used a facet catalogue or
dual-polyhedron vertices: its `exv`/`exv2` groups already impose exactness
EXISTENTIALLY (one attaining core witness per coalition, linear -- part/
Theorem A) and its `cert`/`cert2` groups already impose leximin optimality by
Farkas certificates (Lemma L / part/ Theorem B).  It is already pipeline-2
style.  So the n=6 wall is not a modelling choice to be undone; it is raw size.
The levers that remain are (a) drop the hypotheses the ablation showed are not
consumed, (b) FIX the bumped coalition S instead of ranging over it with 62
one-hot booleans, and (c) exploit within-stratum symmetry so that only a few S
per shape need be tried.

(b) is the big one: with S fixed, v' is concrete, the inS booleans vanish, and
the solver sees a pure conjunction of linear constraints plus the certificate
implications.

(c) is sound: players inside a payoff stratum are interchangeable -- permuting
them permutes v as well and carries a counterexample to a counterexample -- so
S may be taken to consist of the first j_i players of stratum i.

usage: d30_lab6.py time <n> <gaps> <cstar>        -- time one shape, all S
       d30_lab6.py control                        -- the two faithfulness controls
       d30_lab6.py sweep <n> <target> <budget_s>  -- the universe of shapes
"""
import sys, time, json, itertools
from fractions import Fraction as F
import z3
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L

DEFAULT = ["core", "exv2", "cert", "cert2", "hmin"]


def bits(n, T):
    return [i for i in range(n) if T >> i & 1]


def build(n, gaps, cstar, S, target, groups=DEFAULT, pin=None):
    """Lean encoding with S FIXED.  Returns (solver, handles)."""
    FULL = (1 << n) - 1
    props = list(range(1, FULL))
    s = z3.Solver()
    v = {T: z3.Real("v_%d" % T) for T in props}
    v[FULL] = z3.RealVal(1)
    phi = [z3.Real("p_%d" % i) for i in range(n)]
    ph2 = [z3.Real("q_%d" % i) for i in range(n)]
    al = z3.Real("alpha")

    def tot(x, T):
        return z3.Sum([x[i] for i in bits(n, T)])

    for i in range(n):
        s.add(v[1 << i] == 0)
    s.add(al > 0)
    v2 = {T: (v[T] + al if T == S else v[T]) for T in props}
    v2[FULL] = z3.RealVal(1)
    for c in range(1, n):
        s.add(phi[c - 1] < phi[c] if c in gaps else phi[c - 1] == phi[c])
    cuts = sorted(gaps)
    Hof = {c: sum(1 << i for i in range(c, n)) for c in cuts}
    Bof = {c: sum(1 << i for i in range(a, c)) for a, c in zip([0] + cuts, cuts)}

    if "core" in groups:
        s.add(tot(phi, FULL) == v[FULL])
        s.add(tot(ph2, FULL) == v2[FULL])
        for T in props:
            s.add(tot(phi, T) >= v[T])
            s.add(tot(ph2, T) >= v2[T])
    if "exv" in groups:
        for T in props:
            y = [z3.Real("y%d_%d" % (T, i)) for i in range(n)]
            s.add(tot(y, FULL) == v[FULL])
            for U in props:
                s.add(tot(y, U) >= v[U])
            s.add(tot(y, T) == v[T])
    if "exv2" in groups:
        for T in props:
            z = [z3.Real("z%d_%d" % (T, i)) for i in range(n)]
            s.add(tot(z, FULL) == v2[FULL])
            for U in props:
                s.add(tot(z, U) >= v2[U])
            s.add(tot(z, T) == v2[T])
    if "cert" in groups:
        for c in cuts:
            H, B = Hof[c], Bof[c]
            lam = {T: z3.Real("l_%d_%d" % (c, T)) for T in props}
            nu = z3.Real("nu_%d" % c)
            for T in props:
                s.add(lam[T] >= 0)
                s.add(z3.Implies(lam[T] > 0, tot(phi, T) == v[T]))
            for i in range(n):
                cov = z3.Sum([lam[T] for T in props if T >> i & 1])
                if H >> i & 1:
                    s.add(cov == nu)
                elif B >> i & 1:
                    s.add(cov <= nu - 1)
    if "cert2" in groups:
        for m in range(n):
            lam = {T: z3.Real("L2_%d_%d" % (m, T)) for T in props}
            nu = z3.Real("nu2_%d" % m)
            for T in props:
                s.add(lam[T] >= 0)
                s.add(z3.Implies(lam[T] > 0, tot(ph2, T) == v2[T]))
            for i in range(n):
                cov = z3.Sum([lam[T] for T in props if T >> i & 1])
                s.add(z3.Implies(ph2[i] > ph2[m], cov == nu))
                s.add(z3.Implies(ph2[i] == ph2[m], cov <= nu - 1))
    Hs = Hof[cstar]
    if "hmin" in groups:                      # cstar = outermost slack cut
        s.add(tot(phi, Hs) > v[Hs])
        for c in cuts:
            if c < cstar:
                s.add(tot(phi, Hof[c]) == v[Hof[c]])
    if "hstar" in groups:                     # cstar = innermost slack cut
        s.add(tot(phi, Hs) > v[Hs])
        for c in cuts:
            if c > cstar:
                s.add(tot(phi, Hof[c]) == v[Hof[c]])

    s.add(z3.Or([ph2[i] < phi[i] for i in bits(n, S)]))       # W nonempty
    if target in ("leftmin", "left"):
        s.add(z3.Or([ph2[i] < phi[i] for i in bits(n, S) if not Hs >> i & 1]))
    elif target == "rightmin":
        if (Hs & ~S) == 0:
            s.add(z3.BoolVal(False))          # conclusion holds for this S
    elif target == "control":
        for i in bits(n, S):
            if not Hs >> i & 1:
                s.add(z3.Not(ph2[i] < phi[i]))
        if (Hs & ~S) != 0:
            s.add(z3.BoolVal(False))
    else:
        raise SystemExit("bad target")

    if pin:
        vv, pp, qq, aa = pin
        for T in props:
            s.add(v[T] == L.to_z3(vv[T] / vv[FULL]))
        for i in range(n):
            s.add(phi[i] == L.to_z3(pp[i] / vv[FULL]))
            s.add(ph2[i] == L.to_z3(qq[i] / vv[FULL]))
        s.add(al == L.to_z3(aa / vv[FULL]))
    return s, dict(v=v, phi=phi, ph2=ph2, al=al, Hs=Hs, cuts=cuts)


def s_choices(n, gaps):
    """S up to within-stratum permutation: take the first j_i of stratum i."""
    cuts = sorted(gaps)
    blocks = []
    a = 0
    for c in cuts + [n]:
        blocks.append(list(range(a, c)))
        a = c
    out = []
    for take in itertools.product(*[range(len(b) + 1) for b in blocks]):
        S = 0
        for b, t in zip(blocks, take):
            for i in b[:t]:
                S |= 1 << i
        if bin(S).count("1") >= 2 and S != (1 << n) - 1:
            out.append(S)
    return sorted(set(out))


def main():
    mode = sys.argv[1]
    if mode == "time":
        n = int(sys.argv[2])
        gaps = tuple(int(x) for x in sys.argv[3].split(","))
        cstar = int(sys.argv[4])
        Ss = s_choices(n, gaps)
        print("n=%d gaps=%s c*=%d   %d inequivalent S (vs %d raw)"
              % (n, gaps, cstar, len(Ss), 2 ** n - 2), flush=True)
        for S in Ss:
            for target in ("leftmin", "rightmin"):
                t0 = time.time()
                s, H = build(n, gaps, cstar, S, target)
                s.set("timeout", 300000)
                r = s.check()
                print("  S=%-12s %-9s %-7s (%.1fs)"
                      % (L.nm(n, S), target, r, time.time() - t0), flush=True)
    elif mode == "control":
        # control 1: the n=5 Theorem-1 game must PIN IN SAT on the left target
        V = [F(q) for q in
             [0, 0, 0, 106, 0, 136, 0, 136, 0, 161, 0, 161, 176, 297, 176, 297,
              0, 242, 0, 242, 242, 393, 242, 484, 176, 418, 176, 418, 418, 534,
              418, 660]]
        S5 = 0b11101
        phi = L.lmin_staged(5, V)
        w = L.bumped(V, S5, F(20))
        ph2 = L.lmin_staged(5, w)
        # the Theorem-1 game refutes the H* left inclusion (W={4,5}, H*={5})
        # and SATISFIES the Hhat one, so: hstar target sat, hmin target unsat.
        for tgt, cs, grp, exp in (("left", 4, ["core","exv2","cert","cert2","hstar"], "sat"),
                                  ("leftmin", 3, DEFAULT, "unsat")):
            s, H = build(5, (3, 4), cs, S5, tgt, grp, pin=(V, phi, ph2, F(20)))
            s.set("timeout", 600000)
            print("control 1 (n=5 Theorem-1 game pinned, %-7s target): %s"
                  "  (must be %s)" % (tgt, s.check(), exp), flush=True)
        # control 2: the two audited n=6 C-C-left failures, on the H* left target
        for tag, rows, S6, al in (
            ("A", [(6, 7, 11, 0, 13, 3), (0, 22, 0, 10, 0, 8),
                   (0, 0, 21, 0, 19, 0)], 0b111110, F(25, 16)),
            ("B", [(3, 0, 37, 0, 0, 0), (5, 4, 22, 0, 5, 4),
                   (0, 18, 0, 11, 11, 0)], 0b011110, F(17, 6))):
            v0 = L.envelope(6, [tuple(F(q) for q in r) for r in rows])
            ph0 = L.lmin_staged(6, v0)
            w0 = L.bumped(v0, S6, al)
            p20 = L.lmin_staged(6, w0)
            # the encoding assumes players are indexed in ascending phi order;
            # these games are not, so relabel and permute v, phi, phi', S with it
            perm = sorted(range(6), key=lambda i: (ph0[i], i))   # new index k -> old perm[k]
            def pmask(T):
                return sum(1 << k for k in range(6) if T >> perm[k] & 1)
            v = [F(0)] * 64
            for T in range(1, 64):
                v[pmask(T)] = v0[T]
            ph = [ph0[perm[k]] for k in range(6)]
            p2 = [p20[perm[k]] for k in range(6)]
            S6 = pmask(S6)
            B = L.strata(6, ph)
            gaps = tuple(sorted(sum(len(b) for b in B[:j + 1])
                                for j in range(len(B) - 1)))
            suf = L.suffixes(6, v, ph)
            sizes = [len(b) for b in B]
            pos = {j: sum(sizes[:j]) for j in range(1, len(B))}   # stratum idx -> cut position
            sl = [pos[j] for j, Hj, sv in suf if sv > 0]
            print("  case %s: strata %s gaps %s  slack cut positions %s"
                  % (tag, [[i + 1 for i in b] for b in B], gaps, sl), flush=True)
            # these games REFUTE the H* left inclusion, so the H* target must be sat
            hstar_pos = max(sl)
            s, H = build(6, gaps, hstar_pos, S6, "left",
                         ["core", "exv2", "cert", "cert2", "hstar"],
                         pin=(v, ph, p2, al))
            s.set("timeout", 900000)
            t0 = time.time()
            print("  control 2%s (n=6 C-C-left failure pinned): %s  (must be"
                  " sat)  (%.0fs)" % (tag, s.check(), time.time() - t0),
                  flush=True)
    elif mode == "sweep":
        n = int(sys.argv[2])
        target = sys.argv[3]
        budget = float(sys.argv[4])
        t0 = time.time()
        tally = {"sat": 0, "unsat": 0, "unknown": 0}
        sats = []
        done = 0
        for r in range(1, n):
            for gaps in itertools.combinations(range(1, n), r):
                for cstar in gaps:
                    for S in s_choices(n, gaps):
                        if time.time() - t0 > budget:
                            print("BUDGET STOP after %d calls" % done, flush=True)
                            print(json.dumps(tally))
                            return
                        s, H = build(n, gaps, cstar, S, target)
                        s.set("timeout", 120000)
                        res = s.check()
                        tally[str(res)] += 1
                        done += 1
                        if res == z3.sat:
                            sats.append(dict(gaps=list(gaps), cstar=cstar,
                                             S=L.nm(n, S)))
                            print("  SAT gaps=%s c*=%d S=%s"
                                  % (gaps, cstar, L.nm(n, S)), flush=True)
                        if done % 25 == 0:
                            print("  %d calls, %.0fs, %s"
                                  % (done, time.time() - t0, json.dumps(tally)),
                                  flush=True)
        print(json.dumps(tally))
        json.dump(dict(tally=tally, sats=sats),
                  open("lab6_%s.json" % target, "w"), indent=1)


if __name__ == "__main__":
    main()
