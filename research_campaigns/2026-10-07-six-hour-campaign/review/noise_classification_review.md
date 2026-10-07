**Provisional verdict: no substantive findings in reviewed scope.** Both documents check out line-by-line; the most delicate steps (the atom-zero mean gap `nu < mu*s` with the factor `s` in the high limit, and the uniform-in-q bound via `q log(1/q) <= 1/e` with explicit floor/ceiling slack) are correct as written.

## Findings

**None of severity high or medium.** Low-severity notes/observations only:

1. **(Low, FIXED_NOISE_CLASSIFICATION §1, lines 33–35)** Correct, but the Hoeffding step silently uses `u >= 1` to pass from `(d/u)Pr(S<=u)` to `d exp(-mu^2 d/2)`. This is established at line 32 ("u=1/x>=1") so no gap; flagging only that the dependency is not restated. The maximization `d e^{-mu^2 d/2} <= 2/(e mu^2)` is correct (max at `d=2/mu^2`), and `sum_C w_h^2 <= d` follows from `w_h<=1`. The case split is exhaustive. Summing `D_e/D(C)` over `e in C` then over `C` gives exactly `K`.

2. **(Low, §4, lines 73–78)** Verified algebra: `a nu + b mu = 3mu/4 + nu/(4s) = mu - d/4 = mu - 10delta` exactly; `a mu s - mu = mu s d/(2nu) > d/2 = 20delta` since `nu < mu s`. The factor `s` in the limit is correctly handled (X'=0 kills the min). The Bernoulli degeneracy `nu = s^2 = mu s` is correctly noted. The simple-DAG transfer to `V=min(X1,X2)` preserves "nonconstant positive conditional" and requires only `X_e<=1`, `X_g>=0` on unsplit edges — consistent with the audited obstruction.

3. **(Low, §2 simple DAGs, lines 50–54)** Lowering one copy of a path creates a 4-way tie among local cuts at score `t+1/2`; correctness relies on the first-priority local cut being among tied minimizers and containing the lowered owner. This is stated and valid for every fixed priority. Note `T` drops to `t+1/2` under the underreport; other diamonds' effective caps stay `1/2` since `T>=1/2`. No error.

4. **(Low, BERNOULLI_SHARP_CONSTANT §A, line 23)** `1 - a/2 - b/2 >= (1-b)/2` uses only `a=(1-q^2)^K <= 1`; the subsequent `(1-q)^{-2K} >= 1+2Kq` is Bernoulli's inequality. Correct.

5. **(Low, §B, lines 37–44)** Verified: `hm <= L-sqrt L` gives `Nq^m >= e^{sqrt L}`; `hR >= sqrt L` gives `q^R <= e^{-sqrt L}`; the floor loses at most 1, absorbed by `h <= 2 log L`. `m/q >= (L-sqrt L-2log L)/(q log(1/q)) >= e(...)`. At `L=16`: `(16-4)/(2 log 16) ≈ 2.16`, so `m>=2` and the numerator `12 - 5.55 > 0`. Cutoff case (6): `K>=L^2` gives `K/(1+2K/L^2) >= L^2/3 >= eL` for `L>=16`. Both constructions have exactly `K` structural cuts, so the `sup_G` is legitimately over the same `K`.

6. **(Observation)** Priority independence holds because on the lower-bound events all minimizers share identical closed D-mass (`m` in §B, `1` or `1/2` in §A). Identity (2) is correctly derived from `1{B_e=0}=1-B_e`.

**Quantifier/limit check:** No overreach found. The `o(1)` in (1) of BERNOULLI_SHARP_CONSTANT depends only on `K` in both directions; the line-9 remark "q may depend arbitrarily on K" is justified. The classification headline (lines 11–23) matches the section-level results, including the `Omega(log K)` simple-DAG zero-noise bound (`K=2^{m+1}`). Both files properly disclaim unrestricted mechanism impossibility and the simple-DAG sharp-e lower.

## Scope limitations
- Relied on FIXED_NOISE_OBSTRUCTION's module cut structure, `K` counts (2),(7), and separation event (previously audited) rather than re-deriving them.
- Relied on BERNOULLI_LOG_BOUND (1),(iii) for the upper bound.
- No execution; no files outside the packet inspected.

## Verdict
**No findings in reviewed scope.** Both class-level claims are supported by the supplied text; the documents correctly refrain from unrestricted impossibility or simple-DAG sharp-constant claims.
