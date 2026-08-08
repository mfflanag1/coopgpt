"""d2: the abstract consistency lab.

Encodes over the rationals every NECESSARY condition a monotonicity failure
must satisfy, together with the negation of one half of C-C, and asks z3.

  UNSAT  ==>  that half of C-C follows from the encoded conditions -- a proof
              whose ingredients are exactly the condition groups switched on.
  SAT    ==>  the encoded conditions are too weak; the model is a blueprint
              for a counterexample (which must then be realized for real).

Condition groups (switchable, so the minimal sufficient set can be located):

  core   phi in core(v), phi' in core(v'), both efficient
  sup    superadditivity of v on disjoint pairs (a consequence of exactness)
  exv    exactness of v : a core(v) witness y^T with y^T(T)=v(T), every proper T
  exv2   exactness of v': a core(v') witness z^T with z^T(T)=v'(T)
  cert   Lemma L (leximin optimality certificate) for phi at every cut
  prot2  protector lemma for phi' (the shape-free consequence of Lemma L)
  hstar  H* is the innermost slack richer suffix of phi

Lemma L.  If phi is leximin-maximal on core(v), with strata B_1 < ... < B_k and
richer suffixes H_j, then for every j there are lambda_T >= 0 supported on
proper phi-tight coalitions and a scalar nu with
      sum_{T ni i} lambda_T  =  nu       for all i in H_j,
      sum_{T ni i} lambda_T  <= nu - 1   for all i in B_j
(no condition on the poorer players).  Witnessed by lambda = 1_{H_j}, nu = 1
whenever H_j is phi-tight.

Protector lemma.  If phi is leximin-maximal on core(v) and phi_i < phi_r then
some proper phi-tight T has r in T and i not in T.

Players are sorted, phi_0 <= ... <= phi_{n-1}, WLOG by relabelling; a gap
pattern is the set of cut positions c in {1..n-1} where phi_{c-1} < phi_c.
S is a *variable* coalition (one-hot booleans), so each z3 call quantifies over
all admissible bumped coalitions at once.

usage: d2_lab.py <n> <right|left|control> [group,group,...] [--timeout=SEC]
"""
import sys, itertools, time, json
import z3

ALLGROUPS = ["core", "sup", "exv", "exv2", "cert", "cert2", "worse", "hstar"]


def bits(n, T):
    return [i for i in range(n) if T >> i & 1]


def build(n, gaps, cstar, target, groups):
    FULL = (1 << n) - 1
    props = list(range(1, FULL))
    R = z3.Real
    s = z3.Solver()

    v = {T: R("v_%d" % T) for T in props}
    v[FULL] = z3.RealVal(1)
    for i in range(n):
        s.add(v[1 << i] == 0)
    al = R("alpha")
    s.add(al > 0)

    cand = [T for T in props if bin(T).count("1") >= 2]
    isS = {T: z3.Bool("isS_%d" % T) for T in cand}
    s.add(z3.PbEq([(isS[T], 1) for T in cand], 1))
    inS = [z3.Bool("inS_%d" % i) for i in range(n)]
    for T in cand:
        s.add(z3.Implies(isS[T], z3.And([inS[i] for i in bits(n, T)] +
                                        [z3.Not(inS[i]) for i in range(n)
                                         if not T >> i & 1])))

    v2 = {}
    for T in props:
        w = R("w_%d" % T)
        v2[T] = w
        if T in isS:
            s.add(z3.If(isS[T], w == v[T] + al, w == v[T]))
        else:
            s.add(w == v[T])
    v2[FULL] = z3.RealVal(1)

    phi = [R("p_%d" % i) for i in range(n)]
    ph2 = [R("q_%d" % i) for i in range(n)]

    def tot(x, T):
        return z3.Sum([x[i] for i in bits(n, T)])

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

    if "sup" in groups:
        for A in props:
            for B in props:
                if A < B and (A & B) == 0:
                    s.add(v[A | B] >= v[A] + v[B])

    if "exv" in groups:
        for T in props:
            y = [R("y%d_%d" % (T, i)) for i in range(n)]
            s.add(tot(y, FULL) == v[FULL])
            for U in props:
                s.add(tot(y, U) >= v[U])
            s.add(tot(y, T) == v[T])

    if "exv2" in groups:
        for T in props:
            zz = [R("z%d_%d" % (T, i)) for i in range(n)]
            s.add(tot(zz, FULL) == v2[FULL])
            for U in props:
                s.add(tot(zz, U) >= v2[U])
            s.add(tot(zz, T) == v2[T])

    if "cert" in groups:
        for c in cuts:
            H, B = Hof[c], Bof[c]
            lam = {T: R("l_%d_%d" % (c, T)) for T in props}
            nu = R("nu_%d" % c)
            for T in props:
                s.add(lam[T] >= 0)
                s.add(z3.Implies(lam[T] > 0, tot(phi, T) == v[T]))
            for i in range(n):
                cover = z3.Sum([lam[T] for T in props if T >> i & 1])
                if H >> i & 1:
                    s.add(cover == nu)
                elif B >> i & 1:
                    s.add(cover <= nu - 1)

    if "cert2" in groups:
        # Lemma L for phi' in shape-free form: one certificate per attained
        # level.  Level m is phi'_m; H = {i : phi'_i > phi'_m}, B = {i : phi'_i
        # = phi'_m}.  Memberships are unknown, so the two constraint families
        # are guarded by the corresponding comparisons.
        for m in range(n):
            lam = {T: R("L2_%d_%d" % (m, T)) for T in props}
            nu = R("nu2_%d" % m)
            for T in props:
                s.add(lam[T] >= 0)
                s.add(z3.Implies(lam[T] > 0, tot(ph2, T) == v2[T]))
            for i in range(n):
                cover = z3.Sum([lam[T] for T in props if T >> i & 1])
                s.add(z3.Implies(ph2[i] > ph2[m], cover == nu))
                s.add(z3.Implies(ph2[i] == ph2[m], cover <= nu - 1))

    if "worse" in groups:
        # phi' lies in core(v) too, and phi is leximin-maximal there, so
        # phi' is leximin-strictly-worse than phi.  Encoded on the ladder
        # Sigma_m(x) = min_{|A|=m} x(A): sorted(phi') <lex sorted(phi) iff
        # (Sigma_m(phi'))_m <lex (Sigma_m(phi))_m.
        Sg, Sf = [], []
        for m in range(1, n + 1):
            A = list(itertools.combinations(range(n), m))
            g = R("Sg_%d" % m)
            for a in A:
                s.add(g <= z3.Sum([ph2[i] for i in a]))
            s.add(z3.Or([g == z3.Sum([ph2[i] for i in a]) for a in A]))
            Sg.append(g)
            Sf.append(z3.Sum([phi[i] for i in range(m)]))   # phi is sorted
        s.add(z3.Or([z3.And([Sg[l] == Sf[l] for l in range(m)] + [Sg[m] < Sf[m]])
                     for m in range(n)]))

    if "prot2" in groups:
        for i in range(n):
            for r in range(n):
                if i == r:
                    continue
                opts = [tot(ph2, T) == v2[T] for T in props
                        if (T >> r & 1) and not (T >> i & 1)]
                s.add(z3.Implies(ph2[i] < ph2[r], z3.Or(opts)))

    Hs = Hof[cstar]
    if "hstar" in groups:                      # cstar = j*, the INNERMOST slack cut
        s.add(tot(phi, Hs) > v[Hs])
        for c in cuts:
            if c > cstar:
                s.add(tot(phi, Hof[c]) == v[Hof[c]])
    if "hmin" in groups:                       # cstar = j_min, the OUTERMOST slack cut
        s.add(tot(phi, Hs) > v[Hs])
        for c in cuts:
            if c < cstar:
                s.add(tot(phi, Hof[c]) == v[Hof[c]])

    # ---- the monotonicity failure: W = {i in S : phi'_i < phi_i} nonempty
    s.add(z3.Or([z3.And(inS[i], ph2[i] < phi[i]) for i in range(n)]))

    if target == "right":                       # negate H* subset S
        s.add(z3.Or([z3.Not(inS[i]) for i in bits(n, Hs)]))
    elif target == "left":                      # negate W subset H*
        s.add(z3.Or([z3.And(inS[i], ph2[i] < phi[i])
                     for i in range(n) if not Hs >> i & 1]))
    elif target == "leftmin":     # negate W subset (outermost slack suffix)
        s.add(z3.Or([z3.And(inS[i], ph2[i] < phi[i])
                     for i in range(n) if not Hs >> i & 1]))
    elif target == "rightmin":    # negate (outermost slack suffix) subset S
        s.add(z3.Or([z3.Not(inS[i]) for i in bits(n, Hs)]))
    elif target == "controlmin":  # assert both; expect SAT
        s.add(z3.And([inS[i] for i in bits(n, Hs)]))
        for i in range(n):
            if not Hs >> i & 1:
                s.add(z3.Not(z3.And(inS[i], ph2[i] < phi[i])))
    elif target == "control":                   # assert C-C; expect SAT
        s.add(z3.And([inS[i] for i in bits(n, Hs)]))
        for i in range(n):
            if not Hs >> i & 1:
                s.add(z3.Not(z3.And(inS[i], ph2[i] < phi[i])))
    else:
        raise SystemExit("bad target")

    return s, dict(v=v, v2=v2, phi=phi, ph2=ph2, isS=isS, inS=inS, al=al,
                   cuts=cuts, Hof=Hof, Bof=Bof, Hs=Hs)


def main():
    n = int(sys.argv[1])
    target = sys.argv[2]
    groups = ALLGROUPS
    tmo = 120000
    for a in sys.argv[3:]:
        if a.startswith("--timeout="):
            tmo = int(float(a.split("=")[1]) * 1000)
        else:
            groups = a.split(",")
    print("n=%d target=%s groups=%s timeout=%ss"
          % (n, target, ",".join(groups), tmo / 1000.0), flush=True)
    tally = {"sat": 0, "unsat": 0, "unknown": 0}
    sats = []
    t0 = time.time()
    for r in range(1, n):
        for gaps in itertools.combinations(range(1, n), r):
            for cstar in gaps:
                s, H = build(n, gaps, cstar, target, groups)
                s.set("timeout", tmo)
                res = s.check()
                tally[str(res)] += 1
                flag = ""
                if res == z3.sat:
                    m = s.model()
                    Sm = [T for T in H["isS"] if z3.is_true(m.eval(H["isS"][T]))]
                    flag = "   S=%s" % Sm
                    sats.append(dict(gaps=list(gaps), cstar=cstar, S=Sm))
                print("  gaps=%-14s c*=%d  %-7s%s  (%.0fs)"
                      % (str(gaps), cstar, res, flag, time.time() - t0), flush=True)
    print(json.dumps(tally))
    if sats:
        print("SAT shapes:", json.dumps(sats)[:3000])
    else:
        print("ALL SHAPES UNSAT -> C-C(%s) follows from {%s} at n=%d"
              % (target, ",".join(groups), n))


if __name__ == "__main__":
    main()
