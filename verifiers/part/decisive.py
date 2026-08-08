"""DECISIVE finite encoding of the PART(p,q) question.

Discharges: the whole of Route B.  UNSAT over every stratification is a
complete impossibility proof for the profile; SAT is a candidate that must
survive the end-to-end audit in audit_model().

WHY THIS ENCODING IS DECISIVE WHERE verifiers/zp/decide.py WAS NOT
==================================================================
Two separate blockers were removed.

(1) EXACTNESS, without the catalogue.
    v is exact  <=>  for every coalition S there is a core point z^S with
    z^S(S) = v(S).  That is EXISTENTIAL and linear, so it is encoded with one
    extra allocation vector per coalition -- no min-semi-balanced catalogue,
    no vertex enumeration, no dependence on the completeness of the
    Studeny-Kratochvil list, and it is exact at every n (the n=6 caveat of
    REPORT.txt simply disappears).  The catalogue cone is retained only as an
    optional independent cross-check (--cone, n=5).

(2) LEXIMIN, in full, quantifier-free and linear.
    Fix the stratification B_1 < ... < B_k of phi.  Then phi = Lmin(v) with
    those strata iff for every stage t and every i in B_t

        max { x_i : x in core(v),  x_l = phi_l (l in B_<t),
                                   x_c >= mu_t (c in B_>=t) }  =  phi_i .

    That is a universally quantified condition -- the blocker identified in
    verifiers/zp/REPORT.txt.  Dualize it.  The feasible set is a polyhedron
    whose ACTIVE constraints at phi are exactly: efficiency; the phi-tight
    coalitions; the pins x_l = phi_l for l in B_<t; and x_c >= mu_t for
    c in B_t only (for c in B_>t that bound is slack at phi).  So the
    condition is "d_i <= 0 on the tangent cone", and Farkas gives an
    EXISTENTIAL certificate: nonnegative y_A supported on phi-TIGHT
    coalitions, free eta, free rho_l (l in B_<t), nonnegative sigma_c
    (c in B_t), with the vector identity

        -sum_A y_A 1_A + eta 1_N + sum_l rho_l e_l - sum_c sigma_c e_c = e_i.

    Complementary slackness at the optimum phi forces the support condition,
    and it is that support condition -- "y_A = 0 OR phi(A) = v(A)" -- which
    keeps the encoding LINEAR (a disjunction, not a product).  The numerical
    side of the dual is then automatic: dotting the identity with phi gives
    the bound with equality.  Both directions are proved, so the encoding is
    an EQUIVALENCE, not a relaxation.

Everything is homogeneous of degree one in (v, phi, z, ...), so normalizing
the boundary slack s_phi(H) = 1 is without loss of generality.

Usage:
  python3 decisive.py part N P Q [--cone] [--timeout S] [--strat IDX]
  python3 decisive.py accept WITNESS.json KEY      (positive control)
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/r23")
sys.path.insert(0, "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/wt/coopgames/verifiers/lib")

import lib23 as L
import z3


# ------------------------------------------------------------ stratifications

def strat_shapes(p, q):
    """Every stratification of the poorer side up to the symmetry that
    permutes P internally and Q internally, encoded as a sequence of pairs
    (alpha_t, beta_t) = (|B_t & P|, |B_t & Q|), poorest block first."""
    out = []

    def rec(ap, aq, acc):
        if ap == 0 and aq == 0:
            out.append(list(acc))
            return
        for da in range(ap + 1):
            for db in range(aq + 1):
                if da == 0 and db == 0:
                    continue
                acc.append((da, db))
                rec(ap - da, aq - db, acc)
                acc.pop()

    rec(p, q, [])
    return out


def stratifications(n, p, q):
    """All (blocks, tag) with H a suffix.  blocks = list of player lists."""
    m = p + q
    f, g = n - 2, n - 1
    res = []
    for shape in strat_shapes(p, q):
        blocks, ip, iq = [], 0, p
        for (da, db) in shape:
            blk = list(range(ip, ip + da)) + list(range(iq, iq + db))
            ip += da
            iq += db
            blocks.append(blk)
        assert ip == p and iq == m
        for htag, hblocks in (("H", [[f, g]]),
                              ("f<g", [[f], [g]]),
                              ("g<f", [[g], [f]])):
            res.append((blocks + hblocks, f"{shape}|{htag}"))
    return res


# ------------------------------------------------------------------- encoding

def build(n, p, q, blocks, use_cone=False, exact_sets=None):
    """Return (solver, v, phi) for one stratification."""
    FULL = (1 << n) - 1
    m = p + q
    assert m == n - 2
    f, g = n - 2, n - 1
    S1 = sum(1 << i for i in range(p)) | (1 << f)
    S2 = sum(1 << i for i in range(p, m)) | (1 << g)
    H = (1 << f) | (1 << g)
    assert S1 | S2 == FULL and S1 & S2 == 0

    v = {S: z3.Real(f"v{S}") for S in range(1, FULL + 1)}
    phi = [z3.Real(f"phi{i}") for i in range(n)]
    s = z3.Solver()

    def tot(vec, S):
        return z3.Sum([vec[i] for i in range(n) if S >> i & 1])

    # -- singleton normalization
    for i in range(n):
        s.add(v[1 << i] == 0)

    # -- phi is a core point
    s.add(z3.Sum(phi) == v[FULL])
    for S in range(1, FULL):
        s.add(tot(phi, S) >= v[S])

    # -- EXACTNESS: one attaining core point per coalition
    if exact_sets is None:
        exact_sets = list(range(1, FULL))
    for S in exact_sets:
        z = [z3.Real(f"z{S}_{i}") for i in range(n)]
        s.add(z3.Sum(z) == v[FULL])
        for A in range(1, FULL):
            s.add(tot(z, A) >= v[A])
        s.add(tot(z, S) == v[S])

    # -- optional independent cross-check: the catalogue cone (n=5 validated
    #    both directions in verifiers/zp/exactcone.py)
    if use_cone:
        import exactcone_shim
        for lam, r in exactcone_shim.systems(n):
            s.add(z3.Sum([c * v[S] for S, c in lam.items()]) <= r * v[FULL])

    # -- the PART configuration
    s.add(tot(phi, S1) == v[S1])
    s.add(tot(phi, S2) == v[S2])
    s.add(tot(phi, H) == v[H] + 1)          # slack normalized to 1 (> 0)

    # -- the stratification: constant on blocks, strictly increasing
    for blk in blocks:
        for i in blk[1:]:
            s.add(phi[i] == phi[blk[0]])
    for t in range(len(blocks) - 1):
        s.add(phi[blocks[t][0]] < phi[blocks[t + 1][0]])
    s.add(phi[blocks[0][0]] >= 0)

    # -- LEXIMIN, stage by stage, as Farkas certificates
    pre = []                                  # players in B_<t
    for t, blk in enumerate(blocks):
        rest = [i for b in blocks[t:] for i in b]     # B_>=t  (unused: see doc)
        for i in blk:
            y = {A: z3.Real(f"y{t}_{i}_{A}") for A in range(1, FULL)}
            eta = z3.Real(f"eta{t}_{i}")
            rho = {l: z3.Real(f"rho{t}_{i}_{l}") for l in pre}
            sig = {c: z3.Real(f"sig{t}_{i}_{c}") for c in blk}
            for A in range(1, FULL):
                s.add(y[A] >= 0)
                # support: y_A > 0 only on phi-tight A
                s.add(z3.Or(y[A] == 0, tot(phi, A) == v[A]))
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
    return s, v, phi, (S1, S2, H)


# --------------------------------------------------------------------- audit

def audit_model(n, p, q, mdl, v):
    """Rebuild the game from the model and re-derive everything from scratch."""
    FULL = (1 << n) - 1
    m = p + q
    f, g = n - 2, n - 1
    S1 = sum(1 << i for i in range(p)) | (1 << f)
    S2 = sum(1 << i for i in range(p, m)) | (1 << g)
    H = (1 << f) | (1 << g)
    w = [F(0)] * (1 << n)
    for S in range(1, FULL + 1):
        w[S] = L.rat(mdl.eval(v[S], model_completion=True))
    out = {"w": {L.nm(n, S): str(w[S]) for S in range(1, FULL + 1)}}
    if w[FULL] <= 0:
        out["verdict"] = "DEGENERATE v(N) <= 0"
        return out
    ex, bad = L.is_exact_lp(n, w)
    out["exact"] = ex
    out["exactness_failure_at"] = None if ex else L.nm(n, bad)
    phi = L.lmin(n, w)
    if phi is None:
        out["verdict"] = "no Lmin"
        return out
    out["lmin"] = [str(x) for x in phi]
    blocks = L.strata(phi)
    out["strata"] = [[L.LETTERS[i] for i in b] for b in blocks]
    sufs = [sum(1 << i for b in blocks[j + 1:] for i in b)
            for j in range(len(blocks) - 1)]
    ok_bd = H in sufs
    slack = sum(phi[i] for i in range(n) if H >> i & 1) - w[H]
    tA = sum(phi[i] for i in range(n) if S1 >> i & 1) == w[S1]
    tB = sum(phi[i] for i in range(n) if S2 >> i & 1) == w[S2]
    out.update({"H_strict_suffix": ok_bd, "slack": str(slack),
                "S1_tight": tA, "S2_tight": tB})
    out["verdict"] = ("GENUINE WITNESS"
                      if (ex and ok_bd and slack > 0 and tA and tB)
                      else "NOT REALIZED AT ITS OWN Lmin")
    return out


# ---------------------------------------------------------------------- main

def run_part(n, p, q, use_cone=False, timeout_s=1800, only=None, quick=None):
    strats = stratifications(n, p, q)
    print(f"PART({p},{q}) on n={n}: {len(strats)} stratifications "
          f"(up to P/Q-internal symmetry)", flush=True)
    results = []
    for idx, (blocks, tag) in enumerate(strats):
        if only is not None and idx != only:
            continue
        s, v, phi, cfg = build(n, p, q, blocks, use_cone=use_cone,
                               exact_sets=quick)
        s.set("timeout", int(timeout_s * 1000))
        t0 = time.time()
        res = s.check()
        el = round(time.time() - t0, 2)
        rec = {"idx": idx, "tag": tag,
               "blocks": [[L.LETTERS[i] for i in b] for b in blocks],
               "status": str(res), "elapsed": el}
        if res == z3.sat:
            rec["audit"] = audit_model(n, p, q, s.model(), v)
        print(f"  [{idx:3d}] {tag:32s} {str(res):6s} {el:8.2f}s"
              + (f"  AUDIT: {rec['audit']['verdict']}" if res == z3.sat else ""),
              flush=True)
        results.append(rec)
        if res == z3.unknown:
            print("    !! UNKNOWN -- this is a FAILURE, not a result", flush=True)
    return results


def main():
    cmd = sys.argv[1]
    if cmd == "part":
        n, p, q = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        use_cone = "--cone" in sys.argv
        to = 1800
        only = None
        if "--timeout" in sys.argv:
            to = float(sys.argv[sys.argv.index("--timeout") + 1])
        if "--strat" in sys.argv:
            only = int(sys.argv[sys.argv.index("--strat") + 1])
        res = run_part(n, p, q, use_cone, to, only)
        tag = f"part_{n}_{p}_{q}" + ("_cone" if use_cone else "")
        json.dump(res, open(f"/private/tmp/claude-501/-Users-maxf/"
                            f"f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/"
                            f"r23/{tag}.json", "w"), indent=1)
        n_unsat = sum(1 for r in res if r["status"] == "unsat")
        n_sat = sum(1 for r in res if r["status"] == "sat")
        n_unk = sum(1 for r in res if r["status"] == "unknown")
        print(f"SUMMARY PART({p},{q}) n={n}: unsat={n_unsat} sat={n_sat} "
              f"unknown={n_unk}")
        return
    raise SystemExit(f"unknown command {cmd}")


if __name__ == "__main__":
    main()
