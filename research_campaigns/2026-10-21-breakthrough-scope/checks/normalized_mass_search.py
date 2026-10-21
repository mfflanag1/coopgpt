#!/usr/bin/env python3
"""Discovery-only normalized KKT-mass search for uniform 0/1 covers.

For each owner i maximize theta_i=q_i/L, not q_i.  With alpha=lambda/L,
t=1/L, and G=A A^T, the exact disjunctive model is

    alpha>=0, sum(alpha)=1, alpha_r<=y_r, 1/n<=t<=n,
    (G alpha)_r>=t                         if i not in row r,
    (G alpha)_r-t+n*y_r<=n                 for every row r.

Binary y_r activates alpha_r.  Thus off-i positive-support rows have value t,
and own positive-support rows have value at most t.  The resulting unscaled
cover uses q=A^T alpha/t, off-i RHS 1, supported own RHS q(S), other own RHS 0.
Full rows are nonempty; empty columns and duplicate rows are allowed.  The
uniform dual-mass lemma gives L<=rho<=n, justifying t>=1/n.  An off-i row gives
t<=n.  If no off-i row exists theta_i=1 directly and is handled separately.

Numerical optimality is not a mathematical proof.  Reports retain solver
status and upper bounds; a separate Fraction check certifies only exhibited
primal/KKT witnesses, never the MILP global bound.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import json
import math
from pathlib import Path
import time

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, linprog, milp, minimize, nnls
from scipy.sparse import lil_matrix


def cyclic(n, seeds):
    """One or more cyclic row orbits; retain each distinct nonempty row."""
    rows = set()
    for seed in seeds:
        for shift in range(n):
            rows.add(tuple(sorted({(j + shift) % n for j in seed})))
    return np.array([[int(j in row) for j in range(n)] for row in sorted(rows)], dtype=float)


def interval(n, k):
    return cyclic(n, [range(k)])


def row_lists(A):
    return [list(map(int, np.flatnonzero(row))) for row in A]


def exact_witness(A, i, alpha, t, max_denominator=1000000):
    """Rationalize a candidate and verify all defining conditions exactly."""
    aa = [F(float(x)).limit_denominator(max_denominator) for x in alpha]
    tt = F(float(t)).limit_denominator(max_denominator)
    n = A.shape[1]
    rows = row_lists(A)
    failed = []
    if sum(aa) != 1:
        failed.append("normalized mass")
    if any(x < 0 for x in aa) or tt <= 0:
        failed.append("sign")
    if tt <= 0:
        return {"certified": False, "failed": failed}
    lam = [x / tt for x in aa]
    q = [sum((lam[r] for r, S in enumerate(rows) if j in S), F(0)) for j in range(n)]
    b = []
    for r, S in enumerate(rows):
        value = sum((q[j] for j in S), F(0))
        rhs = F(1) if i not in S else (value if lam[r] > 0 else F(0))
        b.append(rhs)
        if not 0 <= rhs <= 1:
            failed.append(f"rhs[{r}]")
        if value < rhs:
            failed.append(f"feasibility[{r}]")
        if lam[r] * (value - rhs) != 0:
            failed.append(f"complementarity[{r}]")
    return {"certified": not failed, "failed": failed,
            "alpha": list(map(str, aa)), "t": str(tt),
            "lambda": list(map(str, lam)), "q": list(map(str, q)),
            "rhs": list(map(str, b)), "theta": str(q[i] / sum(lam)),
            "L": str(sum(lam)), "norm2": str(sum(x*x for x in q))}


def full_projection(A, transitive=False):
    n = A.shape[1]
    sizes = A.sum(axis=1)
    k = int(min(sizes))
    if transitive:
        # Transitivity is checked algebraically through regular minimum rows.
        active = A[sizes == k]
        degree = active.sum(axis=0)
        if not np.all(degree == degree[0]) or degree[0] == 0:
            raise ValueError("minimum-size row incidence is not regular")
        rho = F(n, k*k)
        lam = np.zeros(len(A))
        lam[sizes == k] = 1 / (k * degree[0])
        return {"rho": float(rho), "rho_exact": str(rho),
                "q": [1/k]*n, "lambda": lam.tolist(),
                "method": "exact regular minimum-row certificate",
                "primal_residual": 0.0, "stationarity_residual": 0.0,
                "duality_gap": 0.0, "valid": True}
    result = minimize(lambda q: .5 * q@q, np.ones(n)/k,
                      jac=lambda q: q, method="SLSQP",
                      bounds=Bounds(np.zeros(n), np.full(n, np.inf)),
                      constraints=LinearConstraint(A, np.ones(len(A)), np.full(len(A), np.inf)),
                      options={"ftol": 1e-12, "maxiter": 2000})
    q = result.x
    active = np.abs(A@q-1) < 2e-7
    lam = np.zeros(len(A))
    lam[active], _ = nnls(A[active].T, q, maxiter=max(1000, 10*len(A)))
    rho = float(q@q)
    stationarity = float(np.max(np.abs(A.T@lam-q)))
    feasibility = float(max(0, np.max(1-A@q), np.max(-q)))
    duality_gap = float(rho - (2*sum(lam)-(A.T@lam)@(A.T@lam)))
    return {"rho": rho, "rho_exact": None, "q": q.tolist(), "lambda": lam.tolist(),
            "method": "SLSQP primal with independent NNLS dual certificate",
            "success": bool(result.success), "message": result.message,
            "primal_residual": feasibility, "stationarity_residual": stationarity,
            "duality_gap": duality_gap,
            "valid": feasibility < 2e-7 and stationarity < 2e-7 and abs(duality_gap) < 2e-7}


def optimize_owner(A, i, seconds=30, gap=0.0, relax=False, endpoint=False, baseline=None, allowed_support=None):
    started = time.monotonic()
    m, n = A.shape
    own = A[:, i] > .5
    off = ~own
    if not off.any():
        # Keep just one row at demand 1; all remaining own demands are 0.
        alpha = np.zeros(m)
        alpha[0] = 1.
        t = float(A[0].sum())
        return {"owner": i, "status": 0, "message": "all rows incident: exact theta=1",
                "theta": 1.0, "theta_upper": 1.0, "elapsed": time.monotonic()-started,
                "alpha": alpha.tolist(), "t": t,
                "exact": exact_witness(A, i, alpha, t), "valid": True}
    G = A @ A.T
    c = np.zeros(2*m+1)
    c[:m] = -A[:, i]
    lower = np.zeros(2*m+1)
    upper = np.ones(2*m+1)
    lower[m] = 1/n
    upper[m] = n
    if allowed_support is not None:
        permitted = set(allowed_support)
        for r in range(m):
            if r not in permitted:
                upper[r] = 0
                upper[m+1+r] = 0
        # The unconstrained full projection need not respect this restriction.
        baseline = None
    integrality = np.zeros(2*m+1)
    if not relax:
        integrality[m+1:] = 1
    # mass; alpha<=support; upper implication; all off-row lower bounds.
    noff = int(off.sum())
    nown_endpoint = int(own.sum()) if endpoint else 0
    C = lil_matrix((1+2*m+noff+nown_endpoint, 2*m+1))
    lo = np.full(C.shape[0], -np.inf)
    hi = np.zeros(C.shape[0])
    C[0, :m] = np.ones(m)
    lo[0] = hi[0] = 1
    for r in range(m):
        C[1+r, r] = 1
        C[1+r, m+1+r] = -1
        C[1+m+r, :m] = G[r]
        C[1+m+r, m] = -1
        C[1+m+r, m+1+r] = n
        hi[1+m+r] = n
    for p, r in enumerate(np.flatnonzero(off)):
        rr = 1+2*m+p
        C[rr, :m] = G[r]
        C[rr, m] = -1
        lo[rr] = 0
        hi[rr] = np.inf
    if endpoint:
        for p, r in enumerate(np.flatnonzero(own)):
            rr = 1+2*m+noff+p
            C[rr, :m] = -G[r]
            C[rr, m] = 1
            C[rr, m+1+r] = n
            hi[rr] = n
    result = milp(c, integrality=integrality, bounds=Bounds(lower, upper),
                  constraints=LinearConstraint(C.tocsr(), lo, hi),
                  options={"time_limit": seconds, "mip_rel_gap": gap, "presolve": False})
    report = {"owner": i, "status": int(result.status), "message": result.message,
              "elapsed": time.monotonic()-started, "relaxation_only": relax,
              "endpoint_only": endpoint,
              "presolve": False,
              "allowed_support": allowed_support,
              "mip_gap": getattr(result, "mip_gap", None),
              "nodes": getattr(result, "mip_node_count", None)}
    bound = getattr(result, "mip_dual_bound", None)
    report["reported_mip_dual_bound"] = float(bound) if bound is not None and np.isfinite(bound) else None
    report["theta_upper"] = min(1., float(-bound)) if bound is not None and np.isfinite(bound) else 1.0
    if result.x is None:
        if baseline is None:
            report.update({"theta": None, "valid": False})
            return report
        alpha, t = baseline
        report["selected_witness_source"] = "full_projection_baseline"
    else:
        alpha, t = result.x[:m], float(result.x[m])
        report["selected_witness_source"] = "milp_support_lp"
    if not relax and result.x is not None:
        # Resolve its support as an ordinary LP to remove MILP feasibility noise.
        support = alpha > 1e-8
        eq_rows = [np.r_[np.ones(m), 0]]
        eq_rhs = [1.]
        ub_rows, ub_rhs = [], []
        for r in range(m):
            row = np.r_[G[r], -1.]
            if off[r]:
                ub_rows.append(-row)
                ub_rhs.append(0.)
            if support[r] and (off[r] or endpoint):
                eq_rows.append(row)
                eq_rhs.append(0.)
            elif support[r]:
                ub_rows.append(row)
                ub_rhs.append(0.)
        lp = linprog(np.r_[-A[:, i], 0], A_ub=np.array(ub_rows), b_ub=np.array(ub_rhs),
                     A_eq=np.array(eq_rows), b_eq=np.array(eq_rhs),
                     bounds=[(0, 1 if yes else 0) for yes in support]+[(1/n, n)], method="highs",
                     options={"presolve": False})
        report["support_lp_success"] = bool(lp.success)
        if lp.success:
            alpha, t = lp.x[:m], float(lp.x[m])
    report["milp_theta"] = float((A.T@alpha)[i]) if result.x is not None else None
    if baseline is not None and (A.T@baseline[0])[i] > (A.T@alpha)[i]+1e-8:
        alpha, t = baseline
        report["selected_witness_source"] = "full_projection_baseline"
    qhat = A.T@alpha
    q = qhat/t
    lam = alpha/t
    rhs = np.where(off, 1., np.where(alpha > 1e-8, A@q, 0.))
    residuals = {"mass": float(abs(alpha.sum()-1)),
                 "nonnegative": float(max(0, -min(alpha), -min(q))),
                 "rhs": float(max(0, max(rhs)-1, -min(rhs))),
                 "primal": float(max(0, max(rhs-A@q))),
                 "stationarity": float(max(abs(q-A.T@lam))),
                 "complementarity": float(max(abs(lam*(A@q-rhs))))}
    theta = float(qhat[i])
    report.update({"theta": theta, "alpha": alpha.tolist(), "t": t,
                   "lambda": lam.tolist(), "q": q.tolist(), "rhs": rhs.tolist(),
                   "L": float(sum(lam)), "norm2": float(q@q),
                   "support": list(map(int, np.flatnonzero(alpha > 1e-8))),
                   "residuals": residuals,
                   "valid": not relax and max(residuals.values()) < 2e-7,
                   "exact": exact_witness(A, i, alpha, t) if not relax else None})
    report["solver_bound_contradiction"] = bool(theta > report["theta_upper"]+2e-7)
    return report


def analyze(A, name, transitive=False, seconds=30, gap=0.0, owners=None, endpoint=False,
            owner_generators=None, allowed_support=None):
    A = np.asarray(A, dtype=float)
    if A.ndim != 2 or not len(A) or not np.isin(A, [0, 1]).all() or min(A.sum(axis=1)) == 0:
        raise ValueError("need a nonempty binary matrix with nonempty rows")
    symmetry = None
    if transitive:
        # Checked owner permutations must preserve rows and act transitively.
        # Regular degrees alone cannot justify multiplying owner 0 by n.
        n = A.shape[1]
        if owner_generators is None:
            owner_generators = [[(j+1) % n for j in range(n)]]
        lookup = {tuple(row): r for r, row in enumerate(A.astype(int).tolist())}
        row_permutations = []
        for generator in owner_generators:
            if sorted(generator) != list(range(n)):
                raise ValueError("owner generator is not a permutation")
            permutation = []
            for row in A:
                moved = np.zeros(n, dtype=int)
                moved[generator] = row.astype(int)
                permutation.append(lookup.get(tuple(moved)))
            if any(r is None for r in permutation):
                raise ValueError("claimed owner permutation does not preserve full row set")
            row_permutations.append(permutation)
        orbit, frontier = {0}, [0]
        while frontier:
            j = frontier.pop()
            for generator in owner_generators:
                image = generator[j]
                if image not in orbit:
                    orbit.add(image)
                    frontier.append(image)
        if len(orbit) != n:
            raise ValueError("verified automorphisms do not act transitively")
        symmetry = {"type": "explicit transitive owner automorphism generators",
                    "owner_generators": owner_generators, "row_permutations": row_permutations,
                    "orbit_size": len(orbit), "verified": True}
    full = full_projection(A, transitive=transitive)
    n = A.shape[1]
    owners = [0] if transitive else (range(n) if owners is None else owners)
    full_lam = np.array(full["lambda"])
    full_mass = float(sum(full_lam))
    baseline = (full_lam/full_mass, 1/full_mass) if full["valid"] and full_mass > 0 else None
    answers = [optimize_owner(A, int(i), seconds, gap, endpoint=endpoint, baseline=baseline,
                              allowed_support=allowed_support) for i in owners]
    valid = full["valid"] and all(a["valid"] for a in answers)
    complete = transitive or len(answers) == n
    h = None
    if valid and complete:
        h = full["rho"] * sum(a["theta"]**2 for a in answers) * (n if transitive else 1)
    hup = full["rho"] * sum(a["theta_upper"]**2 for a in answers) * (n if transitive else 1) if complete else None
    return {"name": name, "n": n, "m": len(A), "rows": row_lists(A),
            "transitive": transitive, "symmetry_certificate": symmetry, "full": full, "owners": answers,
            "H": h, "H_solver_upper": hup, "all_witnesses_valid": valid,
            "all_milp_optimal": all(a["status"] == 0 and not a.get("solver_bound_contradiction", False) for a in answers),
            "exact_witnesses": all(a.get("exact", {}).get("certified", False) for a in answers),
            "complete_owner_set": complete,
            "strict_candidate": h is not None and h > 2+1e-7}


def benchmark():
    out = []
    for k in (3, 4, 6, 10, 20):
        n, D = 2*k-1, 3*k+2
        A = interval(n, k)
        # Recover rows by set, since cyclic() lexically orders them.
        lam_by_set = {}
        for r, w in ((0, 2), (k, 2), (1, 1), (k-1, 1)):
            S = tuple(sorted((r+j) % n for j in range(k)))
            lam_by_set[S] = lam_by_set.get(S, F(0)) + F(w, D)
        lam = [lam_by_set.get(tuple(S), F(0)) for S in row_lists(A)]
        L = sum(lam)
        alpha, t = [x/L for x in lam], 1/L
        exact = exact_witness(A, 0, alpha, t)
        assert exact["certified"], exact
        assert F(exact["theta"]) == F(2, 3)
        out.append({"k": k, "n": n, "rho": str(F(n, k*k)),
                    "theta": "2/3", "H": str(F(4*n*n, 9*k*k)), "exact": exact})
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["benchmark", "intervals", "circulants", "perturbations", "json"], default="benchmark")
    parser.add_argument("--output", required=True)
    parser.add_argument("--seconds", type=float, default=20)
    parser.add_argument("--gap", type=float, default=0.)
    parser.add_argument("--budget", type=float, default=600)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--input")
    parser.add_argument("--endpoint", action="store_true", help="compare against incident-row deletion only")
    args = parser.parse_args()
    started = time.monotonic()
    reports = []
    known = benchmark()
    todo = []
    rng = np.random.default_rng(args.seed)
    if args.mode == "benchmark":
        todo = [(f"interval_calibration_k{k}", interval(2*k-1, k), True) for k in (3, 4, 6, 10)]
    elif args.mode == "intervals":
        # The 2k-1 family has theta=2/3 witnesses; vary the circumference around it.
        for k in (3, 4, 5, 6, 8, 10, 14, 20, 30):
            for delta in (-2, -1, 0, 1, 2):
                n = 2*k+delta
                if n > k:
                    todo.append((f"interval_n{n}_k{k}", interval(n, k), True))
    elif args.mode == "circulants":
        # Single-gap, interlaced, and union-orbit incidence disrupt interval overlap.
        for n in (7, 9, 11, 13, 15, 19, 23):
            k = (n+1)//2
            patterns = [("gap", list(range(k-1))+[k]),
                        ("two_gap", list(range(k-2))+[k, k+1]),
                        ("interlace", [(2*j) % n for j in range(k)]),
                        ("two_arcs", list(range((k+1)//2))+list(range(k, k+k//2)))]
            for label, seed in patterns:
                todo.append((f"cyclic_{label}_n{n}_k{k}", cyclic(n, [seed]), True))
            for smaller in (k-1, k-2):
                if smaller > 1:
                    todo.append((f"mixed_orbits_n{n}_k{smaller}_{k}",
                                 cyclic(n, [range(smaller), patterns[0][1]]), True))
            for r in range(3):
                seed = sorted(rng.choice(n, size=k, replace=False).tolist())
                todo.append((f"random_cyclic_n{n}_k{k}_r{r}", cyclic(n, [seed]), True))
    elif args.mode == "perturbations":
        # Start near the known family and make one localized incidence change.
        for k in (3, 4, 5, 6, 8):
            A = interval(2*k-1, k)
            for r in range(3):
                B = A.copy()
                zero = np.flatnonzero(B[r] == 0)
                one = np.flatnonzero(B[r] == 1)
                B[r, rng.choice(zero)] = 1
                B[r, rng.choice(one)] = 0
                todo.append((f"interval_swap_k{k}_r{r}", B, False))
            todo.append((f"interval_delete_row_k{k}", A[1:], False))
    else:
        supplied = json.loads(Path(args.input).read_text())
        for case in supplied:
            n = case["n"]
            A = np.array([[int(j in row) for j in range(n)] for row in case["rows"]], dtype=float)
            todo.append((case["name"], A, case.get("transitive", False), case))
    payload = {"discovery_only": True, "model": __doc__, "arguments": vars(args),
               "benchmarks": known, "results": reports, "planned_cases": len(todo),
               "pending_cases": [t[0] for t in todo]}
    for entry in todo:
        name, A, transitive = entry[:3]
        extra = entry[3] if len(entry) > 3 else {}
        if time.monotonic()-started >= args.budget:
            break
        report = analyze(A, name, transitive, args.seconds, args.gap, endpoint=args.endpoint,
                         owner_generators=extra.get("owner_generators"),
                         allowed_support=extra.get("allowed_support"))
        reports.append(report)
        payload["pending_cases"].remove(name)
        payload["elapsed"] = time.monotonic()-started
        payload["timed_out_cases"] = [r["name"] for r in reports if any(o["status"] == 1 for o in r["owners"])]
        payload["nonoptimal_cases"] = [r["name"] for r in reports if not r["all_milp_optimal"]]
        Path(args.output).write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
        print(json.dumps({key: report[key] for key in ("name", "n", "m", "H", "H_solver_upper", "all_milp_optimal", "exact_witnesses", "strict_candidate")}), flush=True)
        if report["strict_candidate"]:
            print("STRICT CANDIDATE: stop and independently certify", flush=True)
            break
    payload["elapsed"] = time.monotonic()-started
    payload["timed_out_cases"] = [r["name"] for r in reports if any(o["status"] == 1 for o in r["owners"])]
    payload["nonoptimal_cases"] = [r["name"] for r in reports if not r["all_milp_optimal"]]
    Path(args.output).write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")


if __name__ == "__main__":
    main()
