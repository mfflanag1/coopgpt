"""d6: closed forms for the BT constructive family.

Within a region of parameter space on which (i) the attaining row of each
coalition value is fixed and (ii) the set of phi-tight coalitions is fixed,
v(T) is a linear form in (a,b,c,e,f,g,h,i,j) and phi is the unique solution of
the linear system {phi(T) = v(T) : T in a spanning set of tight coalitions}.
So phi, every richer-suffix slack, s_phi(S) and the window endpoint alpha_ex
are explicit LINEAR (hence rational) functions of the parameters there.

This driver derives them symbolically with sympy over the rationals and then
checks each formula against the exactly computed numerical value on every
family member of that region -- symbolic vs numeric, no floats.

usage: d6_closed.py <family_axis.json> [family_box.json ...]
"""
import sys, json, itertools
from fractions import Fraction as F
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r12")
import lib12 as L
import sympy as sp

N = 6
FULL = 63
PN = ["a", "b", "c", "e", "f", "g", "h", "i", "j"]
SYM = {k: sp.Symbol(k, rational=True) for k in PN}
# rows as symbolic vectors
ROWA = [0, SYM["a"], 0, SYM["b"], 0, 0]
ROWB = [0, SYM["c"], 0, SYM["e"], SYM["f"], SYM["g"]]
ROWC = [SYM["h"], 0, SYM["i"], 0, SYM["j"], 0]
ROWS = [ROWA, ROWB, ROWC]


def sym_row_val(r, T):
    return sp.expand(sum(r[i] for i in L.members(N, T)))


def load(paths):
    hits = []
    for p in paths:
        d = json.load(open(p))
        hits += d["hits"]
    return hits


def numeric(p):
    rows = ((0, p["a"], 0, p["b"], 0, 0),
            (0, p["c"], 0, p["e"], p["f"], p["g"]),
            (p["h"], 0, p["i"], 0, p["j"], 0))
    v = L.envelope(N, [tuple(F(q) for q in r) for r in rows])
    phi = L.lmin_staged(N, v)
    return v, phi


def region_key(p, v, phi):
    """(argmin-row pattern, tight-coalition family) -- constant on a region."""
    rowvals = {}
    for T in range(1, FULL):
        vals = [sum(r[i] for i in L.members(N, T)) for r in
                ((0, p["a"], 0, p["b"], 0, 0),
                 (0, p["c"], 0, p["e"], p["f"], p["g"]),
                 (p["h"], 0, p["i"], 0, p["j"], 0))]
        m = min(vals)
        rowvals[T] = tuple(k for k in range(3) if vals[k] == m)
    tight = tuple(T for T in L.masks(N) if L.xsum(phi, N, T) == v[T])
    strata = tuple(tuple(b) for b in L.strata(N, phi))
    return (tuple(sorted(rowvals.items())), tight, strata), rowvals


def sym_v(T, rowvals):
    return sym_row_val(ROWS[rowvals[T][0]], T)


def spanning_system(tight, strata, rowvals):
    """phi is pinned by (i) phi(T) = v(T) at tight coalitions, including T = N,
    and (ii) phi_i = phi_j inside each payoff stratum.  Collect an independent
    subsystem of rank 6; return (rows, rhs, labels)."""
    rows, rhs, lab, M = [], [], [], []
    cands = []
    for b in strata:                                  # intra-stratum equalities
        for x, y in zip(b, b[1:]):
            r = [0] * N
            r[x], r[y] = 1, -1
            cands.append((r, sp.Integer(0), "phi_%d=phi_%d" % (x + 1, y + 1)))
    for T in [FULL] + list(tight):                    # tight coalitions
        r = [1 if T >> i & 1 else 0 for i in range(N)]
        val = sym_row_val(ROWS[0], FULL) if T == FULL else sym_v(T, rowvals)
        cands.append((r, val, "phi(%s)=v(%s)" % (L.nm(N, T), L.nm(N, T))))
    for r, val, name in cands:
        if sp.Matrix(M + [r]).rank() > len(M):
            M.append(r)
            rows.append(r)
            rhs.append(val)
            lab.append(name)
        if len(M) == N:
            return rows, rhs, lab
    return None, None, None


def derive(members, rowvals, tight, strata):
    rows, rhs, lab = spanning_system(tight, strata, rowvals)
    if rows is None:
        return None, None
    sol = sp.Matrix(rows).solve(sp.Matrix(rhs))
    return [sp.simplify(sp.expand(sol[i])) for i in range(N)], lab


def main():
    hits = load(sys.argv[1:])
    groups = {}
    for h in hits:
        p = {k: h["params"][k] for k in PN}
        v, phi = numeric(p)
        key, rowvals = region_key(h["params"], v, phi)
        groups.setdefault(key, []).append((h, p, v, phi, rowvals))
    print("family members: %d   regions: %d   sizes: %s"
          % (len(hits), len(groups),
             sorted((len(g) for g in groups.values()), reverse=True)))
    report = []
    for gi, (key, mem) in enumerate(sorted(groups.items(),
                                           key=lambda kv: -len(kv[1]))):
        rowvals = mem[0][4]
        tight = key[1]
        strata = key[2]
        phisym, basis = derive(mem, rowvals, tight, strata)
        if phisym is None:
            print("region %d: system rank < 6 (size %d)" % (gi, len(mem)))
            continue
        ok = True
        for h, p, v, phi, rv in mem:
            sub = {SYM[k]: sp.Rational(p[k]) for k in PN}
            val = [sp.nsimplify(x.subs(sub)) for x in phisym]
            if [sp.Rational(q.numerator, q.denominator) for q in phi] != val:
                ok = False
                print("  MISMATCH", p, phi, val)
        # richer-suffix slacks and H*, symbolically
        h0, p0, v0, phi0, rv0 = mem[0]
        suf = []
        for _, Hj, s in L.suffixes(N, v0, phi0):
            e = sp.expand(sum(phisym[i] for i in L.members(N, Hj))
                          - sym_v(Hj, rowvals))
            suf.append((L.nm(N, Hj), sp.simplify(e), str(s)))
        info = dict(region=gi, size=len(mem),
                    strata=[[i + 1 for i in b] for b in strata],
                    basis=basis,
                    phi=[sp.srepr(x) if False else str(x) for x in phisym],
                    suffix_slacks=[(nmH, str(e)) for nmH, e, _ in suf],
                    verified_on_all_members=ok,
                    example_params=p0)
        # window for each recorded violating S in this region
        wins = []
        for h, p, v, phi, rv in mem[:1]:
            seen=set()
            for viol in h["viol"]:
                if viol["Smask"] in seen: continue
                seen.add(viol["Smask"])
                Sm = viol["Smask"]
                sS = sp.expand(sum(phisym[i] for i in L.members(N, Sm))
                               - sym_v(Sm, rowvals))
                aex, Tstar, xstar = L.alpha_exact_argmin(N, v, Sm)
                asym = None
                if xstar is not None:
                    # x* is pinned by its active core constraints together with
                    # x(T*) = v(T*); solve that subsystem symbolically.
                    rows, rhs, M = [], [], []
                    act = [FULL, Tstar] + [T for T in L.masks(N)
                                           if L.xsum(xstar, N, T) == v[T]]
                    for T in act:
                        r = [1 if T >> k & 1 else 0 for k in range(N)]
                        if sp.Matrix(M + [r]).rank() > len(M):
                            M.append(r)
                            rows.append(r)
                            rhs.append(sym_row_val(ROWS[0], FULL) if T == FULL
                                       else sym_v(T, rowvals))
                        if len(M) == N:
                            break
                    if len(M) == N:
                        xs = sp.Matrix(rows).solve(sp.Matrix(rhs))
                        asym = sp.simplify(sp.expand(
                            sum(xs[k] for k in L.members(N, Sm))
                            - sym_v(Sm, rowvals)))
                        sub = {SYM[k]: sp.Rational(p[k]) for k in PN}
                        chk = sp.nsimplify(asym.subs(sub))
                        if chk != sp.Rational(aex.numerator, aex.denominator):
                            asym = "MISMATCH %s vs %s" % (chk, aex)
                wins.append(dict(S=viol["S"], s_phi_S=str(sp.simplify(sS)),
                                 s_phi_S_numeric=viol["s_phi_S"],
                                 alpha_ex=str(asym), Tstar=L.nm(N, Tstar),
                                 alpha_ex_numeric=str(aex),
                                 W=viol["W"]))
        info["windows"] = wins
        report.append(info)
        print("\n=== region %d  (%d members)  strata %s  verified=%s"
              % (gi, len(mem), info["strata"], ok))
        print("    pinning system:", info["basis"])
        for i, x in enumerate(phisym):
            print("    phi_%d = %s" % (i + 1, x))
        for nmH, e, sval in suf:
            print("    s_phi(%s) = %s        [%s at the base point]" % (nmH, e, sval))
        for w in wins:
            print("    S=%s   window = ( %s , %s ]   [numeric ( %s , %s ]]"
                  "   binding T*=%s   W=%s"
                  % (w["S"], w["s_phi_S"], w["alpha_ex"], w["s_phi_S_numeric"],
                     w["alpha_ex_numeric"], w["Tstar"], w["W"]))
    json.dump(report, open("closed_forms.json", "w"), indent=1)
    print("\nregions with verified closed forms: %d / %d"
          % (sum(1 for r in report if r["verified_on_all_members"]), len(report)))


if __name__ == "__main__":
    main()
